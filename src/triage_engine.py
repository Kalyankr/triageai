import json
import re
from pathlib import Path

from .function_schemas import format_tools_for_prompt, TOOL_SCHEMAS
from .knowledge_base import (
    get_protocols_for_emergency,
    format_protocols_for_prompt,
    search_protocols_by_keywords,
)
from .triage_card import render_triage_card_html, render_triage_card_text
from .utils import (
    detect_language_simple,
    get_emergency_info,
    preprocess_image,
    LANGUAGE_MAP,
)


SYSTEM_PROMPT = """You are TriageAI, an expert emergency triage assistant powered by Gemma 4.
Your purpose is to help bystanders and first responders make rapid, accurate emergency assessments and provide life-saving guidance.

You follow the START (Simple Triage and Rapid Treatment) protocol:
- RED (Immediate): Life-threatening conditions requiring immediate intervention
- YELLOW (Delayed): Serious injuries that can wait briefly for treatment
- GREEN (Minor): Walking wounded, minor injuries
- BLACK (Expectant): Beyond help with current resources

CRITICAL RULES:
1. ALWAYS prioritize scene safety — never put the helper at risk
2. ALWAYS include a medical disclaimer — you are an AI, not a doctor
3. ALWAYS provide "DO NOT" warnings to prevent common mistakes
4. When analyzing images, describe what you observe and base your assessment on visible signs
5. Use function calling tools in this order: classify_emergency → assess_severity → generate_action_plan
6. Respond in the user's language when detected
7. Be direct, clear, and actionable — people in emergencies need simple instructions

{tools}

When you need to classify, assess, or generate an action plan, call the appropriate tool by outputting a JSON object with 'name' and 'arguments' wrapped in ```tool_call``` blocks.

Example tool call:
```tool_call
{{"name": "classify_emergency", "arguments": {{"emergency_type": "medical_injury", "scene_safe": true, "hazards_detected": []}}}}
```

After receiving tool results, use them to provide your final structured response."""


