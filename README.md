# Harmonized Tariff Schedule – Ingestion, Embedding & Reasoning Pipeline

This repository implements an end-to-end pipeline to **download, parse, and store** the Harmonized Tariff Schedule (HTS) data — including general notes, section notes, chapter notes, additional U.S. notes, tariff tables, and rules of interpretation — and then **encode them into embeddings** for semantic search, retrieval, and analysis.
It also includes **a reasoning module (Llama 3.2)** to generate structured clarifying questions about HTS-related queries using contextual embeddings and rules of interpretation.

---

## Features

- **Automated PDF and JSON ingestion** of HTS sections, chapters, notes, and tariff tables.  
- **Clean, structured JSON outputs** for each data type with versioned and `_latest` copies.  
- **Sentence-transformers embeddings** for all notes, tables, and titles.  
- **Hierarchical semantic search**: query → section → chapter → notes → tariff rows.  
- **Integrated Llama reasoning**: contextual reflection and clarification using retrieved content.  
- **CBP Rulings downloader and parser** for cross-referencing legal rulings.  
- **Rules of Interpretation ingestion** (General and Additional U.S.).  
- **Benchmarking & size analytics** for ingestion, encoding, and storage footprint.  
- **Fully OOP architecture**: every data source inherits from a `Source` base class.

---

## Project Structure

```
.
├── ingesting.py                – Main script to fetch and parse HTS data
├── encoding.py                 – Generates embeddings for all notes, titles, and tables
├── query.py                    – Performs hierarchical semantic search & similarity graphs
├── llama.py                    – Llama 3.2 reasoning on top of retrieved HTS context
├── size.py                     – Generates markdown report on file sizes and projections
├── requirements.txt            – Python dependencies
├── benchmarkIngest.md          – Timing results for ingesting
├── benchmarks.md               – Timing results for encoding
│
├── data/
│   ├── notes/
│   │   ├── general/ (general_notes_latest.json)
│   │   ├── section/ (section_notes_latest.json)
│   │   ├── chapter/ (chapter_notes_latest.json)
│   │   └── additional/ (additional_us_notes_latest.json)
│   ├── tables/ (tariff_tables_all_latest.json)
│   ├── rules/ (general_rules_latest.json)
│   └── hts/ (hts_full_latest.json)
│
├── embeddings/                 – Generated embeddings (.npy) and metadata (.json)
├── CBPrulings/                 – CBP ruling PDFs, DOCs, and parsed JSONs
├── graphs/                     – Similarity and trend graph images
│
└── src/
    ├── base.py                 – Abstract class for data sources
    ├── ingest.py               – HTSSource (Table of Contents parser)
    ├── notes.py                – GeneralNotesSource, SectionNotesSource, etc.
    ├── tables.py               – TariffTableSource
    ├── rules.py                – GeneralRules (General & Additional U.S. Rules)
    ├── rulings.py              – CBP Rulings scraper and parser
    ├── models.py               – Pydantic models for structured HTS data
    └── utils.py                – Helper functions for retries, deduplication, and combination
```

---

## Class Hierarchy

All scraper classes inherit from a `Source` base (in `src/base.py`):

- **HTSSource** – downloads and parses the HTS Table of Contents.  
- **GeneralNotesSource** – fetches and parses General Notes.  
- **SectionNotesSource** – fetches and parses Section Notes.  
- **ChapterNotesSource** – fetches and parses Chapter Notes.  
- **AdditionalUSNotesSource** – fetches and parses Additional U.S. Notes.  
- **TariffTableSource** – fetches and parses Tariff Tables (JSON endpoints).  
- **GeneralRules** – fetches and parses the General and Additional Rules of Interpretation.  
- **Rulings** – fetches CBP ruling PDFs/DOCs for given HTS codes.  

Each implements:
- `fetch(...)` – download the corresponding PDF or JSON file.
- `parse(...)` – extract structured text from the PDF or JSON file.
- `save(...)` – store JSON with version and latest copies.

---

## Utilities

The repo includes helper utilities (`src/utils.py`):

- `get_retry(url, retries=5, backoff_factor=0.5)` – HTTP GET with automatic retries.  
- `deduplicate(data_list, key_attr)` – remove duplicates by attribute.  
- `combine()` – merges all parsed data (sections, notes, tables) into a unified `hts_full_latest.json`.

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

### 1. Ingest PDFs and JSONs into Structured Data

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


### 3. Perform Hierarchical Query & Similarity Analysis

```bash
python query.py
```

This will:
- Run multi-stage semantic retrieval (section → chapter → notes → tariff tables)  
- Generate reports (`query_report.md`)  
- Create similarity and trend graphs (`graphs.md`, `trend_graphs.md`)  

---

### 4. Llama 3.2 Reasoning

```bash
(Llama reasoning is invoked automatically when running query.py for selected queries.)
```

Performs contextual reasoning using **Llama 3.2-3B-Instruct**:
- Loads the retrieved notes and table rows  
- Reflects on missing product information  
- Generates **clarifying questions** based on HTS General Rules  

---

### 5. Storage Size Report

```bash
python size.py
```

Generates `size_report.md` showing:
- Total and average file sizes across stages  
- Expansion ratios between raw PDFs → structured JSONs  
- Projected full-HTS storage footprint  

---

## Benchmarks

- **Encoding**: `benchmarks.md` (texts encoded, model used, time taken)
- **Ingestion**: `benchmarkIngest.md` (dataset timings and throughput)
- **Reasoning**: `llama.md` (prompt and response timing)
- **Size Analysis**: `size_report.md` (space metrics and projections)
- **Query Report**: `query_report.md` (semantic retrieval and similarity scores)

---

## Testing & Reliability

- **Stress Tests** (`stressTest.md`) – Shows pipeline performance on small, medium, and large ingestion runs.
- **Robustness Evaluation** (`robustness_report.md`) – Documents idempotency, consistency, interruption handling, and retry behavior.
- **Size Report** (`size_report.md`) – Estimates storage requirements for raw PDFs, raw JSON, and structured JSON, including projections for the full HTS dataset.

---

## Extending the Pipeline

- Add new subclasses of `Source` for additional data types.  
- Change embedding model in `encoding.py` by updating:

```python
model = SentenceTransformer("all-MiniLM-L6-v2")
```

- Integrate new reasoning models in `llama.py` by replacing:

```python
model_id = "meta-llama/Llama-3.2-3B-Instruct"
```

---
