import json, time
import numpy as np
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

def load_embeddings(prefix: str):
    """
    Load the latest embeddings and their associated texts.
    """
    emb_path = Path(f"embeddings/{prefix}_embeddings_latest.npy")
    txt_path = Path(f"embeddings/{prefix}_texts_latest.json")

    if not emb_path.exists() or not txt_path.exists():
        raise FileNotFoundError(f"Missing files for prefix '{prefix}'")

    embeddings = np.load(emb_path)
    texts = json.load(open(txt_path, "r", encoding="utf-8"))
    return texts, embeddings

def query_embeddings(query: str, model, texts, embeddings, top_k=3):
    """
    Encode a query and return the top_k most similar entries.
    Returns a list of dicts for reporting.
    """
    query_emb = model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_emb, embeddings)[0]
    top_results = np.argsort(-cosine_scores)[:top_k]

    results = []
    for rank, idx in enumerate(top_results, start=1):
        score = float(cosine_scores[idx])
        snippet = texts[idx][:300].replace("\n", " ")
        results.append({
            "rank": rank,
            "score": score,
            "text_snippet": snippet
        })
    return results


def generate_report(report_path: str, query_results: dict):
    """
    Generate a Markdown report from query results including time taken.
    """
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# HTS Hierarchical Query Report\n\n")
        f.write("This report shows top semantic matches across all HTS layers.\n\n")

        for query, layer_data in query_results.items():
            f.write(f"## 🔍 Query: **{query}**\n\n")

            for layer_name, results_info in layer_data.items():
                if not results_info:
                    continue
                results = results_info["results"]
                elapsed = results_info["time_taken"]

                f.write(f"### 📘 {layer_name.replace('_', ' ').title()}\n")
                f.write(f"Time taken: `{elapsed:.3f}s`\n\n")

                if not results:
                    f.write("_No matches found._\n\n")
                    continue

                for r in results:
                    f.write(f"- **Rank {r['rank']}** | Score `{r['score']:.4f}`\n")
                    f.write(f"  > {r['text_snippet']}...\n\n")

            f.write("\n---\n\n")


def main():
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Hierarchical datasets to include
    prefixes = [
        "general_notes",
        "section_notes",
        "chapter_notes",
        "additional_us_notes",
        "tariff_tables"
    ]

    # Hardcoded queries
    queries = [
        "Live cattle and other animals",
        "Dairy products including milk and butter",
        "Edible roots and tubers",
        "Coffee, tea, and spices",
        "yogurt",
        "unroasted iron pyrites",
        "milk and cream",
        "Meat of bovine animals",
        
    ]

    query_results = {}

    # Loop through each query and evaluate on all datasets
    for query in queries:
        layer_results = {}
        for prefix in prefixes:
            texts, embeddings = load_embeddings(prefix)
            if texts is None or embeddings is None:
                continue

            start = time.perf_counter()
            results = query_embeddings(query, model, texts, embeddings, top_k=3)
            elapsed = time.perf_counter() - start
            layer_results[prefix] = {"results": results, "time_taken": elapsed}

        query_results[query] = layer_results

    # Generate Markdown report
    report_path = "query_report.md"
    generate_report(report_path, query_results)

if __name__ == "__main__":
    main()
