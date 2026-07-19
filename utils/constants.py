APP_NAME = "FloodMind"

PAGE_PREDICTOR = "Flood Risk Predictor"
PAGE_ASSISTANT = "AI Flood Assistant"
PAGE_IMAGE_ANALYSIS = "Flood Image Analysis"

PAGE_ORDER = [
    PAGE_PREDICTOR,
    PAGE_ASSISTANT,
    PAGE_IMAGE_ANALYSIS,
]

NAV_ICONS = {
    PAGE_PREDICTOR: "🌊",
    PAGE_ASSISTANT: "🤖",
    PAGE_IMAGE_ANALYSIS: "🖼️",
}

NAV_TRANSLATION_KEYS = {
    PAGE_PREDICTOR: "nav_predictor",
    PAGE_ASSISTANT: "nav_assistant",
    PAGE_IMAGE_ANALYSIS: "nav_image_analysis",
}

NAV_ITEMS = {
    "🌊  Flood Risk Predictor": PAGE_PREDICTOR,
    "🤖  AI Flood Assistant": PAGE_ASSISTANT,
    "🖼️  Image Analysis": PAGE_IMAGE_ANALYSIS,
}

LANGUAGE_OPTIONS = ["English", "မြန်မာဘာသာ", "日本語"]

LANGUAGE_CODE_MAP = {
    "English": "en",
    "မြန်မာဘာသာ": "my",
    "日本語": "ja",
}

LANGUAGE_DISPLAY_BY_CODE = {
    "en": "English",
    "my": "မြန်မာဘာသာ",
    "ja": "日本語",
}

COLORS = {
    "white": "#fafafa",
    "light_gradient": "#bde2f1",
    "normal_gradient": "#82c8e5",
    "dark_gradient": "#47aed9",
    "navy": "#003152",
    "gray": "#9d9d9d",
    "black": "#121212",
    "light_green": "#8ceeb4",
    "green": "#049b41",
    "light_yellow": "#eed78c",
    "yellow": "#e2ba38",
    "dark_yellow": "#9b7804",
    "light_red": "#ee8c8e",
    "red": "#b42f31",
}

RISK_PALETTE = {
    "Low Risk": {
        "soft": COLORS["light_green"],
        "strong": COLORS["green"],
        "text": COLORS["green"],
    },
    "Medium Risk": {
        "soft": COLORS["light_yellow"],
        "strong": COLORS["yellow"],
        "text": COLORS["dark_yellow"],
    },
    "High Risk": {
        "soft": COLORS["light_red"],
        "strong": COLORS["red"],
        "text": COLORS["red"],
    },
}

DEFAULT_PREDICTOR_INPUTS = {
    "rainfall_level": "Heavy",
    "weather_trend": "Same",
    "area_type": "Hilly",
    "distance_to_coast": "Not sure",
    "river_control": "Not sure",
    "dam_condition": "Average",
    "drainage_quality": "Strong",
}

QUICK_PROMPTS = [
    "What should I do during a flood?",
    "What are flood warning signs?",
    "How to protect my home from floods?",
    "When should I evacuate?",
    "What to pack in an emergency kit?",
]


