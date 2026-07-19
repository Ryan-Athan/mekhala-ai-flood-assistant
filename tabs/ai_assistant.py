from __future__ import annotations

import base64
import re
import time
import uuid
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

# Prefer the RAG/LLM engine if your project has it.
# Fallback to mock_ai so the page still runs in offline mode.
try:
    from utils.rag_llm_chatbot_engine import get_flood_assistant_response as _base_get_flood_assistant_response
except Exception:
    from utils.mock_ai import get_flood_assistant_response as _base_get_flood_assistant_response


AI_NAME = "Mekhala"
AI_DISPLAY_NAME = "Mekhala AI"
USER_ICON = "👤"
CHAT_ENGINE_VERSION = "mekhala_guarded_logo_chat_v6_15_lang"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "assets" / "mekhala_logo.png"

SCOPE_GUIDANCE_EN = (
    "I can help with flood causes, flood warning signs, emergency kits, evacuation, "
    "road safety, electricity safety, safe water, medical help, cleanup after flooding, "
    "and protecting your home. Please ask your question in more detail."
)

NAME_GUIDANCE_EN = (
    "My name is Mekhala and I can help with flood causes, flood warning signs, "
    "emergency kits, evacuation, road safety, electricity safety, safe water, "
    "medical help, cleanup after flooding, and protecting your home. "
    "Please ask your question in more detail."
)

# Hand-written important fallback translations.
# These are used for off-topic/name questions even if internet translation is unavailable.
SCOPE_GUIDANCE_BY_LANG: Dict[str, str] = {
    "en": SCOPE_GUIDANCE_EN,
    "my": (
        "ရေကြီးရခြင်းအကြောင်းရင်းများ၊ ရေကြီးမည့်သတိပေးလက္ခဏာများ၊ အရေးပေါ်ပစ္စည်းအိတ်၊ "
        "ဘေးလွတ်ရာရွှေ့ပြောင်းခြင်း၊ လမ်းဘေးကင်းရေး၊ လျှပ်စစ်ဘေးကင်းရေး၊ သန့်ရှင်းသောရေ၊ "
        "ဆေးဘက်ဆိုင်ရာအကူအညီ၊ ရေကြီးပြီးနောက် သန့်ရှင်းရေးလုပ်ခြင်းနှင့် အိမ်ကိုရေကြီးမှုမှကာကွယ်ခြင်းတို့ကို "
        "ကူညီပေးနိုင်ပါတယ်။ မေးခွန်းကို ပိုပြီးအသေးစိတ်မေးပေးပါ။"
    ),
    "th": (
        "ฉันสามารถช่วยเรื่องสาเหตุของน้ำท่วม สัญญาณเตือนน้ำท่วม ชุดอุปกรณ์ฉุกเฉิน "
        "การอพยพ ความปลอดภัยบนถนน ความปลอดภัยทางไฟฟ้า น้ำสะอาด ความช่วยเหลือทางการแพทย์ "
        "การทำความสะอาดหลังน้ำท่วม และการปกป้องบ้านของคุณได้ กรุณาถามคำถามให้ละเอียดมากขึ้น"
    ),
    "zh": (
        "我可以帮助解答洪水原因、洪水预警信号、应急包、疏散、道路安全、用电安全、"
        "安全饮水、医疗帮助、洪水后的清理以及保护房屋等问题。请更详细地提出你的问题。"
    ),
    "zh-CN": (
        "我可以帮助解答洪水原因、洪水预警信号、应急包、疏散、道路安全、用电安全、"
        "安全饮水、医疗帮助、洪水后的清理以及保护房屋等问题。请更详细地提出你的问题。"
    ),
    "hi": (
        "मैं बाढ़ के कारणों, बाढ़ चेतावनी संकेतों, आपातकालीन किट, निकासी, सड़क सुरक्षा, "
        "विद्युत सुरक्षा, सुरक्षित पानी, चिकित्सा सहायता, बाढ़ के बाद सफाई और घर की सुरक्षा में मदद कर सकता हूँ। "
        "कृपया अपना प्रश्न अधिक विस्तार से पूछें।"
    ),
    "bn": (
        "আমি বন্যার কারণ, বন্যার সতর্ক সংকেত, জরুরি কিট, সরিয়ে নেওয়া, সড়ক নিরাপত্তা, "
        "বিদ্যুৎ নিরাপত্তা, নিরাপদ পানি, চিকিৎসা সহায়তা, বন্যার পর পরিষ্কার-পরিচ্ছন্নতা এবং "
        "আপনার বাড়ি সুরক্ষার বিষয়ে সাহায্য করতে পারি। অনুগ্রহ করে আপনার প্রশ্নটি আরও বিস্তারিতভাবে করুন।"
    ),
    "id": (
        "Saya dapat membantu tentang penyebab banjir, tanda peringatan banjir, perlengkapan darurat, "
        "evakuasi, keselamatan jalan, keselamatan listrik, air bersih, bantuan medis, pembersihan setelah banjir, "
        "dan perlindungan rumah Anda. Silakan ajukan pertanyaan Anda dengan lebih rinci."
    ),
    "vi": (
        "Tôi có thể hỗ trợ về nguyên nhân gây lũ lụt, dấu hiệu cảnh báo lũ, bộ dụng cụ khẩn cấp, "
        "sơ tán, an toàn đường bộ, an toàn điện, nước sạch, hỗ trợ y tế, dọn dẹp sau lũ và bảo vệ ngôi nhà của bạn. "
        "Vui lòng đặt câu hỏi chi tiết hơn."
    ),
    "ja": (
        "洪水の原因、洪水の警告サイン、非常用持ち出し品、避難、道路の安全、電気の安全、"
        "安全な水、医療支援、洪水後の清掃、家を守る方法についてお手伝いできます。"
        "質問をもう少し詳しく入力してください。"
    ),
    "ko": (
        "저는 홍수 원인, 홍수 경고 신호, 비상용품, 대피, 도로 안전, 전기 안전, 안전한 물, "
        "의료 도움, 홍수 후 청소, 집 보호 방법에 대해 도와드릴 수 있습니다. 질문을 더 자세히 해 주세요."
    ),
    "fr": (
        "Je peux vous aider avec les causes des inondations, les signes d'alerte, les kits d'urgence, "
        "l'évacuation, la sécurité routière, la sécurité électrique, l'eau potable, l'aide médicale, "
        "le nettoyage après une inondation et la protection de votre maison. Veuillez poser votre question plus en détail."
    ),
    "es": (
        "Puedo ayudar con las causas de las inundaciones, las señales de advertencia, los kits de emergencia, "
        "la evacuación, la seguridad vial, la seguridad eléctrica, el agua segura, la ayuda médica, "
        "la limpieza después de una inundación y la protección de su hogar. Por favor, haga su pregunta con más detalle."
    ),
    "ar": (
        "يمكنني المساعدة في أسباب الفيضانات، علامات التحذير من الفيضانات، أدوات الطوارئ، الإخلاء، "
        "سلامة الطرق، السلامة الكهربائية، المياه الآمنة، المساعدة الطبية، التنظيف بعد الفيضانات، وحماية منزلك. "
        "يرجى طرح سؤالك بمزيد من التفاصيل."
    ),
    "de": (
        "Ich kann bei Ursachen von Überschwemmungen, Warnzeichen, Notfallausrüstung, Evakuierung, "
        "Verkehrssicherheit, elektrischer Sicherheit, sauberem Wasser, medizinischer Hilfe, Reinigung nach Überschwemmungen "
        "und dem Schutz Ihres Hauses helfen. Bitte stellen Sie Ihre Frage genauer."
    ),
    "ms": (
        "Saya boleh membantu tentang punca banjir, tanda amaran banjir, kit kecemasan, pemindahan, "
        "keselamatan jalan raya, keselamatan elektrik, air bersih, bantuan perubatan, pembersihan selepas banjir "
        "dan perlindungan rumah anda. Sila tanya soalan anda dengan lebih terperinci."
    ),
}

