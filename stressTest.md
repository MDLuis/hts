# Stress Test Results (HTS Ingestion)

## Small Run
- General Notes: 4 chapters
- Others: 4 chapters
- Total time: 44.98s 
- Raw size: 5.62 MB
- Structured size: 1.79 MB
- Slowest step: parse

## Medium Run
- General Notes: 9 chapters
- Chapters: 9 chapters
- Total time: 84.79s 
- Raw size: 11.95 MB
- Structured size: 3.16 MB
- Slowest step: parse

## Large Run
- General Notes: 18 chapters
- Chapters: 18 chapters
- Total time: 140.85s
- Raw size: 21.92 MB
- Structured size: 5.25 MB
- Slowest step: parse

---

## Observations

1. **Linearity / Scaling**  
   - Runtime, raw size, and structured size scale roughly linearly with the number of chapters.  
   - Parsing remains the dominant time contributor across all runs.  

   ### Runtime vs Chapters

   | Chapters | Total Time (s) |
   |----------|----------------|
   | 4        | 44.98          |
   | 9        | 84.79          |
   | 18       | 140.85         |

   ### Size vs Chapters

   | Chapters | Raw Size (MB) | Structured Size (MB) |
   |----------|---------------|---------------------|
   | 4        | 5.62          | 1.79                |
   | 9        | 11.95         | 3.16                |
   | 18       | 21.92         | 5.25                |
 
2. **Errors / Reliability**  
   - During all tests, no errors or crashes occurred.  
   - The pipeline successfully ingested chapters and notes.
