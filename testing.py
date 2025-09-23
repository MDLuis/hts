from src.ingest import HTSSource

def main():
    source = HTSSource()
    pdf_path = source.fetch()
    sections = source.parse(pdf_path)
    source.save(sections)

if __name__ == "__main__":
    main()
