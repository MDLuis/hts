# Benchmarks – HTS Ingestion

This file records how long the ingestion process takes on the available hardware.

## Summary (Total per dataset)

| Dataset              | # Items | Time (seconds) | Items/sec | Sec/Item | Slowest Step |
|----------------------|---------|----------------|-----------|----------|--------------|
| General Notes        |     9 |       9.23 |      0.98 |      1.03 | parse        |
| Section Notes        |     2 |      60.83 |      0.03 |     30.41 | parse        |
| Chapter Notes        |     9 |      45.30 |      0.20 |      5.03 | parse        |
| Additional U.S. Notes |     8 |      30.01 |      0.27 |      3.75 | parse        |
| Tariff Tables        |     9 |       3.28 |      2.74 |      0.36 | fetch        |

## Per-stage timings

| Dataset              | Fetch(s) | Parse(s) | Save(s) |
|----------------------|----------|----------|---------|
| General Notes        |     2.26 |     6.96 |    0.01 |
| Section Notes        |     3.87 |    56.95 |    0.00 |
| Chapter Notes        |     4.93 |    40.37 |    0.00 |
| Additional U.S. Notes |     4.52 |    25.48 |    0.00 |
| Tariff Tables        |     2.73 |     0.35 |    0.20 |

## Per-chapter timings

### General Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.25 |     0.12 |
|       2 |     0.32 |     0.03 |
|       3 |     0.27 |     1.79 |
|       4 |     0.33 |     2.52 |
|       5 |     0.16 |     0.27 |
|       6 |     0.28 |     0.42 |
|       7 |     0.26 |     1.25 |
|       8 |     0.24 |     0.52 |
|       9 |     0.14 |     0.04 |

### Section Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.35 |     2.42 |
|       2 |     0.71 |     5.03 |
|       3 |     0.48 |    21.51 |
|       4 |     0.40 |    10.90 |
|       5 |     0.62 |     1.75 |
|       6 |     0.33 |     1.12 |
|       7 |     0.31 |     7.28 |
|       8 |     0.36 |     4.14 |
|       9 |     0.32 |     2.81 |

### Chapter Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.32 |     1.17 |
|       2 |     0.40 |     3.05 |
|       3 |     0.49 |    16.96 |
|       4 |     0.59 |     8.23 |
|       5 |     0.56 |     0.98 |
|       6 |     0.71 |     0.88 |
|       7 |     0.42 |     4.46 |
|       8 |     0.46 |     2.85 |
|       9 |     0.97 |     1.80 |

### Additional U.S. Notes

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.64 |     0.86 |
|       2 |     0.49 |     2.04 |
|       3 |     0.38 |     5.66 |
|       4 |     0.35 |     6.78 |
|       5 |     0.94 |     0.98 |
|       6 |     0.52 |     0.80 |
|       7 |     0.46 |     4.54 |
|       8 |     0.30 |     2.63 |
|       9 |     0.44 |     1.20 |

### Tariff Tables

| Chapter | Fetch(s) | Parse(s) |
|---------|----------|----------|
|       1 |     0.30 |     0.03 |
|       2 |     0.32 |     0.03 |
|       3 |     0.46 |     0.04 |
|       4 |     0.24 |     0.11 |
|       5 |     0.24 |     0.02 |
|       6 |     0.23 |     0.02 |
|       7 |     0.31 |     0.03 |
|       8 |     0.34 |     0.03 |
|       9 |     0.29 |     0.03 |

