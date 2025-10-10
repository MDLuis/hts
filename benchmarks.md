# Benchmarks – HTS Embedding Encoding

This file records how long the embedding process takes on the available hardware.  
All embeddings were generated with [`sentence-transformers`](https://www.sbert.net) using the `all-MiniLM-L6-v2` model.

## Notes

- All times measured with `time.time()` before and after `model.encode()`.
- Batch size: 32

## Results

| Dataset              | # Texts | Model                | Time (seconds) |
|----------------------|---------|----------------------|----------------|
| General Notes             |  8765 | all-MiniLM-L6-v2     |     138.33 |
| Section Notes             |    35 | all-MiniLM-L6-v2     |       1.93 |
| Chapter Notes             |  1050 | all-MiniLM-L6-v2     |      11.99 |
| Additional Us Notes       |   537 | all-MiniLM-L6-v2     |      12.07 |
| Tariff Tables             | 36108 | all-MiniLM-L6-v2     |     230.92 |
