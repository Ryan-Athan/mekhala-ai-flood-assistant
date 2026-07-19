from __future__ import annotations

import re
from typing import Optional


SUPPORTED_LANGUAGES = [
    "en",
    "my",
    "th",
    "zh-CN",
    "hi",
    "bn",
    "id",
    "vi",
    "ja",
    "ko",
    "fr",
    "es",
    "ar",
    "de",
    "ms",
]


HELP_RESPONSES = {
    "en": "I can help with flood causes, flood warning signs, emergency kits, evacuation, road safety, electricity safety, safe water, medical help, cleanup after flooding, and protecting your home. Please ask your question in more detail.",
    "my": "ကျွန်ုပ်သည် ရေကြီးရခြင်းအကြောင်းရင်းများ၊ ရေကြီးမည့် သတိပေးလက္ခဏာများ၊ အရေးပေါ်ကိရိယာများ၊ ပြောင်းရွှေ့နေထိုင်ခြင်း၊ လမ်းအန္တရာယ်ကင်းရှင်းရေး၊ လျှပ်စစ်အန္တရာယ်ကင်းရှင်းရေး၊ သောက်သုံးရေသန့်၊ ဆေးဘက်ဆိုင်ရာအကူအညီ၊ ရေကြီးပြီးနောက် သန့်ရှင်းရေးနှင့် အိမ်ကိုကာကွယ်ခြင်းတို့အတွက် ကူညီနိုင်ပါသည်။ မေးခွန်းကို ပိုမိုအသေးစိတ် မေးပါ။",
    "th": "ฉันสามารถช่วยเรื่องสาเหตุของน้ำท่วม สัญญาณเตือนภัยน้ำท่วม ชุดอุปกรณ์ฉุกเฉิน การอพยพ ความปลอดภัยบนถนน ความปลอดภัยด้านไฟฟ้า น้ำสะอาด ความช่วยเหลือทางการแพทย์ การทำความสะอาดหลังน้ำท่วม และการปกป้องบ้านของคุณ กรุณาถามคำถามให้ละเอียดมากขึ้น",
    "zh-CN": "我可以帮助解答洪水成因、洪水预警信号、应急包、疏散、道路安全、电力安全、安全饮水、医疗帮助、洪水后的清理以及保护家庭等问题。请更详细地提出您的问题。",
    "hi": "मैं बाढ़ के कारणों, बाढ़ चेतावनी संकेतों, आपातकालीन किट, निकासी, सड़क सुरक्षा, विद्युत सुरक्षा, सुरक्षित पानी, चिकित्सा सहायता, बाढ़ के बाद सफाई और घर की सुरक्षा में मदद कर सकता हूँ। कृपया अपना प्रश्न अधिक विस्तार से पूछें।",
    "bn": "আমি বন্যার কারণ, বন্যার সতর্ক সংকেত, জরুরি কিট, সরিয়ে নেওয়া, সড়ক নিরাপত্তা, বিদ্যুৎ নিরাপত্তা, নিরাপদ পানি, চিকিৎসা সহায়তা, বন্যার পর পরিষ্কার-পরিচ্ছন্নতা এবং আপনার বাড়ি সুরক্ষার বিষয়ে সাহায্য করতে পারি। অনুগ্রহ করে আপনার প্রশ্নটি আরও বিস্তারিতভাবে করুন।",
    "id": "Saya dapat membantu tentang penyebab banjir, tanda peringatan banjir, perlengkapan darurat, evakuasi, keselamatan jalan, keselamatan listrik, air bersih, bantuan medis, pembersihan setelah banjir, dan perlindungan rumah Anda. Silakan ajukan pertanyaan Anda dengan lebih rinci.",
    "vi": "Tôi có thể hỗ trợ về nguyên nhân gây lũ lụt, dấu hiệu cảnh báo lũ, bộ dụng cụ khẩn cấp, sơ tán, an toàn đường bộ, an toàn điện, nước sạch, hỗ trợ y tế, dọn dẹp sau lũ và bảo vệ ngôi nhà của bạn. Vui lòng đặt câu hỏi chi tiết hơn.",
    "ja": "洪水の原因、洪水の警告サイン、非常用キット、避難、道路の安全、電気の安全、安全な水、医療支援、洪水後の清掃、家の保護についてお手伝いできます。質問をもう少し詳しくしてください。",
    "ko": "저는 홍수 원인, 홍수 경고 신호, 비상 키트, 대피, 도로 안전, 전기 안전, 안전한 물, 의료 지원, 홍수 후 청소, 집 보호에 대해 도와드릴 수 있습니다. 질문을 더 자세히 해 주세요.",
    "fr": "Je peux vous aider avec les causes des inondations, les signes d'alerte, les kits d'urgence, l'évacuation, la sécurité routière, la sécurité électrique, l'eau potable, l'aide médicale, le nettoyage après une inondation et la protection de votre maison. Veuillez poser votre question plus en détail.",
    "es": "Puedo ayudar con las causas de las inundaciones, las señales de advertencia, los kits de emergencia, la evacuación, la seguridad vial, la seguridad eléctrica, el agua segura, la ayuda médica, la limpieza después de una inundación y la protección de su hogar. Por favor, haga su pregunta con más detalle.",
    "ar": "يمكنني المساعدة في أسباب الفيضانات، علامات التحذير من الفيضانات، أدوات الطوارئ، الإخلاء، سلامة الطرق، السلامة الكهربائية، المياه الآمنة، المساعدة الطبية، التنظيف بعد الفيضانات، وحماية منزلك. يرجى طرح سؤالك بمزيد من التفاصيل.",
    "de": "Ich kann bei Ursachen von Überschwemmungen, Warnzeichen, Notfallausrüstung, Evakuierung, Verkehrssicherheit, elektrischer Sicherheit, sauberem Wasser, medizinischer Hilfe, Reinigung nach Überschwemmungen und dem Schutz Ihres Hauses helfen. Bitte stellen Sie Ihre Frage genauer.",
    "ms": "Saya boleh membantu tentang punca banjir, tanda amaran banjir, kit kecemasan, pemindahan, keselamatan jalan raya, keselamatan elektrik, air bersih, bantuan perubatan, pembersihan selepas banjir dan perlindungan rumah anda. Sila tanya soalan anda dengan lebih terperinci.",
}


