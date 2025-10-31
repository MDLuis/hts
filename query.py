import json, time, re
import numpy as np
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import matplotlib.pyplot as plt
from .llama import load_llama, analyze_hts, chat_llama, analyze_notes

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
    # emb_path = Path(f"embeddings/{prefix}_embeddings_latest.npy")
    # meta_path = Path(f"embeddings/{prefix}_metadata_latest.json")
    base_dir = Path(__file__).resolve().parent / "embeddings"
    emb_path = base_dir / f"{prefix}_embeddings_latest.npy"
    meta_path = base_dir / f"{prefix}_metadata_latest.json"

    if not emb_path.exists() or not meta_path.exists():
        raise FileNotFoundError(f"Missing files for prefix '{prefix}'")

    embeddings = np.load(emb_path)
    metadata = json.load(open(meta_path, "r", encoding="utf-8"))
    return metadata, embeddings

def hierarchical_search(
    query,
    model,
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
        "global_top_table": global_top_table,
        "notes_for_top_global_tables": notes_for_top_global_tables,
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
    if level == "table":
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

        print(response_n)
        reply = input("Response: ")
        llama_text.append({
            "role": "user",
            "content": reply,
        })

        total_time = 0
        while True:
            response, new_messages, llama_time = chat_llama(llama_pipe, llama_text)
            llama_text = new_messages
            total_time += llama_time

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
            "time_taken": total_time,
            "time_t": time_t,
            "time_n": time_n,
        }

    generate_llama_report("llama.md", llama_results)

def start_conv(description):
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Load embeddings
    notes, _ = load_embeddings("chapter_notes")
    tables, _ = load_embeddings("tariff_tables")

    # Precompute all tariff table embeddings once
    all_table_texts = [t["text"] for t in tables]
    all_table_embs = model.encode(all_table_texts, convert_to_tensor=True)

    result = hierarchical_search(
            description,
            model,
            notes,
            tables,
            global_table_embs=all_table_embs,
            global_table_texts=all_table_texts,
        )
    
    pipe = load_llama()

    global_tables = []
    if result.get("global_table_scores") is not None and result.get("global_table_texts") is not None:
        scores = np.array(result["global_table_scores"])
        texts = result["global_table_texts"]
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
    elif result.get("global_top_table"):
        global_tables = [result["global_top_table"]]

    filtered_notes = result.get("notes_for_top_global_tables", [])

    llama_tables = analyze_hts(
        query=description,
        tables=global_tables,
    )
    _, messages_t, _ = chat_llama(pipe, llama_tables)

    llama_notes = analyze_notes(filtered_notes,messages_t)
    response_n, messages_n, _ = chat_llama(pipe, llama_notes)


    return {
        "response": response_n,
        "messages": messages_n,
    }

def continue_conv(reply, messages):
    pipe = load_llama()
    messages.append({
        "role": "user",
        "content": reply,
    })
    response, new_messages, _ = chat_llama(pipe, messages)
    return {
        "response": response,
        "messages": new_messages,
    }

if __name__ == "__main__":
    main()
