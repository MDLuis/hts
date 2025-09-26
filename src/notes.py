from .base import Source
from .models import GeneralNote, SectionNote, ChapterNote, Note, AdditionalUSNotes
import requests, pdfplumber, json, re
from datetime import date
from pathlib import Path

BASE_URL = "https://hts.usitc.gov/reststop/file"
pdf_ch = Path("pdf/chapters")

def versioning(data, base_filename: str, folder: str = "pdf", version: str | None = None) -> str:
    """
    Save data to a JSON file with versioned filename and 'latest' copy.

    Args:
        data: A list of Pydantic models or a single model.
        base_filename: Base name without extension (e.g. 'general_notes').
        folder: Subfolder under 'data/' where files will be stored.
        version: Optional version string. Defaults to today's date.

    Returns:
        str: Path to the versioned file.
    """
    version = version or date.today().isoformat()
    out_dir = Path(folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    versioned_path = out_dir / f"{base_filename}_v{version}.json"
    latest_path = out_dir / f"{base_filename}_latest.json"

    # convert to list of dicts or dict
    if isinstance(data, list):
        payload = [d.model_dump() for d in data]
    else:
        payload = data.model_dump()

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    versioned_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")

    return str(versioned_path)

def download_chapter_pdf(chapter_num: int, filename: str = None) -> str:
    """
    Download a chapter PDF from the HTS site and save it under pdf.

    Args:
        chapter_num (int): Chapter number to download.
        filename (str, optional): Custom PDF filename.
            Defaults to 'chapter_{chapter_num}.pdf'.

    Returns:
        str: Full path to the saved PDF file.
    """
    if filename is None:
        filename = f"chapter_{chapter_num}.pdf"
    pdf_path = pdf_ch / filename
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    url = f"{BASE_URL}?release=currentRelease&filename=Chapter%20{chapter_num}"
    r = requests.get(url)
    r.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(r.content)

    return str(pdf_path)

class GeneralNotesSource(Source):
    """
    Source class to fetch & parse one specific General Note.
    """
    # Fetch
    def fetch(self, note_num: int, pdf_path: str = None) -> str:
        """
        Download a specific General Note PDF to the default folder.
        """
        # ensure folder exists
        pdf_dir = Path("pdf/general_notes")
        pdf_dir.mkdir(parents=True, exist_ok=True)

        # if user didn’t pass a path, build one automatically
        if pdf_path is None:
            pdf_path = pdf_dir / f"general_note_{note_num}.pdf"
        else:
            pdf_path = Path(pdf_path)

        params = {
            "filename": f"General Note {note_num}",
            "release": "currentRelease"
        }
        resp = requests.get(BASE_URL, params=params, stream=True)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return str(pdf_path)

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
    def save(self, data: GeneralNote | list[GeneralNote], filepath: str = None, version: str = None):
        base_filename = filepath or "general_notes"
        return versioning(data, base_filename, folder="data/notes/general", version=version)
        
# Section Notes
class SectionNotesSource(Source):
    """
    Source class to fetch, parse, and save Section Notes.
    """
    def fetch(self, chapter_num: int, filename: str = None) -> str:
        return download_chapter_pdf(chapter_num, filename)

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

    def save(self, data: list[SectionNote], filepath: str = None, version: str = None):
        base_filename = filepath or "section_notes"
        return versioning(data, base_filename, folder="data/notes/section", version=version)

class ChapterNotesSource(Source):
    """
    Source class to fetch, parse, and save Chapter Notes.
    """
    def fetch(self, chapter_num: int, filename: str = None) -> str:
        return download_chapter_pdf(chapter_num, filename)

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

    def save(self, data: list[ChapterNote], filepath: str = None, version: str = None):
        base_filename = filepath or "chapter_notes"
        return versioning(data, base_filename, folder="data/notes/chapter", version=version)

class AdditionalUSNotesSource(Source):
    """
    Source class to fetch, parse, and save Additional U.S. Notes.
    """
    def fetch(self, chapter_num: int, filename: str = None) -> str:
        return download_chapter_pdf(chapter_num, filename)

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

    def save(self, data: list[AdditionalUSNotes], filepath: str = None, version: str = None):
        base_filename = filepath or "additional_us_notes"
        return versioning(data, base_filename, folder="data/notes/additional", version=version)
