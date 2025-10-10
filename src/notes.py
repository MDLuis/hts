from .base import Source
from .models import GeneralNote, SectionNote, ChapterNote, Note, AdditionalUSNotes
import pdfplumber, json, re
from datetime import date
from pathlib import Path
from typing import Optional
from .utils import get_retry, deduplicate

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
    r = get_retry(url)
    r.raise_for_status()

    with open(pdf_path, "wb") as f:
        f.write(r.content)

    return str(pdf_path)

def find_repeated(lines_list: list[str]) -> list[str]:
    """Find repeated lines in a list """
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

def extract_clean_text(pdf_path: str, crop_top: int = 50, crop_bottom: int = 50) -> tuple[str, list[str], list[str]]:
    """
    Read PDF and return combined text (headers/footers removed), plus
    header_candidates and footer_candidates lists.
    """
    lines_per_page = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            bbox = (0, crop_top, page.width, page.height - crop_bottom)
            t = page.within_bbox(bbox).extract_text()
            if t:
                lines_per_page.append(t.split("\n"))

    if not lines_per_page:
        return "", [], []

    first_lines = [lines[0] for lines in lines_per_page if lines]
    last_lines = [lines[-1] for lines in lines_per_page if lines]

    header_candidates = find_repeated(first_lines)
    footer_candidates = find_repeated(last_lines)

    text = ""
    for lines in lines_per_page:
        lines = [l for l in lines if l not in header_candidates + footer_candidates]
        text += "\n".join(lines) + "\n"

    text = re.sub(r"\n+", "\n", text).strip()
    return text, header_candidates, footer_candidates

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
        resp = get_retry(BASE_URL, params=params, stream=True)
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
            if re.search(rf"\b{note_num}\b", ln):
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

        # --- 6) Subitem parsing ---
        lead_marker_re = re.compile(r"^\(([A-Za-z0-9IVXLCDM]+)\)\s*(.*)$")

        def marker_level(marker: str):
            """Assign level to markers for hierarchy"""
            if re.match(r'^[a-hj-uw-z]$', marker): return 1         
            if re.match(r'^[ivxlcdm]+$', marker): return 2   
            if re.match(r'^[A-HJ-UW-Z]$', marker): return 3       
            if re.match(r'^\d+$', marker): return 4         
            if re.match(r'^[IVXLCDM]+$', marker): return 5 
            return 0

        sub_items = []
        stack = []
        main_text_lines = []

        for raw_ln in body_lines:
            ln = re.sub(r"\s+", " ", raw_ln).strip()
            if not ln:
                continue

            m = lead_marker_re.match(ln)
            if m:
                marker, rest = m.group(1), m.group(2).strip()
                text = f"({marker}) {rest}" if rest else f"({marker})"
                node = {"text": text, "sub_items": []}
                level = marker_level(marker)

                while stack and marker_level(stack[-1][0]) >= level:
                    stack.pop()

                if stack:
                    stack[-1][1]["sub_items"].append(node)
                else:
                    sub_items.append(node)

                stack.append((marker, node))
            else:
                if stack:
                    stack[-1][1]["text"] += " " + ln
                else:
                    main_text_lines.append(ln)

        main_text = " ".join(main_text_lines).strip()

        return GeneralNote( note_number=str(note_num), title=title, text=main_text, sub_items=sub_items if sub_items else None)

    # Save
    def save(self, data: GeneralNote | list[GeneralNote], filepath: str = None, version: str = None):
        if data:
            data = deduplicate(data, "note_number")
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
        text, _, _ = extract_clean_text(pdf_path)
        if not text:
            return SectionNote(section_number="?", notes=[])

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

        # ---- Step 5: Extract Notes block ----
        m_notes_block = re.search(
            r"Notes?\s*(.*?)(?=(?:\n\d{1,2}\.)|\Z)",
            section_text,
            re.S | re.I,
        )
        if not m_notes_block:
            return SectionNote(section_number=section_number, notes=[])

        notes_block = section_text[m_notes_block.start():]

        # ---- Step 6: Note & sub-item parsing ----
        note_pattern = re.compile(
            r"(\d{1,2})\.\s*(.*?)(?=(?:\n\d{1,2}\.)|\Z)",
            re.S
        )

        def parse_sub_items(text):
            """
            Parse top-level (a),(b),... and nested (i),(ii) sub-items.
            Returns a list of strings or dicts with 'sub_items'.
            """
            items = []
            text = re.sub(r"\n+", " ", text).strip()

            # Match top-level items (a), (b), etc.
            top_pattern = re.compile(r"\(([a-z])\)\s*(.*?)(?=(\([a-z]\)|$))", re.S)
            for top_match in top_pattern.finditer(text):
                top_letter = top_match.group(1)
                content = top_match.group(2).strip()
                content = re.sub(r"\n+", " ", content)

                # Match nested (i),(ii), etc.
                nested_pattern = re.compile(r"\(([ivx]+)\)\s*(.*?)(?=(\([ivx]+\)|$))", re.S)
                nested_matches = list(nested_pattern.finditer(content))
                if nested_matches:
                    nested_items = []
                    for nm in nested_matches:
                        nm_text = re.sub(r"\n+", " ", nm.group(2)).strip()
                        nested_items.append(f"({nm.group(1)}) {nm_text}")
                    items.append({"sub_items": nested_items})
                else:
                    items.append(f"({top_letter}) {content}")
            return items or None

        notes = []
        for match in note_pattern.finditer(notes_block):
            note_number = match.group(1)
            note_text = match.group(2).strip()

            parts = re.split(r"(?=\([a-z]\))", note_text, 1)
            main_text = re.sub(r"\n+", " ", parts[0]).strip()
            sub_items = None
            if len(parts) > 1:
                sub_items = parse_sub_items(parts[1])

            notes.append(Note(
                note_number=note_number,
                text=main_text,
                sub_items=sub_items
            ))

        return SectionNote(section_number=section_number, notes=notes)

    def save(self, data: list[SectionNote], filepath: str = None, version: str = None):
        if data:
            data = deduplicate(data, "section_number")
        base_filename = filepath or "section_notes"
        return versioning(data, base_filename, folder="data/notes/section", version=version)


