import json, time
import numpy as np
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

def load_embeddings(prefix: str):
    emb_path = Path(f"embeddings/{prefix}_embeddings_latest.npy")
    meta_path = Path(f"embeddings/{prefix}_metadata_latest.json")

    if not emb_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Missing files for prefix '{prefix}'")

    embeddings = np.load(emb_path)
    metadata = json.load(open(meta_path, "r", encoding="utf-8"))
    return metadata, embeddings

def hierarchical_search(
    query,
    model,
    section_titles,
    section_emb,
    chapter_titles,
    chapter_emb,
    notes,
    tables,
    top_k=3,
    global_table_embs=None,
    global_table_texts=None,
):
    """
    Hierarchical semantic search for HTS queries:
      1. Find best section (with score)
      2. Find best chapter (with score) using precomputed embeddings
      3. Within chapter: top_k notes and top_k tariff table rows
      4. Across all data: global top tariff table row (uses precomputed embeddings)
    """
    # Encode query once
    q_emb = model.encode(query, convert_to_tensor=True)

    # ---------- Step 1: Best Section ----------
    section_scores = util.cos_sim(q_emb, section_emb)[0]
    best_section_idx = int(np.argmax(section_scores))
    best_section = section_titles[best_section_idx]
    best_section_score = float(section_scores[best_section_idx])

    # ---------- Step 2: Best Chapter within section ----------
    chapters_in_section = [(i, ch) for i, ch in enumerate(chapter_titles) if ch.startswith(best_section)]
    if not chapters_in_section:
        return {
            "section": best_section,
            "section_score": best_section_score,
            "chapter": None,
            "chapter_score": 0.0,
            "top_notes": [],
            "top_tables": [],
            "global_top_table": None,
        }

    filtered_ch_idxs = [i for i, _ in chapters_in_section]
    filtered_ch_emb = chapter_emb[filtered_ch_idxs]
    chapter_scores = util.cos_sim(q_emb, filtered_ch_emb)[0]

    best_chapter_idx = filtered_ch_idxs[int(np.argmax(chapter_scores))]
    best_chapter = chapter_titles[best_chapter_idx]
    best_chapter_score = float(chapter_scores[np.argmax(chapter_scores)])
    chapter_name_only = best_chapter.split("|")[-1].strip()

    # ---------- Step 3: Top Notes and Tariff Tables within Chapter ----------
    notes_in_chapter = [n for n in notes if n["chapter_title"] == chapter_name_only]
    tables_in_chapter = [t for t in tables if t["chapter_title"] == chapter_name_only]

    def get_top_results(items):
        if not items:
            return []
        texts = [i["text"] for i in items]
        embs = model.encode(texts, convert_to_tensor=True)
        scores = util.cos_sim(q_emb, embs)[0]
        top_idxs = np.argsort(-scores)[:top_k]
        return [{"text": texts[i], "score": float(scores[i]), "htsno": items[i].get("htsno")} for i in top_idxs]

    top_notes = get_top_results(notes_in_chapter)
    top_tables = get_top_results(tables_in_chapter)

    # ---------- Step 4: Global Top Tariff Table Row ----------
    global_top_table = None
    if global_table_embs is not None and global_table_texts is not None and len(global_table_texts) > 0:
        all_scores = util.cos_sim(q_emb, global_table_embs)[0]
        best_idx = int(np.argmax(all_scores))
        global_top_table = {
            "text": global_table_texts[best_idx],
            "score": float(all_scores[best_idx]),
            "htsno": tables[best_idx].get("htsno"),
            "chapter_title": tables[best_idx].get("chapter_title"),
            "section_title": tables[best_idx].get("section_title"),
        }

    return {
        "section": best_section,
        "section_score": best_section_score,
        "chapter": chapter_name_only,
        "chapter_score": best_chapter_score,
        "top_notes": top_notes,
        "top_tables": top_tables,
        "global_top_table": global_top_table,
    }


def generate_report(report_path: str, query_results: dict):
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# HTS Hierarchical Embedding Query Report\n\n")
        for query, result in query_results.items():
            f.write(f"## Query: {query}\n")
            f.write(f"**Processing Time:** {result['time_taken']:.3f} seconds\n\n")

            f.write(f"### Closest Section\n")
            f.write(f"- **Name:** {result['section']}\n")
            f.write(f"- **Score:** {result['section_score']:.4f}\n\n")

            f.write(f"### Closest Chapter Within Section\n")
            f.write(f"- **Name:** {result['chapter']}\n")
            f.write(f"- **Score:** {result['chapter_score']:.4f}\n\n")

            f.write(f"### Top Notes From Current Chapter\n")
            for note in result["top_notes"]:
                f.write(f"- **Score: {note['score']:.3f}** \n\t - {note['text'][:200]}...\n")
            if not result["top_notes"]:
                f.write("- No notes found.\n")

            f.write(f"\n### Top Tariff Table Rows From Current Chapter\n")
            for row in result["top_tables"]:
                f.write(f"- **Score: {row['score']:.3f}** \n\t - HTS Code: {row.get('htsno')}, {row['text'][:200]}...\n")
            if not result["top_tables"]:
                f.write("- No table rows found.\n")

            if result.get("global_top_table"):
                g = result["global_top_table"]
                f.write("\n### Overall Top Tariff Table Row (From all Chapters)\n")
                f.write(f"- **Score:** {g['score']:.4f}\n")
                f.write(f"- **HTS Code:** {g.get('htsno')}\n")
                f.write(f"- **Section:** {g.get('section_title')}\n")
                f.write(f"- **Chapter:** {g.get('chapter_title')}\n")
                f.write(f"- **Description:** {g['text'][:250]}...\n")
            else:
                f.write("\n### Overall Top Tariff Table Row (From all Chapters)\n- None found.\n")

            f.write("\n---\n\n")


# ---------- Main ----------
def main():
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Load embeddings
    section_titles, section_emb = load_embeddings("section_titles")
    chapter_titles, chapter_emb = load_embeddings("chapter_titles")
    notes, _ = load_embeddings("chapter_notes")
    tables, _ = load_embeddings("tariff_tables")

    # Precompute all tariff table embeddings once
    all_table_texts = [t["text"] for t in tables]
    all_table_embs = model.encode(all_table_texts, convert_to_tensor=True)

    queries = [
        "Meat of bovine animals",
        "Wheat and meslin",
        "Silk fabrics",
        "Passenger motor vehicles",
        "Medicaments containing antibiotics",
        "Flat-rolled products of stainless steel",
        "Mobile phones",
        "Footwear with rubber soles",
        "Jewelry of precious metals",
        "Coffee beans, roasted",
    ]

    query_results = {}
    for q in queries:
        start = time.perf_counter()
        result = hierarchical_search(
            q,
            model,
            section_titles,
            section_emb,
            chapter_titles,
            chapter_emb,
            notes,
            tables,
            top_k=3,
            global_table_embs=all_table_embs,   
            global_table_texts=all_table_texts, 
        )
        elapsed = time.perf_counter() - start
        result["time_taken"] = elapsed
        query_results[q] = result

    # Generate Markdown report
    generate_report("query_report.md", query_results)

if __name__ == "__main__":
    main()
