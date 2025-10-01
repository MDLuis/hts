from .base import Source
from .models import GeneralNote, SectionNote, ChapterNote, Note, AdditionalUSNotes
import requests, pdfplumber, json, re
from datetime import date
from pathlib import Path
from typing import Optional

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
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        # --- 1) Clean headers/footers ---
        header_re = re.compile(
            r"(harmonized tariff schedule|annotated for statistical reporting|revision\s*\d+|\bgn\s*p\.?\d+\b)",
            re.I
        )
        cleaned_lines = []
        for page in pages:
            for ln in page.splitlines():
                ln = ln.strip()
                if not ln or header_re.search(ln):
                    continue
                if re.fullmatch(r"\d+", ln):  # skip page numbers
                    continue
                cleaned_lines.append(ln)

        # --- 2) Locate note start ---
        note_start_idx = None
        for i, ln in enumerate(cleaned_lines):
            if re.search(rf"{note_num}", ln):
                note_start_idx = i
                break
        if note_start_idx is None:
            raise ValueError(f"Could not find General Note {note_num} start")

        note_lines = cleaned_lines[note_start_idx:]

        # --- 3) Find the actual title ---
        title_line = None
        body_start_idx = 0

        for i, ln in enumerate(note_lines):
            ln_clean = re.sub(
                rf"^(?:General\s+Notes?\s*)?{note_num}[\.\)]?\s*", "", ln, flags=re.I
            ).strip()
            if ln_clean and not re.match(r"^General\s+Notes?$", ln_clean, re.I):
                title_line = ln_clean
                body_start_idx = i + 1
                break

        if title_line is None:
            title_line = ""
            body_start_idx = 1

        # --- 4) Split title at first '.' or ')' ---
        m_split = re.match(r"^(.*?[\.\)])\s*(.*)$", title_line)
        if m_split:
            title = m_split.group(1).strip()
            # Everything after the first dot/parenthesis goes to the body
            body_lines = [m_split.group(2).strip()] + note_lines[body_start_idx:]
        else:
            title = title_line
            body_lines = note_lines[body_start_idx:]

        # --- 5) Build body ---
        body_lines = [ln for ln in body_lines if not re.match(r"^General\s+Notes?$", ln, re.I)]

        body = " ".join(body_lines)
        body = re.sub(r"\s*\n\s*", " ", body)
        body = re.sub(r"\s+", " ", body).strip()
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

    def parse(self, pdf_path: str) -> Optional[SectionNote]:
        """
        Extracts section notes from the PDF, automatically detecting the section number.
        Stops parsing if the beginning of the document doesn't mention a section.
        """
        # Extract all text from the PDF
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return None

            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

            # Normalize whitespace
            text = re.sub(r"\r\n?", " ", text)
            text = re.sub(r"\n+", " ", text).strip()

        # Check the beginning of the document for SECTION header
        beginning_snippet = text[:200]
        m_begin_section = re.search(r"SECTION\s+([IVXLCDM]+)", beginning_snippet, re.I)
        if not m_begin_section:
            # No section at the start = skip parsing
            return None

        section_number = m_begin_section.group(1)

        # Grab the block between SECTION and next big header or footer
        m_clip = re.search(
            rf"(SECTION\s+{section_number}.*?)(?=(Subheading\s+Notes|Additional\s+U\.S\.|CHAPTER\s+\d+|Harmonized Tariff Schedule of the United States))",
            text,
            re.S | re.I,
        )
        section_text = m_clip.group(1) if m_clip else ""

        # Extract all numbered notes
        note_pattern = re.compile(r"(\d+)\.\s*(.*?)(?=(\d+\.|$))", re.S)
        notes: list[Note] = []
        for match in note_pattern.finditer(section_text):
            note_number = match.group(1)
            note_text = match.group(2).strip()
            if note_text:
                notes.append(Note(note_number=note_number, text=note_text))

        if not notes:
            return None

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
        or table headers. Automatically removes repeated headers/footers.
        """
        # 1. Read all text, page by page
        lines_per_page = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                bbox = (0, 50, page.width, page.height - 50)
                t = page.within_bbox(bbox).extract_text()
                if t:
                    lines_per_page.append(t.split("\n"))

        if not lines_per_page:
            return ChapterNote(chapter_number="?", notes=[])

        # 2. Detect repeated first and last lines manually
        def find_repeated(lines_list):
            repeated = []
            checked = set()
            for line in lines_list:
                if line in checked:
                    continue
                count = sum(1 for l in lines_list if l == line)
                if count > 1:
                    repeated.append(line)
                checked.add(line)
            return repeated

        first_lines = [lines[0] for lines in lines_per_page if lines]
        last_lines = [lines[-1] for lines in lines_per_page if lines]

        header_candidates = find_repeated(first_lines)
        footer_candidates = find_repeated(last_lines)

        # 3. Combine lines into clean text, removing headers/footers
        clean_text = ""
        for lines in lines_per_page:
            lines = [line for line in lines if line not in header_candidates + footer_candidates]
            clean_text += "\n".join(lines) + "\n"

        # 4. Detect chapter number
        m_chapter = re.search(r"CHAPTER\s+(\d+)", clean_text, re.I)
        if not m_chapter:
            return ChapterNote(chapter_number="?", notes=[])
        chapter_number = m_chapter.group(1)

        # 5. Trim everything before "CHAPTER X"
        text_after_chapter = clean_text[m_chapter.start():]

        # 6. Find notes block
        m_notes_block = re.search(
            r"Notes?\s*(.*?)(?=(?:\nAdditional\s+U\.S\.|\nSubheading\s+Notes|\nStatistical\s+Notes|\nHeading/|\nRates\s+of\s+Duty|\Z))",
            text_after_chapter,
            re.S | re.I
        )
        if not m_notes_block:
            return ChapterNote(chapter_number=chapter_number, notes=[])

        notes_block = m_notes_block.group(1)

        # 7. Extract numbered notes
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
            clean_note = cut[0].strip()
            # Remove any leftover headers/footers inside the note
            for header in header_candidates + footer_candidates:
                clean_note = clean_note.replace(header, "")
            # Remove extra newlines
            clean_note = re.sub(r"\n+", " ", clean_note).strip()
            notes.append(
                Note(
                    note_number=match.group(1),
                    text=clean_note
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
                # crop margins to avoid headers/footers
                bbox = (0, 50, page.width,page.height)
                t = page.within_bbox(bbox).extract_text()
                if t:
                    t = re.sub(r"Additional U\.S\. Notes \(con\.\)", "", t)
                    t = re.sub(r"Additional U\.S\. Notes: \(con\.\)", "", t)
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

        # 4) stop at next known section/table markers
        stop_re = re.compile(r"(?=\n(Subheading\s+Notes?|Statistical\s+Notes?|Heading/|Rates\s+of\s+Duty|\Z))", re.I)
        m_stop = stop_re.search(text_after)
        if m_stop:
            notes_block = text_after[:m_stop.start()]
        else:
            notes_block = text_after

        # 5) Normalize line breaks
        notes_block = re.sub(r"\r\n?", "\n", notes_block)
        notes_block = re.sub(r"\n{2,}", "\n\n", notes_block)

        # 6) Split into note parts
        parts = re.split(r"\n(?=\s*\d{1,3}\.(?!\d|[-–])\s)", notes_block, flags=re.M)

        notes = []
        note_re = re.compile(r"^\s*(\d{1,3})\.(?!\d|[-–])\s*(.*)", re.S | re.M)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = note_re.match(part)
            if not m:
                continue
            number = m.group(1)
            body = m.group(2).strip()
            body = re.sub(r"\n+", " ", body).strip()
            # Remove any trailing table markers accidentally included
            body = re.split(r"\n(?:Heading/|Rates\s+of\s+Duty|Subheading\s+Notes?|Statistical\s+Notes?|Additional\s+U\.S\.)",
                            body, 1, flags=re.I)[0].strip()
            # Remove "N-N" fragments inside the body (keeps rest of text)
            body = re.sub(r"\b\d+\s*[-–]\s*\d+\b", "", body)

            notes.append(Note(note_number=number, text=body))
        if not notes:
            return None

        return AdditionalUSNotes(chapter_number=chapter_number, notes=notes)

    def save(self, data: list[AdditionalUSNotes], filepath: str = None, version: str = None):
        base_filename = filepath or "additional_us_notes"
        return versioning(data, base_filename, folder="data/notes/additional", version=version)
