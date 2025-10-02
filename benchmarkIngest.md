# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       4.99 |      1.80 |      0.55 | parse        |
| Section Notes        |     2 |      24.72 |      0.08 |     12.36 | parse        |
| Chapter Notes        |     9 |      24.75 |      0.36 |      2.75 | parse        |
| Additional U.S. Notes |     8 |      24.74 |      0.32 |      3.09 | parse        |
| Tariff Tables        |     9 |       2.09 |      4.31 |      0.23 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.73 |     3.25 |    0.00 |
| Section Notes        |     4.42 |    20.30 |    0.00 |
| Chapter Notes        |     4.53 |    20.22 |    0.00 |
| Additional U.S. Notes |     3.77 |    20.97 |    0.00 |
| Tariff Tables        |     1.82 |     0.18 |    0.09 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.41 |     0.05 |
|       2 |     0.26 |     0.05 |
|       3 |     0.16 |     1.09 |
|       4 |     0.18 |     1.21 |
|       5 |     0.14 |     0.11 |
|       6 |     0.14 |     0.20 |
|       7 |     0.16 |     0.37 |
|       8 |     0.13 |     0.14 |
|       9 |     0.16 |     0.03 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.28 |     0.67 |
|       2 |     0.29 |     1.61 |
|       3 |     0.52 |     4.48 |
|       4 |     0.55 |     5.73 |
|       5 |     0.35 |     0.79 |
|       6 |     0.97 |     0.66 |
|       7 |     0.62 |     3.39 |
|       8 |     0.45 |     2.18 |
|       9 |     0.40 |     0.79 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.30 |     0.65 |
|       2 |     0.43 |     1.53 |
|       3 |     0.49 |     4.67 |
|       4 |     0.44 |     5.54 |
|       5 |     1.31 |     0.77 |
|       6 |     0.32 |     0.72 |
|       7 |     0.28 |     3.32 |
|       8 |     0.70 |     2.23 |
|       9 |     0.27 |     0.79 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.36 |     0.63 |
|       2 |     0.32 |     1.65 |
|       3 |     0.36 |     4.73 |
|       4 |     0.62 |     6.13 |
|       5 |     0.48 |     0.81 |
|       6 |     0.44 |     0.62 |
|       7 |     0.60 |     3.41 |
|       8 |     0.32 |     2.20 |
|       9 |     0.28 |     0.80 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.18 |     0.05 |
|       2 |     0.21 |     0.01 |
|       3 |     0.27 |     0.02 |
|       4 |     0.22 |     0.01 |
|       5 |     0.15 |     0.01 |
|       6 |     0.20 |     0.01 |
|       7 |     0.20 |     0.02 |
|       8 |     0.19 |     0.01 |
|       9 |     0.19 |     0.02 |