NAME_GUIDANCE_BY_LANG: Dict[str, str] = {
    "en": NAME_GUIDANCE_EN,
    "my": (
        "ကျွန်မနာမည်က Mekhala ပါ။ ရေကြီးရခြင်းအကြောင်းရင်းများ၊ ရေကြီးမည့်သတိပေးလက္ခဏာများ၊ "
        "အရေးပေါ်ပစ္စည်းအိတ်၊ ဘေးလွတ်ရာရွှေ့ပြောင်းခြင်း၊ လမ်းဘေးကင်းရေး၊ လျှပ်စစ်ဘေးကင်းရေး၊ "
        "သန့်ရှင်းသောရေ၊ ဆေးဘက်ဆိုင်ရာအကူအညီ၊ ရေကြီးပြီးနောက် သန့်ရှင်းရေးလုပ်ခြင်းနှင့် "
        "အိမ်ကိုရေကြီးမှုမှကာကွယ်ခြင်းတို့ကို ကူညီပေးနိုင်ပါတယ်။ မေးခွန်းကို ပိုပြီးအသေးစိတ်မေးပေးပါ။"
    ),
    "th": (
        "ฉันชื่อ Mekhala และฉันสามารถช่วยเรื่องสาเหตุของน้ำท่วม สัญญาณเตือนน้ำท่วม "
        "ชุดอุปกรณ์ฉุกเฉิน การอพยพ ความปลอดภัยบนถนน ความปลอดภัยทางไฟฟ้า น้ำสะอาด "
        "ความช่วยเหลือทางการแพทย์ การทำความสะอาดหลังน้ำท่วม และการปกป้องบ้านของคุณได้ "
        "กรุณาถามคำถามให้ละเอียดมากขึ้น"
    ),
    "zh": (
        "我的名字是 Mekhala。我可以帮助解答洪水原因、洪水预警信号、应急包、疏散、道路安全、"
        "用电安全、安全饮水、医疗帮助、洪水后的清理以及保护房屋等问题。请更详细地提出你的问题。"
    ),
    "zh-CN": (
        "我的名字是 Mekhala。我可以帮助解答洪水原因、洪水预警信号、应急包、疏散、道路安全、"
        "用电安全、安全饮水、医疗帮助、洪水后的清理以及保护房屋等问题。请更详细地提出你的问题。"
    ),
    "hi": (
        "मेरा नाम Mekhala है और मैं बाढ़ के कारणों, बाढ़ चेतावनी संकेतों, आपातकालीन किट, निकासी, "
        "सड़क सुरक्षा, विद्युत सुरक्षा, सुरक्षित पानी, चिकित्सा सहायता, बाढ़ के बाद सफाई और घर की सुरक्षा में मदद कर सकता हूँ। "
        "कृपया अपना प्रश्न अधिक विस्तार से पूछें।"
    ),
    "bn": (
        "আমার নাম Mekhala এবং আমি বন্যার কারণ, বন্যার সতর্ক সংকেত, জরুরি কিট, সরিয়ে নেওয়া, "
        "সড়ক নিরাপত্তা, বিদ্যুৎ নিরাপত্তা, নিরাপদ পানি, চিকিৎসা সহায়তা, বন্যার পর পরিষ্কার-পরিচ্ছন্নতা এবং "
        "আপনার বাড়ি সুরক্ষার বিষয়ে সাহায্য করতে পারি। অনুগ্রহ করে আপনার প্রশ্নটি আরও বিস্তারিতভাবে করুন।"
    ),
    "id": (
        "Nama saya Mekhala dan saya dapat membantu tentang penyebab banjir, tanda peringatan banjir, perlengkapan darurat, "
        "evakuasi, keselamatan jalan, keselamatan listrik, air bersih, bantuan medis, pembersihan setelah banjir, "
        "dan perlindungan rumah Anda. Silakan ajukan pertanyaan Anda dengan lebih rinci."
    ),
    "vi": (
        "Tên tôi là Mekhala và tôi có thể hỗ trợ về nguyên nhân gây lũ lụt, dấu hiệu cảnh báo lũ, bộ dụng cụ khẩn cấp, "
        "sơ tán, an toàn đường bộ, an toàn điện, nước sạch, hỗ trợ y tế, dọn dẹp sau lũ và bảo vệ ngôi nhà của bạn. "
        "Vui lòng đặt câu hỏi chi tiết hơn."
    ),
    "ja": (
        "私の名前はMekhalaです。洪水の原因、洪水の警告サイン、非常用持ち出し品、避難、道路の安全、"
        "電気の安全、安全な水、医療支援、洪水後の清掃、家を守る方法についてお手伝いできます。"
        "質問をもう少し詳しく入力してください。"
    ),
    "ko": (
        "제 이름은 Mekhala입니다. 저는 홍수 원인, 홍수 경고 신호, 비상용품, 대피, 도로 안전, "
        "전기 안전, 안전한 물, 의료 도움, 홍수 후 청소, 집 보호 방법에 대해 도와드릴 수 있습니다. "
        "질문을 더 자세히 해 주세요."
    ),
    "fr": (
        "Je m'appelle Mekhala et je peux vous aider avec les causes des inondations, les signes d'alerte, les kits d'urgence, "
        "l'évacuation, la sécurité routière, la sécurité électrique, l'eau potable, l'aide médicale, "
        "le nettoyage après une inondation et la protection de votre maison. Veuillez poser votre question plus en détail."
    ),
    "es": (
        "Me llamo Mekhala y puedo ayudar con las causas de las inundaciones, las señales de advertencia, los kits de emergencia, "
        "la evacuación, la seguridad vial, la seguridad eléctrica, el agua segura, la ayuda médica, "
        "la limpieza después de una inundación y la protección de su hogar. Por favor, haga su pregunta con más detalle."
    ),
    "ar": (
        "اسمي Mekhala ويمكنني المساعدة في أسباب الفيضانات، علامات التحذير من الفيضانات، أدوات الطوارئ، الإخلاء، "
        "سلامة الطرق، السلامة الكهربائية، المياه الآمنة، المساعدة الطبية، التنظيف بعد الفيضانات، وحماية منزلك. "
        "يرجى طرح سؤالك بمزيد من التفاصيل."
    ),
    "de": (
        "Mein Name ist Mekhala und ich kann bei Ursachen von Überschwemmungen, Warnzeichen, Notfallausrüstung, Evakuierung, "
        "Verkehrssicherheit, elektrischer Sicherheit, sauberem Wasser, medizinischer Hilfe, Reinigung nach Überschwemmungen "
        "und dem Schutz Ihres Hauses helfen. Bitte stellen Sie Ihre Frage genauer."
    ),
    "ms": (
        "Nama saya Mekhala dan saya boleh membantu tentang punca banjir, tanda amaran banjir, kit kecemasan, pemindahan, "
        "keselamatan jalan raya, keselamatan elektrik, air bersih, bantuan perubatan, pembersihan selepas banjir "
        "dan perlindungan rumah anda. Sila tanya soalan anda dengan lebih terperinci."
    ),
}

