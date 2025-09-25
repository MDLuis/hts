from .base import Source
from .models import GeneralNote, SectionNote, ChapterNote, Note, AdditionalUSNotes
import requests, pdfplumber, json, re

BASE_URL = "https://hts.usitc.gov/reststop/file"

class GeneralNotesSource(Source):
    """
    Source class to fetch & parse one specific General Note.
    """
    # Fetch
    def fetch(self, note_num: int, pdf_path: str = None) -> str:
        """
        Download a specific General Note PDF.

        Args:
            note_num (int): The General Note number to download.
            pdf_path (str, optional): File path to save the PDF.
                Defaults to 'general_note_{note_num}.pdf'.

        Returns:
            str: Path to the saved PDF file.
        """
        if pdf_path is None:
            pdf_path = f"general_note_{note_num}.pdf"

        params = {
            "filename": f"General Note {note_num}",
            "release": "currentRelease"
        }
        resp = requests.get(BASE_URL, params=params, stream=True)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return pdf_path

    # Parse
    def parse(self, pdf_path: str, note_num: int) -> GeneralNote:
        """
        Parse one General Note PDF into a `GeneralNote` object.

        Scans line by line for a more robust approach to inconsistent layouts
        (e.g., titles on their own line or dot without space).

        Args:
            pdf_path (str): Path to the General Note PDF file.
            note_num (int): The General Note number to parse.

        Returns:
            GeneralNote: Structured representation of the General Note.
        """
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]

        # Clean out headers/footers
        header_re = re.compile(
            r"(harmonized tariff schedule|annotated for statistical reporting|revision\s*\d+|\bgn\s*p\.?\d+\b)",
            re.I
        )

        cleaned_lines = []
        for page in pages:
            for ln in page.splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                if header_re.search(ln):
                    continue
                if re.fullmatch(r"\d+", ln):  # pure page numbers
                    continue
                cleaned_lines.append(ln)

        # Now find where this note begins
        note_start_idx = None
        note_pattern = re.compile(rf"^(General\s+Note\s*)?{note_num}[\.\)]?\b", re.I)
        for i, ln in enumerate(cleaned_lines):
            if note_pattern.match(ln):
                note_start_idx = i
                break
        if note_start_idx is None:
            raise ValueError(f"Could not find General Note {note_num} start")

        note_lines = cleaned_lines[note_start_idx:]

        # Strip the leading "General Note {n}" or "{n}" from the first line
        first_line = re.sub(
            rf"^(General\s+Note\s*)?{note_num}[\.\)]?\s*", "", note_lines[0], flags=re.I
        ).strip()

        # If first line is now empty, take the next non-empty line as part of the title
        if not first_line and len(note_lines) > 1:
            first_line = note_lines[1].strip()
            rest_lines = note_lines[2:]
        else:
            rest_lines = note_lines[1:]

        # If first_line doesn’t contain '.' or ')', try concatenating next line to form full title
        if not re.search(r"[.)]", first_line) and rest_lines:
            combined = first_line + " " + rest_lines[0]
            if re.search(r"[.)]", combined):
                first_line = combined
                rest_lines = rest_lines[1:]

        # Split at '.' or ')' for title vs body_start
        mtitle = re.match(r"(?P<title>.+?)[\.)]\s*(?P<rest>.*)", first_line)
        if mtitle:
            title = mtitle.group("title").strip()
            body_start = mtitle.group("rest").strip()
        else:
            title = first_line.strip()
            body_start = ""

        body_lines = []
        if body_start:
            body_lines.append(body_start)
        body_lines.extend(rest_lines)

        body = re.sub(r"\s+", " ", " ".join(body_lines)).strip()
        title = re.sub(r"\s+", " ", title).strip()

        return GeneralNote(note_number=str(note_num), title=title, text=body)


    # Save
    def save(self, data: GeneralNote, filepath: str = None):
        """
        Save a `GeneralNote` or a list of `GeneralNote` objects to JSON.

        Args:
            data (GeneralNote or list[GeneralNote]): Note data to save.
            filepath (str, optional): Destination file path. Defaults to 'general_notes.json'.
        """
        if filepath is None:
            filepath = "general_notes.json"

        if isinstance(data, list):
            payload = [d.model_dump() for d in data]
        else:
            payload = data.model_dump()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