class ChapterNotesSource(Source):
    """
    Source class to fetch, parse, and save Chapter Notes.
    """
    def fetch(self, chapter_num: int, filename: str = None) -> str:
        return download_chapter_pdf(chapter_num, filename)

    def parse(self, pdf_path: str) -> ChapterNote:
        clean_text, header_candidates, footer_candidates = extract_clean_text(pdf_path)
        if not clean_text:
            return ChapterNote(chapter_number="?", notes=[])
        # 4. Detect chapter number
        m_chapter = re.search(r"CHAPTER\s+(\d+)", clean_text, re.I)
        chapter_number = m_chapter.group(1) if m_chapter else "?"

        # 5. Trim everything before "CHAPTER X"
        text_after_chapter = clean_text[m_chapter.start():] if m_chapter else clean_text

        # 6. Find notes block
        m_notes_block = re.search(
            r"Notes?\s*(.*?)(?=(?:\nAdditional\s+U\.S\.|\nSubheading\s+Notes?|\nStatistical\s+Notes?|\nHeading/|\nRates\s+of\s+Duty|\Z))",
            text_after_chapter,
            re.S | re.I
        )
        notes_block = m_notes_block.group(1) if m_notes_block else ""

        # 7. Helper to parse hierarchical sub-items
        def parse_sub_items(text):
            """Recursively parse sub-items: (a), (b), ... and nested (i), (ii), ..."""
            items = []
            # Top-level sub-items (a), (b), (c)…
            top_pattern = re.compile(r"\n?\s*\(([a-z])\)\s*(.*?)((?=\n\s*\([a-z]\))|$)", re.S)
            for top_match in top_pattern.finditer(text):
                content = re.sub(r"\n+", " ", top_match.group(2)).strip()
                # Check for nested (i), (ii), ...
                nested_pattern = re.compile(r"\n?\s*\(([ivx]+)\)\s*(.*?)(?=(\n\s*\([ivx]+\))|$)", re.S | re.I)
                nested_matches = list(nested_pattern.finditer(content))
                if nested_matches:
                    nested_items = []
                    last_end = 0
                    for nm in nested_matches:
                        # Anything before the first nested item goes into text
                        prefix = content[last_end:nm.start()].strip()
                        if prefix:
                            nested_items.append(prefix)
                        cleaned_text = re.sub(r"\n+", " ", nm.group(2)).strip()
                        nested_items.append(f"({nm.group(1)}) {cleaned_text}")
                        last_end = nm.end()
                    suffix = content[last_end:].strip()
                    if suffix:
                        nested_items.append(suffix)
                    items.append({"sub_items": nested_items})
                else:
                    items.append(f"({top_match.group(1)}) {content}")
            return items

        # 8. Extract numbered notes
        note_pattern = re.compile(
            r"(\d{1,2})\.\s*(.*?)(?=(?:\n\d{1,2}\.)|(?:\nAdditional\s+U\.S\.)|(?:\nSubheading\s+Notes?)|(?:\nStatistical\s+Notes?)|(?:\nHeading/)|(?:\nRates\s+of\s+Duty)|\Z)",
            re.S | re.I
        )

        notes: list[Note] = []
        for match in note_pattern.finditer(notes_block):
            raw_text = match.group(2).strip()
            # Remove leftover headers/footers
            for header in header_candidates + footer_candidates:
                raw_text = raw_text.replace(header, "")
            raw_text = re.sub(r"\n+", "\n", raw_text).strip()
            # Split into main text and sub-items
            main_text_split = re.split(r"\n\s*\([a-z]\)", raw_text, 1, flags=re.I)
            main_text = re.sub(r"\n+", " ", main_text_split[0]).strip()
            sub_items = parse_sub_items(raw_text) if len(main_text_split) > 1 else None
            notes.append(
                Note(
                    note_number=match.group(1),
                    text=main_text,
                    sub_items=sub_items
                )
            )

        return ChapterNote(chapter_number=chapter_number, notes=notes)

    def save(self, data: list[ChapterNote], filepath: str = None, version: str = None):
        if data:
            data = deduplicate(data, "chapter_number")
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
        notes_block = text_after[:m_stop.start()] if m_stop else text_after

        # 5) Normalize line breaks
        notes_block = re.sub(r"\r\n?", "\n", notes_block)
        notes_block = re.sub(r"\n{3,}", "\n\n", notes_block)
        notes_block = re.sub(r"[ \t]{2,}", " ", notes_block)
        # 6) Split into note parts
        parts = re.split(r"\n(?=\s*\d{1,3}\.(?!\d|[-–])\s)", notes_block, flags=re.M)
        note_re = re.compile(r"^\s*(\d{1,3})\.(?!\d|[-–])\s*(.*)", re.S | re.M)

        notes = []

        # --- Subitem patterns ---
        level_patterns = [
            re.compile(r"^\(([a-hj-uw-z])\)"),        
            re.compile(r"^\(([ivxlcdm]+)\)"),       
            re.compile(r"^\((\d+)\)"),  
            re.compile(r"^\(([A-Z])\)")           
        ]
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = note_re.match(part)
            if not m:
                continue
            number = m.group(1)
            body = m.group(2).strip()

            # Remove unrelated sections
            body = re.split(
                r"\n(?:Heading/|Rates\s+of\s+Duty|Subheading\s+Notes?|Statistical\s+Notes?|Additional\s+U\.S\.)",
                body, 1, flags=re.I
            )[0].strip()

            # --- Split lines and normalize ---
            lines = re.sub(r"[ \t]*\n[ \t]*", "\n", body).split("\n")

            main_text = ""
            sub_items_stack = []
            sub_items = []

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # --- Handle inline numeric subitems (1), (2), ... ---
                inline_numeric = re.findall(r"\((\d+)\)\s*([^()]+(?:\([^()]*\)[^()]*)*)", line)
                if inline_numeric and len(inline_numeric) > 1:
                    for num, text_part in inline_numeric:
                        text_part = text_part.strip().rstrip(",;.")
                        new_item = {"text": text_part, "sub_items": []}
                        if sub_items_stack:
                            sub_items_stack[-1]["sub_items"].append(new_item)
                        else:
                            sub_items.append(new_item)
                    continue

                # --- Determine level ---
                level = None
                for i, pat in enumerate(level_patterns):
                    if pat.match(line):
                        level = i + 1
                        break

                if level is None:
                    # Continuation text
                    if sub_items_stack:
                        sub_items_stack[-1]["text"] += " " + line
                    else:
                        main_text += (" " if main_text else "") + line
                    continue

                # --- Create new subitem ---
                new_item = {"text": line, "sub_items": []}

                # --- Attach to proper parent using stack ---
                if sub_items_stack:
                    # Pop from stack if current level <= stack depth
                    while len(sub_items_stack) >= level:
                        sub_items_stack.pop()

                    if sub_items_stack:
                        sub_items_stack[-1]["sub_items"].append(new_item)
                    else:
                        sub_items.append(new_item)
                else:
                    sub_items.append(new_item)

                sub_items_stack.append(new_item)

            notes.append(Note(
                note_number=number,
                text=main_text.strip(),
                sub_items=sub_items or None
            ))

        if not notes:
            return None

        return AdditionalUSNotes(chapter_number=chapter_number, notes=notes)

    def save(self, data: list[AdditionalUSNotes], filepath: str = None, version: str = None):
        if data:
            data = deduplicate(data, "chapter_number")
        base_filename = filepath or "additional_us_notes"
        return versioning(data, base_filename, folder="data/notes/additional", version=version)
