import torch, time, json
from transformers import pipeline

def load_llama():
    """
    Load and initialize the Meta Llama-3.2-3B-Instruct model using Hugging Face's transformers pipeline.
    Returns:
        transformers.Pipeline: A text-generation pipeline ready for inference.
    """
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    pipe = pipeline(
        "text-generation",
        model=model_id,
        dtype=torch.bfloat16,
        device_map="auto",
        return_full_text=False,
    )
    return pipe

def load_general_rules(path="hts/data/rules/general_rules_latest.json") -> str:
    """
    Load and format the General Rules of Interpretation and Additional U.S. Rules from a JSON file into a readable string.
    Args:
        path (str): Path to the JSON rules file.
    Returns:
        str: Formatted multiline string containing all rules and compiler notes.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = ["General Rules of Interpretation: "]

    # Build General Rules of Interpretation text
    for rule in data.get("general_rules", []):
        if rule.get("text"):
            lines.append(f"Rule {rule['rule_number']}: {rule['text'].strip()}")
        if rule.get("sub_items"):
            for sub in rule["sub_items"]:
                lines.append(f"  {sub['label']} {sub['text'].strip()}")

    # Append Additional U.S. Rules
    lines.append("\n Additional U.S. Rules of Interpretation: ")
    for rule in data.get("additional_rules", []):
        lines.append(f"Rule {rule['rule_number']}: {rule['text'].strip()}")
        for sub in rule.get("sub_items", []):
            lines.append(f"  {sub['label']} {sub['text'].strip()}")

    # Append compiler note if present
    lines.append("\n Compiler's Note: ")
    lines.append(data.get("compiler_note", "").strip())

    return "\n".join(lines)

def analyze_hts(query, tables):
    """
    Construct the message context for a conversational LLama model to analyze missing information in an HTS classification query.
    The model is guided by the General Rules of Interpretation and Additional U.S. Rules.
    Args:
        query (str): The user query (e.g., description of a product).
        tables (list[dict]): Top-relevant tariff table entries.
    Returns:
        list[dict]: A message sequence suitable for Llama chat completion.
    """
    general_rules = load_general_rules()

    # Summarize top-relevant tariff table rows
    tables_text = "\n".join([
        f"- [Chapter: {t.get('chapter_title', 'N/A')}] HTSNO {t.get('htsno', 'N/A')}, Score {t['score']:.3f}: {t['text'][:200]}"
         for t in tables
    ]) or "No tables available."

    # Build structured conversation for the model
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert analyst of the U.S. Harmonized Tariff Schedule (HTS). "
                "You must always apply the General Rules of Interpretation  and "
                "the Additional U.S. Rules of Interpretation as guiding legal principles "
                "when reasoning about classification or when deciding what clarifying questions to ask.\n\n"
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
                "Here are the full General Rules of Interpretation for your reference:\n\n"
                f"{general_rules}"
            ),
        },
        {
            "role": "user",
            "content": (
                f"Query: '{query}'\n\n"
                f"Here are the top relevant tariff table rows:\n{tables_text}\n\n"
                "Based only on these, ask clear, specific questions."
            ),
        },
    ]
    return messages

def analyze_notes(notes, messages):
    # notes (list[dict]): Top-relevant note entries with scores and text.
    # Summarize top-relevant notes
    notes_text = "\n".join([
        f"- [Chapter: {n.get('chapter_title', 'N/A')}] Score {n['score']:.3f}: {n['text'][:200]}" for n in notes
     ]) or "No notes available."

    messages.append({
        "role": "user",
        "content": (
            f"Here are the most relevant chapter notes for the same chapters:\n{notes_text}\n\n"
            "Please refine or add to your previous questions using the legal nuances from these notes. "
            "Ensure the final set of questions would cover all potential ambiguities a customs analyst should clarify."
        ),
    })

    return messages 

def chat_llama(pipe, messages):
    """
    Generate a chat response from the Llama pipeline based on structured messages.
    Args:
        pipe (transformers.Pipeline): Preloaded Llama pipeline.
        messages (list[dict]): Conversation messages (system, user, etc.).
    Returns:
        tuple[str, list[dict], float]:
            - Generated assistant reply
            - Updated messages list including assistant reply
            - Response generation time in seconds
    """
    start = time.perf_counter()
    response = pipe(
        messages,
        temperature=0.6,
        top_p=0.9,
        do_sample=True
    )
    end = time.perf_counter() - start
    # Extract model’s text output
    result = response[0]["generated_text"].strip()
    # Append the assistant response for conversational continuity
    messages.append({
        "role": "assistant",
        "content": result,
    })
    return result, messages, end