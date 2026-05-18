---
title: TriageAI — Emergency Triage
emoji: 🚨
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.9.1
app_file: demo/app.py
pinned: true
license: apache-2.0
short_description: Offline multilingual emergency triage powered by Gemma 4
---

# TriageAI — Offline Multilingual Emergency Triage

**When every second counts and networks are down.**

[![Kaggle](https://img.shields.io/badge/Kaggle-Competition-20BEFF.svg?logo=kaggle)](https://www.kaggle.com/competitions/gemma-4-good-hackathon)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> In the 2023 Turkey-Syria earthquake, over 50,000 people died. In the first 72 hours, overwhelmed first responders had to make impossible triage decisions. Untrained bystanders — the actual first people on scene — had no guidance on who needed help first, how to stop bleeding, or when NOT to move someone with a spinal injury.
>
> **TriageAI is built for that moment.**

## What It Does

TriageAI is an **offline-first, multilingual emergency triage AI** powered by Gemma 4 that helps bystanders and first responders make rapid, accurate emergency assessments.

- Analyzes emergency scenes from **photos + text** (multimodal)
- Performs **START triage** classification (RED/YELLOW/GREEN/BLACK)
- Provides **step-by-step first-aid guidance** grounded in medical protocols
- Responds in **35+ languages** automatically
- Works **completely offline** — no internet required

## Architecture

```
User Input (photo + text, any language)
       |
[1. Language Detection + Input Processing]
       |
[2. Emergency Classification — Gemma 4 Function Calling]
   classify_emergency() → type + hazards + scene safety
       |
[3. Severity Assessment — Gemma 4 Thinking Mode]
   assess_severity() → START triage: RED/YELLOW/GREEN/BLACK
       |
[4. RAG: Emergency Protocol Retrieval]
   29 first-aid protocols loaded based on classification
       |
[5. Action Plan Generation — Gemma 4 Function Calling]
   generate_action_plan() → step-by-step in user's language
       |
[6. Structured Triage Card Output]
   Color-coded card + actions + DO NOT warnings + dispatcher script
```

## How We Use Gemma 4

| Capability | Implementation |
|---|---|
| **Multimodal Vision** | Photo analysis of injuries, disaster scenes, accident sites |
| **Native Function Calling** | 4 structured tools: classify → assess → plan → localize |
| **Thinking Mode** | Step-by-step clinical reasoning for critical decisions |
| **Multilingual (35+ langs)** | Emergency guidance in victim's language |
| **Offline Deployment** | Ollama, llama.cpp, LiteRT — works without internet |

## Notebooks

| Notebook | Description |
|---|---|
| [01_triageai_main](notebooks/01_triageai_main.ipynb) | Full triage pipeline with 5 demo scenarios |
| [02_unsloth_finetune](notebooks/02_unsloth_finetune.ipynb) | Fine-tune on 200+ triage examples, before/after benchmarks |
| [03_ollama_deploy](notebooks/03_ollama_deploy.ipynb) | Local deployment via Ollama, 3 languages |
| [04_llamacpp_cpu](notebooks/04_llamacpp_cpu.ipynb) | CPU-only inference via GGUF, no GPU required |
| [05_cactus_routing](notebooks/05_cactus_routing.ipynb) | Intelligent E2B/E4B routing by severity |

## Knowledge Base

29 curated emergency protocol files covering:
- **Medical** (16): Bleeding, burns, CPR, fractures, choking, shock, allergic reaction, head injury, poisoning, heatstroke, hypothermia, seizure, stroke, heart attack, drowning
- **Disaster** (4): Earthquake, flood, fire, hurricane
- **Accident** (4): Vehicle crash, electrical, chemical spill, fall from height
- **General** (5): START triage protocol, scene safety, recovery position, emergency numbers, psychological first aid

All protocols include translations in Spanish, Hindi, Arabic, and French.

## Live Demo

**[🚀 Try TriageAI on HuggingFace Spaces](https://huggingface.co/spaces/kalyanreddy77/triageai)**

## Quick Start

### Run the Kaggle Notebook
Upload `01_triageai_main.ipynb` to Kaggle with GPU T4 accelerator.

### Run Locally with Ollama
```bash
ollama pull gemma4:e2b
cd demo
pip install -r requirements.txt
python app.py
```

### Run on CPU with llama.cpp
```bash
pip install llama-cpp-python
python -c "
from llama_cpp import Llama
llm = Llama(model_path='gemma-4-E2B-Q4_K_M.gguf', n_gpu_layers=0)
print(llm('Someone is bleeding heavily from a cut. What do I do?')['choices'][0]['text'])
"
```

## Impact

| Metric | Number |
|---|---|
| People affected by natural disasters annually | 160 million |
| Disaster deaths in low-to-middle-income countries | 90% |
| Bystander first aid reduces trauma mortality | 50% |
| Smartphone users globally (potential reach) | 4.6 billion |
| Average rural emergency response time | 14-30 minutes |

**Bystanders are the real first responders.** TriageAI puts expert triage guidance in their pocket.

## Project Structure

```
triageai/
├── src/
│   ├── triage_engine.py       # Core pipeline
│   ├── function_schemas.py    # 4 tool definitions
│   ├── knowledge_base.py      # Protocol retrieval
│   ├── triage_card.py         # HTML/text card renderer
│   └── utils.py               # Image processing, language detection
├── knowledge_base/            # 29 emergency protocol JSONs
├── training_data/             # Fine-tuning dataset
├── notebooks/                 # 5 Kaggle notebooks
└── demo/                      # Gradio app for HuggingFace Space
```

## License

Apache 2.0 — same as Gemma 4.

## Disclaimer

TriageAI is an AI assistant and **NOT a substitute for professional medical care.** Always call emergency services for life-threatening situations. This tool provides general first-aid guidance based on established protocols (AHA, Red Cross, WHO, FEMA).

---

*TriageAI — Because the next life saved shouldn't depend on cell signal.*

*Built with Gemma 4 for the Gemma 4 Good Hackathon 2026.*
*Kaggle x Google DeepMind*
