# Harmonized Tariff Schedule – Ingestion & Embedding Pipeline

This repository implements an end-to-end pipeline to **download, parse, and store** the Harmonized Tariff Schedule (HTS) data — including general notes, section notes, chapter notes, additional U.S. notes, and tariff tables — and then **encode them into embeddings** for search, retrieval, and analysis.

---

## Features

- **Automated PDF ingestion** of HTS sections, chapters, notes, and tariff tables.
- **Clean, structured JSON** outputs for each data type with versioned filenames.
- **Sentence-transformers embeddings** of all texts (notes and tariff tables).
- **Benchmarks** files to track ingesting and encoding performance across datasets.
- **Fully OOP architecture**: each data source is represented by its own class.

---

## Project Structure

```
.
├── ingesting.py                – Main script to fetch and parse HTS data
├── encoding.py                 – Script to generate embeddings from JSON files
├── requirements.txt            - To install libraries needed
├── benchmarkIngest.md          – Timing results for ingesting
├── benchmarks.md               – Timing results for encoding
├── data/
│   ├── notes/
│   │   ├── general/ (general_notes_latest.json)
│   │   ├── section/ (section_notes_latest.json)
│   │   ├── chapter/ (chapter_notes_latest.json)
│   │   └── additional/ (additional_us_notes_latest.json)
│   └── tables/ (tariff_tables_all_latest.json)
├── embeddings/                 – Generated embeddings (.npy) + text files (.json)
└── src/
    ├── base.py     - Abstract class for data sources
    ├── ingest.py   - HTSSource
    ├── models.py   - Data models
    ├── notes.py    – GeneralNotesSource, SectionNotesSource, etc.
    ├── tables.py   – TariffTableSource    
    └── utils.py    - Helper functions for deduplication and retry
```

---

## Class Hierarchy

All scraper classes inherit from a `Source` base (in `src`):

- **GeneralNotesSource** – fetch, parse, and save General Notes.
- **SectionNotesSource** – fetch, parse, and save Section Notes.
- **ChapterNotesSource** – fetch, parse, and save Chapter Notes.
- **AdditionalUSNotesSource** – fetch, parse, and save Additional U.S. Notes.
- **TariffTableSource** – fetch, parse, and save tariff tables.

Each implements:
- `fetch(...)` – download the corresponding PDF or JSON file.
- `parse(pdf_path)` – extract structured text from the PDF or JSON file.
- `save(data, filepath, version)` – store JSON with version and latest copies.

---

## Utilities

The repo also includes helper functions in `utils.py`:

- `get_retry(url, ...)` – download with automatic retries and exponential backoff.

- `deduplicate(data_list, key_attr)` – remove duplicate objects by attribute.

---

## Installation

```bash
git clone <this-repo>
cd <this-repo>
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## How to Run

### 1. Ingest PDFs into JSON

Edit the chapter range in `ingesting.py` as needed (default `range(1,10)`), then:

```bash
python ingesting.py
```

This produces versioned and `_latest.json` files under `data/notes/…` and `data/tables/…`.

### 2. Encode Texts into Embeddings

After ingestion, run:

```bash
python encoding.py
```

This will:
- Load all `_latest.json` files
- Generate embeddings with `all-MiniLM-L6-v2`
- Save versioned `.npy` arrays and `.json` texts under `embeddings/`.

---

## Versioning

Both ingestion and encoding scripts automatically:
- Save a file with today’s date in the filename (e.g. `general_notes_v2025-09-25.json`)
- Update a `_latest.json` or `_latest.npy` copy for convenience.

This ensures reproducibility and a permanent record of past runs.

---

## Benchmarks

### Encoding 
See `benchmarks.md` for encoding performance by dataset, including:
- Number of texts encoded
- Model used
- Time taken on your hardware

### Ingestion
See `benchmarkIngest.md` for ingestion performance by dataset, including:
- Number of items processed
- Total processing time
- Items per second
- Seconds per item
- Per-stage timing (fetch, parse, save)
- Per-chapter timing

---

## Testing & Reliability

- **Stress Tests** (`stressTest.md`) – Shows pipeline performance on small, medium, and large ingestion runs.
- **Robustness Evaluation** (`robustness_report.md`) – Documents idempotency, consistency, interruption handling, and retry behavior.
- **Size Report** (`size_report.md`) – Estimates storage requirements for raw PDFs, raw JSON, and structured JSON, including projections for the full HTS dataset.

---

## Extending the Pipeline

- Increase the chapter ranges in `ingesting.py` to fetch more data.
- Add additional `Source` subclasses in `src` for new document types.
- Swap out the embedding model in `encoding.py` by changing:

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
```

