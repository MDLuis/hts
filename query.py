import json, time, re
import numpy as np
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import matplotlib.pyplot as plt
from llama import load_llama, analyze_hts, chat_llama, analyze_notes

def load_embeddings(prefix: str):
    """
    Load precomputed embeddings and metadata given a prefix name.
    Args:
        prefix (str): Dataset prefix (e.g., 'section_titles', 'chapter_notes').
    Returns:
        tuple: (metadata, embeddings)
            - metadata: List of dictionaries describing the text entries.
            - embeddings: NumPy array of corresponding embeddings.
    """
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
            "notes_for_top_global_tables": [],
            "section_scores": section_scores.cpu().numpy(),
            "section_labels": section_titles,
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
    table_scores = None
    table_labels = None
    if tables_in_chapter:
        table_texts = [t["text"] for t in tables_in_chapter]
        table_embs = model.encode(table_texts, convert_to_tensor=True)
        table_scores = util.cos_sim(q_emb, table_embs)[0].cpu().numpy()
        table_labels = [t.get("htsno") for t in tables_in_chapter]

    def get_top_results(items):
        """Helper: compute top_k results with cosine similarity."""
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
    all_table_scores = None
    if global_table_embs is not None and global_table_texts is not None:
        all_table_scores = util.cos_sim(q_emb, global_table_embs)[0].cpu().numpy()
        best_idx = int(np.argmax(all_table_scores))
        global_top_table = {
            "text": global_table_texts[best_idx],
            "score": float(all_table_scores[best_idx]),
            "htsno": tables[best_idx].get("htsno"),
            "chapter_title": tables[best_idx].get("chapter_title"),
            "section_title": tables[best_idx].get("section_title"),
        }

    notes_for_top_global_tables = []
    if all_table_scores is not None:
        top_table_idx = np.argsort(-all_table_scores)[:10]
        chapters_in_top_tables = {tables[i]["chapter_title"] for i in top_table_idx if tables[i].get("chapter_title")}

        matching_notes = [n for n in notes if n["chapter_title"] in chapters_in_top_tables]
        if matching_notes:
            note_texts = [n["text"] for n in matching_notes]
            note_embs = model.encode(note_texts, convert_to_tensor=True)
            note_scores = util.cos_sim(q_emb, note_embs)[0].cpu().numpy()
            top_note_idx = np.argsort(-note_scores)[:10]
            notes_for_top_global_tables = [
                {
                    "text": note_texts[i],
                    "score": float(note_scores[i]),
                    "chapter_title": matching_notes[i]["chapter_title"],
                    "section_title": matching_notes[i]["section_title"],
                }
                for i in top_note_idx
            ]

    return {
        "section": best_section,
        "section_score": best_section_score,
        "chapter": chapter_name_only,
        "chapter_score": best_chapter_score,
        "top_notes": top_notes,
        "top_tables": top_tables,
        "global_top_table": global_top_table,
        "notes_for_top_global_tables": notes_for_top_global_tables,
        "section_scores": section_scores.cpu().numpy(),
        "section_labels": section_titles,
        "chapter_scores": chapter_scores.cpu().numpy(),
        "chapter_labels": [ch for _, ch in chapters_in_section],
        "chapter_table_scores": table_scores,
        "chapter_table_labels": table_labels,
        "global_table_scores": all_table_scores,
    }


def generate_report(report_path: str, query_results: dict):
    """
    Generate a Markdown report summarizing hierarchical search results for multiple queries, including similarity scores and top matches.
    """
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

def extract_number(text, level="generic"):
    if level == "section":
        m = re.search(r"Section\s+([IVXLCDM]+)", text)
        if m:
            return f"Section {m.group(1)}"
    elif level == "chapter":
        m = re.search(r"(\d{1,3})(?::|\s|$)", text.split("|")[-1].strip())
        if m:
            return f"Chapter {m.group(1)}"
    elif level == "table":
        m = re.search(r"(\d{2,8}(?:\.\d+)*)", text)
        if m:
            return f"HTSNO {m.group(1)}"
    return text.strip()[:15]

def plot_similarity_graph(labels, scores, title, output_path):
    """Plot a basic bar chart for similarity scores."""
    plt.figure(figsize=(6, 5))
    plt.bar(labels, scores)
    plt.ylabel("Cosine Similarity")
    plt.title(title)
    plt.ylim(0, 1)
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

