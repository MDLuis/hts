import re
import json
import requests
import pdfplumber
from typing import List
from .base import Source
from .models import Section, Chapter

class HTSSource(Source):
    """
    Handles downloading, parsing, and saving the HTS Table of Contents PDF.

    - Downloads the PDF from the USITC website.
    - Parses it into Section and Chapter objects.
    - Saves the parsed data to a JSON file.
    """

    TOC_URL = "https://hts.usitc.gov/reststop/file?filename=Table+of+Contents&release=currentRelease"

    def fetch(self, pdf_path: str = "hts_toc.pdf") -> str:
        """
        Download the HTS Table of Contents PDF.
        Args:
            pdf_path: Local path to save the file (default 'hts_toc.pdf').
        Returns:
            Path to the saved PDF file.
        """
        resp = requests.get(self.TOC_URL, stream=True)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return pdf_path

    def parse(self, pdf_path: str = "hts_toc.pdf") -> List[Section]:
        """
        Read the PDF and turn it into a list of Section objects.

        Each Section contains its number, title, and Chapters.
        Chapters with titles spanning multiple lines are merged.

        Args:
            pdf_path: Path to the PDF file (default 'hts_toc.pdf').
        Returns:
            List of Section objects.
        """
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        lines = [line.strip() for line in "\n".join(text_parts).splitlines() if line.strip()]

        # Regex to detect Sections, Chapters and page numbers
        section_pattern = re.compile(r"^SECTION\s+([IVXLCDM]+)$", re.IGNORECASE)
        chapter_pattern = re.compile(r"^(?:Chapter\s+)?(\d+)\s+(.+)$", re.IGNORECASE)
        skip_page_pattern = re.compile(r"^(?:\d+|page\s+\d+|pg\s+\d+)$", re.IGNORECASE)

        sections: List[Section] = []
        current_section = None
        i = 0

        while i < len(lines):
            line = lines[i]

            # Section header
            sec_match = section_pattern.match(line)
            if sec_match:
                if current_section:
                    sections.append(current_section)
                sec_num = sec_match.group(1)
                sec_title = lines[i + 1].strip() if i + 1 < len(lines) else ""
                current_section = Section(sec_number=sec_num, title=sec_title, chapters=[])
                i += 2
                continue

            # Chapter
            chap_match = chapter_pattern.match(line)
            if current_section and chap_match:
                chap_num, chap_title = chap_match.groups()
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if (
                        section_pattern.match(next_line)
                        or chapter_pattern.match(next_line)
                        or next_line.lower().startswith("section notes")
                    ):
                        break
                    if skip_page_pattern.match(next_line):
                        j += 1
                        continue
                    chap_title += " " + next_line.strip()
                    j += 1

                current_section.chapters.append(
                    Chapter(ch_number=chap_num, title=chap_title, notes=None)
                )
                i = j
                continue

            i += 1

        if current_section:
            sections.append(current_section)
        return sections

    def save(self, data: List[Section], filepath: str = "hts_sections.json") -> None:
        """
        Save the parsed Sections and Chapters to a JSON file.

        Args:
            data: List of Section objects.
            filepath: Path to the JSON file (default 'hts_sections.json').
        """

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in data], f, indent=2, ensure_ascii=False)
