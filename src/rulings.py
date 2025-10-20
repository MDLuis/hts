from .base import Source
from .models import Ruling
from .utils import get_retry
import re, time, json, pdfplumber, win32com.client
from pathlib import Path
from playwright.sync_api import sync_playwright
from typing import List

BASE_URL = "https://rulings.cbp.gov"

def extract_text(file: Path) -> str:
    if file.suffix.lower() == ".pdf":
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    elif file.suffix.lower() == ".doc":
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False

            doc = word.Documents.Open(str(file.resolve()))
            text = doc.Content.Text
            doc.Close(False)
            word.Quit()
            return text.strip()

        except Exception as e:
            print(f"[Warning] Could not extract {file.name} with pywin32: {e}")
            return ""

    else:
        raise ValueError(f"Unsupported file type: {file.suffix}")

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"U\.S\. Customs.*?Protection", "", text, flags=re.IGNORECASE)
    return text.strip()

class Rulings(Source):

    def fetch(self, hts_code: str, delay: float = 1.0, out_dir: str = "CBPrulings/fetch"):
        save_dir = Path(out_dir) / hts_code.replace('.', '_')
        save_dir.mkdir(parents=True, exist_ok=True)

        all_rulings = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{BASE_URL}/search?term={hts_code}", wait_until="networkidle")

            while True:
                page.wait_for_selector('mat-row.ruling-row', timeout=15000)
                rows = page.query_selector_all('mat-row.ruling-row')
                for row in rows:
                    date_cell = row.query_selector('mat-cell.mat-column-date')
                    date_text = date_cell.inner_text().strip() if date_cell else ""
                    year_match = re.search(r'(19|20)\d{2}', date_text)
                    year = year_match.group(0) if year_match else "unknown"

                    link = row.query_selector('a[id^="rulingLink_"]')
                    if not link:
                        continue
                    href = link.get_attribute("href")
                    ruling_id = href.split("/")[-1].strip()

                    link_text = link.inner_text().strip().upper()
                    if "HQ" in link_text:
                        prefix = "hq"
                    elif "NY" in link_text:
                        prefix = "ny"

                    all_rulings.append({
                        "id": ruling_id,
                        "prefix": prefix,
                        "year": year
                    })

                next_button = page.locator('button[aria-label="Next page"]').first
                if next_button.count() == 0 or next_button.get_attribute("disabled"):
                    break
                next_button.click()
                time.sleep(delay)
                page.wait_for_load_state("networkidle")

            browser.close()

        downloaded = 0
        for r in all_rulings:
            if r["year"] == "unknown":
                continue

            api_url = f"https://rulings.cbp.gov/api/getdoc/{r['prefix']}/{r['year']}/{r['id']}"

            try:
                resp = get_retry(api_url)
                if resp.status_code != 200:
                    continue

                filename = r['id']
                content_type = resp.headers.get("Content-Type", "").lower()

                if "Content-Disposition" in resp.headers:
                    disp = resp.headers["Content-Disposition"]
                    match = re.search(r'filename="?([^";]+)"?', disp)
                    if match:
                        filename = match.group(1)
                else:
                    if "pdf" in content_type:
                        filename += ".pdf"
                    elif "word" in content_type or "doc" in content_type:
                        filename += ".doc"

                file_path = save_dir / filename
                with open(file_path, "wb") as f:
                    f.write(resp.content)

                downloaded += 1
                time.sleep(delay)

            except Exception as e:
                print(f"Error downloading {r['id']} from {api_url}: {e}")

        print(f"Rulings Downloaded {downloaded}/{len(all_rulings)} rulings for {hts_code}")
        return hts_code, save_dir

    def parse(self, hts_code: str, folder_path: Path) -> List[Ruling]:
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        rulings = []

        for file in folder_path.glob("*.*"):
            if file.suffix.lower() not in [".pdf", ".doc"]:
                continue

            text = clean_text(extract_text(file))
            prefix = "hq" if " HQ " in text.upper()[:400] else "ny"
            rulings.append(Ruling(
                id=file.stem,
                hts_code=hts_code,
                prefix=prefix,
                text=text
            ))

        return rulings

    def save(self, structured_data: List[Ruling], hts_code: str) -> Path:
        json_dir = Path("CBPrulings/json")
        json_dir.mkdir(parents=True, exist_ok=True)

        out_path = json_dir / f"{hts_code.replace('.', '_')}_rulings.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([r.model_dump() for r in structured_data], f, indent=2, ensure_ascii=False)

        return out_path