NAME_RESPONSES = {
    "en": "My name is Mekhala and I can help with flood causes, flood warning signs, emergency kits, evacuation, road safety, electricity safety, safe water, medical help, cleanup after flooding, and protecting your home. Please ask your question in more detail.",
    "my": "ကျွန်ုပ်နာမည်က မေခလာ ဖြစ်ပါသည်။ ကျွန်ုပ်သည် ရေကြီးရခြင်းအကြောင်းရင်းများ၊ ရေကြီးမည့် သတိပေးလက္ခဏာများ၊ အရေးပေါ်ကိရိယာများ၊ ပြောင်းရွှေ့နေထိုင်ခြင်း၊ လမ်းအန္တရာယ်ကင်းရှင်းရေး၊ လျှပ်စစ်အန္တရာယ်ကင်းရှင်းရေး၊ သောက်သုံးရေသန့်၊ ဆေးဘက်ဆိုင်ရာအကူအညီ၊ ရေကြီးပြီးနောက် သန့်ရှင်းရေးနှင့် အိမ်ကိုကာကွယ်ခြင်းတို့အတွက် ကူညီနိုင်ပါသည်။ မေးခွန်းကို ပိုမိုအသေးစိတ် မေးပါ။",
    "th": "ฉันชื่อ Mekhala และฉันสามารถช่วยเรื่องสาเหตุของน้ำท่วม สัญญาณเตือนภัยน้ำท่วม ชุดอุปกรณ์ฉุกเฉิน การอพยพ ความปลอดภัยบนถนน ความปลอดภัยด้านไฟฟ้า น้ำสะอาด ความช่วยเหลือทางการแพทย์ การทำความสะอาดหลังน้ำท่วม และการปกป้องบ้านของคุณ กรุณาถามคำถามให้ละเอียดมากขึ้น",
    "zh-CN": "我的名字是 Mekhala，我可以帮助解答洪水成因、洪水预警信号、应急包、疏散、道路安全、电力安全、安全饮水、医疗帮助、洪水后的清理以及保护家庭等问题。请更详细地提出您的问题。",
    "hi": "मेरा नाम Mekhala है और मैं बाढ़ के कारणों, बाढ़ चेतावनी संकेतों, आपातकालीन किट, निकासी, सड़क सुरक्षा, विद्युत सुरक्षा, सुरक्षित पानी, चिकित्सा सहायता, बाढ़ के बाद सफाई और घर की सुरक्षा में मदद कर सकता हूँ। कृपया अपना प्रश्न अधिक विस्तार से पूछें।",
    "bn": "আমার নাম Mekhala এবং আমি বন্যার কারণ, বন্যার সতর্ক সংকেত, জরুরি কিট, সরিয়ে নেওয়া, সড়ক নিরাপত্তা, বিদ্যুৎ নিরাপত্তা, নিরাপদ পানি, চিকিৎসা সহায়তা, বন্যার পর পরিষ্কার-পরিচ্ছন্নতা এবং আপনার বাড়ি সুরক্ষার বিষয়ে সাহায্য করতে পারি। অনুগ্রহ করে আপনার প্রশ্নটি আরও বিস্তারিতভাবে করুন।",
    "id": "Nama saya Mekhala dan saya dapat membantu tentang penyebab banjir, tanda peringatan banjir, perlengkapan darurat, evakuasi, keselamatan jalan, keselamatan listrik, air bersih, bantuan medis, pembersihan setelah banjir, dan perlindungan rumah Anda. Silakan ajukan pertanyaan Anda dengan lebih rinci.",
    "vi": "Tên tôi là Mekhala và tôi có thể hỗ trợ về nguyên nhân gây lũ lụt, dấu hiệu cảnh báo lũ, bộ dụng cụ khẩn cấp, sơ tán, an toàn đường bộ, an toàn điện, nước sạch, hỗ trợ y tế, dọn dẹp sau lũ và bảo vệ ngôi nhà của bạn. Vui lòng đặt câu hỏi chi tiết hơn.",
    "ja": "私の名前は Mekhala です。洪水の原因、洪水の警告サイン、非常用キット、避難、道路の安全、電気の安全、安全な水、医療支援、洪水後の清掃、家の保護についてお手伝いできます。質問をもう少し詳しくしてください。",
    "ko": "제 이름은 Mekhala입니다. 저는 홍수 원인, 홍수 경고 신호, 비상 키트, 대피, 도로 안전, 전기 안전, 안전한 물, 의료 지원, 홍수 후 청소, 집 보호에 대해 도와드릴 수 있습니다. 질문을 더 자세히 해 주세요.",
    "fr": "Je m'appelle Mekhala et je peux vous aider avec les causes des inondations, les signes d'alerte, les kits d'urgence, l'évacuation, la sécurité routière, la sécurité électrique, l'eau potable, l'aide médicale, le nettoyage après une inondation et la protection de votre maison. Veuillez poser votre question plus en détail.",
    "es": "Me llamo Mekhala y puedo ayudar con las causas de las inundaciones, las señales de advertencia, los kits de emergencia, la evacuación, la seguridad vial, la seguridad eléctrica, el agua segura, la ayuda médica, la limpieza después de una inundación y la protección de su hogar. Por favor, haga su pregunta con más detalle.",
    "ar": "اسمي Mekhala ويمكنني المساعدة في أسباب الفيضانات، علامات التحذير من الفيضانات، أدوات الطوارئ، الإخلاء، سلامة الطرق، السلامة الكهربائية، المياه الآمنة، المساعدة الطبية، التنظيف بعد الفيضانات، وحماية منزلك. يرجى طرح سؤالك بمزيد من التفاصيل.",
    "de": "Mein Name ist Mekhala und ich kann bei Ursachen von Überschwemmungen, Warnzeichen, Notfallausrüstung, Evakuierung, Verkehrssicherheit, elektrischer Sicherheit, sauberem Wasser, medizinischer Hilfe, Reinigung nach Überschwemmungen und dem Schutz Ihres Hauses helfen. Bitte stellen Sie Ihre Frage genauer.",
    "ms": "Nama saya Mekhala dan saya boleh membantu tentang punca banjir, tanda amaran banjir, kit kecemasan, pemindahan, keselamatan jalan raya, keselamatan elektrik, air bersih, bantuan perubatan, pembersihan selepas banjir dan perlindungan rumah anda. Sila tanya soalan anda dengan lebih terperinci.",
}


