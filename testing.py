from src.notes import GeneralNotesSource

def main():
    # # Testing the ingest of Sections and Chapters
    # source = HTSSource()
    # pdf_path = source.fetch()
    # sections = source.parse(pdf_path)
    # source.save(sections)

    # # Testing for general notes
    note_num = 4
    src = GeneralNotesSource()
    pdf_path = src.fetch(note_num=note_num)
    notes = src.parse(pdf_path, note_num=note_num)
    src.save(notes)

if __name__ == "__main__":
    main()
