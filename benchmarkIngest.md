# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       5.09 |      1.77 |      0.57 | parse        |
| Section Notes        |     2 |      22.47 |      0.09 |     11.24 | parse        |
| Chapter Notes        |     9 |      23.19 |      0.39 |      2.58 | parse        |
| Additional U.S. Notes |     8 |      24.05 |      0.33 |      3.01 | parse        |
| Tariff Tables        |     9 |       2.30 |      3.91 |      0.26 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     1.83 |     3.25 |    0.00 |
| Section Notes        |     4.00 |    18.47 |    0.00 |
| Chapter Notes        |     3.60 |    19.58 |    0.00 |
| Additional U.S. Notes |     4.38 |    19.67 |    0.00 |
| Tariff Tables        |     2.03 |     0.18 |    0.09 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.25 |     0.05 |
|       2 |     0.16 |     0.04 |
|       3 |     0.35 |     1.10 |
|       4 |     0.20 |     1.18 |
|       5 |     0.18 |     0.13 |
|       6 |     0.18 |     0.21 |
|       7 |     0.16 |     0.35 |
|       8 |     0.20 |     0.15 |
|       9 |     0.15 |     0.03 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.34 |     0.62 |
|       2 |     0.39 |     1.43 |
|       3 |     0.27 |     4.20 |
|       4 |     0.34 |     4.98 |
|       5 |     0.27 |     0.79 |
|       6 |     0.43 |     0.61 |
|       7 |     0.39 |     3.16 |
|       8 |     1.26 |     1.98 |
|       9 |     0.31 |     0.72 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.23 |     0.66 |
|       2 |     0.33 |     1.43 |
|       3 |     0.36 |     4.61 |
|       4 |     0.40 |     5.28 |
|       5 |     0.37 |     0.79 |
|       6 |     0.53 |     0.68 |
|       7 |     0.74 |     3.19 |
|       8 |     0.30 |     2.12 |
|       9 |     0.35 |     0.82 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.43 |     0.63 |
|       2 |     0.50 |     1.55 |
|       3 |     0.82 |     4.51 |
|       4 |     0.35 |     5.39 |
|       5 |     0.73 |     0.81 |
|       6 |     0.40 |     0.63 |
|       7 |     0.59 |     3.29 |
|       8 |     0.29 |     2.10 |
|       9 |     0.26 |     0.77 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.22 |     0.06 |
|       2 |     0.21 |     0.01 |
|       3 |     0.34 |     0.02 |
|       4 |     0.22 |     0.02 |
|       5 |     0.17 |     0.01 |
|       6 |     0.25 |     0.01 |
|       7 |     0.21 |     0.02 |
|       8 |     0.21 |     0.01 |
|       9 |     0.20 |     0.02 |

