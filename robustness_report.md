# Robustness Evaluation Report

This report documents robustness tests for the HTS ingestion pipeline.  
Focus: idempotency, consistency, interruption handling, retries, and failure modes.

---

## 1. Same Input Repeated (During same ingestion)

**Test Setup:**  
- Ingested Chapter 1 five times within the same ingestion run.

**Observations:**  
- No duplicates created in the structured JSON file.  
- PDF files were not duplicated.

**Result:**  
**Pass** - Duplicate chapters are automatically removed before saving, ensuring the structured data remains unique.

---

## 2. Overlapping Runs Test (Different Batches)

**Test Setup:**  
- Run 1: Chapters 1-4  
- Run 2: Chapters 1-9  

**Observations:**  
- No duplicate entries for Chapters 1-4.  
- Final output contained all chapters 1-9 exactly once.

**Result:**  
**Pass** - Overlapping runs do not cause duplication or corruption.

---

## 3. Interrupted Run Test

**Test Setup:**  
- Ran ingestion for Chapters 1-9.  
- Stopped the process manually after several chapters had been parsed (using `Ctrl+C`).  
- System does not resume from where it stopped, ingestion always starts from the beginning.

**Observations:**  
- No corrupted or partial JSON files were left behind.  
- Only the PDF files fetched before interruption remained.  
- Upon re-running ingestion, the process completed successfully without errors.  
- All chapters were processed correctly on the second run.

**Result:**  
**Pass** - System handles interruptions gracefully, no manual cleanup required and ingestion completes successfully on re-run.

---

## 4. Retry & Backoff Test

**Test Setup:**  
- Disabled network temporarily while fetching.  
- Observed retry behavior.

**Observations:**  
- Automatic retries triggered according to `retries=5` and `backoff_factor=0.5`. (Can be increased)
- Each retry waited exponentially longer (0.5s → 1s → 2s → 4s) before the next attempt.
- Once the network was restored within the retry window, the ingestion completed successfully without manual restart.
- If the connection remained unavailable past the maximum retries, the ingestion aborts.

**Result:**  
**Pass** - Retry and backoff logic correctly handled connection failures, preventing ingestion aborts.

---