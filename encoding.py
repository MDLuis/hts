import json, time
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import date

# ---------- Data loading ----------
def load_texts(json_path: Path, mode: str) -> list[str]:
    """
    Load and normalize text data from a JSON file for embedding.

    Args:
        json_path (Path): Path to the JSON file to load.
        mode (str): Determines how to extract text:
            - 'notes': For General, Section, Chapter, and Additional US Notes.
                       Extracts 'text' fields from each note object, prepending 'title' if present.
            - 'tariff': For Tariff Tables.
                        Combines 'htsno' (if present) with 'description' for each row.

    Returns:
        list[str]: A flat list of strings ready for embedding.

    Raises:
        ValueError: If an unsupported mode is provided.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []

    if mode == "notes":
        if isinstance(data, list):
            for obj in data:
                if isinstance(obj, dict):
                    if "notes" in obj:
                        for note in obj["notes"]:
                            if "text" in note:
                                texts.append(note["text"])
                    elif "text" in obj:
                        title = obj.get("title", "")
                        t = f"{title} {obj['text']}".strip() if title else obj["text"]
                        texts.append(t)
        elif isinstance(data, dict):
            title = data.get("title", "")
            t = f"{title} {data['text']}".strip() if "text" in data else ""
            if t:
                texts.append(t)

    elif mode == "tariff":
        if isinstance(data, list):
            for table in data:
                if isinstance(table, dict) and "rows" in table:
                    for row in table["rows"]:
                        desc = row.get("description") or ""
                        hts = row.get("htsno") or ""
                        if desc:
                            texts.append(f"{hts} {desc}".strip())
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return texts

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

    Side effects:
        - Creates 'embeddings/' directory if not present.
        - Saves embeddings as `.npy` (versioned by date and 'latest').
        - Saves texts as `.json` (versioned by date and 'latest').
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
        2. Load all datasets from disk (General Notes, Section Notes, etc.).
        3. Encode each dataset, save embeddings and texts, and record timing.
        4. Write a Markdown benchmark file summarizing performance.

    Inputs:
        - Data files under `data/notes/` and `data/tables/`.

    Outputs:
        - Embedding files saved under `embeddings/`.
        - Markdown benchmark summary saved as `benchmarks.md`.
    """
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    base = Path("data/notes")

    datasets = [
        ("General Notes", load_texts(base / "general/general_notes_latest.json", "notes")),
        ("Section Notes", load_texts(base / "section/section_notes_latest.json", "notes")),
        ("Chapter Notes", load_texts(base / "chapter/chapter_notes_latest.json", "notes")),
        ("Additional U.S. Notes", load_texts(base / "additional/additional_us_notes_latest.json", "notes")),
        ("Tariff Tables", load_texts(Path("data/tables/tariff_tables_all_latest.json"), "tariff")),
    ]

    # encode + measure
    results = []
    for name, texts in datasets:
        duration = encode_and_save(texts, model, name.replace(" ", "_").lower())
        results.append((name, len(texts), model_name, duration))

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
        lines.append(f"| {name:<20} | {count:5d} | {model_name:<20} | {duration:10.2f} |\n")

    md_path.write_text("".join(lines), encoding="utf-8")
    print("Benchmarks written to benchmarks.md")

if __name__ == "__main__":
    main()
