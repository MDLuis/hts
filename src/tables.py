import json, requests, re
from .base import Source  # your abstract base class
from .models import TariffRow, TariffTable  # the models we just defined


class TariffTableSource(Source):
    """
    Source class to fetch, parse, and save Tariff Table rows for a given chapter.
    """

    BASE_URL = "https://hts.usitc.gov/reststop/exportList"

    def fetch(self, chapter_num: int, json_path: str = None) -> str:
        """
        Download the JSON for a chapter tariff table.

        Args:
            chapter_num (int): Chapter number to download.
            json_path (str, optional): Destination file path.
                Defaults to 'chapter_{chapter_num}_table.json'.

        Returns:
            str: Path to the saved JSON file.
        """
        if json_path is None:
            json_path = f"chapter_{chapter_num}_table.json"

        # HTS expects from=chapter*100, to=(chapter+1)*100
        start = chapter_num * 100
        end = (chapter_num + 1) * 100
        if end > 9999:
            end = 9999

        url = f"{self.BASE_URL}?from={start:04d}&to={end:04d}&format=JSON&styles=true"
        r = requests.get(url)
        r.raise_for_status()

        with open(json_path, "w", encoding="utf-8") as f:
            f.write(r.text)

        return json_path

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

    def save(self, tables: list[TariffTable], filepath: str = None):
        """
        Save a list of TariffTable objects into one JSON file.

        Args:
            tables (list[TariffTable]): List of TariffTable objects.
            filepath (str, optional): Destination JSON file path.
                Defaults to 'tariff_tables_all.json'.
        """
        if filepath is None:
            filepath = "tariff_tables_all.json"

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([t.model_dump() for t in tables],f,ensure_ascii=False,indent=2)
