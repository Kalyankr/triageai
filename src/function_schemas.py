TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "classify_emergency",
            "description": (
                "Classifies the type of emergency situation based on the scene "
                "description and/or image. Must be called first before other tools."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "emergency_type": {
                        "type": "string",
                        "enum": [
                            "medical_injury",
                            "medical_illness",
                            "fire",
                            "flood",
                            "earthquake",
                            "vehicle_accident",
                            "chemical_hazard",
                            "electrical_hazard",
                            "drowning",
                            "unknown",
                        ],
                        "description": "The primary category of emergency",
                    },
                    "sub_type": {
                        "type": "string",
                        "description": (
                            "Specific sub-category, e.g. 'laceration', "
                            "'burn_second_degree', 'cardiac_arrest'"
                        ),
                    },
                    "num_victims": {
                        "type": "integer",
                        "description": "Estimated number of people affected",
                    },
                    "scene_safe": {
                        "type": "boolean",
                        "description": (
                            "Whether the scene appears safe for a bystander to approach"
                        ),
                    },
                    "hazards_detected": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of environmental hazards visible",
                    },
                },
                "required": ["emergency_type", "scene_safe"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "assess_severity",
            "description": (
                "Performs START triage assessment using Respiration, Perfusion, "
                "and Mental Status criteria to assign a triage color. "
                "RED=Immediate life-threatening, YELLOW=Delayed but serious, "
                "GREEN=Minor/walking wounded, BLACK=Expectant/deceased."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "triage_color": {
                        "type": "string",
                        "enum": ["RED", "YELLOW", "GREEN", "BLACK"],
                        "description": (
                            "RED=Immediate, YELLOW=Delayed, GREEN=Minor, "
                            "BLACK=Expectant"
                        ),
                    },
                    "can_walk": {
                        "type": "boolean",
                        "description": "Whether patient is ambulatory (automatic GREEN)",
                    },
                    "breathing": {
                        "type": "string",
                        "enum": [
                            "normal",
                            "rapid_over_30",
                            "absent",
                            "present_after_repositioning",
                            "unknown",
                        ],
                    },
                    "perfusion": {
                        "type": "string",
                        "enum": [
                            "normal_pulse",
                            "weak_or_absent_pulse",
                            "capillary_refill_over_2s",
                            "unknown",
                        ],
                    },
                    "mental_status": {
                        "type": "string",
                        "enum": [
                            "alert_and_oriented",
                            "confused",
                            "unresponsive",
                            "follows_commands",
                            "unknown",
                        ],
                    },
                    "visible_injuries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Injuries visible in image or described",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence in triage assessment 0.0-1.0",
                    },
                    "clinical_reasoning": {
                        "type": "string",
                        "description": (
                            "Step-by-step reasoning for the triage decision"
                        ),
                    },
                },
                "required": ["triage_color", "clinical_reasoning"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_action_plan",
            "description": (
                "Generates a prioritized emergency action plan based on "
                "situation assessment and severity level."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "immediate_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Actions to take RIGHT NOW (first 60 seconds)",
                    },
                    "follow_up_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Actions for the next 5-15 minutes",
                    },
                    "do_not_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Critical things to AVOID doing",
                    },
                    "monitoring_signs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What to watch for while waiting for help",
                    },
                    "escalation_criteria": {
                        "type": "string",
                        "description": "When to upgrade urgency level",
                    },
                    "dispatcher_script": {
                        "type": "string",
                        "description": (
                            "What to tell emergency dispatchers when calling"
                        ),
                    },
                },
                "required": ["immediate_actions", "do_not_actions"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "detect_language_and_localize",
            "description": (
                "Detects the user's language and provides localized emergency "
                "information including local emergency numbers."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "detected_language": {
                        "type": "string",
                        "description": "ISO 639-1 code, e.g. 'en', 'es', 'hi', 'ar'",
                    },
                    "response_language": {
                        "type": "string",
                        "description": "Language to respond in",
                    },
                    "local_emergency_number": {
                        "type": "string",
                        "description": "Emergency number for likely region",
                    },
                    "country_context": {
                        "type": "string",
                        "description": "Inferred country/region from language + context",
                    },
                },
                "required": ["detected_language", "response_language"],
            },
        },
    },
]


def get_tool_schemas():
    return TOOL_SCHEMAS


def get_tool_names():
    return [t["function"]["name"] for t in TOOL_SCHEMAS]


def format_tools_for_prompt(schemas=None):
    """Format tool schemas into Gemma 4 system prompt format."""
    schemas = schemas or TOOL_SCHEMAS
    lines = ["You have access to the following tools:\n"]
    for tool in schemas:
        fn = tool["function"]
        lines.append(f"### {fn['name']}")
        lines.append(f"Description: {fn['description']}")
        props = fn["parameters"]["properties"]
        required = fn["parameters"].get("required", [])
        lines.append("Parameters:")
        for pname, pinfo in props.items():
            req_marker = " (required)" if pname in required else ""
            ptype = pinfo.get("type", "string")
            desc = pinfo.get("description", "")
            if "enum" in pinfo:
                desc += f" Options: {pinfo['enum']}"
            lines.append(f"  - {pname} ({ptype}{req_marker}): {desc}")
        lines.append("")
    lines.append(
        "To call a tool, output a JSON object with 'name' and 'arguments' keys "
        "wrapped in ```tool_call``` code blocks."
    )
    return "\n".join(lines)
