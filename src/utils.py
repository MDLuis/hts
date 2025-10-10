import requests, json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .models import Chapter, Section, HTSData, SectionNote, ChapterNote, AdditionalUSNotes, TariffTable, GeneralNote
from pathlib import Path
from datetime import date

def get_retry(url: str, retries: int = 5, backoff_factor: float = 0.5, timeout: int = 30, **kwargs) -> requests.Response:
    """
    Perform a GET request with automatic retries and exponential backoff.

    Retry logic:
        sleep_time = backoff_factor * (2 ** (retry_number - 1))
    Args:
        url (str): The full URL to fetch.
        retries (int, optional): Maximum number of retry attempts. Defaults to 5.
        backoff_factor (float, optional): Base factor for exponential backoff. Defaults to 0.5.
        timeout (int, optional): Timeout in seconds for the request. Defaults to 30.
        **kwargs: Additional keyword arguments passed directly to `requests.get()`.
            Examples:
                - stream=True (for large files)
                - headers={'User-Agent': '...'}
                - params={'key': 'value'}
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)

    response = session.get(url, timeout=timeout, **kwargs)

    return response

def deduplicate(data_list, key_attr: str):
    """
    Deduplicate a list of objects based on a specified attribute.

    Keeps the first occurrence of each unique key.
    """
    seen = set()
    deduped = []
    for item in data_list:
        key_val = getattr(item, key_attr, None)
        if key_val is None:
            deduped.append(item)
        elif key_val not in seen:
            deduped.append(item)
            seen.add(key_val)
    return deduped

def combine():
    """
    Combine all parsed HTS components (sections, notes, tables)
    into one hierarchical JSON structure.
    """

    def load_json(path):
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []

    # Load components
    sections = load_json(Path(f"data/sections/hts_sections_latest.json"))
    general_notes = load_json(Path("data/notes/general/general_notes_latest.json"))
    section_notes = load_json(Path(f"data/notes/section/section_notes_latest.json"))
    chapter_notes = load_json(Path(f"data/notes/chapter/chapter_notes_latest.json"))
    add_us_notes = load_json(Path(f"data/notes/additional/additional_us_notes_latest.json"))
    tables = load_json(Path(f"data/tables/tariff_tables_all_latest.json"))

    # Convert lists to dicts of proper Pydantic objects
    general_notes_map = [GeneralNote(**g) for g in general_notes]
    sec_notes_map = {s["section_number"]: SectionNote(**s) for s in section_notes}
    ch_notes_map = {c["chapter_number"]: ChapterNote(**c) for c in chapter_notes}
    add_notes_map = {a["chapter_number"]: AdditionalUSNotes(**a) for a in add_us_notes}
    tables_map = {t["chapter_number"]: TariffTable(**t) for t in tables}

    full_sections = []
    for s in sections:
        sec_number = s["sec_number"]
        chapters = []
        for ch in s["chapters"]:
            ch_num = ch["ch_number"]
            chapter = Chapter(
                ch_number=ch_num,
                title=ch["title"],
                notes=ch_notes_map.get(ch_num),
                additional=add_notes_map.get(ch_num),
                table=tables_map.get(ch_num),
            )
            chapters.append(chapter)

        section = Section(
            sec_number=sec_number,
            title=s["title"],
            notes=sec_notes_map.get(sec_number),
            chapters=chapters,
        )
        full_sections.append(section)

    path = Path("data/hts")
    path.mkdir(parents=True, exist_ok=True)
    full_data = HTSData(general_notes=general_notes_map, sections=full_sections)
    full_data_json = json.dumps(full_data.model_dump(), indent=2, ensure_ascii=False)
    latest_path = path / (f"hts_full_latest.json")
    version_path = path / (f"hts_full_v{date.today().isoformat()}.json")
    latest_path.write_text(full_data_json, encoding="utf-8")
    version_path.write_text(full_data_json, encoding="utf-8")