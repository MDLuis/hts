import torch, time
from transformers import pipeline

def load_llama():
    model_id = "meta-llama/Llama-3.2-3B"
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
        f"- Score {n['score']:.3f}: {n['text'][:200]}" for n in notes
    ]) or "No notes available."

    tables_text = "\n".join([
        f"- HTSNO {t.get('htsno', 'N/A')}, Score {t['score']:.3f}: {t['text'][:200]}"
        for t in tables
    ]) or "No tables available."

    prompt = f"""
    You are an expert in the U.S. Harmonized Tariff Schedule (HTS) classification.

    Query: "{query}"

    Top Global Chapter Notes:
    {notes_text}

    Top Global Tariff Table Rows:
    {tables_text}

    Using the meaning of these notes and the table rows, decide which HTS code (HTSNO) best fits the query.
    The notes should guide your interpretation of what classification applies.

    Return ONLY valid JSON:
    {{
    "best_htsno": "<code>",
    "confidence": "<0-1>",
    "reason": "<short explanation>"
    }}
    Answer:
    """
    start = time.perf_counter()
    response = pipe(
        prompt.strip(),
        temperature=0.2,
        top_p=0.9,
        do_sample=True,
        max_new_tokens=300,
    )
    end = time.perf_counter() - start
    result = response[0]["generated_text"].strip()
    return result, end