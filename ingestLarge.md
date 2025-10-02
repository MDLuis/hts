# Large Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |    18 |      21.43 |      0.84 |      1.19 | parse        |
| Section Notes        |     3 |      37.73 |      0.08 |     12.58 | parse        |
| Chapter Notes        |    18 |      39.44 |      0.46 |      2.19 | parse        |
| Additional U.S. Notes |    15 |      37.52 |      0.40 |      2.50 | parse        |
| Tariff Tables        |    18 |       4.73 |      3.80 |      0.26 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     3.22 |    18.20 |    0.01 |
| Section Notes        |     8.40 |    29.33 |    0.00 |
| Chapter Notes        |    10.39 |    29.05 |    0.00 |
| Additional U.S. Notes |     8.74 |    28.77 |    0.00 |
| Tariff Tables        |     4.27 |     0.25 |    0.21 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.17 |     0.06 |
|       2 |     0.12 |     0.03 |
|       3 |     0.16 |     1.12 |
|       4 |     0.35 |     1.19 |
|       5 |     0.13 |     0.12 |
|       6 |     0.13 |     0.23 |
|       7 |     0.14 |     0.34 |
|       8 |     0.18 |     0.15 |
|       9 |     0.13 |     0.03 |
|      10 |     0.14 |     0.24 |
|      11 |     0.21 |    13.54 |
|      12 |     0.15 |     0.05 |
|      13 |     0.17 |     0.07 |
|      14 |     0.14 |     0.04 |
|      15 |     0.13 |     0.11 |
|      16 |     0.26 |     0.19 |
|      17 |     0.14 |     0.21 |
|      18 |     0.37 |     0.47 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.45 |     0.58 |
|       2 |     0.53 |     2.18 |
|       3 |     0.26 |     4.32 |
|       4 |     0.59 |     5.20 |
|       5 |     0.30 |     0.75 |
|       6 |     0.30 |     0.70 |
|       7 |     0.55 |     3.37 |
|       8 |     0.33 |     2.05 |
|       9 |     0.41 |     0.79 |
|      10 |     0.38 |     0.57 |
|      11 |     0.55 |     0.60 |
|      12 |     0.73 |     1.34 |
|      13 |     0.46 |     0.30 |
|      14 |     0.91 |     0.19 |
|      15 |     0.42 |     1.23 |
|      16 |     0.47 |     1.70 |
|      17 |     0.45 |     1.86 |
|      18 |     0.31 |     1.60 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.39 |     0.64 |
|       2 |     0.49 |     1.48 |
|       3 |     1.01 |     4.54 |
|       4 |     0.52 |     5.42 |
|       5 |     0.40 |     0.61 |
|       6 |     0.91 |     0.84 |
|       7 |     0.53 |     3.31 |
|       8 |     0.52 |     1.98 |
|       9 |     0.65 |     0.77 |
|      10 |     0.43 |     0.61 |
|      11 |     0.44 |     0.62 |
|      12 |     0.50 |     1.27 |
|      13 |     0.58 |     0.32 |
|      14 |     0.27 |     0.21 |
|      15 |     0.77 |     1.26 |
|      16 |     0.71 |     1.64 |
|      17 |     0.46 |     1.95 |
|      18 |     0.82 |     1.58 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.37 |     0.68 |
|       2 |     0.47 |     1.52 |
|       3 |     0.55 |     4.48 |
|       4 |     0.57 |     5.31 |
|       5 |     0.36 |     0.73 |
|       6 |     0.72 |     0.62 |
|       7 |     0.51 |     3.24 |
|       8 |     0.76 |     2.13 |
|       9 |     0.42 |     0.76 |
|      10 |     0.39 |     0.57 |
|      11 |     0.31 |     0.58 |
|      12 |     0.59 |     1.34 |
|      13 |     0.35 |     0.36 |
|      14 |     0.46 |     0.18 |
|      15 |     0.59 |     1.17 |
|      16 |     0.51 |     1.70 |
|      17 |     0.47 |     1.82 |
|      18 |     0.35 |     1.59 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.26 |     0.02 |
|       2 |     0.24 |     0.01 |
|       3 |     0.34 |     0.02 |
|       4 |     0.29 |     0.01 |
|       5 |     0.20 |     0.01 |
|       6 |     0.26 |     0.01 |
|       7 |     0.24 |     0.01 |
|       8 |     0.24 |     0.02 |
|       9 |     0.18 |     0.02 |
|      10 |     0.26 |     0.01 |
|      11 |     0.19 |     0.01 |
|      12 |     0.21 |     0.01 |
|      13 |     0.16 |     0.01 |
|      14 |     0.15 |     0.01 |
|      15 |     0.23 |     0.01 |
|      16 |     0.33 |     0.02 |
|      17 |     0.21 |     0.02 |
|      18 |     0.29 |     0.01 |

# Large Data Size Report

## Raw PDFs

- **Chapter PDFs**
  - File Count: 18
  - Total Size: 19.8 MB
  - Average Size: 1.1 MB
  - Min Size: 805.6 KB
  - Max Size: 1.5 MB
- **General Notes PDFs**
  - File Count: 18
  - Total Size: 623.3 KB
  - Average Size: 34.6 KB
  - Min Size: 5.9 KB
  - Max Size: 386.2 KB

## Raw JSON

- **Tables**
  - File Count: 18
  - Total Size: 1.5 MB
  - Average Size: 87.2 KB
  - Min Size: 8.8 KB
  - Max Size: 287.8 KB

## Structured JSON

- **General Notes**
  - File Count: 2
  - Total Size: 1.0 MB
  - Average Size: 522.2 KB
- **Additional Notes**
  - File Count: 2
  - Total Size: 106.9 KB
  - Average Size: 53.5 KB
- **Chapter Notes**
  - File Count: 2
  - Total Size: 45.0 KB
  - Average Size: 22.5 KB
- **Section Notes**
  - File Count: 2
  - Total Size: 2.4 KB
  - Average Size: 1.2 KB
- **Tables**
  - File Count: 2
  - Total Size: 4.1 MB
  - Average Size: 2.1 MB

## Expansion Ratios

- Chapters PDF → Structured JSON Notes Ratio: 0.01
- General Notes PDF → Structured JSON Notes Ratio: 1.68
- Raw JSON Tables → Structured JSON Tables Ratio: 2.69

## Projected Full HTS Storage

- **Raw**
  - **Chapter PDFs:** Projected Size: 108.8 MB (based on 99 chapters)
  - **General Notes PDFs:** Projected Size: 1.2 MB (based on 36 chapters)
  - **Raw JSON Tables:** Projected Size: 8.4 MB (based on 99 chapters)

- **Structured**
  - **General Notes:** Projected Size: 2.0 MB (based on 36 chapters, ~58.0 KB per chapter)
  - **Additional Notes:** Projected Size: 705.8 KB (based on 99 chapters, ~7.1 KB per chapter)
  - **Chapter Notes:** Projected Size: 247.5 KB (based on 99 chapters, ~2.5 KB per chapter)
  - **Section Notes:** Projected Size: 17.4 KB (based on 22 chapters, ~810.0 B per chapter)
  - **Tables:** Projected Size: 22.7 MB (based on 99 chapters, ~234.4 KB per chapter)

- **Total:** 144.1 MB