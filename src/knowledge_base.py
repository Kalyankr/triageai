import json
import os
from pathlib import Path


KB_ROOT = Path(__file__).resolve().parent.parent / "knowledge_base"


def load_protocol(protocol_id: str) -> dict | None:
    """Load a single protocol JSON by id, searching all subdirectories."""
    for subdir in KB_ROOT.iterdir():
        if not subdir.is_dir():
            continue
        path = subdir / f"{protocol_id}.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    return None


def load_all_protocols() -> list[dict]:
    """Load every protocol JSON in the knowledge base."""
    protocols = []
    for subdir in sorted(KB_ROOT.iterdir()):
        if not subdir.is_dir():
            continue
        for path in sorted(subdir.glob("*.json")):
            with open(path, encoding="utf-8") as f:
                protocols.append(json.load(f))
    return protocols


TYPE_TO_PROTOCOLS = {
    "medical_injury": [
        "bleeding_control", "fractures", "shock", "head_injury", "burns",
    ],
    "medical_illness": [
        "cpr_adult", "stroke", "heart_attack", "shock", "seizure",
        "allergic_reaction",
    ],
    "fire": ["fire", "burns", "shock", "scene_safety"],
    "flood": ["flood", "drowning", "hypothermia", "scene_safety"],
    "earthquake": [
        "earthquake", "fractures", "bleeding_control", "scene_safety",
    ],
    "vehicle_accident": [
        "vehicle_crash", "bleeding_control", "fractures", "shock",
    ],
    "chemical_hazard": [
        "chemical_spill", "poisoning", "burns", "scene_safety",
    ],
    "electrical_hazard": [
        "electrical", "cpr_adult", "burns", "scene_safety",
    ],
    "drowning": ["drowning", "cpr_adult", "cpr_child", "hypothermia"],
    "unknown": ["scene_safety", "start_triage", "recovery_position"],
}


def get_protocols_for_emergency(
    emergency_type: str, max_protocols: int = 3
) -> list[dict]:
    """Retrieve the most relevant protocols for a given emergency type."""
    protocol_ids = TYPE_TO_PROTOCOLS.get(emergency_type, TYPE_TO_PROTOCOLS["unknown"])
    results = []
    for pid in protocol_ids[:max_protocols]:
        proto = load_protocol(pid)
        if proto:
            results.append(proto)
    if not results:
        for fallback_id in ["scene_safety", "start_triage"]:
            proto = load_protocol(fallback_id)
            if proto:
                results.append(proto)
    return results


def format_protocols_for_prompt(protocols: list[dict], lang: str = "en") -> str:
    """Format retrieved protocols into a context string for the LLM prompt."""
    sections = []
    for proto in protocols:
        title = proto["title"]
        if lang != "en" and lang in proto.get("translations", {}):
            title = proto["translations"][lang].get("title", title)

        p = proto["protocol"]
        lines = [
            f"## {title}",
            f"**Assessment:** {p['assessment']}",
            "",
            "**Steps:**",
        ]
        for step in p["steps"]:
            lines.append(f"  {step}")
        lines.append("")
        lines.append("**DO NOT:**")
        for warning in p["do_not"]:
            lines.append(f"  - {warning}")
        lines.append("")
        lines.append(f"**Escalate when:** {p['when_to_escalate']}")
        sections.append("\n".join(lines))
    return "\n\n---\n\n".join(sections)


def search_protocols_by_keywords(query: str, top_k: int = 3) -> list[dict]:
    """Simple keyword-based retrieval across all protocols."""
    query_words = set(query.lower().split())
    scored = []
    for proto in load_all_protocols():
        keywords = set(k.lower() for k in proto.get("keywords", []))
        overlap = len(query_words & keywords)
        title_words = set(proto["title"].lower().split())
        overlap += len(query_words & title_words) * 2
        if overlap > 0:
            scored.append((overlap, proto))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [proto for _, proto in scored[:top_k]]
