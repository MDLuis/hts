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

def analyze_hts(pipe, query, notes, tables):
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
            "content": (
                "You are an expert analyst of the U.S. Harmonized Tariff Schedule (HTS). "
                "Your task is NOT to classify or suggest any HTS code, not even tentatively. "
                "You must not mention chapters, headings, or HTS numbers as possible classifications. "
                "Instead, your only goal is to determine whether there is enough information "
                "to make a confident classification later.\n\n"
                "Focus entirely on identifying what information is missing, "
                "and ask clear, specific clarifying questions about the product.\n\n"
                "Structure your reasoning around three pillars:\n"
                "1. Where it is from (source or origin)\n"
                "2. How it is made (composition or process)\n"
                "3. What it is used for (purpose or application)\n\n"
                "For each unclear pillar, ask questions to clarify it. "
                "Do not give any indication of which HTS chapter or code it might belong to."
            ),
        },
        {
            "role": "user",
            "content": f"Query: '{query}'\n\nTop Relevant Notes:\n{notes_text}\n\nTop Relevant Tariff Table Rows:\n{tables_text}\n\nBased on this, reflect on what information is missing."
        },
    ]

    start = time.perf_counter()
    response = pipe(
        messages,
        temperature=0.6,
        top_p=0.9,
        do_sample=True
    )
    end = time.perf_counter() - start
    result = response[0]["generated_text"].strip()
    return result, end