# Exercise #2 - Local Benchmark of Ollama Using GuideLLM

## Description

### Objective
- Run Ollama locally with the **phi3** model
- Benchmark it using **GuideLLM** from a clean Python 3.10 environment
- Validate and briefly analyze results

### Prerequisites
- Python 3.10 (recommended via Conda)
- Ollama installed locally
- Network access to the GuideLLM repository and its Python packages

---

## Setup Steps

### 1) Create a Python 3.10 Environment

```bash
conda create -n guide_bench python=3.10 -y
conda activate guide_bench
```

### 2) Obtain GuideLLM

Clone or download the GuideLLM repo/release:

```bash
git clone https://github.com/vllm-project/guidellm.git
cd guidellm
```

### 3) Install GuideLLM

Follow the repo's main README. Typical pattern:

```bash
pip install -U pip
pip install -r requirements.txt
pip install .
```

If GuideLLM ships a CLI entry point, verify it:

```bash
guidellm --help
```

### 4) Skim the GuideLLM Docs

Review the quick-start / README to understand:
- OpenAI-compatible request mode
- How to point GuideLLM to a custom endpoint
- How to configure prompt/output token settings and runtime

### 5) Ensure Ollama is Running with phi3

Install Ollama:

```bash
brew install ollama
brew services start ollama

# Check it's running:
curl http://localhost:11434
```

Start or verify Ollama:

```bash
ollama run phi3  # first run pulls the model

# In another terminal:
ollama serve     # ensure the server is up
```

By default, Ollama's OpenAI-compatible endpoint is available at:
```
http://localhost:11434/v1
```

### 6) Sanity Check: OpenAI-Compatible Request to Ollama

Confirm the endpoint responds before benchmarking:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
        "model": "phi3",
        "messages": [{"role":"user","content":"Say hello"}],
        "temperature": 0
      }'
```

A successful call returns HTTP 200 with a JSON completion.

---

## Running the Benchmark

### 7) Run GuideLLM Against Ollama (phi3)

Use GuideLLM in OpenAI-compatible mode, pointing to your local endpoint:

```bash
uv run guidellm benchmark run \
  --target http://localhost:11434/v1 \
  --model phi3 \
  --backend openai_http \
  --backend-kwargs '{"validate_backend": false}' \
  --data '{"prompt_tokens": 50, "output_tokens": 100}' \
  --processor gpt2 \
  --profile constant \
  --rate 1 \
  --max-seconds 300 \
  --output-dir ./results_phi3/pt50_ot100 \
  --outputs benchmarks.json,benchmarks.csv,benchmarks.html
```

**Notes:**
- `--backend openai_http` tells GuideLLM to use OpenAI-compatible API calls
- `--target` points to Ollama's endpoint
- `--model phi3` must match the model name Ollama serves
- `--outputs` should use explicit filenames (e.g., `benchmarks.json`) not just aliases
- If healthcheck fails, add `--backend-kwargs '{"validate_backend":false}'`

---

## Analyzing Results

### 8) Validate Benchmark Results

If the run is correct, you should see 200 responses in the server logs:

```
[GIN] 2024/10/01 - 12:58:48 | 200 | 2.62s | 127.0.0.1 | POST "/v1/chat/completions"
```

### 9) Inspect Outputs with Python

Run the analysis script:

```bash
python3 analyze_results.py
```

Or view the HTML report directly:

```bash
open ./guidellm/results_phi3/pt50_ot100/benchmarks.html
```

---

## Results Summary

### Benchmark Configuration
| Parameter | Value |
|-----------|-------|
| Target | http://localhost:11434/v1 |
| Model | phi3 |
| Profile | constant |
| Rate | 1.0 req/sec |
| Duration | 300 seconds |

### Request Statistics
| Metric | Value |
|--------|-------|
| Successful Requests | 24 (4.2%) |
| Errored Requests | 215 (37.3%) |
| Incomplete/Cancelled | 338 |
| Total Processed | 577 |

### Performance Metrics (Successful Requests)
| Metric | Value |
|--------|-------|
| Mean Latency | 56.95 sec |
| Median Latency | 61.84 sec |
| P95 Latency | 118.95 sec |
| P99 Latency | 164.01 sec |
| Min Latency | 2.17 sec |
| Max Latency | 164.01 sec |

### Token Metrics
| Metric | Value |
|--------|-------|
| Time to First Token (TTFT) Mean | 44,874 ms (~45 sec) |
| Inter-Token Latency (ITL) Mean | 9.36 ms |
| Output Tokens/sec Mean | 106.44 |
| Requests/sec Mean | 0.08 |

---

## Analysis

### Key Findings

1. **High Error Rate (37.3%)**: Ollama was overwhelmed by the benchmark load. Requests were sent at 1/sec, but each took ~57 seconds to complete, causing a massive backlog and timeouts.

2. **Very Slow Time to First Token (~45 sec)**: This indicates slow model loading or inference startup on CPU.

3. **Decent Generation Speed Once Started**: ITL of 9.36ms translates to ~107 tokens/sec after the first token arrives.

4. **Low Throughput**: Only 24 successful completions in 5 minutes due to timeouts.

### Recommendations

For better benchmark results, consider:
- Running Ollama on GPU (if available)
- Using a smaller/faster model
- Reducing the request rate (e.g., `--rate 0.1`)
- Increasing Ollama's timeout settings
- Running with fewer concurrent requests

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Model not found | Ensure `ollama run phi3` completed successfully before `ollama serve` |
| HTTP errors | Double-check `--target` URL and that Ollama exposes `/v1/*` |
| GuideLLM CLI flags | Use `guidellm --help` and project README; flag names may differ between versions |
| Healthcheck fails | Use `--backend-kwargs '{"validate_backend":false}'` |
| Output file error | Use explicit filenames like `benchmarks.json` instead of just `json` |

---

## Project Structure

```
.
├── README.md                 # This file
├── analyze_results.py        # Python script to analyze benchmark results
└── guidellm/                 # Cloned GuideLLM repository
    └── results_phi3/
        └── pt50_ot100/
            ├── benchmarks.json   # Raw benchmark data
            ├── benchmarks.csv    # Tabular results
            └── benchmarks.html   # Interactive HTML report
```

---

## Environment Info

- **GuideLLM Version**: 0.5.0
- **Python Version**: 3.13.9
- **Platform**: macOS-26.1-arm64-arm-64bit-Mach-O (Apple Silicon)