FLOOD_KEYWORDS = {
    "en": ["flood", "flooding", "rain", "storm", "evacuation", "evacuate", "water", "road", "emergency", "rescue", "shelter", "warning"],
    "my": ["ရေကြီး", "ရေလွှမ်း", "မိုး", "မုန်တိုင်း", "ပြောင်းရွှေ့", "အရေးပေါ်", "ကယ်ဆယ်", "သောက်ရေ", "လမ်း"],
    "th": ["น้ำท่วม", "ฝน", "พายุ", "อพยพ", "ฉุกเฉิน", "ช่วยเหลือ", "ถนน", "น้ำสะอาด"],
    "zh-CN": ["洪水", "暴雨", "风暴", "疏散", "应急", "救援", "道路", "安全", "饮水"],
    "hi": ["बाढ़", "बारिश", "तूफान", "निकासी", "आपातकाल", "बचाव", "सड़क", "पानी"],
    "bn": ["বন্যা", "বৃষ্টি", "ঝড়", "সরিয়ে", "জরুরি", "উদ্ধার", "রাস্তা", "পানি"],
    "id": ["banjir", "hujan", "badai", "evakuasi", "darurat", "penyelamatan", "jalan", "air"],
    "vi": ["lũ", "lụt", "mưa", "bão", "sơ tán", "khẩn cấp", "cứu hộ", "đường", "nước"],
    "ja": ["洪水", "浸水", "大雨", "嵐", "避難", "緊急", "救助", "道路", "水"],
    "ko": ["홍수", "침수", "비", "폭풍", "대피", "비상", "구조", "도로", "물"],
    "fr": ["inondation", "inondations", "pluie", "tempête", "évacuation", "urgence", "secours", "route", "eau"],
    "es": ["inundación", "inundaciones", "lluvia", "tormenta", "evacuación", "emergencia", "rescate", "carretera", "agua"],
    "ar": ["فيض", "فيضان", "فيضانات", "مطر", "عاصفة", "إخلاء", "طوارئ", "إنقاذ", "طريق", "ماء"],
    "de": ["überschwemmung", "hochwasser", "regen", "sturm", "evakuierung", "notfall", "rettung", "straße", "wasser"],
    "ms": ["banjir", "hujan", "ribut", "pemindahan", "kecemasan", "menyelamat", "jalan", "air"],
}


