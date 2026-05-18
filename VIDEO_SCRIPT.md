# TriageAI — Video Script
**Target length:** 3 minutes (180 seconds)  
**Format:** Screen recording + voiceover  
**Tone:** Urgent, human, grounded — not a product demo

---

## SCREEN SETUP BEFORE RECORDING
- HuggingFace Space open: https://huggingface.co/spaces/kalyanreddy77/triageai
- Terminal ready with: `ollama run triageai`
- NB01 output open (triage cards rendered)
- Font size bumped up for readability

---

## [0:00 – 0:25] HOOK — The real story

**SCREEN:** Black screen. White text appears, line by line:

> *A bus carrying 40 children hit a train.*  
> *Unstaffed level crossing. Village in India.*  
> *Nearest ambulance: 50 kilometers.*  
> *16 children did not go home that day.*

**VOICEOVER (personal, quiet — this is your voice, your story):**
> "I was there. I helped pull children from the wreckage.
> The farmers around me rushed in — they wanted to help.
> They didn't know how.
>
> Nobody moved with certainty. Nobody knew who to help first.
> Nobody knew which child might have a spinal injury.
> Nobody knew what not to do.
>
> I had some knowledge. Most people there had none.
> And I kept asking myself — what if there had been something
> that could have told us what to do?
>
> That question is why I built TriageAI."

---

## [0:25 – 0:40] PROBLEM STATEMENT

**SCREEN:** Simple white text on black

> *160 million people affected by disasters every year.*  
> *8–30 minutes before paramedics arrive.*  
> *The bystander is always there first.*  
> *Nobody has ever given them the tools to act.*

**VOICEOVER:**
> "That crossing in India is not an exception. It is the rule.
> Every day, in disaster zones, on rural roads, in villages — the first person on scene
> is untrained, unequipped, and alone.
> They are the difference between life and death.
> And for decades, we have given them nothing."

---

## [0:35 – 0:50] WHAT IT IS — One-line + Live Demo intro

**SCREEN:** Switch to HuggingFace Space. Pause on the landing page so viewers see the UI.

**VOICEOVER:**
> "TriageAI is an offline-first, multilingual emergency triage assistant — for the person
> with no training, no signal, and no time.
> Describe what you see. Get back exactly what a paramedic would tell you."

---

## [0:50 – 1:20] LIVE DEMO — 3 quick scenarios

**SCREEN:** Type into HF Space, show triage card output. Move fast — 10s per scenario.

**Scenario 1 — English, severe**
- Type: *"Person hit by car, not breathing, pulse weak"*
- Show: RED card appearing — IMMEDIATE, numbered steps, DO NOT list
- **VOICEOVER:** "Severe trauma. RED — Immediate. Step by step. What to do, what not to do, what to say to the dispatcher."

**Scenario 2 — Spanish**
- Type: *"Terremoto. Hombre atrapado bajo escombros, consciente pero no puede moverse"*
- Show: Response in Spanish
- **VOICEOVER:** "Emergencies don't happen in English only. TriageAI detects the language and responds in kind — automatically."

**Scenario 3 — Image upload**
- Upload a burn wound photo (use a stock image or the sample in the repo)
- Show: Assessment that references the visual
- **VOICEOVER:** "A photo tells you more than any description. Gemma 4's vision analyzes both together."

---

## [1:20 – 1:50] FOUR GEMMA 4 CAPABILITIES

**SCREEN:** Split — left side shows code/notebook output, right side shows text callouts

**VOICEOVER (fast, punchy — one line each):**

> "**Native function calling** — not prose, not guesses. A deterministic three-stage pipeline:
> classify, assess severity, generate action plan. Always structured. Always scannable.

> **Thinking mode** — for complex scenes with multiple victims or competing priorities,
> Gemma 4 reasons step by step before responding. Chain-of-thought, applied to save lives.

> **Multimodal vision** — photos of wounds, crash scenes, chemical spills — analyzed alongside text.

> **Multilingual** — English, Spanish, Hindi, Arabic, French. The protocol knowledge base
> is translated in all five. Because when someone is in shock, they need answers in their own language."

**SCREEN CUE:** Show the function calling pipeline briefly from NB01 output — the `classify_emergency → assess_severity → generate_action_plan` flow with the tool call blocks visible.

---

## [1:50 – 2:15] WORKS EVERYWHERE

**SCREEN:** Quick cuts between each deployment mode — 5–6 seconds each

1. **HF Space** — already shown
2. **Ollama terminal** — `ollama run triageai`, type a query, show response
3. **llama.cpp** — show NB04 output: "n_gpu_layers=0 · CPU only · 3.5 GB RAM"
4. **Unsloth fine-tune** — show NB02 accuracy chart: "20% → 99% in 60 steps"
5. **Cactus routing** — show NB05 routing table: "GREEN → E2B · RED → E4B"

**VOICEOVER:**
> "No WiFi? Ollama runs it locally — one command.
> No GPU? llama.cpp runs on any laptop, pure CPU, 3.5 gigabytes of RAM.
> Want it domain-trained? Unsloth fine-tuning took triage accuracy from 20% to 99% in 60 steps.
> Want efficient inference? Cactus routing sends simple queries to the fast model,
> critical queries to the full-reasoning model — saving compute where it doesn't matter,
> preserving power where it does."

---

## [2:15 – 2:40] THE PEOPLE THIS IS FOR

**SCREEN:** Simple white text on dark background, one portrait at a time

**VOICEOVER (slow, deliberate):**

> "The farmer at an unstaffed rail crossing in India,
> holding an injured child, not knowing if moving her will kill her.

> The community health worker in rural Kenya —
> serving a village 60 kilometers from the nearest hospital,
> on a 150-dollar Android phone.

> The disaster volunteer at a mass casualty event,
> trying to coordinate triage across 40 victims in a language they don't speak.

> The parent whose child just stopped breathing in a pool,
> whose hands are shaking so badly they can barely type.

> These are not edge cases.
> These are the people who need this most.
> And they are the people that almost every other AI product has forgotten."

---

## [2:40 – 3:00] CLOSE

**SCREEN:** GitHub repo URL + HF Space URL + "Try it now" — hold for 10 seconds

**VOICEOVER:**
> "The technology to save lives in those critical minutes already exists.
> It's free. It's open. It's small enough to run on a phone.
> It speaks five languages. It works without internet.

> The only thing missing was someone putting it together
> for the people who need it most.

> **That is TriageAI. And we built it.**"

**SCREEN:** Fade to black.  
Text: *TriageAI — Because the next life saved shouldn't depend on cell signal.*  
Text: *Built with Gemma 4 · Open source, forever · github.com/Kalyankr/triageai*

---

## RECORDING CHECKLIST
- [ ] HF Space demo — 3 scenarios (English RED, Spanish earthquake, image upload)
- [ ] Terminal: `ollama run triageai` — one query, show response
- [ ] NB04 output — CPU inference, show "n_gpu_layers=0"
- [ ] NB02 output — accuracy table 20% → 99%
- [ ] NB05 output — routing table with scores
- [ ] NB01 output — function calling pipeline with tool call blocks visible

## TOOLS FOR RECORDING (Windows)
- **Screen record:** Xbox Game Bar (`Win + G`) or OBS Studio (free)
- **Voiceover:** Record separately, sync in any editor (DaVinci Resolve free, Clipchamp built into Windows)
- **Text overlays:** Canva, DaVinci Resolve, or Windows Clipchamp

## SUBMISSION NOTE
Competition allows up to 5 minutes. 3 minutes is ideal — judges watch many videos.
Keep cuts tight. The voiceover carries the emotion; the screen recording proves the tech is real.