def generate_graphs_for_query(query, result, tables):
    """
    Generate similarity graphs (sections, chapters, tables, global tables) for a single query using precomputed cosine similarity scores.
    """
    graphs_dir = Path("graphs")
    graphs_dir.mkdir(exist_ok=True)
    paths = {}

    # ---- Sections ----
    section_scores = result["section_scores"]
    section_labels = [extract_number(s, "section") for s in result["section_labels"]]
    top_idx = np.argsort(-section_scores)[:5]
    path = graphs_dir / f"{query.replace(' ', '_')}_sections.png"
    plot_similarity_graph([section_labels[i] for i in top_idx], section_scores[top_idx], f"Top 5 Sections – {query}", path)
    paths["sections"] = path

    # ---- Chapters ----
    if "chapter_scores" in result:
        chapter_scores = result["chapter_scores"]
        chapter_labels = [extract_number(ch, "chapter") for ch in result["chapter_labels"]]
        top_idx = np.argsort(-chapter_scores)[:5]
        path = graphs_dir / f"{query.replace(' ', '_')}_chapters.png"
        plot_similarity_graph([chapter_labels[i] for i in top_idx], chapter_scores[top_idx], f"Top 5 Chapters in {extract_number(result['section'], 'section')}", path)
        paths["chapters"] = path

    # ---- Tables within Chapter ----
    if "chapter_table_scores" in result and result["chapter_table_scores"] is not None:
        tbl_scores = result["chapter_table_scores"]
        tbl_labels = [
            extract_number(htsno or f"Row{i}", "table")
            for i, htsno in enumerate(result["chapter_table_labels"])
        ]
        top_idx = np.argsort(-tbl_scores)[:5]
        path = graphs_dir / f"{query.replace(' ', '_')}_tables.png"
        plot_similarity_graph(
            [tbl_labels[i] for i in top_idx],
            tbl_scores[top_idx],
            f"Top 5 Tables Rows in {extract_number(result['chapter'], 'chapter')}",
            path
        )
        paths["tables"] = path

    # ---- Global Tables ----
    if "global_table_scores" in result and result["global_table_scores"] is not None:
        global_scores = result["global_table_scores"]
        top_idx = np.argsort(-global_scores)[:5]
        global_labels = [extract_number(tables[i].get("htsno", f"Row{i}"), "table") for i in top_idx]
        path = graphs_dir / f"{query.replace(' ', '_')}_global.png"
        plot_similarity_graph(global_labels, global_scores[top_idx],"Top 5 Overall Tables Rows (All Chapters)", path)
        paths["global"] = path

    return paths

def write_graphs_markdown(md_path, title, graph_files):
    """Write Markdown file embedding all generated graph images."""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        for query, paths in graph_files.items():
            f.write(f"## Query: {query}\n\n")
            for label, path in paths.items():
                f.write(f"**{label.replace('_', ' ').title()}:**\n\n![]({path.as_posix()})\n\n")
            f.write("\n---\n\n")

def generate_graphs(output_path, query_results, tables):
    """
    Generate and aggregate all similarity graphs for every query.
    """
    graph_files = {}
    for query, result in query_results.items():
        graph_files[query] = generate_graphs_for_query(query, result, tables)
    write_graphs_markdown(output_path, "HTS Hierarchical Similarity Graphs", graph_files)

def plot_trend_graph(scores, title, output_path):
    """Plot a bar-style similarity trend graph for a chapter or set of tables."""
    colors = ["royalblue", "darkorange"]
    bar_colors = [colors[i % 2] for i in range(len(scores))]
    plt.figure(figsize=(8, 4))
    plt.bar(range(len(scores)), scores, color=bar_colors)
    plt.ylabel("Cosine Similarity")
    plt.title(title)
    plt.ylim(0, 1)
    plt.xticks([]) 
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

def generate_table_trend_graphs_for_query(query, result, tables):
    """
    Create trend graphs showing similarity patterns for tables within one chapter and across all chapters.
    """
    graphs_dir = Path("trend_graphs")
    graphs_dir.mkdir(exist_ok=True)
    paths = {}
    # Chapter trend
    if "chapter_table_scores" in result and result["chapter_table_scores"] is not None:
        tbl_scores = result["chapter_table_scores"]
        path = graphs_dir / f"{query.replace(' ', '_')}_chapter_trend.png"
        plot_trend_graph(
            tbl_scores,
            f"Table Similarity Trend – {extract_number(result['chapter'], 'chapter')}",
            path
        )
        paths["chapter_trend"] = path

    # All chapters trend
    all_ch_paths = generate_all_chapters_trend_graph_for_query(query, result, tables)
    paths.update(all_ch_paths)

    return paths

def generate_table_trend_graphs(output_path, query_results, tables):
    """
    Generate Markdown file containing all per-query trend graphs.
    """
    trend_graph_files = {}
    for query, result in query_results.items():
        trend_graph_files[query] = generate_table_trend_graphs_for_query(query, result, tables)
    write_graphs_markdown(output_path,"HTS Table Similarity Trend Graphs",trend_graph_files)

