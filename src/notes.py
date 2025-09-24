from .base import Source
from .models import GeneralNote
import requests, pdfplumber, json, re

class GeneralNotesSource(Source):
    """
    Source class to fetch & parse one specific General Note.
    """

    BASE_URL = "https://hts.usitc.gov/reststop/file"

    # Fetch
    def fetch(self, note_num: int, pdf_path: str = None) -> str:
        """
        Download a specific General Note PDF.
        """
        if pdf_path is None:
            pdf_path = f"general_note_{note_num}.pdf"

        params = {
            "filename": f"General Note {note_num}",
            "release": "currentRelease"
        }
        resp = requests.get(self.BASE_URL, params=params, stream=True)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return pdf_path

    # Parse
    def parse(self, pdf_path: str, note_num: int) -> GeneralNote:
        """
        Parse one General Note PDF into a GeneralNote by scanning line by line.
        More robust for inconsistent layouts (titles on their own line or dot without space).
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
        if filepath is None:
            filepath = "general_notes.json"

        if isinstance(data, list):
            payload = [d.model_dump() for d in data]
        else:
            payload = data.model_dump()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
