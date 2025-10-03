# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       5.13 |      1.75 |      0.57 | parse        |
| Section Notes        |     2 |      23.19 |      0.09 |     11.60 | parse        |
| Chapter Notes        |     9 |      23.60 |      0.38 |      2.62 | parse        |
| Additional U.S. Notes |     8 |      22.97 |      0.35 |      2.87 | parse        |
| Tariff Tables        |     9 |       2.32 |      3.88 |      0.26 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.79 |     3.33 |    0.00 |
| Section Notes        |     4.32 |    18.88 |    0.00 |
| Chapter Notes        |     3.60 |    20.00 |    0.00 |
| Additional U.S. Notes |     3.28 |    19.69 |    0.00 |
| Tariff Tables        |     2.04 |     0.18 |    0.11 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.17 |     0.04 |
|       2 |     0.14 |     0.04 |
|       3 |     0.18 |     1.12 |
|       4 |     0.23 |     1.20 |
|       5 |     0.35 |     0.12 |
|       6 |     0.22 |     0.21 |
|       7 |     0.17 |     0.39 |
|       8 |     0.15 |     0.18 |
|       9 |     0.19 |     0.04 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.66 |     0.61 |
|       2 |     0.29 |     1.47 |
|       3 |     0.37 |     4.26 |
|       4 |     0.64 |     5.13 |
|       5 |     0.50 |     0.78 |
|       6 |     0.75 |     0.57 |
|       7 |     0.31 |     3.17 |
|       8 |     0.45 |     2.14 |
|       9 |     0.33 |     0.74 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.27 |     0.63 |
|       2 |     0.40 |     1.51 |
|       3 |     0.57 |     4.77 |
|       4 |     0.50 |     5.46 |
|       5 |     0.50 |     0.72 |
|       6 |     0.30 |     0.62 |
|       7 |     0.36 |     3.37 |
|       8 |     0.31 |     2.11 |
|       9 |     0.39 |     0.82 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.25 |     0.63 |
|       2 |     0.26 |     1.46 |
|       3 |     0.33 |     4.63 |
|       4 |     0.53 |     5.47 |
|       5 |     0.26 |     0.77 |
|       6 |     0.50 |     0.60 |
|       7 |     0.34 |     3.21 |
|       8 |     0.50 |     2.14 |
|       9 |     0.31 |     0.78 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.38 |     0.05 |
|       2 |     0.19 |     0.01 |
|       3 |     0.26 |     0.02 |
|       4 |     0.24 |     0.02 |
|       5 |     0.19 |     0.01 |
|       6 |     0.20 |     0.01 |
|       7 |     0.19 |     0.02 |
|       8 |     0.21 |     0.01 |
|       9 |     0.18 |     0.01 |

