# TriageAI: Offline Emergency Triage for Everyone, Powered by Gemma 4
*When cell towers fall, lives still shouldn't.*

---

## Why This Exists — A Real Story

I was there.

A bus carrying over 40 children — aged three to fourteen — collided with the Nanded-Hyderabad Passenger train at an unstaffed level crossing in a village in India. Sixteen children, the bus driver, and the cleaner were killed. Twenty more children were pulled out and taken to hospital in Kompally, 50 kilometers away.

The farmers who rushed to the scene wanted desperately to help. They did not know how. They moved children without knowing whether their spines were intact. They didn't know how to check if a child was breathing, how to stop bleeding, how to tell who needed help first. They had never been taught. Nobody had ever taught them. There was no infrastructure at that crossing, no signal, no trained person within reach — just a dirt road, a broken bus, and forty children.

I helped pull children from the wreckage. I tried to be careful. But I was terrified too — not of the scene, but of my own uncertainty. Is this child concussed? Does she have a spinal injury? Am I making it worse by moving her? What do I do if she stops breathing? I had some knowledge. Most people there had none.

Sixteen children did not go home that day.

I don't know if better information in that moment would have changed the outcome. But I know that no one standing at that crossing had any tools to act on. No guidance. No protocol. No way to know what to do first.

That is why I built TriageAI.

Not as a product. Not as a competition entry. As an answer to a question I couldn't stop asking: **what if there had been something — anything — that could have told those farmers what to do?**

Until now, that something did not exist for people like them — no internet, no training, no English, no time. TriageAI is that something.

---

## What TriageAI Is

TriageAI is an **offline-first, multilingual, AI-powered emergency triage assistant** built for the person with no training, no signal, and no time.

A bystander describes what they see — in any language, as text or a photo — and TriageAI responds in seconds with the same assessment a trained paramedic would make:

- **Who needs help first** — START triage: RED (immediate), YELLOW (delayed), GREEN (minor), BLACK (expectant)
- **Exactly what to do** — numbered steps, plain language, no medical jargon
- **What not to do** — the mistakes that kill (moving spinal injuries, removing embedded objects, giving water to unconscious patients)
- **What to say to 911** — a dispatcher script so precious time isn't lost explaining

No internet. No GPU. No medical degree. Just answers — in the moments that matter most.

---

## Why This Problem Cannot Wait

> *Research shows bystander first aid can reduce trauma mortality by up to 50%.*  
> *The average rural emergency response time is 14–30 minutes.*  
> *90% of disaster deaths occur in low-to-middle-income countries.*  
> *160 million people are affected by natural disasters every year.*

The gap between "disaster happens" and "paramedic arrives" is where most preventable deaths occur. That gap is 8 to 30 minutes. In those minutes, the only person who can help is whoever happens to be standing there.

We have been asking untrained people to make life-or-death decisions for decades — with nothing but panic and instinct.

TriageAI changes that equation.

---

## How Gemma 4 Makes This Possible

This is not a chatbot wrapped in a medical theme. TriageAI is a purpose-built clinical decision pipeline that uses four breakthrough capabilities of Gemma 4 that **no other open model at this size provides simultaneously:**

### Native Function Calling — Structured, Trustworthy Output
Medical guidance cannot be unstructured prose. A bystander reading a wall of text while someone bleeds out will miss the critical step. TriageAI uses Gemma 4's native function calling to enforce a deterministic 3-stage pipeline:

```
classify_emergency()  →  assess_severity()  →  generate_action_plan()
```

Each stage is a formal tool call with typed parameters and validated output. The result is always a structured triage card — consistent, scannable, actionable. Gemma 4 is the first open model capable of reliable multi-round function calling at edge-deployable size. This pipeline simply was not possible before.

### Thinking Mode — Reasoning Like a Paramedic
A cardiac arrest and a severe burn in the same scene. Who do you treat first? How do you assess someone who cannot speak? These are not lookup questions — they require reasoning.