class TriageEngine:
    """Orchestrates the full triage pipeline using Gemma 4."""

    def __init__(self, model=None, processor=None, tokenizer=None, device="cuda"):
        self.model = model
        self.processor = processor
        self.tokenizer = tokenizer
        self.device = device

    @classmethod
    def from_pretrained(
        cls,
        model_id: str = "google/gemma-4-4b-it",
        quantize_4bit: bool = True,
        device: str = "cuda",
    ):
        """Load Gemma 4 with optional 4-bit quantization."""
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText

        load_kwargs = {"device_map": "auto", "torch_dtype": torch.bfloat16}

        if quantize_4bit:
            from transformers import BitsAndBytesConfig

            load_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_use_double_quant=True,
            )

        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForImageTextToText.from_pretrained(model_id, **load_kwargs)

        return cls(model=model, processor=processor, device=device)

    def _build_system_prompt(self) -> str:
        tools_text = format_tools_for_prompt()
        return SYSTEM_PROMPT.format(tools=tools_text)

    def _generate(
        self,
        messages: list[dict],
        images: list = None,
        max_new_tokens: int = 1024,
        enable_thinking: bool = False,
        temperature: float = 0.3,
    ) -> str:
        """Run inference on Gemma 4."""
        import torch

        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        if images:
            inputs = self.processor(
                text=prompt, images=images, return_tensors="pt"
            ).to(self.model.device)
        else:
            inputs = self.processor(
                text=prompt, return_tensors="pt"
            ).to(self.model.device)

        generate_kwargs = {
            "max_new_tokens": max_new_tokens,
            "do_sample": temperature > 0,
        }
        if temperature > 0:
            generate_kwargs["temperature"] = temperature

        with torch.no_grad():
            output_ids = self.model.generate(**inputs, **generate_kwargs)

        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        return self.processor.decode(new_tokens, skip_special_tokens=True)

    def _parse_tool_calls(self, text: str) -> list[dict]:
        """Extract tool calls from model output."""
        calls = []
        pattern = r"```tool_call\s*\n?(.*?)\n?```"
        for match in re.finditer(pattern, text, re.DOTALL):
            try:
                call = json.loads(match.group(1).strip())
                if "name" in call and "arguments" in call:
                    calls.append(call)
            except json.JSONDecodeError:
                continue

        if not calls:
            json_pattern = r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"arguments"\s*:\s*(\{[^{}]*\})[^{}]*\}'
            for match in re.finditer(json_pattern, text, re.DOTALL):
                try:
                    name = match.group(1)
                    args = json.loads(match.group(2))
                    calls.append({"name": name, "arguments": args})
                except (json.JSONDecodeError, IndexError):
                    continue

        return calls

    def _extract_structured_response(self, text: str) -> dict:
        """Extract structured data from free-text model response when tool calls fail."""
        result = {
            "emergency_type": "unknown",
            "triage_color": "YELLOW",
            "reasoning": "",
            "actions": {},
        }

        color_patterns = {
            "RED": r"(?:RED|IMMEDIATE|life.?threaten|critical|urgent)",
            "YELLOW": r"(?:YELLOW|DELAYED|serious|moderate)",
            "GREEN": r"(?:GREEN|MINOR|walking|mild|stable)",
            "BLACK": r"(?:BLACK|EXPECTANT|deceased|beyond)",
        }
        for color, pat in color_patterns.items():
            if re.search(pat, text, re.IGNORECASE):
                result["triage_color"] = color
                break

        type_patterns = {
            "medical_injury": r"(?:injur|wound|bleed|fractur|burn|cut|lacerat)",
            "medical_illness": r"(?:heart|stroke|seizur|cardiac|chest pain|breath)",
            "fire": r"(?:fire|flame|smoke|burning building)",
            "flood": r"(?:flood|water level|drowning|submerge)",
            "earthquake": r"(?:earthquake|tremor|rubble|collapse|aftershock)",
            "vehicle_accident": r"(?:car|vehicle|crash|collision|accident|traffic)",
            "chemical_hazard": r"(?:chemical|toxic|spill|fume|hazmat)",
            "electrical_hazard": r"(?:electric|shock|power line|wire)",
            "drowning": r"(?:drown|submers|water rescue|pool|river)",
        }
        for etype, pat in type_patterns.items():
            if re.search(pat, text, re.IGNORECASE):
                result["emergency_type"] = etype
                break

        result["reasoning"] = text[:500]

        action_patterns = {
            "immediate_actions": r"(?:immediately|right now|first|do now)[:\s]*(.*?)(?:\n\n|\Z)",
            "do_not_actions": r"(?:do not|don't|never|avoid)[:\s]*(.*?)(?:\n\n|\Z)",
        }
        for key, pat in action_patterns.items():
            matches = re.findall(pat, text, re.IGNORECASE | re.DOTALL)
            if matches:
                items = []
                for m in matches:
                    for line in m.strip().split("\n"):
                        line = line.strip().lstrip("•-*123456789. ")
                        if line and len(line) > 5:
                            items.append(line)
                result["actions"][key] = items[:5]

        return result

    def run_triage(
        self,
        text: str = "",
        image=None,
        language: str = "auto",
        enable_thinking: bool = True,
        max_tool_rounds: int = 3,
    ) -> dict:
        """Run the full triage pipeline.

        Returns a dict with:
            - classification: emergency type + hazards
            - severity: triage color + reasoning
            - actions: immediate + follow-up + do-not + monitoring
            - language_info: detected language + emergency number
            - triage_card_html: rendered HTML card
            - triage_card_text: plain-text card
            - raw_responses: list of model outputs
            - thinking_trace: model's reasoning if thinking mode was on
        """
        if language == "auto" and text:
            language = detect_language_simple(text)
        elif language == "auto":
            language = "en"

        emergency_info = get_emergency_info(language)
        lang_name = LANGUAGE_MAP.get(language, "English")

        images = []
        if image is not None:
            img = preprocess_image(image)
            images = [img]

        system_prompt = self._build_system_prompt()

        user_content = ""
        if text:
            user_content += text
        if images:
            if user_content:
                user_content += "\n\n[An image of the emergency scene is attached. Analyze it carefully.]"
            else:
                user_content = "[An image of the emergency scene is attached. Analyze it carefully and perform triage.]"

        user_content += (
            f"\n\nRespond in {lang_name}. "
            f"Use function calling tools to: "
            f"1) classify the emergency, "
            f"2) assess severity using START triage, "
            f"3) generate a step-by-step action plan. "
            f"Think step-by-step about your clinical reasoning."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        raw_responses = []
        classification = {}
        severity = {}
        actions = {}
        language_info = {
            "detected_language": language,
            "response_language": lang_name,
            "local_emergency_number": emergency_info["number"],
            "country_context": emergency_info["country"],
        }
        thinking_trace = ""

        for round_num in range(max_tool_rounds):
            response = self._generate(
                messages,
                images=images if round_num == 0 else None,
                max_new_tokens=1024,
                enable_thinking=enable_thinking,
                temperature=0.3,
            )
            raw_responses.append(response)

            thinking_match = re.search(
                r"<think>(.*?)</think>", response, re.DOTALL
            )
            if thinking_match:
                thinking_trace += thinking_match.group(1).strip() + "\n"

            tool_calls = self._parse_tool_calls(response)

            if not tool_calls:
                fallback = self._extract_structured_response(response)
                if not classification:
                    classification = {
                        "emergency_type": fallback["emergency_type"],
                        "scene_safe": True,
                    }
                if not severity:
                    severity = {
                        "triage_color": fallback["triage_color"],
                        "clinical_reasoning": fallback["reasoning"],
                    }
                if not actions and fallback["actions"]:
                    actions = fallback["actions"]
                break

            for call in tool_calls:
                name = call["name"]
                args = call["arguments"]

                if name == "classify_emergency":
                    classification = args
                    protocols = get_protocols_for_emergency(
                        args.get("emergency_type", "unknown")
                    )
                    protocol_text = format_protocols_for_prompt(protocols, language)
                    tool_result = (
                        f"Emergency classified as: {args.get('emergency_type')}. "
                        f"Scene safe: {args.get('scene_safe', 'unknown')}. "
                        f"Relevant protocols loaded:\n\n{protocol_text}"
                    )

                elif name == "assess_severity":
                    severity = args
                    tool_result = (
                        f"Triage assessment recorded: {args.get('triage_color')}. "
                        f"Now generate an action plan."
                    )

                elif name == "generate_action_plan":
                    actions = args
                    tool_result = "Action plan generated successfully."

                elif name == "detect_language_and_localize":
                    language_info.update(args)
                    tool_result = (
                        f"Language: {args.get('detected_language')}, "
                        f"Emergency number: {args.get('local_emergency_number', 'N/A')}"
                    )

                else:
                    tool_result = f"Unknown tool: {name}"

                messages.append({"role": "assistant", "content": response})
                messages.append({
                    "role": "user",
                    "content": f"Tool result for {name}: {tool_result}",
                })

            if classification and severity and actions:
                break

        triage_color = severity.get("triage_color", "YELLOW")
        emergency_type = classification.get("emergency_type", "unknown")
        reasoning = severity.get("clinical_reasoning", "Assessment pending")

        card_html = render_triage_card_html(
            color=triage_color,
            emergency_type=emergency_type,
            reasoning=reasoning,
            actions=actions,
            language_info=language_info,
        )
        card_text = render_triage_card_text(
            color=triage_color,
            emergency_type=emergency_type,
            reasoning=reasoning,
            actions=actions,
        )

        return {
            "classification": classification,
            "severity": severity,
            "actions": actions,
            "language_info": language_info,
            "triage_card_html": card_html,
            "triage_card_text": card_text,
            "raw_responses": raw_responses,
            "thinking_trace": thinking_trace,
        }


class TriageEngineOffline:
    """Lightweight triage engine that works without a model loaded.

    Uses the knowledge base directly with deterministic rules for
    demonstrating offline capability.
    """

    def run_triage(self, text: str = "", language: str = "auto") -> dict:
        if language == "auto":
            language = detect_language_simple(text)

        emergency_info = get_emergency_info(language)
        protocols = search_protocols_by_keywords(text, top_k=3)

        if not protocols:
            emergency_type = "unknown"
            triage_color = "YELLOW"
        else:
            top = protocols[0]
            emergency_type = top.get("category", "unknown")
            tags = top.get("severity_tags", ["YELLOW"])
            triage_color = tags[0] if tags else "YELLOW"

        actions = {}
        if protocols:
            p = protocols[0]["protocol"]
            actions = {
                "immediate_actions": p.get("steps", [])[:3],
                "do_not_actions": p.get("do_not", []),
                "escalation_criteria": p.get("when_to_escalate", ""),
            }

        reasoning = (
            f"Based on keyword analysis of the input, matched protocols: "
            f"{', '.join(p['title'] for p in protocols)}."
        )

        card_html = render_triage_card_html(
            color=triage_color,
            emergency_type=emergency_type,
            reasoning=reasoning,
            actions=actions,
            language_info={
                "local_emergency_number": emergency_info["number"],
            },
        )
        card_text = render_triage_card_text(
            color=triage_color,
            emergency_type=emergency_type,
            reasoning=reasoning,
            actions=actions,
        )

        return {
            "classification": {"emergency_type": emergency_type},
            "severity": {"triage_color": triage_color, "clinical_reasoning": reasoning},
            "actions": actions,
            "language_info": {
                "detected_language": language,
                "local_emergency_number": emergency_info["number"],
                "country_context": emergency_info["country"],
            },
            "triage_card_html": card_html,
            "triage_card_text": card_text,
            "raw_responses": [],
            "thinking_trace": "",
        }
