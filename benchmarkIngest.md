# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       7.35 |      1.23 |      0.82 | parse        |
| Section Notes        |     2 |      29.15 |      0.07 |     14.58 | parse        |
| Chapter Notes        |     9 |      31.16 |      0.29 |      3.46 | parse        |
| Additional U.S. Notes |     8 |      28.05 |      0.29 |      3.51 | parse        |
| Tariff Tables        |     9 |       2.55 |      3.53 |      0.28 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.69 |     5.64 |    0.01 |
| Section Notes        |     4.33 |    24.82 |    0.00 |
| Chapter Notes        |     5.62 |    25.54 |    0.00 |
| Additional U.S. Notes |     7.94 |    20.10 |    0.00 |
| Tariff Tables        |     2.24 |     0.23 |    0.08 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.14 |     0.04 |
|       2 |     0.19 |     0.03 |
|       3 |     0.34 |     1.91 |
|       4 |     0.15 |     1.89 |
|       5 |     0.14 |     0.33 |
|       6 |     0.19 |     0.29 |
|       7 |     0.19 |     0.86 |
|       8 |     0.19 |     0.25 |
|       9 |     0.17 |     0.04 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.31 |     0.95 |
|       2 |     0.31 |     2.13 |
|       3 |     0.43 |     5.58 |
|       4 |     0.44 |     6.62 |
|       5 |     0.28 |     1.06 |
|       6 |     0.31 |     0.85 |
|       7 |     0.36 |     3.98 |
|       8 |     0.63 |     2.61 |
|       9 |     1.26 |     1.04 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.41 |     0.78 |
|       2 |     1.00 |     1.85 |
|       3 |     1.32 |     5.61 |
|       4 |     0.52 |     6.54 |
|       5 |     0.60 |     1.07 |
|       6 |     0.76 |     0.76 |
|       7 |     0.35 |     5.51 |
|       8 |     0.41 |     2.65 |
|       9 |     0.26 |     0.79 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.33 |     0.63 |
|       2 |     0.41 |     1.55 |
|       3 |     0.41 |     4.69 |
|       4 |     0.53 |     5.59 |
|       5 |     4.31 |     0.59 |
|       6 |     0.86 |     0.82 |
|       7 |     0.30 |     3.29 |
|       8 |     0.37 |     2.15 |
|       9 |     0.41 |     0.81 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.22 |     0.03 |
|       2 |     0.22 |     0.04 |
|       3 |     0.41 |     0.04 |
|       4 |     0.30 |     0.03 |
|       5 |     0.18 |     0.02 |
|       6 |     0.23 |     0.02 |
|       7 |     0.23 |     0.02 |
|       8 |     0.19 |     0.02 |
|       9 |     0.25 |     0.02 |

