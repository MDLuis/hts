from .base import Source
from .models import GeneralNote
import requests
import pdfplumber, json, re

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
        Parse one General Note PDF into a GeneralNote, removing header/front-matter.
        Handles titles ending in '.' or ')', and strips the note number from the title.
        """
        with pdfplumber.open(pdf_path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]

        # basic clean: strip headers/footers
        lines = []
        for page in pages:
            for ln in page.splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                if re.search(r'harmonized tariff schedule', ln, re.I): continue
                if re.search(r'annotated for statistical reporting', ln, re.I): continue
                if re.search(r'\bGN\s*p\.?\d+\b', ln, re.I): continue
                if re.search(r'\brevision\s*\d+\b', ln, re.I): continue
                if re.fullmatch(r'\d+', ln): continue  # pure page number
                lines.append(ln)

        text = " ".join(lines)

        # For GN1, start after GENERAL NOTES heading
        if note_num == 1:
            m_gn = re.search(r"GENERAL\s+NOTES", text, re.I)
            if m_gn:
                text = text[m_gn.end():].lstrip()

        # locate the start of this note
        mstart = re.search(rf"(General\s+Note\s*)?{note_num}[\.\)]?\s+", text, re.I)
        if not mstart:
            raise ValueError(f"Could not find General Note {note_num} start")

        text_after_num = text[mstart.end():].lstrip()

        # Title ends at first '.' or ')' after some words
        mtitle = re.search(r"(?P<title>.+?)(?:[.)])\s*(?P<body>.*)", text_after_num, re.S)
        if not mtitle:
            # fallback: no clear title delimiter, everything is body
            title = ""
            body = text_after_num.strip()
        else:
            raw_title = re.sub(r"\s+", " ", mtitle.group("title")).strip()
            # strip any leading note number left in the title
            title = re.sub(rf"^\s*{note_num}\s*", "", raw_title).strip()
            body = re.sub(r"\s+", " ", mtitle.group("body")).strip()

        return GeneralNote(note_number=str(note_num), title=title, text=body)

    # Save
    def save(self, data: GeneralNote, filepath: str = None):
        if filepath is None:
            filepath = f"general_note_{data.note_number}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data.dict(), f, ensure_ascii=False, indent=2)