QUICK_PROMPTS = [
    "What should I do during a flood?",
    "What are flood warning signs?",
    "How to protect my home from floods?",
    "When should I evacuate?",
    "What to pack in an emergency kit?",
]


# ============================================================
# Language / guardrail helpers
# ============================================================

def _detect_language_simple(text: str) -> str:
    """Detect the user's language for 15-language Mekhala guardrails."""
    value = text.strip()
    lowered = value.lower()

    # Script-based detection first.
    if re.search(r"[\u0E00-\u0E7F]", value):
        return "th"
    if re.search(r"[\u1000-\u109F]", value):
        return "my"
    if re.search(r"[\u3040-\u30FF]", value):
        return "ja"
    if re.search(r"[\u4E00-\u9FFF]", value):
        return "zh-CN"
    if re.search(r"[\uAC00-\uD7AF]", value):
        return "ko"
    if re.search(r"[\u0600-\u06FF]", value):
        return "ar"
    if re.search(r"[\u0900-\u097F]", value):
        return "hi"
    if re.search(r"[\u0980-\u09FF]", value):
        return "bn"

    # Strong phrase hints for Latin-script languages.
    latin_hints = {
        "fr": [
            "quel est ton nom", "quel est votre nom", "ton nom", "votre nom",
            "qui es-tu", "qui êtes-vous", "inondation", "inondations",
            "pluie", "tempête", "évacuation", "urgence", "eau",
        ],
        "es": [
            "cómo te llamas", "como te llamas", "cuál es tu nombre", "cual es tu nombre",
            "tu nombre", "quién eres", "quien eres", "inundación", "inundaciones",
            "lluvia", "tormenta", "evacuación", "emergencia", "agua",
        ],
        "de": [
            "wie heißt du", "wie heisst du", "wie ist dein name", "dein name", "wer bist du",
            "überschwemmung", "ueberschwemmung", "hochwasser", "regen", "sturm",
            "evakuierung", "notfall", "wasser",
        ],
        "id": [
            "nama kamu", "nama anda", "siapa kamu", "banjir", "hujan", "badai",
            "evakuasi", "darurat", "jalan", "air",
        ],
        "vi": [
            "tên bạn", "ten ban", "bạn tên", "ban ten", "bạn là ai", "ban la ai",
            "lũ", "lụt", "mưa", "bão", "sơ tán", "khẩn cấp", "nước",
        ],
        "ms": [
            "nama awak", "nama anda", "siapa awak", "banjir", "hujan", "ribut",
            "pemindahan", "kecemasan", "jalan", "air",
        ],
        "en": [
            "what is your name", "what's your name", "your name", "who are you",
            "flood", "flooding", "rain", "storm", "evacuation", "emergency",
        ],
    }

    for lang, phrases in latin_hints.items():
        if any(phrase in lowered for phrase in phrases):
            return lang

    # langdetect fallback for other Latin-script questions.
    try:
        from langdetect import detect

        detected = detect(value)
        if detected in {"zh-cn", "zh-tw", "zh"}:
            return "zh-CN"
        if detected in {"en", "fr", "es", "de", "id", "vi", "ms", "ar", "hi", "bn", "th", "ja", "ko"}:
            return detected
    except Exception:
        pass

    return "en"


