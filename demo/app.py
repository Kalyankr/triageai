"""TriageAI — Gradio Demo App for HuggingFace Space."""

import json
import os
import re
import sys
from pathlib import Path

import gradio as gr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TRIAGE_COLORS = {
    "RED": {"bg": "#FFEBEE", "border": "#CC0000", "label": "IMMEDIATE", "emoji": "🔴", "description": "Life-threatening — needs immediate intervention"},
    "YELLOW": {"bg": "#FFFDE7", "border": "#F9A825", "label": "DELAYED", "emoji": "🟡", "description": "Serious but can wait — monitor closely"},
    "GREEN": {"bg": "#E8F5E9", "border": "#2E7D32", "label": "MINOR", "emoji": "🟢", "description": "Walking wounded — minimal intervention needed"},
    "BLACK": {"bg": "#ECEFF1", "border": "#455A64", "label": "EXPECTANT", "emoji": "⚫", "description": "Beyond current help — comfort care only"},
}

KNOWLEDGE_BASE = {
    "medical_injury": {
        "title": "Injury Management",
        "steps": [
            "Ensure your own safety before approaching",
            "Apply direct pressure to any bleeding wounds with clean cloth",
            "If bleeding won't stop on a limb, apply tourniquet 2-3 inches above wound",
            "Immobilize suspected fractures — do not try to realign bones",
            "Monitor breathing and pulse continuously",
            "Keep the person warm with a blanket or coat",
            "Talk to them calmly and reassure them help is coming",
        ],
        "do_not": [
            "Do NOT remove objects embedded in wounds",
            "Do NOT remove blood-soaked bandages — add more on top",
            "Do NOT move someone with suspected spinal injury",
            "Do NOT give food or water if surgery may be needed",
        ],
    },
    "medical_illness": {
        "title": "Medical Emergency",
        "steps": [
            "Check responsiveness — tap shoulders and shout 'Are you okay?'",
            "If unresponsive, check breathing for 10 seconds",
            "If not breathing: begin CPR — 30 chest compressions, 2 breaths",
            "Push hard and fast in center of chest, at least 2 inches deep",
            "If they're breathing but unconscious, place in recovery position",
            "For chest pain: have them sit upright, loosen tight clothing",
            "For seizure: clear area of hazards, protect head, time the seizure",
        ],
        "do_not": [
            "Do NOT put anything in the mouth of a seizing person",
            "Do NOT move an unconscious person unless in immediate danger",
            "Do NOT stop CPR until professional help arrives",
            "Do NOT give aspirin if allergic or if stroke is suspected",
        ],
    },
    "fire": {
        "title": "Fire Emergency",
        "steps": [
            "Alert everyone — shout 'FIRE!' and activate alarms",
            "Evacuate immediately — do not stop to collect belongings",
            "Stay low to avoid smoke — crawl if necessary",
            "Feel doors before opening — if hot, find another exit",
            "If clothes catch fire: STOP, DROP, and ROLL",
            "Once outside, move to designated meeting point",
            "Call emergency services — report location and trapped people",
        ],
        "do_not": [
            "Do NOT use elevators during a fire",
            "Do NOT re-enter a burning building",
            "Do NOT open windows if smoke is entering from outside",
            "Do NOT try to fight a large fire with an extinguisher",
        ],
    },
    "flood": {
        "title": "Flood Emergency",
        "steps": [
            "Move to higher ground immediately",
            "Avoid walking in moving water — 6 inches can knock you down",
            "Do not drive through flooded roads — 12 inches can float a car",
            "If trapped in a vehicle, get on the roof if water is rising",
            "Avoid contact with floodwater — it may contain sewage or chemicals",
            "After flooding, check for structural damage before entering buildings",
            "Discard any food that has been in contact with floodwater",
        ],
        "do_not": [
            "Do NOT walk through moving floodwater",
            "Do NOT drive through flooded roads — 'Turn Around, Don't Drown'",
            "Do NOT touch electrical equipment if wet or standing in water",
            "Do NOT drink floodwater or use it for cooking",
        ],
    },
    "earthquake": {
        "title": "Earthquake Response",
        "steps": [
            "DROP to your hands and knees",
            "Take COVER under a sturdy desk or table",
            "HOLD ON until shaking stops",
            "If outdoors, move away from buildings, power lines, trees",
            "After shaking stops, check yourself and others for injuries",
            "Be prepared for aftershocks",
            "Check for gas leaks — if you smell gas, open windows and leave",
        ],
        "do_not": [
            "Do NOT stand in doorways — this is outdated advice",
            "Do NOT run outside during shaking",
            "Do NOT use elevators after an earthquake",
            "Do NOT light matches if you smell gas",
        ],
    },
    "vehicle_accident": {
        "title": "Vehicle Accident Response",
        "steps": [
            "Ensure scene safety — turn on hazard lights, set up warning triangles",
            "Turn off ignitions of involved vehicles if safe to do so",
            "Check all occupants for injuries, starting with unresponsive ones",
            "Call emergency services with exact location",
            "Control bleeding with direct pressure",
            "Do not remove helmets from motorcyclists unless not breathing",
            "Keep injured people still and warm until help arrives",
        ],
        "do_not": [
            "Do NOT move injured people unless there's immediate danger (fire/explosion)",
            "Do NOT remove someone from a vehicle if spinal injury is suspected",
            "Do NOT approach if there's a fuel leak and fire risk",
            "Do NOT crowd the scene — keep bystanders back",
        ],
    },
    "chemical_hazard": {
        "title": "Chemical Hazard Response",
        "steps": [
            "Move upwind and uphill from the chemical source",
            "Remove contaminated clothing immediately",
            "Flush affected skin with large amounts of water for 20+ minutes",
            "For eye exposure, flush eyes with clean water for 15+ minutes",
            "Ventilate enclosed areas — open all windows and doors",
            "Identify the chemical if possible — check labels and safety sheets",
            "Isolate the area and warn others",
        ],
        "do_not": [
            "Do NOT induce vomiting if chemical was swallowed",
            "Do NOT use neutralizing agents on skin burns",
            "Do NOT touch contaminated surfaces without protection",
            "Do NOT re-enter contaminated area until cleared",
        ],
    },
    "drowning": {
        "title": "Drowning Response",
        "steps": [
            "Call for help immediately — do not enter water unless trained",
            "Reach with a pole, rope, or branch if victim is close to shore",
            "Throw a flotation device if available",
            "If person is out of water and not breathing, begin rescue breaths",
            "Give 5 initial rescue breaths, then start CPR if no pulse",
            "Place unconscious but breathing person in recovery position",
            "Remove wet clothing and keep warm to prevent hypothermia",
        ],
        "do_not": [
            "Do NOT enter water unless you are a trained swimmer and it's safe",
            "Do NOT perform abdominal thrusts to expel water",
            "Do NOT assume someone is fine after a near-drowning — monitor for hours",
            "Do NOT leave a near-drowning victim alone",
        ],
    },
}