TRANSLATIONS = {
    "en": {
        "brand_subtitle": "AI Flood Intelligence",
        "language_label": "Language",
        "nav_label": "Main Navigation",
        "nav_predictor": "Flood Risk Predictor",
        "nav_assistant": "AI Flood Assistant",
        "nav_image_analysis": "Image Analysis",

        "predictor_title": "Flood Risk Predictor",
        "powered_by_ai": "Powered by AI",
        "simulation_parameters": "Simulation Parameters",
        "simulation_description": (
            "Enter environmental data to get instant flood risk prediction and receive "
            "real-time AI assessment of current conditions."
        ),
        "weather_climate": "Weather & Climate",
        "rainfall_label": "Rainfall Level",
        "weather_trend_label": "Weather getting worse?",
        "location_topography": "Location & Topography",
        "area_type_label": "Area Type",
        "distance_to_coast_label": "Distance to coast",
        "infrastructure_systems": "Infrastructure & Systems",
        "river_control_label": "River control",
        "dam_condition_label": "Dam condition",
        "drainage_quality_label": "Drainage quality",
        "reset_values_button": "Reset Values",
        "predict_risk_button": "Predict Risk",
        "predictor_spinner": "Running FloodMind risk simulation...",
        "ai_prediction_result": "AI Prediction Result",
        "flood_probability": "Flood Probability",
        "confidence_score": "Confidence Score",
        "predicted_peak": "Predicted Peak",
        "emergency_actions": "Emergency Actions",
        "local_weather_forecast": "Local Weather Forecast",
        "heavy_rain_expected": "Heavy Rain Expected",

        "risk_labels": {
            "Low Risk": "Low Risk",
            "Medium Risk": "Medium Risk",
            "High Risk": "High Risk",
        },

        "risk_explanations": {
            "Low Risk": (
                "Flood risk is low under the current simulated conditions. Continue monitoring "
                "weather updates and nearby water levels."
            ),
            "Medium Risk": (
                "Flood risk is currently moderate. Conditions may become dangerous if rainfall "
                "continues or drainage capacity decreases."
            ),
            "High Risk": (
                "Flood risk is high based on rainfall intensity, infrastructure condition, "
                "and environmental exposure. Immediate preparedness actions are recommended."
            ),
        },

        "emergency_actions_by_risk": {
            "Low Risk": [
                {
                    "icon": "✅",
                    "title": "Continue Monitoring",
                    "text": "Current conditions are stable, but weather and drainage status should still be watched.",
                },
                {
                    "icon": "🧹",
                    "title": "Clear Drainage Paths",
                    "text": "Remove waste or blockage from nearby drains before rainfall increases.",
                },
                {
                    "icon": "🌦️",
                    "title": "Review Weather Updates",
                    "text": "Check local rainfall alerts and river-level reports throughout the day.",
                },
            ],
            "Medium Risk": [
                {
                    "icon": "📢",
                    "title": "Notify Residents",
                    "text": "Send early warning notifications to residents in flood-prone zones.",
                },
                {
                    "icon": "🛡️",
                    "title": "Prepare Flood Barriers",
                    "text": "Check and prepare flood gates, sandbags, and drainage barriers.",
                },
                {
                    "icon": "⛑️",
                    "title": "Standby Emergency Teams",
                    "text": "Keep response teams ready in case rainfall or water levels rise quickly.",
                },
            ],
            "High Risk": [
                {
                    "icon": "🚨",
                    "title": "Activate Evacuation Plan",
                    "text": "Move residents from low-lying zones to safer elevated shelters immediately.",
                },
                {
                    "icon": "🛡️",
                    "title": "Deploy Emergency Teams",
                    "text": "Prepare rescue, medical, and local response teams for rapid deployment.",
                },
                {
                    "icon": "🚧",
                    "title": "Close Flooded Roads",
                    "text": "Restrict vehicle access to roads where water movement or depth is unsafe.",
                },
            ],
        },

        "options": {
            "rainfall_level": {
                "Light": "Light",
                "Medium": "Medium",
                "Heavy": "Heavy",
                "Extreme": "Extreme",
            },
            "weather_trend": {
                "Less worse": "Less worse",
                "Same": "Same",
                "Worse": "Worse",
                "Not sure": "Not sure",
            },
            "area_type": {
                "Low land": "Low land",
                "Slightly elevated": "Slightly elevated",
                "Hilly": "Hilly",
            },
            "distance_to_coast": {
                "Inland": "Inland",
                "Near": "Near",
                "Coastal": "Coastal",
                "Not sure": "Not sure",
            },
            "system_quality": {
                "Poor": "Poor",
                "Average": "Average",
                "Strong": "Strong",
                "Not sure": "Not sure",
            },
        },

        "assistant_title": "AI Flood Assistant",
        "assistant_subtitle": "Conversational flood safety guidance and preparedness support.",
        "assistant_badge": "Ask Flood AI",
        "assistant_welcome": "Welcome to AI Flood Assistant",
        "assistant_description": (
            "Ask me anything about floods, flood prevention, flood preparedness, "
            "emergency response, flood safety, or flood risk assessment."
        ),
        "chat_input_placeholder": "Ask me anything about floods",
        "assistant_spinner": "FloodMind assistant is preparing a safety response...",
        "quick_prompts": [
            "What should I do during a flood?",
            "What are flood warning signs?",
            "How to protect my home from floods?",
            "When should I evacuate?",
            "What to pack in an emergency kit?",
        ],

        "image_title": "Flood Image Analysis",
        "image_subtitle": "Upload an image to analyze flood conditions and estimate severity.",
        "recent_samples": "Recent Samples",
        "upload_title": "Upload image here or browse file",
        "upload_description": "Supported formats: JPG, PNG, JPEG • Max file size: 20MB",
        "upload_label": "Upload flood image",
        "analyze_image_button": "Analyze Image",
        "upload_warning": "Please upload a JPG, PNG, or JPEG image before analysis.",
        "image_spinner": "Analyzing image with FloodMind vision pipeline...",
        "analysis_results": "Analysis Results",
        "quick_status": "Quick Status",
        "flood_detected": "Flood Detected",
        "risk_level": "Risk Level",
        "confidence": "Confidence",
        "water_coverage": "Water Coverage",
        "whats_happening": "What’s Happening",
        "what_you_should_do": "What You Should Do",
        "ai_info": "AI Info",
        "ai_model": "AI Model",
        "accuracy": "Accuracy",
        "data_analyzed": "Data Analyzed",
        "how_accurate": "How Accurate Is This?",
        "accuracy_description": (
            "This AI checks images to tell the difference between normal road water, "
            "floodwater, and visually dangerous flood conditions with high confidence."
        ),
        "yes": "Yes",
        "no": "No",
        "use_high_sample": "Use High Sample",
        "use_medium_sample": "Use Medium Sample",
        "use_low_sample": "Use Low Sample",
    },

    "my": {
        "brand_subtitle": "AI ရေကြီးမှု အချက်အလက်စနစ်",
        "language_label": "ဘာသာစကား",
        "nav_label": "အဓိက မီနူး",
        "nav_predictor": "ရေကြီးမှု အန္တရာယ် ခန့်မှန်းခြင်း",
        "nav_assistant": "AI ရေကြီးမှု အကူအညီ",
        "nav_image_analysis": "ပုံရိပ် ခွဲခြမ်းစိတ်ဖြာခြင်း",

        "predictor_title": "ရေကြီးမှု အန္တရာယ် ခန့်မှန်းခြင်း",
        "powered_by_ai": "AI ဖြင့် မောင်းနှင်ထားသည်",
        "simulation_parameters": "စမ်းသပ်မှု အချက်အလက်များ",
        "simulation_description": (
            "ပတ်ဝန်းကျင်ဆိုင်ရာ အချက်အလက်များ ထည့်သွင်းပြီး ရေကြီးမှု အန္တရာယ်ကို "
            "ချက်ချင်း ခန့်မှန်းနိုင်ပြီး လက်ရှိအခြေအနေကို AI ဖြင့် သုံးသပ်ပေးနိုင်သည်။"
        ),
        "weather_climate": "ရာသီဥတုနှင့် မိုးလေဝသ",
        "rainfall_label": "မိုးရွာနှုန်း",
        "weather_trend_label": "ရာသီဥတု ပိုဆိုးလာနေပါသလား?",
        "location_topography": "တည်နေရာနှင့် မြေမျက်နှာသွင်ပြင်",
        "area_type_label": "ဒေသအမျိုးအစား",
        "distance_to_coast_label": "ကမ်းရိုးတန်းနှင့် အကွာအဝေး",
        "infrastructure_systems": "အခြေခံအဆောက်အအုံနှင့် စနစ်များ",
        "river_control_label": "မြစ်ရေ ထိန်းချုပ်မှု",
        "dam_condition_label": "ဆည်အခြေအနေ",
        "drainage_quality_label": "ရေစီးဆင်းမှု စနစ်အရည်အသွေး",
        "reset_values_button": "တန်ဖိုးများ ပြန်သတ်မှတ်ရန်",
        "predict_risk_button": "အန္တရာယ် ခန့်မှန်းရန်",
        "predictor_spinner": "FloodMind ရေကြီးမှု အန္တရာယ် ခန့်မှန်းနေသည်...",
        "ai_prediction_result": "AI ခန့်မှန်းချက် ရလဒ်",
        "flood_probability": "ရေကြီးနိုင်ခြေ",
        "confidence_score": "ယုံကြည်စိတ်ချမှု အမှတ်",
        "predicted_peak": "အမြင့်ဆုံး ဖြစ်နိုင်ချိန်",
        "emergency_actions": "အရေးပေါ် လုပ်ဆောင်ရန်များ",
        "local_weather_forecast": "ဒေသတွင်း မိုးလေဝသ ခန့်မှန်းချက်",
        "heavy_rain_expected": "မိုးသည်းထန်စွာ ရွာနိုင်သည်",

        "risk_labels": {
            "Low Risk": "အန္တရာယ်နည်း",
            "Medium Risk": "အလယ်အလတ် အန္တရာယ်",
            "High Risk": "အန္တရာယ်မြင့်",
        },

        "risk_explanations": {
            "Low Risk": (
                "လက်ရှိ စမ်းသပ်ထားသော အခြေအနေများအရ ရေကြီးမှု အန္တရာယ် နည်းပါးသည်။ "
                "သို့သော် မိုးလေဝသ အချက်အလက်နှင့် ရေမျက်နှာပြင် အခြေအနေများကို ဆက်လက်စောင့်ကြည့်ပါ။"
            ),
            "Medium Risk": (
                "လက်ရှိ ရေကြီးမှု အန္တရာယ်သည် အလယ်အလတ်အဆင့် ဖြစ်သည်။ မိုးဆက်လက်ရွာပါက "
                "သို့မဟုတ် ရေစီးဆင်းမှု စနစ် အားနည်းလာပါက အန္တရာယ် မြင့်တက်နိုင်သည်။"
            ),
            "High Risk": (
                "မိုးရွာနှုန်း၊ အခြေခံအဆောက်အအုံ အခြေအနေ၊ နှင့် ပတ်ဝန်းကျင် ထိတွေ့မှုအရ "
                "ရေကြီးမှု အန္တရာယ် မြင့်မားနေသည်။ အရေးပေါ် ကြိုတင်ပြင်ဆင်မှုများ လုပ်ဆောင်ရန် လိုအပ်သည်။"
            ),
        },

        "emergency_actions_by_risk": {
            "Low Risk": [
                {
                    "icon": "✅",
                    "title": "ဆက်လက် စောင့်ကြည့်ရန်",
                    "text": "လက်ရှိအခြေအနေ တည်ငြိမ်နေသော်လည်း မိုးလေဝသနှင့် ရေစီးဆင်းမှုအခြေအနေကို ဆက်လက်စောင့်ကြည့်ပါ။",
                },
                {
                    "icon": "🧹",
                    "title": "ရေစီးလမ်းကြောင်း ရှင်းလင်းရန်",
                    "text": "မိုးများလာမီ ရေမြောင်းများတွင် အမှိုက်နှင့် ပိတ်ဆို့မှုများကို ဖယ်ရှားပါ။",
                },
                {
                    "icon": "🌦️",
                    "title": "မိုးလေဝသ သတင်းများ စစ်ဆေးရန်",
                    "text": "ဒေသတွင်း မိုးရွာသွန်းမှု သတိပေးချက်နှင့် မြစ်ရေ အခြေအနေများကို စစ်ဆေးပါ။",
                },
            ],
            "Medium Risk": [
                {
                    "icon": "📢",
                    "title": "နေထိုင်သူများကို အသိပေးရန်",
                    "text": "ရေကြီးနိုင်သော ဒေသရှိ နေထိုင်သူများထံ အစောပိုင်း သတိပေးချက်များ ပေးပို့ပါ။",
                },
                {
                    "icon": "🛡️",
                    "title": "ရေကာတားဆီးရေး စနစ် ပြင်ဆင်ရန်",
                    "text": "ရေတံခါးများ၊ သဲအိတ်များနှင့် ရေကာအတားများကို စစ်ဆေးပြင်ဆင်ပါ။",
                },
                {
                    "icon": "⛑️",
                    "title": "အရေးပေါ်အဖွဲ့များ အသင့်ထားရန်",
                    "text": "မိုးရွာနှုန်း သို့မဟုတ် ရေမျက်နှာပြင် မြင့်တက်လာပါက တုံ့ပြန်နိုင်ရန် အဖွဲ့များကို အသင့်ထားပါ။",
                },
            ],
            "High Risk": [
                {
                    "icon": "🚨",
                    "title": "ရွှေ့ပြောင်းရေး အစီအစဉ် စတင်ရန်",
                    "text": "နိမ့်သောဒေသရှိ နေထိုင်သူများကို မြင့်သော လုံခြုံရာနေရာများသို့ ချက်ချင်းရွှေ့ပြောင်းပါ။",
                },
                {
                    "icon": "🛡️",
                    "title": "အရေးပေါ် ကယ်ဆယ်ရေးအဖွဲ့များ စေလွှတ်ရန်",
                    "text": "ကယ်ဆယ်ရေး၊ ဆေးဘက်ဆိုင်ရာနှင့် ဒေသတွင်း တုံ့ပြန်ရေးအဖွဲ့များကို အသင့်ပြင်ဆင်ပါ။",
                },
                {
                    "icon": "🚧",
                    "title": "ရေဝင်နေသော လမ်းများ ပိတ်ရန်",
                    "text": "ရေစီးအား သို့မဟုတ် ရေအနက်ကြောင့် မလုံခြုံသော လမ်းများတွင် ယာဉ်သွားလာမှုကို ပိတ်ပါ။",
                },
            ],
        },

        "options": {
            "rainfall_level": {
                "Light": "အနည်းငယ်",
                "Medium": "အလယ်အလတ်",
                "Heavy": "ပြင်းထန်",
                "Extreme": "အလွန်ပြင်းထန်",
            },
            "weather_trend": {
                "Less worse": "လျော့နည်း",
                "Same": "အတူတူ",
                "Worse": "ပိုဆိုး",
                "Not sure": "မသေချာ",
            },
            "area_type": {
                "Low land": "မြေနိမ့်ပိုင်း",
                "Slightly elevated": "အနည်းငယ် မြင့်သောနေရာ",
                "Hilly": "တောင်ကုန်းဒေသ",
            },
            "distance_to_coast": {
                "Inland": "ကုန်းတွင်းပိုင်း",
                "Near": "အနီး",
                "Coastal": "ကမ်းရိုးတန်း",
                "Not sure": "မသေချာ",
            },
            "system_quality": {
                "Poor": "အားနည်း",
                "Average": "ပုံမှန်",
                "Strong": "ကောင်းမွန်",
                "Not sure": "မသေချာ",
            },
        },

        "assistant_title": "AI ရေကြီးမှု အကူအညီ",
        "assistant_subtitle": "ရေကြီးမှု ဘေးကင်းရေးနှင့် ကြိုတင်ပြင်ဆင်မှုအတွက် စကားပြောအကူအညီ။",
        "assistant_badge": "Flood AI ကို မေးရန်",
        "assistant_welcome": "AI ရေကြီးမှု အကူအညီမှ ကြိုဆိုပါသည်",
        "assistant_description": (
            "ရေကြီးမှု၊ ရေကြီးမှု ကာကွယ်ရေး၊ ကြိုတင်ပြင်ဆင်မှု၊ အရေးပေါ်တုံ့ပြန်မှု၊ "
            "ဘေးကင်းရေးနှင့် အန္တရာယ် ခန့်မှန်းမှုများကို မေးမြန်းနိုင်သည်။"
        ),
        "chat_input_placeholder": "ရေကြီးမှုအကြောင်း မေးမြန်းပါ",
        "assistant_spinner": "FloodMind အကူအညီက အဖြေပြင်ဆင်နေသည်...",
        "quick_prompts": [
            "ရေကြီးနေချိန်မှာ ဘာလုပ်သင့်လဲ?",
            "ရေကြီးမှု သတိပေးလက္ခဏာတွေက ဘာတွေလဲ?",
            "အိမ်ကို ရေကြီးမှုမှ ဘယ်လိုကာကွယ်မလဲ?",
            "ဘယ်အချိန်မှာ ရွှေ့ပြောင်းသင့်လဲ?",
            "အရေးပေါ်အိတ်ထဲမှာ ဘာတွေ ထည့်သင့်လဲ?",
        ],

        "image_title": "ရေကြီးမှု ပုံရိပ် ခွဲခြမ်းစိတ်ဖြာခြင်း",
        "image_subtitle": "ရေကြီးမှု အခြေအနေနှင့် ပြင်းထန်မှုကို ခန့်မှန်းရန် ပုံတင်ပါ။",
        "recent_samples": "နမူနာ ပုံများ",
        "upload_title": "ပုံကို ဒီနေရာတွင် တင်ပါ သို့မဟုတ် ဖိုင်ရွေးပါ",
        "upload_description": "ထောက်ပံ့သော ဖော်မတ်များ: JPG, PNG, JPEG • အများဆုံး 20MB",
        "upload_label": "ရေကြီးမှု ပုံတင်ရန်",
        "analyze_image_button": "ပုံကို ခွဲခြမ်းစိတ်ဖြာရန်",
        "upload_warning": "ခွဲခြမ်းစိတ်ဖြာမှု မလုပ်မီ JPG, PNG, JPEG ပုံတစ်ပုံ တင်ပါ။",
        "image_spinner": "FloodMind ပုံရိပ် AI စနစ်ဖြင့် ခွဲခြမ်းစိတ်ဖြာနေသည်...",
        "analysis_results": "ခွဲခြမ်းစိတ်ဖြာမှု ရလဒ်",
        "quick_status": "အမြန်အခြေအနေ",
        "flood_detected": "ရေကြီးမှု တွေ့ရှိ",
        "risk_level": "အန္တရာယ်အဆင့်",
        "confidence": "ယုံကြည်စိတ်ချမှု",
        "water_coverage": "ရေဖုံးလွှမ်းမှု",
        "whats_happening": "ဘာဖြစ်နေသလဲ",
        "what_you_should_do": "လုပ်သင့်သောအရာများ",
        "ai_info": "AI အချက်အလက်",
        "ai_model": "AI မော်ဒယ်",
        "accuracy": "တိကျမှု",
        "data_analyzed": "ခွဲခြမ်းစိတ်ဖြာထားသော ဒေတာ",
        "how_accurate": "ဒီစနစ် ဘယ်လောက်တိကျသလဲ?",
        "accuracy_description": (
            "ဒီ AI သည် ပုံများကို စစ်ဆေးပြီး လမ်းပေါ်ရေ၊ ရေကြီးရေစီးနှင့် "
            "အန္တရာယ်ရှိသော ရေကြီးမှုအခြေအနေများကို ခွဲခြားနိုင်သည်။"
        ),
        "yes": "ဟုတ်ကဲ့",
        "no": "မဟုတ်ပါ",
        "use_high_sample": "အန္တရာယ်မြင့် နမူနာသုံးရန်",
        "use_medium_sample": "အလယ်အလတ် နမူနာသုံးရန်",
        "use_low_sample": "အန္တရာယ်နည်း နမူနာသုံးရန်",
    },

    "ja": {
        "brand_subtitle": "AI 洪水インテリジェンス",
        "language_label": "言語",
        "nav_label": "メインナビゲーション",
        "nav_predictor": "洪水リスク予測",
        "nav_assistant": "AI 洪水アシスタント",
        "nav_image_analysis": "画像解析",

        "predictor_title": "洪水リスク予測",
        "powered_by_ai": "AI 搭載",
        "simulation_parameters": "シミュレーション条件",
        "simulation_description": (
            "環境データを入力すると、現在の状況に基づいて洪水リスクを即時に予測し、"
            "AI による評価を表示します。"
        ),
        "weather_climate": "天候・気候",
        "rainfall_label": "降雨レベル",
        "weather_trend_label": "天候は悪化していますか？",
        "location_topography": "位置・地形",
        "area_type_label": "地域タイプ",
        "distance_to_coast_label": "海岸までの距離",
        "infrastructure_systems": "インフラ・システム",
        "river_control_label": "河川制御",
        "dam_condition_label": "ダムの状態",
        "drainage_quality_label": "排水品質",
        "reset_values_button": "値をリセット",
        "predict_risk_button": "リスクを予測",
        "predictor_spinner": "FloodMind が洪水リスクを計算しています...",
        "ai_prediction_result": "AI 予測結果",
        "flood_probability": "洪水確率",
        "confidence_score": "信頼度",
        "predicted_peak": "予測ピーク",
        "emergency_actions": "緊急対応",
        "local_weather_forecast": "地域の天気予報",
        "heavy_rain_expected": "大雨の可能性",

        "risk_labels": {
            "Low Risk": "低リスク",
            "Medium Risk": "中リスク",
            "High Risk": "高リスク",
        },

        "risk_explanations": {
            "Low Risk": (
                "現在のシミュレーション条件では洪水リスクは低いです。"
                "ただし、天気情報と周辺の水位は引き続き確認してください。"
            ),
            "Medium Risk": (
                "現在の洪水リスクは中程度です。雨が続いたり排水能力が低下したりすると、"
                "危険度が高まる可能性があります。"
            ),
            "High Risk": (
                "降雨量、インフラ状態、環境条件により洪水リスクは高い状態です。"
                "直ちに防災対応を準備することを推奨します。"
            ),
        },

        "emergency_actions_by_risk": {
            "Low Risk": [
                {
                    "icon": "✅",
                    "title": "監視を継続",
                    "text": "現在の状況は安定していますが、天候と排水状態は継続して確認してください。",
                },
                {
                    "icon": "🧹",
                    "title": "排水経路を清掃",
                    "text": "雨が強くなる前に、排水路のごみや詰まりを取り除いてください。",
                },
                {
                    "icon": "🌦️",
                    "title": "気象情報を確認",
                    "text": "地域の降雨警報と河川水位情報を定期的に確認してください。",
                },
            ],
            "Medium Risk": [
                {
                    "icon": "📢",
                    "title": "住民へ通知",
                    "text": "洪水の可能性がある地域の住民へ早期警報を送信してください。",
                },
                {
                    "icon": "🛡️",
                    "title": "洪水防止設備を準備",
                    "text": "水門、土のう、排水設備を確認し、すぐ使用できるようにしてください。",
                },
                {
                    "icon": "⛑️",
                    "title": "緊急チームを待機",
                    "text": "雨量や水位が急上昇した場合に備え、対応チームを待機させてください。",
                },
            ],
            "High Risk": [
                {
                    "icon": "🚨",
                    "title": "避難計画を開始",
                    "text": "低地の住民を安全な高台や避難所へ直ちに移動させてください。",
                },
                {
                    "icon": "🛡️",
                    "title": "緊急対応チームを配置",
                    "text": "救助、医療、地域対応チームを迅速に展開できるよう準備してください。",
                },
                {
                    "icon": "🚧",
                    "title": "冠水道路を閉鎖",
                    "text": "水流や水深により危険な道路では車両通行を制限してください。",
                },
            ],
        },

        "options": {
            "rainfall_level": {
                "Light": "弱い",
                "Medium": "中程度",
                "Heavy": "強い",
                "Extreme": "非常に強い",
            },
            "weather_trend": {
                "Less worse": "改善傾向",
                "Same": "変化なし",
                "Worse": "悪化",
                "Not sure": "不明",
            },
            "area_type": {
                "Low land": "低地",
                "Slightly elevated": "やや高い地域",
                "Hilly": "丘陵地",
            },
            "distance_to_coast": {
                "Inland": "内陸",
                "Near": "近い",
                "Coastal": "沿岸",
                "Not sure": "不明",
            },
            "system_quality": {
                "Poor": "弱い",
                "Average": "普通",
                "Strong": "強い",
                "Not sure": "不明",
            },
        },

        "assistant_title": "AI 洪水アシスタント",
        "assistant_subtitle": "洪水安全と防災準備のための会話型サポート。",
        "assistant_badge": "Flood AI に質問",
        "assistant_welcome": "AI 洪水アシスタントへようこそ",
        "assistant_description": (
            "洪水、防災、避難準備、緊急対応、安全対策、洪水リスク評価について質問できます。"
        ),
        "chat_input_placeholder": "洪水について質問してください",
        "assistant_spinner": "FloodMind アシスタントが回答を準備しています...",
        "quick_prompts": [
            "洪水時には何をすべきですか？",
            "洪水の警告サインは何ですか？",
            "家を洪水から守るには？",
            "いつ避難すべきですか？",
            "非常用バッグには何を入れるべきですか？",
        ],

        "image_title": "洪水画像解析",
        "image_subtitle": "画像をアップロードして洪水状況と深刻度を推定します。",
        "recent_samples": "最近のサンプル",
        "upload_title": "画像をここにアップロード、またはファイルを選択",
        "upload_description": "対応形式: JPG, PNG, JPEG • 最大ファイルサイズ: 20MB",
        "upload_label": "洪水画像をアップロード",
        "analyze_image_button": "画像を解析",
        "upload_warning": "解析前に JPG、PNG、JPEG 画像をアップロードしてください。",
        "image_spinner": "FloodMind 画像解析パイプラインで解析中...",
        "analysis_results": "解析結果",
        "quick_status": "クイックステータス",
        "flood_detected": "洪水検出",
        "risk_level": "リスクレベル",
        "confidence": "信頼度",
        "water_coverage": "水面被覆率",
        "whats_happening": "現在の状況",
        "what_you_should_do": "取るべき行動",
        "ai_info": "AI 情報",
        "ai_model": "AI モデル",
        "accuracy": "精度",
        "data_analyzed": "解析済みデータ",
        "how_accurate": "この解析はどのくらい正確ですか？",
        "accuracy_description": (
            "この AI は通常の路面水、洪水、水害の危険な状態を高い信頼度で判別します。"
        ),
        "yes": "はい",
        "no": "いいえ",
        "use_high_sample": "高リスクサンプルを使用",
        "use_medium_sample": "中リスクサンプルを使用",
        "use_low_sample": "低リスクサンプルを使用",
    },
}