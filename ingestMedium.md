# Medium Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       5.52 |      1.63 |      0.61 | parse        |
| Section Notes        |     2 |      24.29 |      0.08 |     12.15 | parse        |
| Chapter Notes        |     9 |      27.88 |      0.32 |      3.10 | parse        |
| Additional U.S. Notes |     8 |      24.43 |      0.33 |      3.05 | parse        |
| Tariff Tables        |     9 |       2.67 |      3.37 |      0.30 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     2.03 |     3.49 |    0.00 |
| Section Notes        |     3.86 |    20.43 |    0.00 |
| Chapter Notes        |     8.69 |    19.19 |    0.00 |
| Additional U.S. Notes |     5.50 |    18.93 |    0.00 |
| Tariff Tables        |     2.35 |     0.21 |    0.11 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.65 |     0.03 |
|       2 |     0.23 |     0.03 |
|       3 |     0.17 |     1.19 |
|       4 |     0.23 |     1.29 |
|       5 |     0.14 |     0.14 |
|       6 |     0.18 |     0.21 |
|       7 |     0.18 |     0.40 |
|       8 |     0.12 |     0.17 |
|       9 |     0.12 |     0.03 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.28 |     0.66 |
|       2 |     0.25 |     1.60 |
|       3 |     0.27 |     4.98 |
|       4 |     0.53 |     5.37 |
|       5 |     0.27 |     0.81 |
|       6 |     0.83 |     0.64 |
|       7 |     0.46 |     3.37 |
|       8 |     0.49 |     2.19 |
|       9 |     0.48 |     0.80 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.30 |     0.69 |
|       2 |     0.44 |     1.51 |
|       3 |     4.32 |     4.60 |
|       4 |     0.43 |     5.33 |
|       5 |     0.30 |     0.73 |
|       6 |     1.26 |     0.59 |
|       7 |     0.52 |     3.01 |
|       8 |     0.45 |     2.00 |
|       9 |     0.67 |     0.73 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.49 |     0.60 |
|       2 |     0.30 |     1.44 |
|       3 |     0.61 |     4.32 |
|       4 |     1.14 |     5.17 |
|       5 |     0.54 |     0.74 |
|       6 |     1.08 |     0.64 |
|       7 |     0.36 |     3.08 |
|       8 |     0.45 |     2.19 |
|       9 |     0.52 |     0.74 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.20 |     0.05 |
|       2 |     0.22 |     0.01 |
|       3 |     0.31 |     0.02 |
|       4 |     0.31 |     0.02 |
|       5 |     0.22 |     0.01 |
|       6 |     0.20 |     0.01 |
|       7 |     0.21 |     0.02 |
|       8 |     0.32 |     0.02 |
|       9 |     0.37 |     0.05 |

# Medium Data Size Report

## Raw PDFs

- **Chapter PDFs**
  - File Count: 9
  - Total Size: 10.7 MB
  - Average Size: 1.2 MB
  - Min Size: 819.2 KB
  - Max Size: 1.5 MB
- **General Notes PDFs**
  - File Count: 9
  - Total Size: 151.9 KB
  - Average Size: 16.9 KB
  - Min Size: 5.9 KB
  - Max Size: 44.4 KB

## Raw JSON

- **Tables**
  - File Count: 9
  - Total Size: 1.1 MB
  - Average Size: 120.9 KB
  - Min Size: 22.1 KB
  - Max Size: 287.8 KB

## Structured JSON

- **General Notes**
  - File Count: 2
  - Total Size: 170.3 KB
  - Average Size: 85.2 KB
- **Additional Notes**
  - File Count: 2
  - Total Size: 69.6 KB
  - Average Size: 34.8 KB
- **Chapter Notes**
  - File Count: 2
  - Total Size: 22.3 KB
  - Average Size: 11.1 KB
- **Section Notes**
  - File Count: 2
  - Total Size: 1.7 KB
  - Average Size: 892.0 B
- **Tables**
  - File Count: 2
  - Total Size: 2.9 MB
  - Average Size: 1.4 MB

## Expansion Ratios

- Chapters PDF → Structured JSON Notes Ratio: 0.01
- General Notes PDF → Structured JSON Notes Ratio: 1.12
- Raw JSON Tables → Structured JSON Tables Ratio: 2.69

## Projected Full HTS Storage

- **Raw**
  - **Chapter PDFs:** Projected Size: 118.1 MB (based on 99 chapters)
  - **General Notes PDFs:** Projected Size: 607.7 KB (based on 36 chapters)
  - **Raw JSON Tables:** Projected Size: 11.7 MB (based on 99 chapters)

- **Structured**
  - **General Notes:** Projected Size: 681.4 KB (based on 36 chapters, ~18.9 KB per chapter)
  - **Additional Notes:** Projected Size: 765.4 KB (based on 99 chapters, ~7.7 KB per chapter)
  - **Chapter Notes:** Projected Size: 244.8 KB (based on 99 chapters, ~2.5 KB per chapter)
  - **Section Notes:** Projected Size: 19.2 KB (based on 22 chapters, ~892.0 B per chapter)
  - **Tables:** Projected Size: 31.4 MB (based on 99 chapters, ~325.3 KB per chapter)

- **Total:** 163.5 MB