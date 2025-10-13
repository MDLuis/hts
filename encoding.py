import json, time
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from datetime import date

def extract_note_text(note_obj, section_title, chapter_title):
    """
    Recursively extract 'text' and 'sub_items' from a note object.

    Each returned item is a dict containing:
        - text (string)
        - section_title (string)
        - chapter_title (string)
        - htsno (optional)
    """
    texts = []
    if isinstance(note_obj, dict):
        main_text = note_obj.get("text", "")
        if main_text:
            texts.append({
                "text": main_text.strip(),
                "section_title": section_title,
                "chapter_title": chapter_title,
                "htsno": note_obj.get("htsno")
            })
        sub_items = note_obj.get("sub_items")
        if sub_items:
            for sub in sub_items:
                if isinstance(sub, str):
                    texts.append({
                        "text": sub.strip(),
                        "section_title": section_title,
                        "chapter_title": chapter_title,
                        "htsno": note_obj.get("htsno")
                    })
                elif isinstance(sub, dict):
                    texts.extend(extract_note_text(sub, section_title, chapter_title))
    return texts

# ---------- Data loading ----------
def load_texts(json_path: Path):
    """
    Load and separate:
      - section_titles
      - chapter_titles
      - chapter_notes
      - tariff_tables
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    section_titles = []
    chapter_titles = []
    chapter_notes = []
    tariff_tables = []

    for section in data.get("sections", []):
        section_title = f"Section {section.get('sec_number', '')}: {section.get('title', '').strip()}".strip(": ")
        section_titles.append(section_title)

        for chapter in section.get("chapters", []) or []:
            chapter_title = f"{chapter.get('ch_number', '')}: {chapter.get('title', '').strip()}"
            chapter_titles.append(f"{section_title} | {chapter_title}")

            notes_container = chapter.get("notes") or {}
            if isinstance(notes_container, dict):
                for note in notes_container.get("notes", []):
                    if not isinstance(note, dict):
                        continue
                    extracted = extract_note_text(note, section_title, chapter_title)
                    chapter_notes.extend(extracted)

            table = chapter.get("table")
            if isinstance(table, dict):
                for row in table.get("rows", []) or []:
                    if not isinstance(row, dict):
                        continue
                    desc = row.get("description", "")
                    hts = row.get("htsno")
                    if desc:
                        tariff_tables.append({
                            "text": desc.strip(),
                            "section_title": section_title,
                            "chapter_title": chapter_title,
                            "htsno": hts
                        })

    return section_titles, chapter_titles, chapter_notes, tariff_tables

# ---------- Encoding ----------
def encode_and_save(items, model, prefix):
    """
    Encode texts or note dicts into embeddings and save embeddings + metadata.
    """
    out_dir = Path("embeddings")
    out_dir.mkdir(parents=True, exist_ok=True)
    version = date.today().isoformat()

    if all(isinstance(i, dict) for i in items):
        texts = [i["text"] for i in items]
    else:
        texts = items

    start = time.perf_counter()
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    duration = time.perf_counter() - start

    # Save embeddings
    np.save(out_dir / f"{prefix}_embeddings_v{version}.npy", embeddings)
    np.save(out_dir / f"{prefix}_embeddings_latest.npy", embeddings)

    # Save metadata
    with open(out_dir / f"{prefix}_metadata_v{version}.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    with open(out_dir / f"{prefix}_metadata_latest.json", "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    return duration

# ---------- Main ----------
def main():
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)
    json_path = Path("data/hts/hts_full_latest.json")

    section_titles, chapter_titles, chapter_notes, tariff_tables = load_texts(json_path)

    results = []

    # Encode each dataset and track performance
    datasets = [
        ("section_titles", section_titles),
        ("chapter_titles", chapter_titles),
        ("chapter_notes", chapter_notes),
        ("tariff_tables", tariff_tables),
    ]

    for name, data_list in datasets:
        if not data_list:
            continue
        duration = encode_and_save(data_list, model, name)
        results.append((name.replace("_", " ").title(), len(data_list), model_name, duration))

    # ---------- Benchmark Markdown ----------
    md_path = Path("benchmarks.md")
    lines = [
        "# Benchmarks – HTS Embedding Encoding\n",
        "\nThis file records how long the embedding process takes on the available hardware.  \n",
        f"All embeddings were generated with [`sentence-transformers`](https://www.sbert.net) using the `{model_name}` model.\n",
        "\n## Notes\n\n",
        "- All times measured with `time.perf_counter()` before and after `model.encode()`.\n",
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