def plot_all_chapters_trend_graph(all_scores, all_labels, title, output_path):
    """
    Scatter-plot showing similarity distribution across all tariff tables grouped by chapter to visualize relative relevance density.
    """
    plt.figure(figsize=(12, 4))
    chapters = [label.split("|")[-1].strip() for label in all_labels]
    unique_chapters = []
    chapter_indices = []
    last_ch = None
    for i, ch in enumerate(chapters):
        if ch != last_ch:
            unique_chapters.append(ch)
            chapter_indices.append(i)
            last_ch = ch
    chapter_indices.append(len(chapters))
    # two alternating colors for points
    colors = ["#3b82f6", "#f97316"]
    # plot each chapter segment with its color
    for i in range(len(unique_chapters)):
        start = chapter_indices[i]
        end = chapter_indices[i + 1]
        color = colors[i % 2]
        plt.scatter(
            np.arange(start, end),
            all_scores[start:end],
            s=2,
            color=color,
            alpha=0.7,
        )
    plt.ylabel("Cosine Similarity")
    plt.title(title)
    plt.xlim(-len(all_scores)*0.01, len(all_scores) - 1 + (len(all_scores)*0.01))
    plt.ylim(0, 1)
    plt.xticks([])
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight", dpi=200)
    plt.close()

def generate_all_chapters_trend_graph_for_query(query, result, tables):
    """
    Generate an all-chapter similarity scatter graph for a given query.
    """
    graphs_dir = Path("trend_graphs")
    graphs_dir.mkdir(exist_ok=True)
    paths = {}
    if "global_table_scores" in result and result["global_table_scores"] is not None:
        scores = result["global_table_scores"]
        labels = [t["chapter_title"] for t in tables]
        path = graphs_dir / f"{query.replace(' ', '_')}_all_chapters_trend.png"
        plot_all_chapters_trend_graph(
            scores,
            labels,
            f"Similarity Trend Across All Chapters – {query}",
            path
        )
        paths["all_chapters_trend"] = path

    return paths

def generate_llama_report(output_path, llama_results):
    """
    Save Markdown summaries of LLaMA model responses for each query.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Llama 3.2-3B Reasoning Results\n\n")
        for query, result in llama_results.items():
            f.write(f"## Query: {query}\n")
            f.write("### Step 1 – Based on Tariff Tables\n")
            f.write(f"**Processing Time:** {result['time_t']:.2f} seconds\n\n")            
            f.write(result["tables"].strip() + "\n\n")
            f.write("### Step 2 – Refined with Chapter Notes\n")
            f.write(f"**Processing Time:** {result['time_n']:.2f} seconds\n\n")
            f.write(result["notes"].strip() + "\n\n")
            f.write("\n\n---\n\n")
            f.write(f"**Processing Time:** {result['time_taken']:.2f} seconds\n\n")
            f.write(result["explanation"].strip())
            f.write("\n\n---\n\n")

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
    all_note_texts = [n["text"] for n in notes]
    all_note_embs = model.encode(all_note_texts, convert_to_tensor=True)

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
        result["time_taken"] = time.perf_counter() - start
        query_results[q] = result

    # Generate Markdown report
    generate_report("query_report.md", query_results)
    generate_graphs("graphs.md", query_results, tables)
    generate_table_trend_graphs("trend_graphs.md", query_results, tables)

    # ---------- Run Llama reasoning for selected queries ----------
    llama_queries = ["Silk fabrics"]
    llama_pipe = load_llama()
    llama_results = {}

    for q in llama_queries:
        print(f"\n[LLAMA] Evaluating: {q}")
        res = query_results[q]

        global_tables = []
        if res.get("global_table_scores") is not None and res.get("global_table_texts") is not None:
            scores = np.array(res["global_table_scores"])
            texts = res["global_table_texts"]
            top_idx = np.argsort(-scores)[:10]
            global_tables = [
                {
                    "text": texts[i],
                    "score": float(scores[i]),
                    "htsno": tables[i].get("htsno"),
                    "chapter_title": tables[i].get("chapter_title"),
                }
                for i in top_idx
            ]
        elif res.get("global_top_table"):
            global_tables = [res["global_top_table"]]

        filtered_notes = res.get("notes_for_top_global_tables", [])

        llama_tables = analyze_hts(
            query=q,
            tables=global_tables,
        )
        response_t, messages_t, time_t = chat_llama(llama_pipe, llama_tables)

        llama_notes = analyze_notes(filtered_notes,messages_t)
        response_n, llama_text, time_n = chat_llama(llama_pipe, llama_notes)

        while True:
            response, new_messages, llama_time = chat_llama(llama_pipe, llama_text)
            llama_text = new_messages

            print(response)

            reply = input("Response (q to exit): ")
            if reply.lower() == 'q':
                break

            llama_text.append({
                "role": "user",
                "content": reply,
            })

        llama_results[q] = {
            "tables": response_t,
            "notes": response_n,
            "explanation": response,
            "time_taken": llama_time,
            "time_t": time_t,
            "time_n": time_n,
        }

    generate_llama_report("llama.md", llama_results)

if __name__ == "__main__":
    main()