EMERGENCY_NUMBERS = {
    "English": "911 (US/Canada) / 112 (Europe) / 999 (UK)",
    "Spanish": "112 (Spain/Europe) / 911 (Americas)",
    "Hindi": "112 (India)",
    "Arabic": "999 / 997 (Middle East)",
    "French": "15 / 112 (France/Europe)",
    "Portuguese": "192 / 112 (Brazil/Portugal)",
    "Chinese": "120 (China)",
    "Auto-detect": "Call your local emergency number",
}

MODEL_LOADED = False
model = None
processor = None

TRANSLATIONS = {
    "Spanish": {
        "call":    "📞 LLAME AL 112 / 911",
        "do_now":  "⚡ ACCIONES INMEDIATAS",
        "do_not":  "🚫 NO HACER",
        "image":   "📷 Imagen recibida. Análisis visual completo disponible en modo GPU.",
        "steps": {
            "medical_injury": [
                "Asegure su propia seguridad antes de acercarse",
                "Aplique presión directa sobre heridas sangrantes con paño limpio",
                "Si sangrado no para en un miembro, aplique torniquete 5–7 cm sobre la herida",
                "Inmovilice fracturas — NO intente realinear huesos",
                "Mantenga a la persona abrigada y tranquila hasta que llegue ayuda",
            ],
            "medical_illness": [
                "Verifique respuesta — golpee hombros y pregunte '¿Estás bien?'",
                "Si no responde, verifique respiración 10 segundos",
                "Si no respira: RCP — 30 compresiones al centro del pecho (5 cm), 2 respiraciones",
                "Si respira pero inconsciente: posición de recuperación",
            ],
            "earthquake": [
                "AGÁCHESE en manos y rodillas",
                "CÚBRASE bajo una mesa resistente o junto a una pared interior",
                "SUJÉTESE hasta que pare el temblor",
                "Revise lesiones en usted y los demás",
                "Prepárese para réplicas",
            ],
            "vehicle_accident": [
                "Señalice la escena — luces de emergencia, triángulos",
                "Llame emergencias con ubicación exacta",
                "Controle hemorragias con presión directa",
                "NO mueva heridos salvo peligro inmediato (fuego/explosión)",
            ],
            "drowning": [
                "NO entre al agua salvo que sea nadador entrenado",
                "Extienda un palo, cuerda o rama si la víctima está cerca",
                "Si está fuera del agua y no respira: 5 respiraciones de rescate, luego RCP",
                "Quite ropa mojada y abrigue para prevenir hipotermia",
            ],
            "fire": [
                "Alerte a todos — grite '¡FUEGO!' y active alarmas",
                "Evacúe inmediatamente — no recoja pertenencias",
                "Manténgase bajo para evitar humo — arrástrece si es necesario",
                "Una vez fuera, muévase al punto de encuentro designado",
            ],
        },
        "do_nots": {
            "medical_injury": [
                "NO retire objetos clavados en heridas",
                "NO retire vendajes empapados — añada más encima",
                "NO mueva a alguien con posible lesión en la columna",
                "NO dé agua a persona inconsciente",
            ],
            "medical_illness": [
                "NO ponga nada en la boca de alguien que convulsiona",
                "NO mueva a persona inconsciente salvo peligro inmediato",
                "NO detenga la RCP hasta que llegue ayuda profesional",
            ],
        },
    },
    "Hindi": {
        "call":    "📞 112 पर कॉल करें",
        "do_now":  "⚡ तत्काल कार्रवाई",
        "do_not":  "🚫 ये न करें",
        "image":   "📷 छवि प्राप्त हुई। पूर्ण दृश्य विश्लेषण GPU मोड में उपलब्ध है।",
        "steps": {
            "medical_injury": [
                "पास जाने से पहले अपनी सुरक्षा सुनिश्चित करें",
                "साफ कपड़े से खून बहने वाले घाव पर सीधा दबाव डालें",
                "अगर हाथ-पैर से खून न रुके तो घाव से 5–7 सेमी ऊपर टूर्निकेट लगाएं",
                "संदिग्ध फ्रैक्चर को स्थिर करें — हड्डियाँ सीधी करने की कोशिश न करें",
                "व्यक्ति को गर्म रखें जब तक मदद न आए",
            ],
            "medical_illness": [
                "प्रतिक्रिया जांचें — कंधे थपथपाएं, पूछें 'क्या आप ठीक हैं?'",
                "बेहोश हो तो 10 सेकंड तक सांस जांचें",
                "सांस नहीं तो CPR: 30 बार छाती दबाएं (5 सेमी गहरा), 2 सांसें दें",
                "सांस है पर बेहोश है तो रिकवरी पोजीशन में रखें",
            ],
            "earthquake": [
                "झुकें — हाथों और घुटनों पर",
                "मजबूत मेज के नीचे या अंदरूनी दीवार के पास ढकें",
                "कंपन रुकने तक पकड़े रहें",
                "बाद में खुद और दूसरों की चोटें जांचें",
            ],
            "vehicle_accident": [
                "दृश्य सुरक्षित करें — हजार्ड लाइट चालू करें",
                "सटीक स्थान के साथ आपातकालीन सेवाओं को कॉल करें",
                "सीधे दबाव से खून रोकें",
                "घायलों को तब तक न हिलाएं जब तक तत्काल खतरा न हो",
            ],
            "drowning": [
                "प्रशिक्षित तैराक न हों तो पानी में न उतरें",
                "डंडा, रस्सी या शाखा बढ़ाएं अगर पीड़ित पास हो",
                "पानी से बाहर हो और सांस न हो: 5 रेस्क्यू सांसें, फिर CPR",
                "गीले कपड़े हटाएं, हाइपोथर्मिया से बचाने के लिए गर्म रखें",
            ],
        },
        "do_nots": {
            "medical_injury": [
                "घाव में फंसी वस्तु न निकालें",
                "खून से भीगी पट्टी न हटाएं — ऊपर से और लगाएं",
                "रीढ़ की हड्डी की संदिग्ध चोट में न हिलाएं",
                "बेहोश को पानी न दें",
            ],
            "medical_illness": [
                "दौरे के दौरान मुंह में कुछ न डालें",
                "बेहोश व्यक्ति को तब तक न हिलाएं जब तक खतरा न हो",
                "CPR तब तक बंद न करें जब तक पेशेवर मदद न आए",
            ],
        },
    },
    "Arabic": {
        "call":    "📞 اتصل بـ 911 / 112",
        "do_now":  "⚡ الإجراءات الفورية",
        "do_not":  "🚫 لا تفعل",
        "image":   "📷 تم استلام الصورة. التحليل البصري الكامل متاح في وضع GPU.",
        "steps": {
            "medical_injury": [
                "تأكد من سلامتك قبل الاقتراب",
                "اضغط مباشرة على الجروح النازفة بقماش نظيف",
                "إذا استمر النزيف في طرف: ضع عاصبة 5-7 سم فوق الجرح",
                "ثبّت الكسور المشتبهة — لا تحاول إعادة تصويب العظام",
                "حافظ على دفء المصاب حتى وصول المساعدة",
            ],
            "medical_illness": [
                "تحقق من الاستجابة — انقر على الكتفين وقل 'هل أنت بخير؟'",
                "إذا لم يستجب، تحقق من التنفس لمدة 10 ثوانٍ",
                "إذا لم يتنفس: إنعاش القلب والرئة — 30 ضغطة على الصدر، نفسان",
            ],
        },
        "do_nots": {
            "medical_injury": [
                "لا تزل الأجسام المغروسة في الجروح",
                "لا تحرك شخصاً يشتبه في إصابته بالعمود الفقري",
                "لا تعطِ ماء لشخص فاقد الوعي",
            ],
        },
    },
    "French": {
        "call":    "📞 Appelez le 15 / 112",
        "do_now":  "⚡ ACTIONS IMMÉDIATES",
        "do_not":  "🚫 NE PAS FAIRE",
        "image":   "📷 Image reçue. Analyse visuelle complète disponible en mode GPU.",
        "steps": {
            "medical_injury": [
                "Assurez votre propre sécurité avant d'approcher",
                "Appuyez directement sur les plaies qui saignent avec un tissu propre",
                "Si le saignement ne s'arrête pas sur un membre, appliquez un garrot 5–7 cm au-dessus",
                "Immobilisez les fractures — ne tentez pas de réaligner les os",
                "Gardez la personne au chaud jusqu'à l'arrivée des secours",
            ],
            "medical_illness": [
                "Vérifiez la réactivité — tapez sur les épaules, demandez 'Vous m'entendez ?'",
                "Si inconscient, vérifiez la respiration 10 secondes",
                "Si pas de respiration: RCP — 30 compressions, 2 insufflations",
                "Si respire mais inconscient: position latérale de sécurité",
            ],
            "earthquake": [
                "BAISSEZ-VOUS à genoux et mains",
                "PROTÉGEZ-VOUS sous un bureau solide",
                "TENEZ-VOUS jusqu'à l'arrêt des secousses",
                "Vérifiez les blessures sur vous et les autres",
            ],
        },
        "do_nots": {
            "medical_injury": [
                "Ne retirez PAS les objets plantés dans les blessures",
                "Ne déplacez PAS quelqu'un avec une blessure rachidienne suspectée",
                "Ne donnez PAS d'eau à une personne inconsciente",
            ],
        },
    },
}


