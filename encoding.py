import json, time
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import date

# ---------- Data loading ----------
def load_texts(json_path: Path) -> dict[str, list[str]]:
    """
    Load and normalize text data from a JSON file for embedding.

    Args:
        json_path (Path): Path to the unified JSON file.

    Returns:
        dict[str, list[str]]: Mapping of dataset name to list of text entries.
     """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    datasets = {
        "general_notes": [],
        "section_notes": [],
        "chapter_notes": [],
        "additional_us_notes": [],
        "tariff_tables": [],
    }

    def extract_note_text(note_obj):
        """Recursively extract text from a note object and its sub-items."""
        texts = []
        if isinstance(note_obj, dict):
            title = note_obj.get("title", "")
            text = note_obj.get("text", "")
            if text:
                combined = f"{title} {text}".strip() if title else text
                texts.append(combined)
            sub_items = note_obj.get("sub_items")
            if sub_items:
                for sub in sub_items:
                    texts.extend(extract_note_text(sub))
        elif isinstance(note_obj, str):
            texts.append(note_obj)
        return texts

    # ---------- General Notes ----------
    for note in data.get("general_notes", []):
        if isinstance(note, dict):
            datasets["general_notes"].extend(extract_note_text(note))

    # ---------- Sections, Chapters, Additional Notes, Tariffs ----------
    for section in data.get("sections", []) or []:
        if not isinstance(section, dict):
            continue

        # Section Notes
        section_notes_container = section.get("notes")
        if isinstance(section_notes_container, dict):
            section_notes = section_notes_container.get("notes", [])
            for note in section_notes:
                datasets["section_notes"].extend(extract_note_text(note))

        # Chapters
        for chapter in section.get("chapters", []) or []:
            if not isinstance(chapter, dict):
                continue

            # Chapter Notes
            chapter_notes_container = chapter.get("notes")
            if isinstance(chapter_notes_container, dict):
                ch_notes = chapter_notes_container.get("notes", [])
                for note in ch_notes:
                    datasets["chapter_notes"].extend(extract_note_text(note))

            # Additional U.S. Notes
            additional = chapter.get("additional")
            if isinstance(additional, dict):
                add_notes = additional.get("notes", [])
                for note in add_notes:
                    datasets["additional_us_notes"].extend(extract_note_text(note))

            # Tariff Table Rows
            table = chapter.get("table")
            if isinstance(table, dict):
                rows = table.get("rows", [])
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    desc = row.get("description")
                    hts = row.get("htsno")
                    if desc:
                        datasets["tariff_tables"].append(f"{hts or ''} {desc}".strip())

    return datasets

# ---------- Encoding ----------
def encode_and_save(texts, model, out_prefix):
    """
    Encode texts into embeddings, save them with versioning, and return encoding duration.

    Args:
        texts (list[str]): List of strings to embed.
        model (SentenceTransformer): Preloaded sentence-transformer model.
        out_prefix (str): Prefix for output filenames (e.g., 'general_notes').

    Returns:
        float: Encoding duration in seconds.
    """
    out_dir = Path("embeddings")
    out_dir.mkdir(parents=True, exist_ok=True)
    version = date.today().isoformat()

    print(f"Encoding {len(texts)} texts for {out_prefix}...")
    start = time.time()
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    end = time.time()
    duration = end - start
    print(f"Encoding took {duration:.2f} seconds for {out_prefix}")

    np.save(out_dir / f"{out_prefix}_embeddings_v{version}.npy", embeddings)
    np.save(out_dir / f"{out_prefix}_embeddings_latest.npy", embeddings)
    with open(out_dir / f"{out_prefix}_texts_v{version}.json", "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)
    with open(out_dir / f"{out_prefix}_texts_latest.json", "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)

    return duration

# ---------- Main ----------
def main():
    """
    Main routine:
        1. Load the SentenceTransformer model.
        2. Load all hierarchical datasets from the unified JSON file.
        3. Encode each dataset, save embeddings/texts, and record timing.
        4. Write a Markdown benchmark summary.
    """
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    json_path = Path("data/hts/hts_full_latest.json")

    datasets = load_texts(json_path)
    results = []

    for key, texts in datasets.items():
        if not texts:
            print(f"Skipping {key} (no texts found)")
            continue
        duration = encode_and_save(texts, model, key)
        results.append((key.replace("_", " ").title(), len(texts), model_name, duration))

    # build the markdown file
    md_path = Path("benchmarks.md")
    lines = [
        "# Benchmarks – HTS Embedding Encoding\n",
        "\nThis file records how long the embedding process takes on the available hardware.  \n",
        f"All embeddings were generated with [`sentence-transformers`](https://www.sbert.net) using the `{model_name}` model.\n",
        "\n## Notes\n\n",
        "- All times measured with `time.time()` before and after `model.encode()`.\n",
        "- Batch size: 32\n\n",
        "## Results\n\n",
        "| Dataset              | # Texts | Model                | Time (seconds) |\n",
        "|----------------------|---------|----------------------|----------------|\n",
    ]
    for name, count, model_name, duration in results:
        lines.append(f"| {name:<25} | {count:5d} | {model_name:<20} | {duration:10.2f} |\n")

    md_path.write_text("".join(lines), encoding="utf-8")
    print("Benchmarks written to benchmarks.md")

if __name__ == "__main__":
    main()
