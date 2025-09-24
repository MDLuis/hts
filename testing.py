from src.notes import GeneralNotesSource, SectionNotesSource, ChapterNotesSource
from src.ingest import HTSSource

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
    # while note_num <= 36:
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
   
    # sections_to_fetch = [1,6,15,16,25,28,39,41,44,47,50,64,68,71,72,84,86,90,93,94,97,98]
    # all_sections = []
    # for chapter_num in sections_to_fetch:
    #     pdf_path = src.fetch(chapter_num)
    #     section_notes = src.parse(pdf_path)
    #     if section_notes.notes:  # skip empty ones
    #         all_sections.append(section_notes)
    # src.save(all_sections)

    # Testing for chapter notes
    src = ChapterNotesSource()
    chapters = [1, 2, 6, 15, 16]  # testing  a few of them
    results = []
    for ch in chapters:
        pdf_path = src.fetch(ch)
        chapter_notes = src.parse(pdf_path)
        results.append(chapter_notes)
        print(f"Chapter {chapter_notes.chapter_number} has {len(chapter_notes.notes)} notes")
    src.save(results)

if __name__ == "__main__":
    main()
