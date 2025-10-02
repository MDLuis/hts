# Robustness Evaluation Report

This report documents robustness tests for the HTS ingestion pipeline.  
Focus: idempotency, consistency, interruption handling, retries, and failure modes.

---

## 1. Same Input Repeated (During same ingestion)

**Test Setup:**  
- Ingested Chapter 1 five times within the same ingestion run.

**Observations:**  
- Duplicates created in the structured JSON file.  
- PDF files were not duplicated.

**Result:**  
**Fail** - The structured data had duplicates of the same chapter.

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
- Fetch failed immediately with a connection error.  
- No retry/backoff mechanism, ingestion was aborted.  
- When network was restored, re-running ingestion succeeded.  
- Manual restart required.

**Result:**  
**Fail** - Retry/backoff logic not implemented.

---

## 5. Summary of Failure Modes

| Failure Mode | When It Happens |  Recovery | 
|--------------|-----------------|-----------|
| Duplicate structured data | Re-ingesting the same chapter during the same run | Manual cleanup required |
| Network fetch failure     | Retry/backoff test                                | Manual restart required |

---
