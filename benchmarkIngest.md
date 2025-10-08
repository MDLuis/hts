# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       5.05 |      1.78 |      0.56 | parse        |
| Section Notes        |     2 |      22.53 |      0.09 |     11.26 | parse        |
| Chapter Notes        |     9 |      23.08 |      0.39 |      2.56 | parse        |
| Additional U.S. Notes |     8 |      23.69 |      0.34 |      2.96 | parse        |
| Tariff Tables        |     9 |       2.32 |      3.88 |      0.26 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.55 |     3.50 |    0.00 |
| Section Notes        |     3.25 |    19.28 |    0.00 |
| Chapter Notes        |     3.35 |    19.72 |    0.00 |
| Additional U.S. Notes |     3.35 |    20.34 |    0.00 |
| Tariff Tables        |     2.03 |     0.18 |    0.11 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.22 |     0.05 |
|       2 |     0.13 |     0.04 |
|       3 |     0.24 |     1.12 |
|       4 |     0.18 |     1.38 |
|       5 |     0.13 |     0.14 |
|       6 |     0.14 |     0.24 |
|       7 |     0.17 |     0.40 |
|       8 |     0.17 |     0.14 |
|       9 |     0.16 |     0.02 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.27 |     0.67 |
|       2 |     0.30 |     1.48 |
|       3 |     0.30 |     4.46 |
|       4 |     0.33 |     5.31 |
|       5 |     0.33 |     0.53 |
|       6 |     0.54 |     0.81 |
|       7 |     0.56 |     3.19 |
|       8 |     0.30 |     2.08 |
|       9 |     0.32 |     0.74 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.25 |     0.65 |
|       2 |     0.53 |     1.59 |
|       3 |     0.30 |     4.54 |
|       4 |     0.50 |     5.44 |
|       5 |     0.42 |     0.76 |
|       6 |     0.35 |     0.63 |
|       7 |     0.40 |     3.28 |
|       8 |     0.29 |     2.09 |
|       9 |     0.31 |     0.74 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.27 |     0.64 |
|       2 |     0.41 |     1.51 |
|       3 |     0.27 |     5.02 |
|       4 |     0.37 |     5.56 |
|       5 |     0.50 |     0.79 |
|       6 |     0.28 |     0.65 |
|       7 |     0.65 |     3.24 |
|       8 |     0.31 |     2.16 |
|       9 |     0.29 |     0.78 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.22 |     0.06 |
|       2 |     0.22 |     0.01 |
|       3 |     0.32 |     0.02 |
|       4 |     0.22 |     0.02 |
|       5 |     0.19 |     0.01 |
|       6 |     0.18 |     0.01 |
|       7 |     0.24 |     0.02 |
|       8 |     0.26 |     0.01 |
|       9 |     0.20 |     0.01 |

