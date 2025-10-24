from .base import Source
from .utils import get_retry
from .models import GeneralRule
from pathlib import Path
import pdfplumber, re, json
from typing import List
from datetime import date

BASE_URL = "https://hts.usitc.gov/reststop/file?release=currentRelease&filename=General%20Rules%20of%20Interpretation"

class GeneralRules(Source):
    def fetch(self) -> Path:
        """
        Downloads the General Rules of Interpretation PDF
        Returns:
            Path: Path to the downloaded PDF file.
        """
        out_dir = Path("pdf/general_rules")
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = out_dir / f"general_rules.pdf"

        resp = get_retry(BASE_URL)
        resp.raise_for_status()

        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return pdf_path

    def parse(self, pdf_path: Path) -> dict[str, list[GeneralRule]]:
        """
        Parse the General Rules of Interpretation
        Args:
            pdf_path (Path): Path to the General Rules PDF.
        Returns:
            dict[str, list[GeneralRule]]: Parsed structured rules.
        """
        lines_per_page = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                bbox = (0, 50, page.width, page.height - 50)
                t = page.within_bbox(bbox).extract_text()
                if not t:
                    continue
                lines = [line.strip() for line in t.split("\n") if line.strip()]
                lines_per_page.extend(lines)

        text = "\n".join(lines_per_page)
        text = re.sub(r"Harmonized Tariff Schedule.*?Purposes", "", text)
        text = re.sub(r"GN p\.\d+", "", text)
        text = text.strip()

        split_pattern = r"ADDITIONAL U\.S\. RULES OF INTERPRETATION"
        parts = re.split(split_pattern, text, maxsplit=1)
        gri_text = parts[0].strip()
        add_text = parts[1].strip() if len(parts) > 1 else ""
     
        compiler_note = None 

        if add_text:
            add_split = re.split(
                r"\[\s*COMPILER'S NOTE:|Presidential Proclamation|Contact officials",
                add_text,
                maxsplit=1
            )
            main_add_text = add_split[0].strip()
            if len(add_split) > 1:
                compiler_note = add_text[len(main_add_text):].strip()

            add_text = main_add_text


        results = {"general_rules": [], "additional_rules": []}

        for key, section_text in [("general_rules", gri_text),
                                  ("additional_rules", add_text)]:

            section_text = re.sub(r"^[A-Z\s]+INTERPRETATION", "", section_text, flags=re.MULTILINE).strip()

            # Match rule numbers only at start of a new line
            rule_pattern = r"(?m)(?=^\d\.\s)"
            raw_rules = re.split(rule_pattern, section_text)
            raw_rules = [r.strip() for r in raw_rules if re.match(r"^\d\.", r.strip())]

            for chunk in raw_rules:
                m = re.match(r"^(\d+)\.\s*(.*)", chunk, re.DOTALL)
                if not m:
                    continue
                num, body = m.groups()
                body = body.strip()

                # Split sub-items (anchored to line start)
                sub_pattern = r"(?m)(?=^\([a-z]\))"
                parts = re.split(sub_pattern, body)
                parts = [p.strip() for p in parts if p.strip()]

                if len(parts) > 1:
                    text_before = None
                    sub_items = []
                    if not parts[0].startswith("("):
                        text_before = parts[0].strip()
                        sub_parts = parts[1:]
                    else:
                        sub_parts = parts

                    for s in sub_parts:
                        sm = re.match(r"^\(([a-z])\)\s*(.*)", s, re.DOTALL)
                        if sm:
                            label, txt = sm.groups()
                            sub_items.append({"label": f"({label})", "text": re.sub(r"\n", " ", txt).strip()})

                    results[key].append(
                        GeneralRule(rule_number=num, text=text_before, sub_items=sub_items)
                    )
                else:
                    results[key].append(GeneralRule(rule_number=num, text=body.strip()))

        if compiler_note:
            results["compiler_note"] = compiler_note

        return results

    def save(self, structured_data: List[GeneralRule]):
        """
        Save the parsed rules as a versioned and 'latest' JSON file.

        Args:
            structured_data (dict): Parsed output from parse().
        """
        out_dir = Path("data/rules")
        out_dir.mkdir(parents=True, exist_ok=True)

        version = date.today().isoformat()
        versioned_path = out_dir / f"general_rules_v{version}.json"
        latest_path = out_dir / "general_rules_latest.json"

        data = {}
        for key, value in structured_data.items():
            if isinstance(value, list):
                data[key] = [
                    rule.model_dump() if hasattr(rule, "model_dump") else rule
                    for rule in value
                ]
            else:
                data[key] = value

        with open(versioned_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)