We enable `enable_thinking=True` for complex multi-victim scenarios. Gemma 4 works through the problem step by step — evaluating competing priorities, identifying hidden hazards, deciding whether to stabilize or evacuate — before producing its recommendation. This is chain-of-thought reasoning applied to save lives.

### Multimodal Vision — See What the Bystander Sees
A photo of a wound tells you more than any description. A picture of a crash scene reveals hazards — fuel leaks, downed wires, unstable vehicles — that a panicking bystander might not think to mention.

TriageAI accepts photos alongside text. Gemma 4 analyzes both together, producing assessments that account for what is visually present, not just what the user managed to type under pressure.

### Multilingual — Because Emergencies Don't Happen in English Only
The 2023 Turkey-Syria earthquake killed over 50,000 people. The 2024 Morocco earthquake. The 2025 Myanmar earthquake. The victims spoke Turkish, Arabic, Burmese. The bystanders spoke whatever language they grew up with.

TriageAI detects the user's language and responds in kind — automatically, without switching, without settings. We tested and verified English, Spanish, Hindi, Arabic, and French. Our 29-protocol knowledge base includes translations for all five. When someone is in shock and terrified, reading guidance in their own language is not a nice-to-have — it is the difference between following instructions and freezing.

---

## The Architecture

```
Photo + Text (any language)
         │
         ▼
┌──────────────────────────────────────────────────┐
│  Stage 1: classify_emergency()                   │
│  → emergency type · hazards · scene safety       │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│  Stage 2: assess_severity()  [Thinking Mode]     │
│  → START triage: RED / YELLOW / GREEN / BLACK    │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│  RAG: 29 Emergency Protocol JSONs                │
│  → grounded in AHA · Red Cross · WHO · FEMA      │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│  Stage 3: generate_action_plan()                 │
│  → immediate actions · do-nots · dispatcher      │
└───────────────────────┬──────────────────────────┘
                        │
                        ▼
          Color-coded triage card in user's language
```

### Knowledge Base
29 curated emergency protocol files grounded in authoritative medical and emergency management sources:

- **Medical (16):** Severe bleeding, burns, CPR, fractures, choking, anaphylaxis, shock, head injury, poisoning, heatstroke, hypothermia, seizure, stroke, cardiac arrest, drowning, pediatric emergencies
- **Disaster (4):** Earthquake, flood, fire, hurricane
- **Accident (4):** Vehicle crash, electrical, chemical spill, fall from height
- **General (5):** START triage protocol, scene safety, recovery position, emergency numbers, psychological first aid

Every protocol includes verified translations in Spanish, Hindi, Arabic, and French.

---

## Works Everywhere — Even When Nothing Else Does

The hardest design constraint we accepted: **TriageAI must function when all infrastructure has failed.**

No WiFi. No cell signal. No cloud. No GPU. Just a device and a person who needs help.

We built five deployment paths to guarantee this:

### Full Pipeline — Cloud / GPU
The complete Gemma 4 pipeline with 4-bit NF4 quantization runs on a single T4 GPU. Five demo scenarios — severe bleeding, chemical burn, Spanish earthquake, Hindi cardiac arrest, multi-vehicle accident — demonstrate the full function calling + thinking mode + RAG system end to end.

### Fine-Tuned Model — Unsloth
We fine-tuned Gemma 4 E2B-IT on 200+ curated triage examples using Unsloth LoRA (r=16, alpha=32). START protocol classification accuracy: **20% → 99% in 60 training steps.** A domain-adapted model that has internalized the triage protocol, not just prompted for it.

### Local Deployment — Ollama
`ollama run triageai` — one command. Gemma 4 E2B-IT running locally with a custom Modelfile embedding the TriageAI system prompt and persona. No API key. No subscription. Tested in English, Spanish, and Hindi.

### CPU-Only Inference — llama.cpp
GGUF Q4_K_M quantization. `n_gpu_layers=0`. ~3.5 GB RAM. Runs on a $200 laptop. Runs on a Raspberry Pi. Runs on anything with a CPU. This is the deployment for when the only available device is whatever someone happened to have in their bag when the earthquake hit.