# Section Notes
class SectionNotesSource(Source):
    """
    Source class to fetch, parse, and save Section Notes.
    """
    def fetch(self, chapter_num: int, filepath: str = None) -> str:
        """
        Download the PDF for a given chapter number.

        Args:
            chapter_num (int): The chapter number containing the section note.
            filepath (str, optional): Destination PDF file path.
                Defaults to 'chapter_{chapter_num}.pdf'.

        Returns:
            str: Path to the saved PDF file.
        """
        if filepath is None:
            filepath = f"chapter_{chapter_num}.pdf"
        url = f"{BASE_URL}?release=currentRelease&filename=Chapter%20{chapter_num}"
        r = requests.get(url)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        return filepath

    def parse(self, pdf_path: str) -> SectionNote:
        """
        Extracts section notes from the PDF, automatically detecting the section number.

        Args:
            pdf_path (str): Path to the Section Note PDF file.

        Returns:
            SectionNote: Structured representation of the section note.
        """
        # 1. Read all text from PDF
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        # 2. Automatically detect section roman numeral (I, II, III...)
        m_section = re.search(r"SECTION\s+([IVXLCDM]+)", text, re.I)
        section_number = m_section.group(1) if m_section else "?"

        # 3. Clip text before first CHAPTER to avoid chapter content
        m_clip = re.search(rf"(SECTION\s+{section_number}.*?)(?=CHAPTER\s+\d+)", text, re.S | re.I)
        section_text = m_clip.group(1) if m_clip else text

        # 4. Extract individual notes as Note objects
        note_pattern = re.compile(r"Notes?\s*(\d+)\.\s*(.*?)(?=(?:\n\d+\.)|\Z)", re.S | re.I)
        notes: list[Note] = []
        for match in note_pattern.finditer(section_text):
            notes.append(
                Note(
                    note_number=match.group(1),
                    text=match.group(2).strip()
                )
            )

        return SectionNote(section_number=section_number, notes=notes)

    def save(self, data: list[SectionNote], filepath: str = None):
        """
        Save a list of `SectionNote` objects to JSON.

        Args:
            data (list[SectionNote]): Section note data to save.
            filepath (str, optional): Destination JSON file path.
                Defaults to 'section_notes.json'.
        """
        if filepath is None:
            filepath = "section_notes.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in data], f, ensure_ascii=False, indent=2)

class ChapterNotesSource(Source):
    """
    Source class to fetch, parse, and save Chapter Notes.
    """
    def fetch(self, chapter_num: int, pdf_path: str = None) -> str:
        """
        Download a chapter PDF.

        Args:
            chapter_num (int): Chapter number to download.
            pdf_path (str, optional): Destination file path.
                Defaults to 'chapter_{chapter_num}.pdf'.

        Returns:
            str: Path to the saved PDF file.
        """
        if pdf_path is None:
            pdf_path = f"chapter_{chapter_num}.pdf"
        url = f"{BASE_URL}?release=currentRelease&filename=Chapter%20{chapter_num}"
        r = requests.get(url)
        r.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(r.content)
        return pdf_path

    def parse(self, pdf_path: str) -> ChapterNote:
        """
        Extract chapter notes from a single-chapter PDF.

        Skips anything before 'CHAPTER X' to avoid section notes.
        Stops at Additional U.S. Notes, Subheading Notes, Statistical Notes,
        or table headers.

        Args:
            pdf_path (str): Path to the Chapter PDF file.

        Returns:
            ChapterNote: Structured representation of the chapter notes.
        """
        # 1. Read all text
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        # 2. Detect chapter number
        m_chapter = re.search(r"CHAPTER\s+(\d+)", text, re.I)
        if not m_chapter:
            return ChapterNote(chapter_number="?", notes=[])
        chapter_number = m_chapter.group(1)

        # 3. Trim everything before "CHAPTER X"
        text_after_chapter = text[m_chapter.start():]

        # 4. Find notes block, stop at any known marker or table header
        m_notes_block = re.search(
            r"Notes?\s*(.*?)(?=(?:\nAdditional\s+U\.S\.|\nSubheading\s+Notes|\nStatistical\s+Notes|\nHeading/|\nRates\s+of\s+Duty|\Z))",
            text_after_chapter,
            re.S | re.I
        )
        if not m_notes_block:
            return ChapterNote(chapter_number=chapter_number, notes=[])

        notes_block = m_notes_block.group(1)

        # 5. Extract numbered notes as Note objects
        note_pattern = re.compile(
            r"(\d+)\.\s*(.*?)(?=(?:\n\d+\.)|(?:\nAdditional\s+U\.S\.)|(?:\nSubheading\s+Notes)|(?:\nStatistical\s+Notes)|(?:\nHeading/)|(?:\nRates\s+of\s+Duty)|\Z)",
            re.S | re.I
        )

        notes: list[Note] = []
        for match in note_pattern.finditer(notes_block):
            raw_text = match.group(2).strip()
            cut = re.split(
                r"\n(?:Heading/|Rates\s+of\s+Duty|Subheading\s+Notes|Statistical\s+Notes|Additional\s+U\.S\.)",
                raw_text, 1, flags=re.I
            )
            clean_text = cut[0].strip()
            notes.append(
                Note(
                    note_number=match.group(1),
                    text=clean_text
                )
            )

        return ChapterNote(chapter_number=chapter_number, notes=notes)

    def save(self, data: list[ChapterNote], filepath: str = None):
        """
        Save a list of `ChapterNote` objects to JSON.

        Args:
            data (list[ChapterNote]): Chapter note data to save.
            filepath (str, optional): Destination JSON file path.
                Defaults to 'chapter_notes.json'.
        """
        """Save a list of ChapterNote objects to JSON."""
        if filepath is None:
            filepath = "chapter_notes.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in data], f, ensure_ascii=False, indent=2)

