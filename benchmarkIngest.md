# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       5.60 |      1.61 |      0.62 | parse        |
| Section Notes        |     2 |      24.49 |      0.08 |     12.24 | parse        |
| Chapter Notes        |     9 |      24.95 |      0.36 |      2.77 | parse        |
| Additional U.S. Notes |     8 |      23.65 |      0.34 |      2.96 | parse        |
| Tariff Tables        |     9 |       2.35 |      3.83 |      0.26 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.65 |     3.95 |    0.00 |
| Section Notes        |     3.88 |    20.60 |    0.00 |
| Chapter Notes        |     4.59 |    20.36 |    0.00 |
| Additional U.S. Notes |     4.10 |    19.55 |    0.00 |
| Tariff Tables        |     2.06 |     0.19 |    0.10 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.31 |     0.05 |
|       2 |     0.17 |     0.02 |
|       3 |     0.18 |     1.42 |
|       4 |     0.20 |     1.45 |
|       5 |     0.15 |     0.14 |
|       6 |     0.14 |     0.20 |
|       7 |     0.19 |     0.45 |
|       8 |     0.16 |     0.19 |
|       9 |     0.15 |     0.02 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.61 |     0.98 |
|       2 |     0.50 |     1.55 |
|       3 |     0.30 |     4.55 |
|       4 |     0.30 |     5.84 |
|       5 |     0.26 |     0.79 |
|       6 |     0.29 |     0.62 |
|       7 |     0.98 |     3.32 |
|       8 |     0.35 |     2.20 |
|       9 |     0.29 |     0.76 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.35 |     0.65 |
|       2 |     0.29 |     1.48 |
|       3 |     0.38 |     4.28 |
|       4 |     0.35 |     5.33 |
|       5 |     0.24 |     0.89 |
|       6 |     0.28 |     0.71 |
|       7 |     0.43 |     3.68 |
|       8 |     0.72 |     2.54 |
|       9 |     1.56 |     0.81 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.45 |     0.59 |
|       2 |     0.43 |     1.46 |
|       3 |     0.52 |     4.47 |
|       4 |     0.62 |     5.39 |
|       5 |     0.25 |     0.81 |
|       6 |     0.48 |     0.61 |
|       7 |     0.47 |     3.31 |
|       8 |     0.33 |     2.13 |
|       9 |     0.56 |     0.74 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.21 |     0.05 |
|       2 |     0.24 |     0.01 |
|       3 |     0.22 |     0.03 |
|       4 |     0.26 |     0.02 |
|       5 |     0.24 |     0.01 |
|       6 |     0.20 |     0.01 |
|       7 |     0.24 |     0.02 |
|       8 |     0.24 |     0.02 |
|       9 |     0.21 |     0.02 |

