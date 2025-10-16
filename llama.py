import torch, time
from transformers import pipeline

model_id = "meta-llama/Llama-3.2-3B"

pipe = pipeline(
    "text-generation", 
    model=model_id, 
    torch_dtype=torch.bfloat16, 
    device_map="auto"
)
prompt = "The key to life is"
start = time.perf_counter()
result = pipe(prompt)
end = time.perf_counter() - start
output = result[0]["generated_text"]
report = f"""
# Llama 3.2-3B Test

**Model:** `{model_id}`
**Prompt:** `{prompt}` 
**Time Taken:** `{end:.2f} seconds`

---

###  Output
{output}
"""

with open("llama.md", "w", encoding="utf-8") as f:
    f.write(report)