def detect_language_from_text(text: str) -> str:
    """Auto-detect language from input text."""
    hindi = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    arabic = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    if hindi > 2:
        return "Hindi"
    if arabic > 2:
        return "Arabic"
    spanish = ['terremoto', 'sangre', 'herida', 'ayuda', 'dolor', 'accidente',
               'mujer', 'hombre', 'niño', 'fuego', 'inundación', 'está']
    if any(w in text.lower() for w in spanish) or any(c in text for c in 'áéíóúñ¿¡'):
        return "Spanish"
    french = ['blessé', 'secours', 'accident', 'incendie', 'noyade', 'tremblement']
    if any(w in text.lower() for w in french) or any(c in text for c in 'àâçèêëîïôùûüÿœæ'):
        return "French"
    return "English"




def load_model():
    """Load Gemma 4 if available, otherwise use offline mode."""
    global MODEL_LOADED, model, processor
    try:
        import torch
        from transformers import AutoProcessor, AutoModelForImageTextToText, BitsAndBytesConfig

        model_id = os.environ.get("TRIAGEAI_MODEL", "google/gemma-4-4b-it")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForImageTextToText.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            torch_dtype=torch.bfloat16,
        )
        MODEL_LOADED = True
    except Exception as e:
        print(f"Model not available ({e}). Running in offline/demo mode.")
        MODEL_LOADED = False