NAME_KEYWORDS = {
    "en": ["what is your name", "what's your name", "your name", "who are you"],
    "my": ["နာမည်", "ဘယ်သူ", "သင်ကဘယ်သူ", "မင်းနာမည်"],
    "th": ["ชื่ออะไร", "คุณชื่อ", "เธอชื่อ", "คุณเป็นใคร"],
    "zh-CN": ["你叫什么", "你的名字", "你是谁"],
    "hi": ["आपका नाम", "तुम्हारा नाम", "आप कौन"],
    "bn": ["আপনার নাম", "তোমার নাম", "আপনি কে"],
    "id": ["nama kamu", "nama anda", "siapa kamu"],
    "vi": ["tên bạn", "bạn tên", "bạn là ai"],
    "ja": ["名前", "あなたは誰", "君の名前"],
    "ko": ["이름", "당신은 누구", "너는 누구"],
    "fr": ["quel est ton nom", "quel est votre nom", "ton nom", "votre nom", "qui es-tu", "qui êtes-vous"],
    "es": ["cómo te llamas", "cuál es tu nombre", "tu nombre", "quién eres"],
    "ar": ["ما اسمك", "اسمك", "من أنت"],
    "de": ["wie heißt du", "wie ist dein name", "dein name", "wer bist du"],
    "ms": ["nama awak", "nama anda", "siapa awak"],
}


