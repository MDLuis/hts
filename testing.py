from src.notes import GeneralNotesSource
from src.ingest import HTSSource

def main():
    # # Testing the ingest of Sections and Chapters
    # source = HTSSource()
    # pdf_path = source.fetch()
    # sections = source.parse(pdf_path)
    # source.save(sections)

    # # Testing for general notes
    note_num = 1
    listNotes = []
    src = GeneralNotesSource()
    while note_num <= 36:
        if note_num == 19:
            note_num=25
        pdf_path = src.fetch(note_num=note_num)
        notes = src.parse(pdf_path, note_num=note_num)
        listNotes.append(notes)
        print(note_num, "=>", repr(notes.title))
        note_num += 1
    src.save(listNotes)

if __name__ == "__main__":
    main()