def _translate_text(text: str, target_lang: str) -> str:
    """Translate if deep-translator is available. Fallback safely to original text."""
    if not text or target_lang == "en":
        return text

    target_map = {
        "zh": "zh-CN",
        "zh-CN": "zh-CN",
        "my": "my",
        "th": "th",
        "hi": "hi",
        "bn": "bn",
        "id": "id",
        "vi": "vi",
        "ja": "ja",
        "ko": "ko",
        "fr": "fr",
        "es": "es",
        "ar": "ar",
        "de": "de",
        "ms": "ms",
    }

    try:
        from deep_translator import GoogleTranslator

        target = target_map.get(target_lang, target_lang)
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        return text


def _looks_mostly_english(text: str) -> bool:
    letters = re.findall(r"[A-Za-z]", text)
    non_ascii = re.findall(r"[^\x00-\x7F]", text)
    return len(letters) >= 12 and len(non_ascii) < 4


NAME_PATTERNS = [
    r"\bwhat\s+is\s+your\s+name\b",
    r"\bwhat's\s+your\s+name\b",
    r"\byour\s+name\b",
    r"\bwho\s+are\s+you\b",
    r"\btell\s+me\s+your\s+name\b",
    r"\bmay\s+i\s+know\s+your\s+name\b",

    # French
    r"\bquel\s+est\s+ton\s+nom\b",
    r"\bquel\s+est\s+votre\s+nom\b",
    r"\bton\s+nom\b",
    r"\bvotre\s+nom\b",
    r"\bqui\s+es\s+tu\b",
    r"\bqui\s+êtes\s+vous\b",
    r"\bqui\s+etes\s+vous\b",

    # Spanish
    r"\bc[oó]mo\s+te\s+llamas\b",
    r"\bcu[aá]l\s+es\s+tu\s+nombre\b",
    r"\btu\s+nombre\b",
    r"\bqui[eé]n\s+eres\b",

    # German
    r"\bwie\s+hei[ßs]t\s+du\b",
    r"\bwie\s+ist\s+dein\s+name\b",
    r"\bdein\s+name\b",
    r"\bwer\s+bist\s+du\b",

    # Indonesian / Malay / Vietnamese
    r"\bnama\s+kamu\b",
    r"\bnama\s+anda\b",
    r"\bnama\s+awak\b",
    r"\bsiapa\s+kamu\b",
    r"\bsiapa\s+awak\b",
    r"\bt[eê]n\s+b[aạ]n\b",
    r"\bb[aạ]n\s+t[eê]n\b",
    r"\bb[aạ]n\s+l[aà]\s+ai\b",
]

NAME_KEYWORDS_ANY_LANG = [
    # Burmese
    "နာမည်", "မင်းကဘယ်သူ", "မင်းဘယ်သူ", "သင်ကဘယ်သူ",
    # Thai
    "คุณชื่อ", "ชื่ออะไร", "คุณคือใคร", "เธอคือใคร",
    # Japanese
    "名前", "お名前", "あなたは誰", "君は誰",
    # Chinese
    "你是谁", "叫什么", "名字", "你的名字",
    # Korean
    "이름", "누구",
    # Hindi
    "आपका नाम", "तुम्हारा नाम", "आप कौन",
    # Bengali
    "আপনার নাম", "তোমার নাম", "আপনি কে",
    # Arabic
    "ما اسمك", "اسمك", "من أنت",
]

FLOOD_KEYWORDS = [
    # English
    "flood", "flooding", "flooded", "flash flood", "water level", "heavy rain", "rainfall",
    "storm", "monsoon", "cyclone", "typhoon", "hurricane", "river overflow", "drainage",
    "evacuate", "evacuation", "emergency kit", "safe water", "road safety", "electricity",
    "power line", "cleanup", "clean up", "sandbag", "levee", "dam", "sewage", "mudslide",
    # Burmese
    "ရေကြီး", "ရေမြုပ်", "ရေလွှမ်း", "မိုးကြီး", "မိုးရွာ", "မုန်တိုင်း", "ဘေးလွတ်ရာ",
    "ရွှေ့ပြောင်း", "အရေးပေါ်", "ရေသန့်", "လျှပ်စစ်", "လမ်း", "မြစ်ရေ", "ရေတက်",
    # Thai
    "น้ำท่วม", "ฝนตกหนัก", "ฝน", "พายุ", "ระดับน้ำ", "อพยพ", "ฉุกเฉิน", "น้ำสะอาด",
    "ไฟฟ้า", "ถนน", "แม่น้ำ", "เตือนภัย",
    # Chinese
    "洪水", "水灾", "暴雨", "撤离", "疏散", "预警", "积水", "河水", "应急",
    # Hindi
    "बाढ़", "बारिश", "तूफान", "निकासी", "आपातकाल", "बचाव", "सड़क", "पानी",
    # Bengali
    "বন্যা", "বৃষ্টি", "ঝড়", "সরিয়ে", "জরুরি", "উদ্ধার", "রাস্তা", "পানি",
    # Indonesian
    "banjir", "hujan", "badai", "evakuasi", "darurat", "penyelamatan", "jalan", "air",
    # Vietnamese
    "lũ", "lụt", "mưa", "bão", "sơ tán", "khẩn cấp", "cứu hộ", "đường", "nước",
    # Japanese
    "洪水", "浸水", "大雨", "避難", "台風", "河川", "氾濫", "警報", "水害", "非常用",
    # Korean
    "홍수", "침수", "폭우", "대피", "태풍", "경보", "비상",
    # French
    "inondation", "inondations", "pluie", "tempête", "evacuation", "évacuation", "urgence", "secours", "route", "eau",
    # Spanish
    "inundación", "inundacion", "inundaciones", "lluvia", "tormenta", "evacuación", "evacuacion", "emergencia", "rescate", "carretera", "agua",
    # Arabic
    "فيض", "فيضان", "فيضانات", "مطر", "عاصفة", "إخلاء", "طوارئ", "إنقاذ", "طريق", "ماء",
    # German
    "überschwemmung", "ueberschwemmung", "hochwasser", "regen", "sturm", "evakuierung", "notfall", "rettung", "straße", "strasse", "wasser",
    # Malay
    "banjir", "hujan", "ribut", "pemindahan", "kecemasan", "menyelamat", "jalan", "air",
]