def _normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[؟?!.،,;:()\[\]{}\"']", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def detect_user_language(text: str) -> str:
    raw = text.strip()
    lower = raw.lower()

    # Strong script-based detection first
    if re.search(r"[\u1000-\u109F]", raw):
        return "my"
    if re.search(r"[\u0E00-\u0E7F]", raw):
        return "th"
    if re.search(r"[\u4E00-\u9FFF]", raw):
        return "zh-CN"
    if re.search(r"[\u0900-\u097F]", raw):
        return "hi"
    if re.search(r"[\u0980-\u09FF]", raw):
        return "bn"
    if re.search(r"[\u3040-\u30FF]", raw):
        return "ja"
    if re.search(r"[\uAC00-\uD7AF]", raw):
        return "ko"
    if re.search(r"[\u0600-\u06FF]", raw):
        return "ar"

    # Manual phrase hints for Latin-script languages
    for lang, phrases in NAME_KEYWORDS.items():
        if lang in {"my", "th", "zh-CN", "hi", "bn", "ja", "ko", "ar"}:
            continue
        if any(phrase in lower for phrase in phrases):
            return lang

    for lang, phrases in FLOOD_KEYWORDS.items():
        if lang in {"my", "th", "zh-CN", "hi", "bn", "ja", "ko", "ar"}:
            continue
        if any(phrase in lower for phrase in phrases):
            return lang

    # langdetect fallback
    try:
        from langdetect import detect

        detected = detect(raw)
        if detected == "zh-cn":
            return "zh-CN"
        if detected in SUPPORTED_LANGUAGES:
            return detected
    except Exception:
        pass

    return "en"


def _contains_any(text: str, phrases: list[str]) -> bool:
    normalized = _normalize(text)
    return any(phrase.lower() in normalized for phrase in phrases)


def is_name_question(text: str, lang: str) -> bool:
    normalized = _normalize(text)

    # Check detected language first
    if _contains_any(normalized, NAME_KEYWORDS.get(lang, [])):
        return True

    # Check all name patterns, useful when langdetect is wrong
    for phrases in NAME_KEYWORDS.values():
        if _contains_any(normalized, phrases):
            return True

    return False


def is_flood_related(text: str) -> bool:
    normalized = _normalize(text)

    for phrases in FLOOD_KEYWORDS.values():
        for phrase in phrases:
            if phrase.lower() in normalized:
                return True

    return False


def get_mekhala_guardrail_response(user_text: str) -> Optional[str]:
    """
    Return:
    - name reply if user asks assistant name
    - flood-only guidance if user asks unrelated topic
    - None if question is flood-related, so normal flood chatbot can answer
    """
    if not user_text or not user_text.strip():
        return None

    lang = detect_user_language(user_text)

    if is_name_question(user_text, lang):
        return NAME_RESPONSES.get(lang, NAME_RESPONSES["en"])

    if not is_flood_related(user_text):
        return HELP_RESPONSES.get(lang, HELP_RESPONSES["en"])

    return None