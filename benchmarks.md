# Benchmarks – HTS Embedding Encoding

This file records how long the embedding process takes on the available hardware.  
All embeddings were generated with [`sentence-transformers`](https://www.sbert.net) using the `all-MiniLM-L6-v2` model.

## Notes

- All times measured with `time.perf_counter()` before and after `model.encode()`.
- Batch size: 32

## Results

| Dataset              | # Texts | Model                | Time (seconds) |
|----------------------|---------|----------------------|----------------|
| Chapter Notes | 1050 | all-MiniLM-L6-v2 | 9.10 |
| Tariff Tables | 36108 | all-MiniLM-L6-v2 | 300.81 |
