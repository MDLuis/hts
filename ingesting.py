from src.notes import GeneralNotesSource, SectionNotesSource, ChapterNotesSource, AdditionalUSNotesSource
from src.tables import TariffTableSource
import time
from pathlib import Path

def main():
    """
    Main pipeline function to fetch, parse, and save tariff-related data.

    Workflow:
        1. Initializes source handlers for each type of note and table.
        2. Iterates over chapters (1–9 by default).
        3. For each chapter:
            - Fetches and parses General Notes.
            - Fetches and parses Section Notes (if available).
            - Fetches and parses Chapter Notes.
            - Fetches and parses Additional US Notes (if available).
            - Fetches and parses Tariff Tables.
        4. Appends parsed data to lists.
        5. Saves all aggregated data using the respective source handlers.

    Variables:
        gen_note (GeneralNotesSource): Handler for General Notes.
        sec_note (SectionNotesSource): Handler for Section Notes.
        ch_note (ChapterNotesSource): Handler for Chapter Notes.
        us_note (AdditionalUSNotesSource): Handler for Additional US Notes.
        table (TariffTableSource): Handler for Tariff Tables.

    Output:
        None. Saves processed data via each source handler's save() method.
    """
    gen_note = GeneralNotesSource()
    sec_note = SectionNotesSource()
    ch_note = ChapterNotesSource()
    us_note = AdditionalUSNotesSource()
    table = TariffTableSource()
    listGen = []
    listSec = []
    listCh = []
    listUs = []
    listTar = []
    benchmarks = []
    # Loop of chapters to ingest, increase range for more chapters
    chapters = range(1, 10)

    # General Notes
    start = time.time()
    for ch in chapters:
        gen_path = gen_note.fetch(ch)
        notes = gen_note.parse(gen_path, ch)
        listGen.append(notes)
    duration = time.time() - start
    benchmarks.append(("General Notes", len(listGen), duration))

    # Section Notes
    start = time.time()
    for ch in chapters:
        sec_path = sec_note.fetch(ch)
        section_notes = sec_note.parse(sec_path)
        if section_notes:  # skip empty ones
            listSec.append(section_notes)
    duration = time.time() - start
    benchmarks.append(("Section Notes", len(listSec), duration))

    # Chapter Notes
    start = time.time()
    for ch in chapters:
        ch_path = ch_note.fetch(ch)
        chapter_notes = ch_note.parse(ch_path)
        listCh.append(chapter_notes)
    duration = time.time() - start
    benchmarks.append(("Chapter Notes", len(listCh), duration))

    # Additional Notes
    start = time.time()
    for ch in chapters:
        us_path = us_note.fetch(ch)
        additional_notes = us_note.parse(us_path)
        if additional_notes:
            listUs.append(additional_notes)
    duration = time.time() - start
    benchmarks.append(("Additional U.S. Notes", len(listUs), duration))

    # Tariff Tables
    start = time.time()
    for ch in chapters:
        path = table.fetch(ch)
        tariff_table = table.parse(path)
        listTar.append(tariff_table)
    duration = time.time() - start
    benchmarks.append(("Tariff Tables", len(listTar), duration))

    # Saving data
    gen_note.save(listGen)
    sec_note.save(listSec)
    ch_note.save(listCh)
    us_note.save(listUs)
    table.save(listTar)

    # Write Benchmarks.md
    md_path = Path("benchmarkIngest.md")
    lines = [
        "# Benchmarks – HTS Ingestion\n\n",
        "This file records how long the ingestion process takes on the available hardware.\n\n",
        "## Notes\n\n",
        "- All times measured with `time.time()` before and after each ingest loop.\n",
        "- Measured on current machine.\n\n",
        "## Results\n\n",
        "| Dataset              | # Items | Time (seconds) |\n",
        "|----------------------|---------|----------------|\n",
    ]
    for name, count, duration in benchmarks:
        lines.append(f"| {name:<20} | {count:5d} | {duration:10.2f} |\n")

    md_path.write_text("".join(lines), encoding="utf-8")
    print(f"Benchmarks written to {md_path}")

if __name__ == "__main__":
    main()