def classify_emergency_offline(text: str) -> tuple[str, bool]:
    """Simple keyword-based classification for offline mode."""
    text_lower = text.lower()
    patterns = {
        "drowning": ["drown", "water", "pool", "submerg", "river", "lake", "swim"],
        "fire": ["fire", "flame", "smoke", "burning", "blaze"],
        "earthquake": ["earthquake", "tremor", "rubble", "terremoto", "shaking", "collapse"],
        "flood": ["flood", "water level", "inundación", "rising water"],
        "vehicle_accident": ["car", "vehicle", "crash", "collision", "accident", "traffic", "highway"],
        "chemical_hazard": ["chemical", "toxic", "spill", "fume", "sodium", "acid", "hazmat"],
        "electrical_hazard": ["electric", "shock", "power line", "wire", "electr"],
        "medical_illness": ["heart", "chest pain", "breathing", "stroke", "seizure", "unconscious", "unresponsive", "cardiac", "CPR", "सीने", "दर्द", "सांस"],
        "medical_injury": ["bleeding", "blood", "cut", "wound", "fracture", "broken", "burn", "laceration", "sangre", "herida"],
    }
    for etype, keywords in patterns.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                scene_hazards = any(h in text_lower for h in ["fire", "gas", "electric", "chemical", "wire", "gasoline"])
                return etype, not scene_hazards
    return "unknown", True


