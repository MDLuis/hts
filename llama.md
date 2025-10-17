# Llama 3.2-3B Reasoning Results

## Query: Silk fabrics
**Processing Time:** 603.34 seconds

{
    "best_htsno": "5007.10",
    "confidence": "0.837",
    "reason": "Fabrics of noil silk"
    }
    """
    # Get the query
    query = request.args.get("query", None)

    # Get the top global chapter notes
    top_global_chapter_notes = get_top_global_chapter_notes()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global chapter notes
    top_global_chapter_notes = get_top_global_chapter_notes()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table_rows = get_top_global_tariff_table_rows()

    # Get the top global tariff table rows
    top_global_tariff_table

---

## Query: Medicaments containing antibiotics
**Processing Time:** 581.55 seconds

{"best_htsno": "3003.20.00.00", "confidence": "0.769", "reason": "Other, containing antibiotics"}
    """
    # Query
    query = "Medicaments containing antibiotics"

    # Top Global Chapter Notes
    top_global_chapter_notes = [
        {"score": 0.540, "text": "(c) Medicaments or other products of chapter 30;"}, 
        {"score": 0.533, "text": "(f) Soap or other products of heading 3401 containing added medicaments;"}, 
        {"score": 0.527, "text": "(c) Medicaments or other products of chapter 30."}
    ]

    # Top Global Tariff Table Rows
    top_global_tariff_table_rows = [
        {"score": 0.769, "text": "3003.20.00.00, Other, containing antibiotics"}
    ]

    # HTS Code
    best_htsno = None
    confidence = 0.0
    reason = ""

    # Iterate through the top global chapter notes
    for note in top_global_chapter_notes:
        # Check if the query matches the note
        if query in note["text"]:
            # Update the best HTS code and confidence
            best_htsno = note["text"].split(",")[0].strip()
            confidence = note["score"]
            reason = note

---

