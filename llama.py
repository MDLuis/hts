import torch, time
from transformers import pipeline

def load_llama():
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        return_full_text=False,
    )
    return pipe

def analyze_best_hts(pipe, query, notes, tables):
    notes_text = "\n".join([
        f"- [Chapter: {n.get('chapter_title', 'N/A')}] Score {n['score']:.3f}: {n['text'][:200]}" for n in notes
    ]) or "No notes available."

    tables_text = "\n".join([
        f"- [Chapter: {t.get('chapter_title', 'N/A')}] HTSNO {t.get('htsno', 'N/A')}, Score {t['score']:.3f}: {t['text'][:200]}"
        for t in tables
    ]) or "No tables available."

    messages = [
        {
            "role": "system",
            "content": "You are an expert in the U.S. Harmonized Tariff Schedule (HTS) classification. Using the meaning of the given notes and the table rows, decide which HTS code (HTSNO) best fits the given query.The notes should guide your interpretation of what classification applies."
        },
        {
            "role": "user",
            "content": f"Query: '{query}'\n\nTop Relevant Notes:\n{notes_text}\n\nTop Relevant Tariff Table Rows:\n{tables_text}\n\nExplain which HTS code best matches the query and why."
        },
    ]

    start = time.perf_counter()
    response = pipe(
        messages,
        temperature=0.2,
        top_p=0.9,
        do_sample=True,
        max_new_tokens=300,
    )
    end = time.perf_counter() - start
    result = response[0]["generated_text"].strip()
    return result, end