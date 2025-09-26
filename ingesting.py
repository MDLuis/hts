from src.notes import GeneralNotesSource, SectionNotesSource, ChapterNotesSource, AdditionalUSNotesSource
from src.tables import TariffTableSource

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
    # Loop of chapters to ingest, increase range for more chapters
    for ch in range(1,10):
        # General Notes
        gen_path = gen_note.fetch(ch)
        notes = gen_note.parse(gen_path, ch)
        listGen.append(notes)

        # Section Notes
        sec_path = sec_note.fetch(ch)
        section_notes = sec_note.parse(sec_path)
        if section_notes:  # skip empty ones
            listSec.append(section_notes)
        
        # Chapter Notes
        ch_path = ch_note.fetch(ch)
        chapter_notes = ch_note.parse(ch_path)
        listCh.append(chapter_notes)

        # Additional Notes
        us_path = us_note.fetch(ch)
        additional_notes = us_note.parse(us_path)
        if additional_notes:
            listUs.append(additional_notes)

        # Tariff Tables
        path = table.fetch(ch)
        tariff_table = table.parse(path)
        listTar.append(tariff_table)

    # Saving data
    gen_note.save(listGen)
    sec_note.save(listSec)        
    ch_note.save(listCh)
    us_note.save(listUs)
    table.save(listTar)

if __name__ == "__main__":
    main()
