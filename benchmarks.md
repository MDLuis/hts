# Benchmarks – HTS Embedding Encoding

This file records how long the embedding process takes on the available hardware.  
All embeddings were generated with [`sentence-transformers`](https://www.sbert.net) using the `all-MiniLM-L6-v2` model.

## Notes

- All times measured with `time.time()` before and after `model.encode()`.
- Batch size: 32

## Results

| Dataset              | # Texts | Model                | Time (seconds) |
|----------------------|---------|----------------------|----------------|
| General Notes        |     9 | all-MiniLM-L6-v2     |       0.59 |
| Section Notes        |     2 | all-MiniLM-L6-v2     |       0.05 |
| Chapter Notes        |    28 | all-MiniLM-L6-v2     |       1.09 |
| Additional U.S. Notes |    45 | all-MiniLM-L6-v2     |       1.80 |
| Tariff Tables        |  2943 | all-MiniLM-L6-v2     |      15.16 |