def _is_name_question(text: str) -> bool:
    lowered = text.lower().strip()
    lowered_clean = re.sub(r"[؟?!.،,;:()\[\]{}\"']", " ", lowered)
    lowered_clean = re.sub(r"\s+", " ", lowered_clean)

    for pattern in NAME_PATTERNS:
        if re.search(pattern, lowered_clean):
            return True

    return any(keyword.lower() in lowered_clean or keyword in text for keyword in NAME_KEYWORDS_ANY_LANG)


def _is_flood_related(text: str) -> bool:
    lowered = text.lower()
    normalized = lowered.replace("_", " ").replace("-", " ")
    return any(keyword.lower() in normalized or keyword in text for keyword in FLOOD_KEYWORDS)


def _guardrail_response(user_message: str) -> Optional[Dict[str, str]]:
    language = _detect_language_simple(user_message)

    if _is_name_question(user_message):
        response = NAME_GUIDANCE_BY_LANG.get(language)
        if not response:
            response = _translate_text(NAME_GUIDANCE_EN, language)
        return {
            "response": response,
            "language": language,
            "source": "mekhala_guardrail_name",
        }

    if not _is_flood_related(user_message):
        response = SCOPE_GUIDANCE_BY_LANG.get(language)
        if not response:
            response = _translate_text(SCOPE_GUIDANCE_EN, language)
        return {
            "response": response,
            "language": language,
            "source": "mekhala_guardrail_scope",
        }

    return None


def _get_mekhala_response(user_message: str, history: List[Dict[str, str]]) -> Dict[str, str]:
    """Apply strict FloodMind/Mekhala scope before calling the base chatbot engine."""
    guard = _guardrail_response(user_message)
    if guard is not None:
        return guard

    language = _detect_language_simple(user_message)

    result = _base_get_flood_assistant_response(
        user_message=user_message,
        history=history,
    )

    if not isinstance(result, dict):
        result = {"response": str(result), "language": language, "source": "base_engine"}

    answer = str(result.get("response", "")).strip()
    if not answer:
        answer = SCOPE_GUIDANCE_BY_LANG.get(language, SCOPE_GUIDANCE_EN)

    # If base engine answers English to a non-English flood question, translate it back.
    if language != "en" and _looks_mostly_english(answer):
        translated = _translate_text(answer, language)
        if translated:
            answer = translated

    result["response"] = answer
    result["language"] = language
    result.setdefault("source", "base_engine")
    return result


# ============================================================
# HTML helpers
# ============================================================

def _safe(value: object) -> str:
    return escape(str(value))


