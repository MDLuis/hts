import json, re
from .base import Source  
from .models import TariffRow, TariffTable 
from datetime import date
from pathlib import Path
from .utils import get_retry, deduplicate

class TariffTableSource(Source):
    """
    Source class to fetch, parse, and save Tariff Table rows for a given chapter.
    """

    BASE_URL = "https://hts.usitc.gov/reststop/exportList"

    def fetch(self, chapter_num: int, json_path: str = None) -> str:
        """
        Download the JSON for a chapter tariff table and store it under json/tables.

        Args:
            chapter_num (int): Chapter number to download.
            json_path (str, optional): Destination file path.
                Defaults to 'chapter_{chapter_num}_table.json'.

        Returns:
            str: Path to the saved JSON file.
        """
        tables_dir = Path("json/tables")
        tables_dir.mkdir(parents=True, exist_ok=True)

        if json_path is None:
            json_path = tables_dir / f"chapter_{chapter_num}_table.json"
        else:
            json_path = Path(json_path)

        # HTS expects from=chapter*100, to=(chapter+1)*100
        start = chapter_num * 100
        end = (chapter_num + 1) * 100
        if end > 9999:
            end = 9999

        url = f"{self.BASE_URL}?from={start:04d}&to={end:04d}&format=JSON&styles=true"
        r = get_retry(url)
        r.raise_for_status()

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(r.text)

        return str(json_path)

    def parse(self, json_path: str) -> TariffTable:
        """
        Parse a downloaded tariff table JSON file into a TariffTable object.

        Automatically detects the chapter number from the filename if possible.
        """
        # auto-detect chapter number from filename
        m = re.search(r"chapter_(\d+)_table\.json", json_path)
        chapter_num = m.group(1) if m else "?"

        # load JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # build rows
        rows = [TariffRow(**row) for row in data]

        return TariffTable(chapter_number=chapter_num, rows=rows)

    def save(self, tables: list[TariffTable], filepath: str = None, version: str = None):
        if tables:
            tables = deduplicate(tables, "chapter_number")
        # default values
        version = version or date.today().isoformat()
        base_filename = filepath or "tariff_tables_all"

        # where to store
        data_dir = Path("data/tables")
        data_dir.mkdir(parents=True, exist_ok=True)

        # paths
        versioned_path = data_dir / f"{base_filename}_v{version}.json"
        latest_path = data_dir / f"{base_filename}_latest.json"

        # convert to list of dicts
        payload = [t.model_dump() for t in tables]

        # write both files
        text = json.dumps(payload, indent=2, ensure_ascii=False)
        versioned_path.write_text(text, encoding="utf-8")
        latest_path.write_text(text, encoding="utf-8")

        return str(versioned_path)
