from src.notes import GeneralNotesSource, SectionNotesSource, ChapterNotesSource, AdditionalUSNotesSource
from src.ingest import HTSSource
from src.tables import TariffTableSource
def main():
    # # Testing the ingest of Sections and Chapters
    # source = HTSSource()
    # pdf_path = source.fetch()
    # sections = source.parse(pdf_path)
    # source.save(sections)

    # # Testing for general notes
    # note_num = 1
    # listNotes = []
    # src = GeneralNotesSource()
    # while note_num <= 9:
    #     if note_num == 19:
    #         note_num=25
    #     pdf_path = src.fetch(note_num=note_num)
    #     notes = src.parse(pdf_path, note_num=note_num)
    #     listNotes.append(notes)
    #     print(note_num, "=>", repr(notes.title))
    #     note_num += 1
    # src.save(listNotes)

    # # Testing for section notes
    # src = SectionNotesSource()
   
    # sections_to_fetch = [1,2,3,5,6,15,16]
    # all_sections = []
    # for chapter_num in sections_to_fetch:
    #     pdf_path = src.fetch(chapter_num)
    #     section_notes = src.parse(pdf_path)
    #     if section_notes:  # skip empty ones
    #         all_sections.append(section_notes)
    # src.save(all_sections)

    # Testing for chapter notes
    src = ChapterNotesSource()
    results = []
    for ch in range(1,10):
        pdf_path = src.fetch(ch)
        chapter_notes = src.parse(pdf_path)
        results.append(chapter_notes)
        print(f"Chapter {chapter_notes.chapter_number} has {len(chapter_notes.notes)} notes")
    src.save(results)

    # # Testing for additional notes
    # src = AdditionalUSNotesSource()
    # results = []
    # for ch in range(1,10):
    #     if ch != 77:
    #         pdf_path = src.fetch(ch)
    #         additional_notes = src.parse(pdf_path)
    #         if additional_notes:
    #             results.append(additional_notes)
    #             print(f"Chapter {additional_notes.chapter_number} has {len(additional_notes.notes)} notes")
    #         else:
    #             print(f"No additional u.s. notes in chapter {ch}")
    # src.save(results)

    # # Testing for tariff tables
    # src = TariffTableSource()
    # results = []
    # for ch in range(1, 5): 
    #     path = src.fetch(ch)
    #     tariff_table = src.parse(path)
    #     results.append(tariff_table)
    # src.save(results)


if __name__ == "__main__":
    main()