def _html(markup: str) -> None:
    st.markdown(markup.strip(), unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def _logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""

    data = LOGO_PATH.read_bytes()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def _ai_avatar_html(hero: bool = False) -> str:
    logo_uri = _logo_data_uri()
    if logo_uri:
        if hero:
            return f'<div class="fm-logo-hero"><img src="{logo_uri}" alt="{AI_NAME} logo" /></div>'
        return f'<div class="fm-chat-avatar fm-ai-avatar"><img class="fm-logo-img" src="{logo_uri}" alt="{AI_NAME} logo" /></div>'

    # Fallback if logo file is missing.
    if hero:
        return '<div class="fm-assistant-bot">🤖</div>'
    return '<div class="fm-chat-avatar">🤖</div>'


def _user_avatar_html() -> str:
    return f'<div class="fm-chat-avatar fm-user-avatar">{USER_ICON}</div>'


# ============================================================
# CSS
# ============================================================

def _inject_chatbot_only_css() -> None:
    st.markdown(
        """
<style>
.block-container {
    max-width: 930px !important;
    min-height: 100dvh !important;
    padding-top: 0.8rem !important;
    padding-left: 2.05rem !important;
    padding-right: 1.7rem !important;
    padding-bottom: 0.75rem !important;
    overflow: visible !important;
    box-sizing: border-box !important;
}

/* ===============================
   EMPTY INTRO SCREEN
================================ */
.fm-assistant-empty {
    width: 100%;
    max-width: 780px;
    margin: 68px auto 0 auto;
    text-align: center;
}

.fm-assistant-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 30px;
}

.fm-logo-hero {
    width: 92px;
    height: 92px;
    border-radius: 28px;
    padding: 9px;
    margin-bottom: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.82);
    box-shadow:
        0 18px 38px rgba(0, 49, 82, 0.14),
        inset 0 1px 0 rgba(255, 255, 255, 0.86);

    backdrop-filter: blur(20px) saturate(185%);
    -webkit-backdrop-filter: blur(20px) saturate(185%);
}

.fm-logo-hero img {
    width: 76px;
    height: 76px;
    object-fit: contain;
    display: block;
    border-radius: 20px;
}

.fm-assistant-bot {
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
    font-size: 46px;
    line-height: 1;
    margin-bottom: 12px;
    color: #003152;
    filter: drop-shadow(0 8px 18px rgba(0, 49, 82, 0.10));
}

.fm-assistant-title {
    margin: 0 0 8px 0;
    color: #003152;
    font-size: 24px;
    font-weight: 950;
    letter-spacing: -0.45px;
    line-height: 1.15;
}

.fm-assistant-subtitle {
    max-width: 610px;
    margin: 0 auto;
    color: rgba(0, 49, 82, 0.68);
    font-size: 13px;
    font-weight: 720;
    line-height: 1.6;
}

/* ===============================
   COMPACT CHAT HISTORY
================================ */
.fm-chat-active {
    width: 100%;
    max-width: 760px;
    height: 430px;
    max-height: 430px;
    margin: 0 auto 0 auto;

    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.fm-chat-history {
    width: 100%;
    height: 430px;
    max-height: 430px;
    overflow-y: auto;
    overflow-x: hidden;

    display: flex;
    flex-direction: column-reverse;
    gap: 14px;

    padding: 4px 8px 8px 8px;
    margin: 0;
    scroll-behavior: smooth;
}

.fm-chat-history::-webkit-scrollbar {
    width: 7px;
}

.fm-chat-history::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.12);
    border-radius: 999px;
}

.fm-chat-history::-webkit-scrollbar-thumb {
    background: rgba(0, 49, 82, 0.22);
    border-radius: 999px;
}

.fm-chat-turn {
    width: 100%;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.fm-chat-user-turn {
    justify-content: flex-end;
}

.fm-chat-ai-turn {
    justify-content: flex-start;
}

.fm-chat-avatar {
    width: 42px;
    height: 42px;
    min-width: 42px;
    border-radius: 50%;

    display: flex;
    align-items: center;
    justify-content: center;

    color: #003152;
    font-family: "Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", sans-serif;
    font-size: 18px;
    font-weight: 950;

    background: rgba(250, 250, 250, 0.76);
    border: 1px solid rgba(255, 255, 255, 0.66);
    box-shadow: 0 9px 22px rgba(0, 49, 82, 0.08);

    backdrop-filter: blur(18px) saturate(180%);
    -webkit-backdrop-filter: blur(18px) saturate(180%);
}

.fm-ai-avatar {
    width: 48px;
    height: 48px;
    min-width: 48px;
    padding: 5px;
    background: rgba(255, 255, 255, 0.86);
    border: 1px solid rgba(255, 255, 255, 0.9);
    box-shadow:
        0 12px 26px rgba(0, 49, 82, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.88);
}

.fm-logo-img {
    width: 38px;
    height: 38px;
    object-fit: contain;
    display: block;
    border-radius: 50%;
}

.fm-user-avatar {
    background: rgba(250, 250, 250, 0.72);
}

.fm-chat-content {
    max-width: 82%;
    text-align: left;
}

.fm-chat-name {
    margin-bottom: 6px;
    color: rgba(0, 49, 82, 0.62);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.2px;
}

.fm-chat-bubble {
    padding: 14px 17px;
    border-radius: 18px;

    color: #003152;
    font-size: 13.5px;
    line-height: 1.65;
    font-weight: 720;

    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: 0 12px 28px rgba(0, 49, 82, 0.055);
}

.fm-user-bubble {
    background: rgba(250, 250, 250, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.76);
    border-bottom-right-radius: 7px;
}

.fm-ai-bubble {
    background: rgba(91, 210, 246, 0.52);
    border: 1px solid rgba(255, 255, 255, 0.42);
    border-bottom-left-radius: 7px;

    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
}

/* ===============================
   LIVE THINKING / TYPING AREA
================================ */
.fm-live-response-zone {
    width: 100%;
    max-width: 760px;
    min-height: 58px;
    margin: 0 auto 6px auto;
}

.fm-thinking-row {
    width: 100%;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.fm-thinking-text {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    color: rgba(0, 49, 82, 0.68);
    font-size: 13px;
    font-weight: 850;
    padding-top: 8px;
}

.fm-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(0, 49, 82, 0.58);
    animation: fmPulse 1.2s infinite ease-in-out;
}

.fm-dot:nth-child(2) { animation-delay: 0.18s; }
.fm-dot:nth-child(3) { animation-delay: 0.36s; }

@keyframes fmPulse {
    0%, 80%, 100% { opacity: 0.25; transform: translateY(0); }
    40% { opacity: 1; transform: translateY(-4px); }
}

.fm-typing-cursor {
    display: inline-block;
    width: 8px;
    color: #003152;
    font-weight: 950;
    animation: fmBlink 0.9s infinite;
}

@keyframes fmBlink {
    0%, 45% { opacity: 1; }
    46%, 100% { opacity: 0; }
}

/* ===============================
   INPUT BAR
================================ */
.fm-chat-input-holder {
    width: 100%;
    max-width: 760px;
    height: 0;
    margin: 0 auto 0 auto;
    padding: 0;
    background: transparent;
}

div[data-testid="stForm"] {
    width: 100% !important;
    max-width: 760px !important;
    margin: 0 auto 12px auto !important;
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

div[data-testid="stForm"] > div {
    border: none !important;
    padding: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
}

div[data-testid="InputInstructions"],
div[data-testid="stTextInput"] div[data-testid="InputInstructions"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
    width: 100% !important;
    align-items: center !important;
    gap: 14px !important;
}

div[data-testid="stForm"] div[data-testid="column"] {
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] {
    width: 100% !important;
    margin: 0 !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] div[data-baseweb="input"] {
    height: 52px !important;
    min-height: 52px !important;
    border-radius: 999px !important;

    background: rgba(255, 255, 255, 0.34) !important;
    border: 1px solid rgba(255, 255, 255, 0.82) !important;

    box-shadow:
        0 16px 34px rgba(0, 49, 82, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.62) !important;

    outline: none !important;

    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    background: rgba(255, 255, 255, 0.58) !important;
    border: 1px solid rgba(255, 255, 255, 0.96) !important;

    box-shadow:
        0 18px 40px rgba(0, 49, 82, 0.12),
        0 0 0 3px rgba(255, 255, 255, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.75) !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] input {
    height: 52px !important;
    min-height: 52px !important;

    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;

    color: #003152 !important;
    font-size: 14px !important;
    font-weight: 720 !important;

    padding: 0 24px !important;
}

div[data-testid="stForm"] div[data-testid="stTextInput"] input::placeholder {
    color: rgba(0, 49, 82, 0.46) !important;
    font-weight: 720 !important;
}

div[data-testid="stFormSubmitButton"] {
    width: 54px !important;
    min-width: 54px !important;
    margin: 0 !important;
}

div[data-testid="stFormSubmitButton"] button {
    width: 54px !important;
    min-width: 54px !important;
    height: 54px !important;
    min-height: 54px !important;

    padding: 0 !important;
    margin: 0 !important;

    border-radius: 999px !important;
    background: rgba(250, 250, 250, 0.97) !important;
    border: 1px solid rgba(255, 255, 255, 0.86) !important;

    color: #003152 !important;
    font-size: 20px !important;
    font-weight: 950 !important;
    line-height: 1 !important;

    box-shadow:
        0 14px 28px rgba(0, 49, 82, 0.10),
        inset 0 1px 0 rgba(255, 255, 255, 0.68) !important;

    transition: all 0.18s ease !important;
}

div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px) scale(1.03);
    background: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.98) !important;
}

div[data-testid="stFormSubmitButton"] button:active {
    transform: scale(0.97);
}

/* QUICK PROMPT BUTTONS */
.stButton > button {
    min-height: 42px !important;
    border-radius: 999px !important;
    background: rgba(255, 255, 255, 0.20) !important;
    border: 1px solid rgba(255, 255, 255, 0.36) !important;

    backdrop-filter: blur(18px) saturate(170%) !important;
    -webkit-backdrop-filter: blur(18px) saturate(170%) !important;

    color: rgba(255, 255, 255, 0.94) !important;
    font-size: 12px !important;
    font-weight: 760 !important;

    box-shadow: 0 9px 22px rgba(0, 49, 82, 0.045) !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
    background: rgba(255, 255, 255, 0.30) !important;
    border-color: rgba(255, 255, 255, 0.56) !important;
}

/* ===============================
   RESPONSIVE
================================ */
@media (max-width: 992px) {
    .block-container {
        min-height: 100dvh !important;
        overflow: visible !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 0.75rem !important;
    }

    .fm-assistant-empty {
        max-width: 100%;
        margin: 42px auto 0 auto;
    }

    .fm-logo-hero {
        width: 82px;
        height: 82px;
        border-radius: 24px;
        margin-bottom: 14px;
    }

    .fm-logo-hero img {
        width: 68px;
        height: 68px;
    }

    .fm-chat-active {
        max-width: 100%;
        height: 380px;
        max-height: 380px;
        margin: 0 auto 0 auto;
        justify-content: flex-end;
    }

    .fm-chat-history {
        height: 380px;
        max-height: 380px;
        gap: 12px;
        padding: 4px 6px 6px 6px;
    }

    .fm-live-response-zone {
        max-width: 100%;
        min-height: 54px;
        margin: 0 auto 6px auto;
    }

    .fm-chat-content {
        max-width: 88%;
    }

    .fm-assistant-title {
        font-size: 22px;
    }

    .fm-assistant-subtitle {
        font-size: 12px;
    }

    .fm-chat-input-holder,
    div[data-testid="stForm"] {
        max-width: 100% !important;
    }

    div[data-testid="stForm"] {
        margin: 0 auto 10px auto !important;
    }
}
</style>
        """.strip(),
        unsafe_allow_html=True,
    )


# ============================================================
# State / rendering
# ============================================================

def _ensure_chat_state() -> None:
    if st.session_state.get("chat_engine_version") != CHAT_ENGINE_VERSION:
        st.session_state.chat_messages = []
        st.session_state.chat_engine_version = CHAT_ENGINE_VERSION
        st.session_state.pending_user_message = None
        st.session_state.pending_user_message_id = None

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    if "pending_user_message" not in st.session_state:
        st.session_state.pending_user_message = None

    if "pending_user_message_id" not in st.session_state:
        st.session_state.pending_user_message_id = None


def _queue_message(message: str) -> None:
    cleaned = message.strip()

    if not cleaned:
        return

    if st.session_state.pending_user_message:
        return

    message_id = uuid.uuid4().hex

    st.session_state.chat_messages.append(
        {
            "id": message_id,
            "role": "user",
            "content": cleaned,
        }
    )

    st.session_state.pending_user_message = cleaned
    st.session_state.pending_user_message_id = message_id


def _assistant_turn_html(content: str, with_cursor: bool = False) -> str:
    cursor = '<span class="fm-typing-cursor">|</span>' if with_cursor else ""

    return (
        '<div class="fm-thinking-row">'
        f'{_ai_avatar_html()}'
        '<div class="fm-chat-content">'
        f'<div class="fm-chat-name">{AI_DISPLAY_NAME}</div>'
        f'<div class="fm-chat-bubble fm-ai-bubble">{_safe(content)}{cursor}</div>'
        '</div>'
        '</div>'
    )


def _thinking_html() -> str:
    return (
        '<div class="fm-thinking-row">'
        f'{_ai_avatar_html()}'
        '<div class="fm-chat-content">'
        f'<div class="fm-chat-name">{AI_DISPLAY_NAME}</div>'
        '<div class="fm-thinking-text">'
        f'<span>{AI_DISPLAY_NAME} is thinking</span>'
        '<span class="fm-dot"></span>'
        '<span class="fm-dot"></span>'
        '<span class="fm-dot"></span>'
        '</div>'
        '</div>'
        '</div>'
    )


def _process_pending_message(live_placeholder) -> None:
    pending_message = st.session_state.pending_user_message
    pending_id = st.session_state.pending_user_message_id

    if not pending_message or not pending_id:
        return

    live_placeholder.markdown(
        f'<div class="fm-live-response-zone">{_thinking_html()}</div>',
        unsafe_allow_html=True,
    )

    history_before_pending = [
        message
        for message in st.session_state.chat_messages
        if message.get("id") != pending_id
    ]

    result = _get_mekhala_response(
        user_message=pending_message,
        history=history_before_pending,
    )

    answer = result.get("response", "I could not generate a response. Please try again.").strip()

    if not answer:
        answer = "I could not generate a response. Please try again."

    typed_text = ""
    chunk_size = 3

    for index in range(0, len(answer), chunk_size):
        typed_text += answer[index : index + chunk_size]

        live_placeholder.markdown(
            f'<div class="fm-live-response-zone">{_assistant_turn_html(typed_text, with_cursor=True)}</div>',
            unsafe_allow_html=True,
        )

        time.sleep(0.012)

    live_placeholder.markdown(
        f'<div class="fm-live-response-zone">{_assistant_turn_html(answer, with_cursor=False)}</div>',
        unsafe_allow_html=True,
    )

    time.sleep(0.25)

    st.session_state.chat_messages.append(
        {
            "id": uuid.uuid4().hex,
            "role": "assistant",
            "content": answer,
            "language": result.get("language", "en"),
            "source": result.get("source", "mekhala"),
        }
    )

    st.session_state.pending_user_message = None
    st.session_state.pending_user_message_id = None
    st.rerun()


def _render_empty_intro() -> None:
    _html(
        f"""
        <div class="fm-assistant-empty">
            <div class="fm-assistant-hero">
                {_ai_avatar_html(hero=True)}
                <h1 class="fm-assistant-title">Welcome to {AI_DISPLAY_NAME} Flood Assistant</h1>
                <p class="fm-assistant-subtitle">
                    Ask me anything about floods, flood prevention, flood preparedness,
                    emergency response, flood safety, or flood risk assessment.
                </p>
            </div>
        </div>
        """
    )


def _render_input_area() -> None:
    is_busy = bool(st.session_state.pending_user_message)

    _html('<div class="fm-chat-input-holder"></div>')

    with st.form(key="assistant_chat_form", clear_on_submit=True):
        input_col, send_col = st.columns([12, 0.85], gap="small")

        with input_col:
            user_message = st.text_input(
                label=f"Ask {AI_DISPLAY_NAME}",
                placeholder="Ask me anything about floods",
                label_visibility="collapsed",
                key="assistant_input_value",
                disabled=is_busy,
            )

        with send_col:
            submitted = st.form_submit_button(
                "➤",
                use_container_width=True,
                disabled=is_busy,
            )

    if submitted and user_message.strip() and not is_busy:
        _queue_message(user_message)
        st.rerun()


def _render_quick_prompts() -> None:
    if st.session_state.pending_user_message:
        return

    top_cols = st.columns(3, gap="small")

    for index, prompt in enumerate(QUICK_PROMPTS[:3]):
        with top_cols[index]:
            if st.button(prompt, key=f"quick_prompt_top_{index}", use_container_width=True):
                _queue_message(prompt)
                st.rerun()

    left_space, center_area, right_space = st.columns([1, 1.45, 1], gap="small")

    with center_area:
        bottom_col_1, bottom_col_2 = st.columns(2, gap="small")

        with bottom_col_1:
            if st.button(QUICK_PROMPTS[3], key="quick_prompt_bottom_1", use_container_width=True):
                _queue_message(QUICK_PROMPTS[3])
                st.rerun()

        with bottom_col_2:
            if st.button(QUICK_PROMPTS[4], key="quick_prompt_bottom_2", use_container_width=True):
                _queue_message(QUICK_PROMPTS[4])
                st.rerun()


def _render_chat_history() -> None:
    rows = ""
    recent_messages = list(reversed(st.session_state.chat_messages[-30:]))

    for message in recent_messages:
        content = _safe(message.get("content", ""))

        if message.get("role") == "user":
            rows += (
                '<div class="fm-chat-turn fm-chat-user-turn">'
                '<div class="fm-chat-content">'
                '<div class="fm-chat-name" style="text-align:right;">You</div>'
                f'<div class="fm-chat-bubble fm-user-bubble">{content}</div>'
                '</div>'
                f'{_user_avatar_html()}'
                '</div>'
            )
        else:
            rows += (
                '<div class="fm-chat-turn fm-chat-ai-turn">'
                f'{_ai_avatar_html()}'
                '<div class="fm-chat-content">'
                f'<div class="fm-chat-name">{AI_DISPLAY_NAME}</div>'
                f'<div class="fm-chat-bubble fm-ai-bubble">{content}</div>'
                '</div>'
                '</div>'
            )

    _html(
        f"""
        <div class="fm-chat-active">
            <div class="fm-chat-history">
                {rows}
            </div>
        </div>
        """
    )


def render_ai_assistant() -> None:
    _ensure_chat_state()
    _inject_chatbot_only_css()

    has_messages = len(st.session_state.chat_messages) > 0

    if has_messages:
        _render_chat_history()
        live_response_placeholder = st.empty()
        _render_input_area()
        _process_pending_message(live_response_placeholder)
    else:
        _render_empty_intro()
        live_response_placeholder = st.empty()
        _render_input_area()
        _render_quick_prompts()
        _process_pending_message(live_response_placeholder)
