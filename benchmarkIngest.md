# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       4.59 |      1.96 |      0.51 | parse        |
| Section Notes        |     2 |      21.46 |      0.09 |     10.73 | parse        |
| Chapter Notes        |     9 |      21.80 |      0.41 |      2.42 | parse        |
| Additional U.S. Notes |     8 |      22.22 |      0.36 |      2.78 | parse        |
| Tariff Tables        |     9 |       2.29 |      3.94 |      0.25 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.37 |     3.21 |    0.00 |
| Section Notes        |     3.43 |    18.03 |    0.00 |
| Chapter Notes        |     3.46 |    18.34 |    0.00 |
| Additional U.S. Notes |     3.56 |    18.66 |    0.00 |
| Tariff Tables        |     2.06 |     0.15 |    0.09 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.17 |     0.05 |
|       2 |     0.19 |     0.04 |
|       3 |     0.17 |     1.11 |
|       4 |     0.16 |     1.16 |
|       5 |     0.14 |     0.14 |
|       6 |     0.12 |     0.18 |
|       7 |     0.15 |     0.37 |
|       8 |     0.13 |     0.13 |
|       9 |     0.15 |     0.02 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.28 |     0.63 |
|       2 |     0.77 |     1.36 |
|       3 |     0.42 |     4.11 |
|       4 |     0.39 |     4.87 |
|       5 |     0.24 |     0.73 |
|       6 |     0.41 |     0.58 |
|       7 |     0.34 |     3.05 |
|       8 |     0.29 |     1.92 |
|       9 |     0.29 |     0.76 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.39 |     0.62 |
|       2 |     0.28 |     1.35 |
|       3 |     0.28 |     4.15 |
|       4 |     0.86 |     5.08 |
|       5 |     0.25 |     0.71 |
|       6 |     0.50 |     0.60 |
|       7 |     0.30 |     3.09 |
|       8 |     0.32 |     2.03 |
|       9 |     0.29 |     0.73 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.49 |     0.61 |
|       2 |     0.32 |     1.39 |
|       3 |     0.31 |     4.34 |
|       4 |     0.31 |     5.17 |
|       5 |     0.31 |     0.58 |
|       6 |     0.28 |     0.79 |
|       7 |     0.62 |     3.04 |
|       8 |     0.59 |     1.99 |
|       9 |     0.32 |     0.75 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.17 |     0.02 |
|       2 |     0.23 |     0.02 |
|       3 |     0.27 |     0.03 |
|       4 |     0.22 |     0.02 |
|       5 |     0.18 |     0.01 |
|       6 |     0.18 |     0.01 |
|       7 |     0.41 |     0.01 |
|       8 |     0.22 |     0.02 |
|       9 |     0.17 |     0.01 |

