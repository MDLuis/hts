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
        snippet = texts[idx][:300]
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
        f.write(f"# HTS Embedding Query Report\n")
        f.write(f"This report shows the top results for each query along with the time taken to compute them.\n\n")

        for query, data in query_results.items():
            results = data["results"]
            elapsed = data["time_taken"]

            f.write(f"## Query: {query}\n")
            f.write(f"**Time taken:** {elapsed:.4f} seconds\n\n")

            for r in results:
                f.write(f"**Rank {r['rank']} | Score: {r['score']:.4f}**\n\n")
                f.write(f"{r['text_snippet']}...\n\n")
            f.write("\n\n")


def main():
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    # Dataset
    prefix = "chapter_notes"
    texts, embeddings = load_embeddings(prefix)

    # Hardcoded queries
    queries = [
        # Related to Chapters 1-9
        "Live cattle and other animals",
        "Dairy products including milk and butter",
        "Edible roots and tubers",
        "Coffee, tea, and spices",
        "Silk and woven textile fabrics",
        # HTS-related but outside Chapters 1-9
        "Vehicles and automotive parts",
        "Pharmaceutical products and chemicals",
        "Iron and steel products",
        "Electronic machinery and components",
        "Plastic and rubber materials"
    ]

    # Run queries and store results
    query_results = {}
    for query in queries:
        start = time.perf_counter()
        results = query_embeddings(query, model, texts, embeddings)
        elapsed = time.perf_counter() - start
        query_results[query] = {
        "results": results,
        "time_taken": elapsed
    }

    # Generate Markdown report
    report_path = "query_report.md"
    generate_report(report_path, query_results)

if __name__ == "__main__":
    main()