def assess_severity_offline(emergency_type: str, text: str) -> tuple[str, str]:
    """Rule-based severity assessment."""
    text_lower = text.lower()
    red_signals = [
        "not breathing", "no pulse", "unconscious", "unresponsive", "arterial",
        "spurting", "trapped", "cardiac arrest", "on fire", "sinking",
        "blue", "choking", "not moving", "nहीं", "no responde",
    ]
    yellow_signals = [
        "pain", "bleeding", "fracture", "broken", "burn", "confused",
        "dizzy", "vomiting", "moderate", "dolor", "दर्द",
    ]
    for signal in red_signals:
        if signal in text_lower:
            return "RED", f"Detected life-threatening indicator: '{signal}'. Immediate intervention needed."
    for signal in yellow_signals:
        if signal in text_lower:
            return "YELLOW", f"Detected serious indicator: '{signal}'. Needs attention but can wait briefly."
    return "GREEN", "No immediately life-threatening indicators detected. Monitor and provide basic care."


def run_triage_offline(text: str, language: str, image=None) -> dict:
    """Run triage using offline rule-based engine."""
    emergency_type, scene_safe = classify_emergency_offline(text)
    triage_color, reasoning = assess_severity_offline(emergency_type, text)

    kb_key = emergency_type if emergency_type in KNOWLEDGE_BASE else "medical_injury"
    protocol = KNOWLEDGE_BASE.get(kb_key, KNOWLEDGE_BASE["medical_injury"])

    # Auto-detect language if not explicitly set
    effective_lang = language
    if language == "Auto-detect":
        effective_lang = detect_language_from_text(text)

    emergency_num = EMERGENCY_NUMBERS.get(effective_lang, EMERGENCY_NUMBERS.get(language, EMERGENCY_NUMBERS["Auto-detect"]))

    # Get translated steps if available
    trans = TRANSLATIONS.get(effective_lang)
    translated_protocol = None
    if trans:
        t_steps = trans.get("steps", {}).get(kb_key) or trans.get("steps", {}).get("medical_injury")
        t_donots = trans.get("do_nots", {}).get(kb_key) or trans.get("do_nots", {}).get("medical_injury")
        if t_steps:
            translated_protocol = {
                "title": protocol.get("title", ""),
                "steps": t_steps,
                "do_not": t_donots or protocol.get("do_not", []),
                "call_label": trans.get("call", ""),
                "do_now_label": trans.get("do_now", "⚡ IMMEDIATE ACTIONS"),
                "do_not_label": trans.get("do_not_label", trans.get("do_not", "🚫 DO NOT")),
            }

    # Image acknowledgment
    image_note = None
    if image is not None:
        if trans:
            image_note = trans.get("image")
        else:
            image_note = "📷 Image received — full visual analysis of wounds, injuries and scene hazards available in GPU deployment mode."

    return {
        "emergency_type": emergency_type,
        "triage_color": triage_color,
        "reasoning": reasoning,
        "scene_safe": scene_safe,
        "protocol": translated_protocol or protocol,
        "emergency_number": emergency_num,
        "model_mode": "offline",
        "effective_language": effective_lang,
        "image_note": image_note,
    }