class AdditionalUSNotesSource(Source):
    """
    Source class to fetch, parse, and save Additional U.S. Notes.
    """
    def fetch(self, chapter_num: int, pdf_path: str = None) -> str:
        """
        Download a chapter PDF.
        Args:
            chapter_num (int): Chapter number to download.
            pdf_path (str, optional): Destination file path.
                Defaults to 'chapter_{chapter_num}.pdf'.
        Returns:
            str: Path to the saved PDF file.
        """
        if pdf_path is None:
            pdf_path = f"chapter_{chapter_num}.pdf"
        url = f"{BASE_URL}?release=currentRelease&filename=Chapter%20{chapter_num}"
        r = requests.get(url)
        r.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(r.content)
        return pdf_path

    def parse(self, pdf_path: str) -> AdditionalUSNotes:
        """
        Extract Additional U.S. Notes from a single-chapter PDF.

        Only triggers if the exact case-sensitive heading "Additional U.S. Notes"
        or "Additional U.S. Note" appears.
        Stops at Subheading Notes, Statistical Notes, table headers, or EOF.
        Splits notes only on lines starting with small integer note numbers
        followed by a dot and whitespace (e.g. "7. The ...") to avoid treating
        HS codes like "1701.91.44" as note boundaries.

        Args:
            pdf_path (str): Path to the chapter PDF file.

        Returns:
            AdditionalUSNotes: Structured representation of the Additional U.S. Notes,
                or None if no such section is found.
        """
        # 1) read pdf text
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        # 2) detect chapter number
        m_chap = re.search(r"^\s*CHAPTER\s+(\d+)", text, re.I | re.M)
        chapter_number = m_chap.group(1) if m_chap else "?"

        # 3) find exact case-sensitive heading (plural or singular)
        idx = text.find("Additional U.S. Notes")
        heading = "Additional U.S. Notes"
        if idx == -1:
            idx = text.find("Additional U.S. Note")
            heading = "Additional U.S. Note"
        if idx == -1:
            return None  # no Additional U.S. Notes/Note in this chapter

        # slice text after the heading
        text_after = text[idx + len(heading):]

        # 4) stop at next known section/table markers (case-insensitive for markers)
        stop_re = re.compile(r"(?=\n(Subheading\s+Notes?|Statistical\s+Notes?|Heading/|Rates\s+of\s+Duty|\Z))", re.I)
        m_stop = stop_re.search(text_after)
        if m_stop:
            notes_block = text_after[:m_stop.start()]
        else:
            notes_block = text_after

        # 5) Normalize line breaks a bit
        #    Keep line breaks so we can split on line-started note numbers, but normalize multiple blank lines.
        notes_block = re.sub(r"\r\n?", "\n", notes_block)
        notes_block = re.sub(r"\n{2,}", "\n\n", notes_block)

        # 6) Split into note-parts by looking for a newline followed by:
        #    optional whitespace, 1-3 digits, dot, whitespace  -> this avoids HS codes like 1701.91.44
        parts = re.split(r"\n(?=\s*\d{1,3}\.\s)", notes_block, flags=re.M)

        notes = []
        note_re = re.compile(r"^\s*(\d{1,3})\.\s*(.*)", re.S | re.M)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = note_re.match(part)
            if not m:
                # skip fragments that don't look like "N. text"
                continue
            number = m.group(1)
            body = m.group(2).strip()
            # Final safety cut: remove any trailing table markers accidentally included
            body = re.split(r"\n(?:Heading/|Rates\s+of\s+Duty|Subheading\s+Notes?|Statistical\s+Notes?|Additional\s+U\.S\.)", body, 1, flags=re.I)[0].strip()
            notes.append(Note(note_number=number, text=body))
        if not notes:
            return None

        return AdditionalUSNotes(chapter_number=chapter_number, notes=notes)

    def save(self, data: list[AdditionalUSNotes], filepath: str = None):
        """
        Save a list of AdditionalUSNotes objects to JSON.

        Args:
            data (list[AdditionalUSNotes]): Additional U.S. Notes data to save.
            filepath (str, optional): Destination JSON file path.
                Defaults to 'additional_us_notes.json'.
        """
        if filepath is None:
            filepath = "additional_us_notes.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([d.model_dump() for d in data], f, ensure_ascii=False, indent=2)