### Intelligent Routing — Cactus
`CactusRouter` scores each query (0–100) by severity. Simple GREEN queries — scraped knee, mild headache — route to the fast, edge-deployable E2B model. Life-threatening RED queries — cardiac arrest, arterial bleeding, trapped victims — route to the full-reasoning E4B model. Both models fit simultaneously on a single T4 GPU (~9 GB total). Result: ~40–60% compute savings on simple cases, full power preserved where it matters.

---

## Live Demo

**Try it now:** https://huggingface.co/spaces/kalyanreddy77/triageai

The live demo requires no signup, no API key, and no installation. Type or upload a scenario and receive a triage assessment in seconds.

---

## The Real-World Reach

| People affected by natural disasters annually | 160 million |
|---|---|
| Disaster deaths in low-income countries | 90% |
| Reduction in trauma mortality with bystander first aid | up to 50% |
| Average rural emergency response time | 14–30 minutes |
| Languages supported | 5 (EN, ES, HI, AR, FR) |
| Emergency protocols grounded in AHA/Red Cross/WHO | 29 |
| Devices that can run TriageAI (CPU-only mode) | Any laptop made in the last 10 years |

### The People This Is For

**The farmer at an unstaffed rail crossing** — holding an injured child, not knowing if moving her will cause more damage than the crash already did.

**The community health worker** in rural Kenya, Nigeria, or Bangladesh — serving a population 60 km from the nearest hospital, on a $150 Android phone.

**The disaster volunteer** at a mass casualty event in a language they don't speak, trying to coordinate triage across 40 victims.

**The parent** whose child just stopped breathing in a pool, whose hands are shaking so badly they can barely type.

These are not edge cases. These are the people who need this most. And they are the people that almost every other AI product has forgotten.

---

## Technical Stack

| Component | Technology |
|---|---|
| Core LLM | Gemma 4 E2B-IT / E4B-IT |
| Quantization | BitsAndBytes NF4 4-bit |
| Fine-tuning | Unsloth LoRA (r=16, 2× faster, 60% less VRAM) |
| Local serving | Ollama with custom Modelfile |
| CPU inference | llama.cpp (GGUF Q4_K_M) |
| Model routing | CactusRouter (keyword + length + language scoring) |
| UI | Gradio Blocks on HuggingFace Spaces |
| Knowledge base | 29 JSON protocols, multilingual |
| Training format | ShareGPT conversational |
| Protocols grounded in | AHA, American Red Cross, WHO, FEMA |

---

## How This Addresses the Competition Themes

| Theme | TriageAI's Answer |
|---|---|
| **Global Resilience** | Offline-first disaster response — designed to work when everything else fails |
| **Health & Sciences** | Puts paramedic-level triage knowledge in the hands of any bystander, anywhere |
| **Digital Equity & Inclusivity** | 5 languages, any device, no internet, no cost |
| **Safety & Trust** | Grounded outputs from 29 verified protocols; explicit DO NOT warnings; always defers to emergency services |
| **Gemma 4 Unique Capabilities** | Function calling + thinking mode + vision + multilingual — all four, working together |

---

## Honest Limitations

We believe in transparency:

- TriageAI is a **decision-support tool**, not a replacement for professional medical care. Every output tells the user to call emergency services.
- Protocols are based on AHA, Red Cross, WHO, and FEMA guidelines but **have not been clinically validated** in a live emergency setting.
- The HuggingFace demo runs in offline mode — the full GPU pipeline requires a T4/A10 GPU instance.
- Fine-tuned GGUF export is constrained by T4 memory limits; the training itself (20% → 99% accuracy) is complete and the LoRA adapters are saved.

---

## The Bottom Line

The technology to save lives in the critical minutes before paramedics arrive already exists. It is free. It is open. It is small enough to run on a phone. It speaks five languages. It works without internet.

The only thing that was missing was someone putting it together for the people who need it most — the untrained bystander, standing over someone who is dying, with eight minutes and no idea what to do.

**That is TriageAI. And we built it.**

---

*TriageAI — Because the next life saved shouldn't depend on cell signal.*  
*Built with Gemma 4 · Apache 2.0 · Open source, forever.*
