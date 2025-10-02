# Small Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     4 |       3.55 |      1.13 |      0.89 | parse        |
| Section Notes        |     1 |      13.31 |      0.08 |     13.31 | parse        |
| Chapter Notes        |     4 |      13.39 |      0.30 |      3.35 | parse        |
| Additional U.S. Notes |     4 |      13.77 |      0.29 |      3.44 | parse        |
| Tariff Tables        |     4 |       0.96 |      4.17 |      0.24 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.08 |     2.47 |    0.00 |
| Section Notes        |     1.70 |    11.60 |    0.00 |
| Chapter Notes        |     1.34 |    12.05 |    0.00 |
| Additional U.S. Notes |     1.45 |    12.32 |    0.00 |
| Tariff Tables        |     0.84 |     0.07 |    0.05 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.19 |     0.06 |
|       2 |     0.14 |     0.03 |
|       3 |     0.35 |     1.15 |
|       4 |     0.40 |     1.22 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.47 |     0.66 |
|       2 |     0.32 |     1.45 |
|       3 |     0.59 |     4.34 |
|       4 |     0.32 |     5.16 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.27 |     0.57 |
|       2 |     0.40 |     1.75 |
|       3 |     0.30 |     4.47 |
|       4 |     0.37 |     5.25 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.29 |     0.77 |
|       2 |     0.60 |     1.55 |
|       3 |     0.29 |     4.54 |
|       4 |     0.27 |     5.45 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.28 |     0.02 |
|       2 |     0.18 |     0.01 |
|       3 |     0.16 |     0.02 |
|       4 |     0.22 |     0.02 |

# Small Data Size Report

## Raw PDFs

- **Chapter PDFs**
  - File Count: 4
  - Total Size: 4.9 MB
  - Average Size: 1.2 MB
  - Min Size: 823.7 KB
  - Max Size: 1.5 MB
- **General Notes PDFs**
  - File Count: 4
  - Total Size: 100.9 KB
  - Average Size: 25.2 KB
  - Min Size: 6.0 KB
  - Max Size: 44.4 KB

## Raw JSON

- **Tables**
  - File Count: 4
  - Total Size: 622.8 KB
  - Average Size: 155.7 KB
  - Min Size: 41.9 KB
  - Max Size: 287.8 KB

## Structured JSON

- **General Notes**
  - File Count: 2
  - Total Size: 130.1 KB
  - Average Size: 65.1 KB
- **Additional Notes**
  - File Count: 2
  - Total Size: 52.0 KB
  - Average Size: 26.0 KB
- **Chapter Notes**
  - File Count: 2
  - Total Size: 10.0 KB
  - Average Size: 5.0 KB
- **Section Notes**
  - File Count: 2
  - Total Size: 1.1 KB
  - Average Size: 569.0 B
- **Tables**
  - File Count: 2
  - Total Size: 1.6 MB
  - Average Size: 839.0 KB

## Expansion Ratios

- Chapters PDF → Structured JSON Notes Ratio: 0.01
- General Notes PDF → Structured JSON Notes Ratio: 1.29
- Raw JSON Tables → Structured JSON Tables Ratio: 2.69

## Projected Full HTS Storage

- **Raw**
  - **Chapter PDFs:** Projected Size: 121.6 MB (based on 99 chapters)
  - **General Notes PDFs:** Projected Size: 908.2 KB (based on 36 chapters)
  - **Raw JSON Tables:** Projected Size: 15.1 MB (based on 99 chapters)

- **Structured**
  - **General Notes:** Projected Size: 1.1 MB (based on 36 chapters, ~32.5 KB per chapter)
  - **Additional Notes:** Projected Size: 1.3 MB (based on 99 chapters, ~13.0 KB per chapter)
  - **Chapter Notes:** Projected Size: 246.8 KB (based on 99 chapters, ~2.5 KB per chapter)
  - **Section Notes:** Projected Size: 24.4 KB (based on 22 chapters, ~1.1 KB per chapter)
  - **Tables:** Projected Size: 40.6 MB (based on 99 chapters, ~419.5 KB per chapter)

- **Total:** 180.7 MB