TRIAGE_COLORS = {
    "RED": {
        "bg": "#FF000020",
        "border": "#FF0000",
        "label": "IMMEDIATE",
        "emoji": "🔴",
        "description": "Life-threatening — needs immediate intervention",
    },
    "YELLOW": {
        "bg": "#FFD70020",
        "border": "#FFD700",
        "label": "DELAYED",
        "emoji": "🟡",
        "description": "Serious but can wait — monitor closely",
    },
    "GREEN": {
        "bg": "#00AA0020",
        "border": "#00AA00",
        "label": "MINOR",
        "emoji": "🟢",
        "description": "Walking wounded — minimal intervention needed",
    },
    "BLACK": {
        "bg": "#33333320",
        "border": "#333333",
        "label": "EXPECTANT",
        "emoji": "⚫",
        "description": "Beyond current help — comfort care only",
    },
}


def render_triage_card_html(
    color: str,
    emergency_type: str,
    reasoning: str,
    actions: dict | None = None,
    language_info: dict | None = None,
) -> str:
    """Render a color-coded HTML triage card."""
    c = TRIAGE_COLORS.get(color, TRIAGE_COLORS["YELLOW"])

    emergency_label = emergency_type.replace("_", " ").title()

    actions = actions or {}
    immediate = actions.get("immediate_actions", [])
    follow_up = actions.get("follow_up_actions", [])
    do_not = actions.get("do_not_actions", [])
    monitoring = actions.get("monitoring_signs", [])
    dispatcher = actions.get("dispatcher_script", "")
    escalation = actions.get("escalation_criteria", "")

    emergency_num = ""
    if language_info:
        emergency_num = language_info.get("local_emergency_number", "")

    def _list_html(items, icon=""):
        if not items:
            return ""
        li = "".join(f"<li>{icon} {item}</li>" for item in items)
        return f"<ul style='margin:5px 0;padding-left:20px;'>{li}</ul>"

    html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:700px;margin:10px auto;">

      <!-- DISCLAIMER -->
      <div style="background:#FFF3CD;border:1px solid #FFEAA7;border-radius:6px;
                  padding:10px 15px;margin-bottom:12px;font-size:13px;color:#856404;">
        ⚠️ <strong>Not a substitute for professional medical care.</strong>
        Call emergency services immediately for life-threatening situations.
        {f'<br>📞 Emergency: <strong>{emergency_num}</strong>' if emergency_num else ''}
      </div>

      <!-- TRIAGE CARD -->
      <div style="background:{c['bg']};border-left:8px solid {c['border']};
                  border-radius:8px;padding:20px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <span style="font-size:36px;">{c['emoji']}</span>
          <div>
            <h2 style="margin:0;color:{c['border']};">{c['label']} — {color}</h2>
            <p style="margin:2px 0;font-size:15px;color:#555;">
              {c['description']}
            </p>
          </div>
        </div>
        <p style="margin:5px 0;"><strong>Emergency Type:</strong> {emergency_label}</p>
        <p style="margin:5px 0;"><strong>Assessment:</strong> {reasoning}</p>
      </div>

      <!-- IMMEDIATE ACTIONS -->
      {f'''
      <div style="background:#FFF0F0;border:1px solid #FF6B6B;border-radius:8px;
                  padding:15px;margin-bottom:10px;">
        <h3 style="margin:0 0 8px 0;color:#D63031;">⚡ DO NOW (first 60 seconds)</h3>
        {_list_html(immediate, "→")}
      </div>
      ''' if immediate else ''}

      <!-- DO NOT -->
      {f'''
      <div style="background:#2D3436;color:#FFF;border-radius:8px;
                  padding:15px;margin-bottom:10px;">
        <h3 style="margin:0 0 8px 0;color:#FF7675;">🚫 DO NOT</h3>
        {_list_html(do_not, "✖")}
      </div>
      ''' if do_not else ''}

      <!-- FOLLOW UP -->
      {f'''
      <div style="background:#F8F9FA;border:1px solid #DDD;border-radius:8px;
                  padding:15px;margin-bottom:10px;">
        <h3 style="margin:0 0 8px 0;color:#2D3436;">📋 Next Steps (5-15 minutes)</h3>
        {_list_html(follow_up, "•")}
      </div>
      ''' if follow_up else ''}

      <!-- MONITORING -->
      {f'''
      <div style="background:#F8F9FA;border:1px solid #DDD;border-radius:8px;
                  padding:15px;margin-bottom:10px;">
        <h3 style="margin:0 0 8px 0;color:#2D3436;">👁️ Watch For</h3>
        {_list_html(monitoring, "⚠")}
      </div>
      ''' if monitoring else ''}

      <!-- DISPATCHER SCRIPT -->
      {f'''
      <div style="background:#E8F4FD;border:1px solid #74B9FF;border-radius:8px;
                  padding:15px;margin-bottom:10px;">
        <h3 style="margin:0 0 8px 0;color:#0984E3;">📞 Tell Emergency Dispatcher</h3>
        <p style="margin:5px 0;font-style:italic;">"{dispatcher}"</p>
      </div>
      ''' if dispatcher else ''}

      <!-- ESCALATION -->
      {f'''
      <div style="background:#FFEAA7;border-radius:8px;padding:12px;
                  margin-bottom:10px;font-size:14px;">
        <strong>⬆️ Escalate if:</strong> {escalation}
      </div>
      ''' if escalation else ''}

      <div style="text-align:center;font-size:11px;color:#999;margin-top:10px;">
        Powered by Gemma 4 · TriageAI · Function Calling + Thinking Mode + Multimodal
      </div>
    </div>
    """
    return html


def render_triage_card_text(
    color: str,
    emergency_type: str,
    reasoning: str,
    actions: dict | None = None,
) -> str:
    """Render a plain-text triage card for notebook display."""
    c = TRIAGE_COLORS.get(color, TRIAGE_COLORS["YELLOW"])
    actions = actions or {}

    lines = [
        f"{'='*60}",
        f"  {c['emoji']} TRIAGE: {c['label']} — {color}",
        f"  {c['description']}",
        f"{'='*60}",
        f"  Type: {emergency_type.replace('_', ' ').title()}",
        f"  Reasoning: {reasoning}",
        "",
    ]

    if actions.get("immediate_actions"):
        lines.append("  ⚡ DO NOW:")
        for a in actions["immediate_actions"]:
            lines.append(f"    → {a}")
        lines.append("")

    if actions.get("do_not_actions"):
        lines.append("  🚫 DO NOT:")
        for a in actions["do_not_actions"]:
            lines.append(f"    ✖ {a}")
        lines.append("")

    if actions.get("follow_up_actions"):
        lines.append("  📋 NEXT STEPS:")
        for a in actions["follow_up_actions"]:
            lines.append(f"    • {a}")
        lines.append("")

    if actions.get("monitoring_signs"):
        lines.append("  👁️ WATCH FOR:")
        for a in actions["monitoring_signs"]:
            lines.append(f"    ⚠ {a}")
        lines.append("")

    if actions.get("dispatcher_script"):
        lines.append(f"  📞 TELL DISPATCHER: \"{actions['dispatcher_script']}\"")
        lines.append("")

    lines.append(f"{'='*60}")
    return "\n".join(lines)