def run_triage_with_model(text: str, image, language: str) -> dict:
    """Run triage using loaded Gemma 4 model."""
    import torch
    from PIL import Image as PILImage

    # image is now a filepath string (from gr.Image type="filepath")
    pil_image = None
    if image is not None:
        try:
            pil_image = PILImage.open(image).convert("RGB")
        except Exception:
            pil_image = None

    tools_text = """You have access to these emergency triage tools. Call them by outputting JSON in ```tool_call``` blocks:

1. classify_emergency: Classify the emergency type
2. assess_severity: Perform START triage (RED/YELLOW/GREEN/BLACK)
3. generate_action_plan: Create step-by-step emergency guidance

Example:
```tool_call
{"name": "classify_emergency", "arguments": {"emergency_type": "medical_injury", "scene_safe": true}}
```"""

    system_prompt = f"""You are TriageAI, an emergency triage AI. Follow START triage protocol.
{tools_text}

RULES: Prioritize safety. Include DO NOT warnings. Be direct and actionable."""

    user_msg = text
    if language != "Auto-detect":
        user_msg += f"\n\nRespond in {language}."
    user_msg += "\n\nClassify the emergency, assess severity (RED/YELLOW/GREEN/BLACK), and provide an action plan with DO NOT warnings."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_msg},
    ]

    prompt = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    if pil_image is not None:
        inputs = processor(text=prompt, images=[pil_image], return_tensors="pt").to(model.device)
    else:
        inputs = processor(text=prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        output_ids = model.generate(**inputs, max_new_tokens=1024, do_sample=True, temperature=0.3)

    new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
    response = processor.decode(new_tokens, skip_special_tokens=True)

    offline_result = run_triage_offline(text, language)
    offline_result["model_response"] = response
    offline_result["model_mode"] = "gemma4"

    color_map = {"RED": "RED", "YELLOW": "YELLOW", "GREEN": "GREEN", "BLACK": "BLACK"}
    for color in color_map:
        if color in response.upper():
            offline_result["triage_color"] = color
            break

    offline_result["reasoning"] = response[:500]

    return offline_result


def render_output(result: dict) -> tuple[str, str, str]:
    """Render triage result into HTML card, actions text, and thinking trace."""
    color = result["triage_color"]
    c = TRIAGE_COLORS.get(color, TRIAGE_COLORS["YELLOW"])
    etype = result["emergency_type"].replace("_", " ").title()
    reasoning = result["reasoning"]
    protocol = result.get("protocol", {})
    emergency_num = result.get("emergency_number", "")

    steps_html = ""
    do_now_label = protocol.get("do_now_label", "⚡ DO NOW")
    do_not_label = protocol.get("do_not_label", "🚫 DO NOT")
    if protocol.get("steps"):
        items = "".join(f"<li style='color:#111111 !important;margin:4px 0;'>→ {s}</li>" for s in protocol["steps"])
        steps_html = f"""
        <div style="background:#FFF0F0 !important;border:1px solid #FF6B6B;border-radius:8px;padding:15px;margin:10px 0;">
          <h3 style="margin:0 0 8px;color:#B71C1C !important;">{do_now_label}</h3>
          <ul style="margin:5px 0;padding-left:20px;color:#111111 !important;">{items}</ul>
        </div>"""

    image_html = ""
    image_note = result.get("image_note")
    if image_note:
        image_html = f"""
        <div style="background:#E3F2FD !important;border:1px solid #1565C0;border-radius:8px;padding:12px 15px;margin:10px 0;color:#0D47A1 !important;">
          {image_note}
        </div>"""

    donot_html = ""
    if protocol.get("do_not"):
        items = "".join(f"<li style='color:#ffffff !important;margin:4px 0;'>✖ {s}</li>" for s in protocol["do_not"])
        donot_html = f"""
        <div style="background:#2D3436 !important;border-radius:8px;padding:15px;margin:10px 0;">
          <h3 style="margin:0 0 8px;color:#FF7675 !important;">{do_not_label}</h3>
          <ul style="margin:5px 0;padding-left:20px;color:#ffffff !important;">{items}</ul>
        </div>"""

    card_html = f"""
    <div style="font-family:system-ui,sans-serif;max-width:700px;background:#ffffff !important;border-radius:12px;padding:6px;">
      <div style="background:#FFF8E1 !important;border:2px solid #F9A825;border-radius:6px;padding:10px 15px;margin-bottom:12px;font-size:13px;">
        <span style="color:#5D4037 !important;">⚠️ <strong style="color:#5D4037 !important;">Not a substitute for professional medical care.</strong> Call emergency services immediately.</span>
        <br><span style="color:#B71C1C !important;font-weight:bold;font-size:15px;">📞 Emergency: {emergency_num}</span>
      </div>
      <div style="background:{c['bg']} !important;border-left:8px solid {c['border']};border-radius:8px;padding:20px;margin-bottom:12px;">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <span style="font-size:36px;">{c['emoji']}</span>
          <div>
            <h2 style="margin:0;color:{c['border']} !important;">{c['label']} — {color}</h2>
            <p style="margin:2px 0;font-size:15px;color:#333333 !important;">{c['description']}</p>
          </div>
        </div>
        <p style="margin:6px 0;color:#111111 !important;"><strong style="color:#111111 !important;">Emergency Type:</strong> <span style="color:#111111 !important;">{etype}</span></p>
        <p style="margin:6px 0;color:#111111 !important;"><strong style="color:#111111 !important;">Scene Safe:</strong> <span style="color:#111111 !important;">{"Yes ✅" if result.get("scene_safe", True) else "NO ⚠️ — ensure your safety first"}</span></p>
        <p style="margin:6px 0;color:#111111 !important;"><strong style="color:#111111 !important;">Assessment:</strong> <span style="color:#111111 !important;">{reasoning[:300]}</span></p>
      </div>
      {image_html}
      {steps_html}
      {donot_html}
      <div style="text-align:center;font-size:11px;color:#888888 !important;margin-top:10px;">
        Mode: {result.get('model_mode', 'offline')} · Powered by Gemma 4 · TriageAI
      </div>
    </div>"""

    actions_text = ""
    if protocol.get("steps"):
        actions_text += "⚡ IMMEDIATE ACTIONS:\n"
        for s in protocol["steps"]:
            actions_text += f"  → {s}\n"
        actions_text += "\n"
    if protocol.get("do_not"):
        actions_text += "🚫 DO NOT:\n"
        for s in protocol["do_not"]:
            actions_text += f"  ✖ {s}\n"

    thinking = result.get("model_response", result.get("reasoning", ""))

    return card_html, actions_text, thinking


def triage(text: str, image, language: str) -> tuple[str, str, str]:
    """Main triage function called by Gradio."""
    try:
        if not text and image is None:
            return "<p style='color:#555;padding:20px;'>Please provide a description of the emergency or upload a photo.</p>", "", ""

        if MODEL_LOADED:
            result = run_triage_with_model(text, image, language)
        else:
            result = run_triage_offline(text, language, image=image)

        return render_output(result)
    except Exception as e:
        error_html = f"""
        <div style="background:#FFF0F0;border:2px solid #FF0000;border-radius:8px;padding:20px;font-family:system-ui;">
          <h3 style="color:#CC0000;">⚠️ Triage Error</h3>
          <p style="color:#333;">{str(e)}</p>
          <p style="color:#666;font-size:13px;">Please try again or use one of the Quick Scenario buttons.</p>
        </div>"""
        return error_html, f"Error: {str(e)}", ""


QUICK_SCENARIOS = {
    "Severe Bleeding": "My friend fell on broken glass and has a deep cut on his forearm. There's a lot of blood spurting out and he's getting pale. We're at a construction site.",
    "Not Breathing": "My father collapsed clutching his chest. He's not breathing and his face is turning blue. I'm alone with him. Please help!",
    "Burn Injury": "A worker spilled industrial cleaner on his arms and chest. The skin is red and blistering. The bottle says 'sodium hydroxide'.",
    "Earthquake": "There was a strong earthquake. My neighbor is trapped under rubble, I can see her arm but she's not responding. There are fallen electrical wires nearby.",
    "Car Accident": "Multi-car pileup on the highway. One car is on fire. People trapped. One person walking with head bleeding. Another lying on the road not moving. I smell gasoline.",
    "Drowning": "A child fell into the pool and was underwater for about 2 minutes. We pulled him out but he's not breathing and his lips are blue.",
}


def fill_scenario(scenario_name: str) -> str:
    return QUICK_SCENARIOS.get(scenario_name, "")


CSS = """
.gradio-container { max-width: 1200px !important; }
.disclaimer { background: #FFF3CD; border: 1px solid #FFEAA7; border-radius: 6px;
              padding: 12px 16px; margin-bottom: 16px; color: #856404; font-size: 14px; }
footer { display: none !important; }
"""

with gr.Blocks(css=CSS, title="TriageAI — Emergency Triage", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align:center;padding:20px 0 10px;">
      <h1 style="margin:0;color:#d32f2f;">🚨 TriageAI</h1>
      <p style="font-size:18px;color:#444;margin:5px 0;">
        Offline Multilingual Emergency Triage · Powered by Gemma 4
      </p>
      <p style="font-size:14px;color:#666;">
        When every second counts and networks are down.
      </p>
    </div>
    """)

    gr.HTML("""<div style="background:#FFF8E1;border:2px solid #F9A825;border-radius:8px;padding:12px 16px;margin:8px 0;color:#333333;font-size:14px;">
      ⚠️ <strong style="color:#E65100;">MEDICAL DISCLAIMER:</strong>
      <span style="color:#333333;">TriageAI is an AI assistant and
      <strong style="color:#E65100;">NOT a substitute for professional medical care.</strong>
      Always call emergency services for life-threatening situations.
      This tool provides general first-aid guidance based on established protocols.</span>
    </div>""")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### Input")
            language = gr.Dropdown(
                choices=["Auto-detect", "English", "Spanish", "Hindi", "Arabic", "French", "Portuguese", "Chinese"],
                value="Auto-detect",
                label="Language",
            )
            image = gr.Image(label="Upload Emergency Photo (optional)", type="filepath")
            text = gr.Textbox(
                label="Describe the Emergency",
                placeholder="E.g., 'My friend cut his arm on broken glass and is bleeding heavily...'",
                lines=4,
            )

            gr.Markdown("**Quick Scenarios (click to fill):**")
            with gr.Row():
                for name in list(QUICK_SCENARIOS.keys())[:3]:
                    gr.Button(name, size="sm").click(
                        fn=lambda n=name: fill_scenario(n), outputs=text, api_name=False
                    )
            with gr.Row():
                for name in list(QUICK_SCENARIOS.keys())[3:]:
                    gr.Button(name, size="sm").click(
                        fn=lambda n=name: fill_scenario(n), outputs=text, api_name=False
                    )

            submit_btn = gr.Button("🚨 TRIAGE NOW", variant="primary", size="lg")

        with gr.Column(scale=1):
            gr.Markdown("### Triage Result")
            triage_card = gr.HTML(label="Triage Card")
            with gr.Accordion("📋 Action Plan (text)", open=False):
                actions_output = gr.Textbox(label="Actions", lines=15, interactive=False)
            with gr.Accordion("🧠 AI Reasoning", open=False):
                thinking_output = gr.Textbox(label="Thinking Trace", lines=10, interactive=False)

    submit_btn.click(
        fn=triage,
        inputs=[text, image, language],
        outputs=[triage_card, actions_output, thinking_output],
        api_name=False,
    )

    gr.HTML("""
    <div style="text-align:center;padding:20px;font-size:12px;color:#999;">
      TriageAI · Gemma 4 Good Hackathon 2026 · Function Calling + Thinking Mode + Multimodal Vision
      <br>Built for Global Resilience & Health
    </div>
    """)


# HuggingFace free tier: always offline mode (no GPU/model).
# load_model() intentionally NOT called at startup — offline rule-based engine handles everything.
print("TriageAI running in offline demo mode.")

demo.queue()  # Required for HF Spaces API to work

if __name__ == "__main__":
    demo.launch(show_api=False)
