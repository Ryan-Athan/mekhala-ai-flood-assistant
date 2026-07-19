from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data" / "knowledge_base"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"

SOURCE_CATALOG = {
    "ready_floods": {
        "title": "Floods",
        "organization": "Ready.gov / FEMA",
        "url": "https://www.ready.gov/floods",
        "notes": "Flood preparedness, evacuation, and stay-away-from-floodwater guidance.",
    },
    "ready_kit": {
        "title": "Build A Kit",
        "organization": "Ready.gov / FEMA",
        "url": "https://www.ready.gov/kit",
        "notes": "Emergency supply kit guidance.",
    },
    "nws_tadd": {
        "title": "Turn Around Don't Drown",
        "organization": "NOAA National Weather Service",
        "url": "https://www.weather.gov/safety/flood-turn-around-dont-drown",
        "notes": "Flooded road and floodwater travel safety guidance.",
    },
    "nws_flood_safety": {
        "title": "Flood Safety Tips and Resources",
        "organization": "NOAA National Weather Service",
        "url": "https://www.weather.gov/safety/flood",
        "notes": "General flood safety before, during, and after flood events.",
    },
    "cdc_floodwater": {
        "title": "Safety Guidelines: Floodwater",
        "organization": "CDC",
        "url": "https://www.cdc.gov/floods/safety/floodwater-after-a-disaster-or-emergency-safety.html",
        "notes": "Health risks from contaminated floodwater.",
    },
    "cdc_reenter_home": {
        "title": "Safety Guidelines: Reentering Your Flooded Home",
        "organization": "CDC",
        "url": "https://www.cdc.gov/floods/safety/reentering-your-flooded-home-safety.html",
        "notes": "Reentering flooded homes, electrical safety, and mold prevention.",
    },
    "cdc_cleanup": {
        "title": "Guidelines for Cleaning Safely After a Disaster",
        "organization": "CDC",
        "url": "https://www.cdc.gov/natural-disasters/safety/index.html",
        "notes": "Cleaning, drying, and mold-prevention guidance after disasters.",
    },
    "epa_cleanup": {
        "title": "Flood Cleanup to Protect Indoor Air and Your Health",
        "organization": "EPA",
        "url": "https://www.epa.gov/emergencies-iaq/flood-cleanup-protect-indoor-air-and-your-health",
        "notes": "Indoor air quality and mold risk after flooding.",
    },
}

# Knowledge base entries are paraphrased from the source catalog above.
KB_INTENTS = {
    "flood_event": {
        "display_name": "Flood happening now",
        "urgency": "high",
        "summary": "Immediate safety guidance for people currently affected by flooding.",
        "keywords": ["flood now", "water rising", "flooding", "during flood", "safe during flood"],
        "source_ids": ["ready_floods", "nws_tadd", "nws_flood_safety"],
        "answer_templates": {
            "en": "If flooding is happening now, move to higher ground immediately, avoid floodwater, and follow official evacuation instructions. Do not walk, swim, or drive through floodwater because depth and current can be dangerous and roads may be damaged underneath.",
            "my": "အခု ရေကြီးနေပါက မြင့်သောနေရာသို့ ချက်ချင်းရွှေ့ပါ။ ရေကြီးရေထဲ လမ်းလျှောက်ခြင်း၊ ရေကူးခြင်း၊ ကားဖြင့်ဖြတ်ခြင်း မလုပ်ပါနှင့်။ ရေအနက်၊ ရေစီးကြောင်းနှင့် လမ်းပျက်စီးမှုများကြောင့် အန္တရာယ်ရှိနိုင်ပါတယ်။ တာဝန်ရှိသူများ၏ ထွက်ခွာရန်ညွှန်ကြားချက်ကို လိုက်နာပါ။",
        },
        "action_steps": {
            "en": [
                "Move to higher ground or an official safe shelter.",
                "Avoid flooded roads, drains, canals, and fast-moving water.",
                "Keep phone, power bank, flashlight, medicine, and important documents with you.",
                "Listen to local authorities and evacuate if instructed.",
            ],
            "my": [
                "မြင့်သောနေရာ သို့မဟုတ် တရားဝင်ဘေးကင်းရေးစခန်းသို့ ရွှေ့ပါ။",
                "ရေမြုပ်လမ်း၊ ရေမြောင်း၊ ချောင်း၊ ရေစီးပြင်းသောနေရာများကို ရှောင်ပါ။",
                "ဖုန်း၊ power bank၊ မီးလင်းတိုင်၊ ဆေးဝါး၊ အရေးကြီးစာရွက်စာတမ်းများကို ယူထားပါ။",
                "ဒေသခံအာဏာပိုင်များ၏ ညွှန်ကြားချက်ကို နားထောင်ပြီး ထွက်ခွာရန်ပြောပါက ထွက်ခွာပါ။",
            ],
        },
        "avoid": {
            "en": ["Do not enter floodwater.", "Do not drive around barricades.", "Do not stay in low-lying areas if water is rising."],
            "my": ["ရေကြီးရေထဲ မဝင်ပါနှင့်။", "ပိတ်ထားသောလမ်း/တားမြစ်ချက်ကို မကျော်ပါနှင့်။", "ရေတက်နေပါက နိမ့်သောနေရာတွင် မနေပါနှင့်။"],
        },
    },
    "flood_causes": {
        "display_name": "Flood causes",
        "urgency": "low",
        "summary": "Explains common natural and human-related flood causes.",
        "keywords": ["causes", "reasons", "why flood", "main reason", "flood happen"],
        "source_ids": ["nws_flood_safety", "ready_floods"],
        "answer_templates": {
            "en": "Floods can be caused by heavy rainfall, river overflow, blocked drainage, storm surge, dam or levee problems, saturated soil, low-lying land, deforestation, and poor urban planning. In cities, blocked drains and too much concrete can make rainwater collect quickly.",
            "my": "ရေကြီးမှုဖြစ်ရခြင်း၏ အကြောင်းရင်းများမှာ မိုးသည်းထန်ခြင်း၊ မြစ်ရေတက်ခြင်း၊ ရေမြောင်းပိတ်ခြင်း၊ မုန်တိုင်းရေလှိုင်း၊ တမံ/ကမ်းပါးပြဿနာ၊ မြေဆီလွှာရေပြည့်ခြင်း၊ နိမ့်သောမြေပြင်၊ သစ်တောပြုန်းတီးခြင်းနှင့် မြို့ပြစီမံကိန်းမကောင်းခြင်းတို့ ဖြစ်နိုင်ပါတယ်။ မြို့ပြတွင် ရေမြောင်းပိတ်ခြင်းနှင့် ကွန်ကရစ်ဧရိယာများလွန်းခြင်းကြောင့် မိုးရေစုဆောင်းမှုမြန်နိုင်ပါတယ်။",
        },
        "action_steps": {
            "en": ["Check rainfall intensity and river level updates.", "Inspect drainage around homes and streets.", "Avoid building or staying in known flood-prone lowland areas when warnings are active."],
            "my": ["မိုးရေချိန်နှင့် မြစ်ရေကြီးမှုသတင်းကို စစ်ဆေးပါ။", "အိမ်ပတ်ဝန်းကျင်နှင့် လမ်းရေမြောင်းများကို စစ်ဆေးပါ။", "ရေကြီးသတိပေးချက်ရှိချိန်တွင် ရေကြီးလွယ်သောနိမ့်မြေများကို ရှောင်ပါ။"],
        },
        "avoid": {"en": ["Do not ignore drainage problems before heavy rain."], "my": ["မိုးသည်းမည့်အချိန် မတိုင်မီ ရေမြောင်းပြဿနာများကို မပေါ့ဆပါနှင့်။"]},
    },
    "weather_warning": {
        "display_name": "Flood warning signs and alerts",
        "urgency": "medium",
        "summary": "How to understand warnings and early signs of flooding.",
        "keywords": ["warning", "signs", "alert", "forecast", "weather"],
        "source_ids": ["ready_floods", "nws_flood_safety"],
        "answer_templates": {
            "en": "Flood warning signs include intense or continuous rain, rapidly rising streams or drains, water covering roads, official flood watches or warnings, and reports of upstream flooding. If you receive a warning, prepare to move quickly and avoid low-lying routes.",
            "my": "ရေကြီးနိုင်သည့် သတိပေးလက္ခဏာများမှာ မိုးသည်းထန်ခြင်း/အချိန်ကြာမိုးရွာခြင်း၊ ချောင်း/ရေမြောင်းရေမြန်မြန်တက်ခြင်း၊ လမ်းပေါ်ရေဖုံးခြင်း၊ တရားဝင် flood watch/warning ထုတ်ပြန်ခြင်းနှင့် အထက်ပိုင်းရေကြီးသတင်းများ ဖြစ်ပါတယ်။ သတိပေးချက်ရပါက အမြန်ရွှေ့နိုင်ရန် ပြင်ဆင်ပြီး နိမ့်သောလမ်းများကို ရှောင်ပါ။",
        },
        "action_steps": {
            "en": ["Monitor official weather alerts.", "Charge phones and power banks.", "Prepare important documents and emergency supplies.", "Plan a safe route to higher ground."],
            "my": ["တရားဝင်မိုးလေဝသသတင်းများကို စောင့်ကြည့်ပါ။", "ဖုန်းနှင့် power bank ကို အားသွင်းထားပါ။", "အရေးကြီးစာရွက်စာတမ်းနှင့် အရေးပေါ်ပစ္စည်းများ ပြင်ဆင်ပါ။", "မြင့်သောနေရာသို့ သွားရန် ဘေးကင်းသောလမ်းကြောင်း စီစဉ်ပါ။"],
        },
        "avoid": {"en": ["Do not wait until water enters the house before preparing."], "my": ["အိမ်ထဲရေဝင်မှ ပြင်ဆင်မည်ဟု မစောင့်ပါနှင့်။"]},
    },
    "storm_weather": {
        "display_name": "Storm and heavy rain safety",
        "urgency": "medium",
        "summary": "Safety guidance for severe rain or storm conditions that can lead to flooding.",
        "keywords": ["storm", "heavy rain", "thunderstorm", "rain", "wind"],
        "source_ids": ["ready_floods", "nws_flood_safety"],
        "answer_templates": {
            "en": "During heavy rain or storms, stay indoors if safe, keep away from flooded streets and drainage channels, and prepare to move if water rises. Heavy rain can cause flash flooding quickly, especially in low-lying or poorly drained areas.",
            "my": "မိုးသည်း/မုန်တိုင်းအချိန်တွင် ဘေးကင်းပါက အိမ်တွင်းနေပါ။ ရေမြုပ်လမ်းများ၊ ရေမြောင်းများ၊ ချောင်းများအနီး မသွားပါနှင့်။ ရေတက်လာပါက အမြန်ရွှေ့ရန် ပြင်ဆင်ထားပါ။ နိမ့်မြေ သို့မဟုတ် ရေစီးရေလာမကောင်းသောနေရာများတွင် ရုတ်တရက်ရေကြီးနိုင်ပါတယ်။",
        },
        "action_steps": {"en": ["Stay updated on weather alerts.", "Move valuables and documents above possible water level.", "Avoid unnecessary travel."], "my": ["မိုးလေဝသသတိပေးချက်များကို စောင့်ကြည့်ပါ။", "တန်ဖိုးရှိပစ္စည်းများနှင့် စာရွက်စာတမ်းများကို ရေမရောက်နိုင်သောနေရာတွင်ထားပါ။", "မလိုအပ်သောခရီးသွားလာမှုကို ရှောင်ပါ။"]},
        "avoid": {"en": ["Do not shelter near rivers, drains, or unstable slopes."], "my": ["မြစ်၊ ရေမြောင်း၊ မတည်ငြိမ်သောတောင်စောင်းအနီး မနားပါနှင့်။"]},
    },
    "water_supply": {
        "display_name": "Safe water and hygiene",
        "urgency": "medium",
        "summary": "Safe drinking water and hygiene advice during and after floods.",
        "keywords": ["water", "drinking", "hygiene", "clean water", "contaminated"],
        "source_ids": ["cdc_floodwater", "ready_kit"],
        "answer_templates": {
            "en": "Floodwater may contain sewage, chemicals, debris, and germs. Use bottled, boiled, or officially treated water for drinking and food preparation. Wash hands often, and clean any wound that touches floodwater.",
            "my": "ရေကြီးရေထဲတွင် မစင်ရေ၊ ဓာတုပစ္စည်း၊ အမှိုက်အကြွင်းအကျန်နှင့် ပိုးမွှားများ ပါနိုင်ပါတယ်။ သောက်ရန်နှင့် အစားအစာပြင်ရန် bottled water၊ ဆူအောင်ကျိုထားသောရေ သို့မဟုတ် တရားဝင်သန့်စင်ထားသောရေကို အသုံးပြုပါ။ လက်ကို မကြာခဏဆေးပြီး ဒဏ်ရာသည် ရေကြီးရေနှင့်ထိပါက သန့်ရှင်းအောင်ဆေးပါ။",
        },
        "action_steps": {"en": ["Store drinking water before heavy rain.", "Use sealed containers.", "Keep children away from floodwater.", "Seek medical help for infected wounds or illness."], "my": ["မိုးသည်းမတိုင်မီ သောက်ရေသိုလှောင်ပါ။", "ပိတ်ထားသောပုံး/ဘူးများကို အသုံးပြုပါ။", "ကလေးများကို ရေကြီးရေထဲ မဝင်စေပါနှင့်။", "ဒဏ်ရာရောင်ရမ်းခြင်း သို့မဟုတ် နာမကျန်းဖြစ်ပါက ဆေးဘက်ဆိုင်ရာအကူအညီယူပါ။"]},
        "avoid": {"en": ["Do not drink untreated flood-affected water.", "Do not let open wounds touch floodwater."], "my": ["ရေကြီးမှုထိခိုက်ထားသော မသန့်စင်ရေကို မသောက်ပါနှင့်။", "ဖွင့်ဒဏ်ရာကို ရေကြီးရေနှင့် မထိစေပါနှင့်။"]},
    },
    "food_supply": {
        "display_name": "Food and emergency supplies",
        "urgency": "medium",
        "summary": "Emergency food and supply preparation.",
        "keywords": ["food", "supplies", "emergency kit", "pack", "prepare"],
        "source_ids": ["ready_kit", "ready_floods"],
        "answer_templates": {
            "en": "Prepare an emergency kit with drinking water, ready-to-eat food, flashlight, extra batteries, power bank, first-aid kit, medicines, hygiene items, important documents, cash, and basic clothing. Keep the kit in a waterproof bag if possible.",
            "my": "အရေးပေါ်အိတ်ထဲတွင် သောက်ရေ၊ ချက်ရန်မလိုသောအစားအစာ၊ မီးလင်းတိုင်၊ ဘက်ထရီအပို၊ power bank၊ first-aid kit၊ ဆေးဝါး၊ သန့်ရှင်းရေးပစ္စည်း၊ အရေးကြီးစာရွက်စာတမ်း၊ ငွေသားနှင့် အဝတ်အစားအနည်းငယ် ထည့်ထားပါ။ ဖြစ်နိုင်ပါက waterproof bag ထဲထားပါ။",
        },
        "action_steps": {"en": ["Prepare supplies for several days.", "Include baby, elderly, and pet needs if relevant.", "Check expiry dates on food and medicine."], "my": ["ရက်အနည်းငယ်အတွက် လုံလောက်အောင် ပြင်ဆင်ပါ။", "ကလေး၊ သက်ကြီးရွယ်အို၊ အိမ်မွေးတိရစ္ဆာန်လိုအပ်ချက်များပါ ထည့်ပါ။", "အစားအစာနှင့် ဆေးဝါးသက်တမ်းကို စစ်ဆေးပါ။"]},
        "avoid": {"en": ["Do not eat food touched by floodwater unless authorities say it is safe."], "my": ["ရေကြီးရေနှင့်ထိထားသောအစားအစာကို တာဝန်ရှိသူများက ဘေးကင်းသည်ဟု မပြောသေးလျှင် မစားပါနှင့်။"]},
    },
    "shelter_evacuation": {
        "display_name": "Shelter and evacuation",
        "urgency": "high",
        "summary": "When and how to evacuate safely.",
        "keywords": ["evacuate", "shelter", "safe place", "leave home", "higher ground"],
        "source_ids": ["ready_floods", "nws_flood_safety"],
        "answer_templates": {
            "en": "Evacuate immediately if authorities tell you to leave, if water is rising near your home, or if your route may soon be blocked. Move to higher ground or an official shelter. Lock your home if time allows, but do not delay evacuation to collect belongings.",
            "my": "တာဝန်ရှိသူများက ထွက်ခွာရန်ပြောပါက၊ အိမ်အနီးရေတက်လာပါက သို့မဟုတ် လမ်းကြောင်းပိတ်နိုင်ပါက ချက်ချင်းထွက်ခွာပါ။ မြင့်သောနေရာ သို့မဟုတ် တရားဝင်ဘေးကင်းရေးစခန်းသို့ သွားပါ။ အချိန်ရှိပါက အိမ်ကိုပိတ်ထားနိုင်သော်လည်း ပစ္စည်းယူရန်အတွက် ထွက်ခွာမှုကို မနှောင့်နှေးပါနှင့်။",
        },
        "action_steps": {"en": ["Use official evacuation routes.", "Tell family members where you are going.", "Carry emergency kit and important documents.", "Help children, older adults, disabled people, and pets move early."], "my": ["တရားဝင်ထွက်ခွာလမ်းကြောင်းများကို အသုံးပြုပါ။", "မိသားစုဝင်များကို သွားမည့်နေရာပြောထားပါ။", "အရေးပေါ်အိတ်နှင့် စာရွက်စာတမ်းများ ယူပါ။", "ကလေး၊ သက်ကြီးရွယ်အို၊ မသန်စွမ်းသူများနှင့် အိမ်မွေးတိရစ္ဆာန်များကို အစောပိုင်းရွှေ့ပါ။"]},
        "avoid": {"en": ["Do not wait until the last minute.", "Do not choose routes through flood-prone roads."], "my": ["နောက်ဆုံးအချိန်ထိ မစောင့်ပါနှင့်။", "ရေကြီးလွယ်သောလမ်းကြောင်းကို မရွေးပါနှင့်။"]},
    },
    "medical_help": {
        "display_name": "Medical help and first aid",
        "urgency": "high",
        "summary": "Medical safety and when to seek help after flood exposure.",
        "keywords": ["medical", "injury", "wound", "sick", "first aid", "medicine"],
        "source_ids": ["cdc_floodwater", "ready_kit"],
        "answer_templates": {
            "en": "Floodwater can expose people to germs, chemicals, sharp objects, and electrical hazards. Clean wounds with safe water, cover them, and seek medical help if there is deep injury, fever, increasing pain, redness, swelling, or signs of infection.",
            "my": "ရေကြီးရေထဲတွင် ပိုးမွှား၊ ဓာတုပစ္စည်း၊ ချွန်ထက်သောအရာများနှင့် လျှပ်စစ်အန္တရာယ်များ ရှိနိုင်ပါတယ်။ ဒဏ်ရာကို သန့်သောရေနှင့်ဆေးပြီး ဖုံးအုပ်ထားပါ။ ဒဏ်ရာနက်ခြင်း၊ ဖျားခြင်း၊ နာကျင်မှုပိုလာခြင်း၊ နီခြင်း၊ ဖောင်းခြင်း သို့မဟုတ် ပိုးဝင်သည့်လက္ခဏာရှိပါက ဆေးဘက်ဆိုင်ရာအကူအညီယူပါ။",
        },
        "action_steps": {"en": ["Keep medicines in a waterproof bag.", "Bring prescriptions during evacuation.", "Call emergency services for serious injury or breathing problems."], "my": ["ဆေးဝါးများကို waterproof bag ထဲထားပါ။", "ထွက်ခွာချိန်တွင် prescription ဆေးများ ယူပါ။", "ပြင်းထန်ဒဏ်ရာ သို့မဟုတ် အသက်ရှူပြဿနာရှိပါက အရေးပေါ်ဝန်ဆောင်မှုကို ခေါ်ပါ။"]},
        "avoid": {"en": ["Do not ignore wounds exposed to floodwater."], "my": ["ရေကြီးရေနှင့်ထိထားသောဒဏ်ရာကို မပေါ့ဆပါနှင့်။"]},
    },
    "search_and_rescue": {
        "display_name": "Search and rescue / trapped people",
        "urgency": "critical",
        "summary": "Guidance when someone is trapped or needs rescue.",
        "keywords": ["trapped", "rescue", "missing", "help", "stranded"],
        "source_ids": ["ready_floods", "nws_flood_safety"],
        "answer_templates": {
            "en": "If someone is trapped or in immediate danger, contact local emergency services immediately. Move to the highest safe place, signal your location, conserve phone battery, and do not enter moving floodwater to attempt a rescue unless you are trained and equipped.",
            "my": "တစ်ယောက်ယောက် ပိတ်မိနေခြင်း သို့မဟုတ် ချက်ချင်းအန္တရာယ်ရှိနေပါက ဒေသခံအရေးပေါ်ဝန်ဆောင်မှုကို ချက်ချင်းဆက်သွယ်ပါ။ ဘေးကင်းသော အမြင့်ဆုံးနေရာသို့ ရွှေ့ပြီး တည်နေရာကို အချက်ပြပါ။ ဖုန်းဘက်ထရီကို ချွေတာပါ။ သင်သည် သင်တန်းနှင့်ကိရိယာမရှိပါက ရေစီးပြင်းသောရေထဲဝင်ပြီး ကယ်ဆယ်ရန် မကြိုးစားပါနှင့်။",
        },
        "action_steps": {"en": ["Call emergency services.", "Share exact location and number of people.", "Use lights, whistle, bright cloth, or phone to signal.", "Stay together if possible."], "my": ["အရေးပေါ်ဝန်ဆောင်မှုကို ခေါ်ပါ။", "တိကျသောတည်နေရာနှင့် လူဦးရေကို ပြောပါ။", "မီး၊ whistle၊ အရောင်တောက်ပသောအဝတ် သို့မဟုတ် ဖုန်းဖြင့် အချက်ပြပါ။", "ဖြစ်နိုင်ပါက အတူတကွနေပါ။"]},
        "avoid": {"en": ["Do not enter fast water for rescue without training."], "my": ["သင်တန်းမရှိဘဲ ရေစီးပြင်းထဲဝင်၍ ကယ်ဆယ်ရန် မလုပ်ပါနှင့်။"]},
    },
    "road_transport": {
        "display_name": "Road and transport safety",
        "urgency": "high",
        "summary": "Driving and walking safety near floodwater.",
        "keywords": ["drive", "road", "car", "transport", "flooded road", "bridge"],
        "source_ids": ["nws_tadd", "ready_floods"],
        "answer_templates": {
            "en": "Do not drive or walk through flooded roads. Water may be deeper or faster than it looks, and the road surface may be washed out. Turn around and choose another route, even if other vehicles seem to pass.",
            "my": "ရေမြုပ်နေသောလမ်းကို ကားဖြင့်ဖြတ်ခြင်း သို့မဟုတ် လမ်းလျှောက်ဖြတ်ခြင်း မလုပ်ပါနှင့်။ ရေသည် မြင်ရသလောက်မဟုတ်ဘဲ ပိုနက်/ပိုမြန်နိုင်ပြီး လမ်းအောက်ပိုင်းပျက်စီးနေနိုင်ပါတယ်။ အခြားကားများဖြတ်နိုင်သလိုမြင်ရသော်လည်း ပြန်လှည့်ပြီး အခြားလမ်းရွေးပါ။",
        },
        "action_steps": {"en": ["Turn around at flooded roads.", "Obey barricades and road closure signs.", "Avoid bridges over fast-moving water.", "Delay travel until authorities say roads are safe."], "my": ["ရေမြုပ်လမ်းတွေ့ပါက ပြန်လှည့်ပါ။", "လမ်းပိတ်ဆိုင်းဘုတ်များနှင့်တားမြစ်ချက်များကို လိုက်နာပါ။", "ရေစီးပြင်းသောတံတားများကို ရှောင်ပါ။", "တာဝန်ရှိသူများက လမ်းဘေးကင်းကြောင်းမပြောမချင်း ခရီးရွှေ့ဆိုင်းပါ။"]},
        "avoid": {"en": ["Do not drive around barricades.", "Do not assume shallow water is safe."], "my": ["လမ်းပိတ်တားဆီးချက်ကို မကျော်ပါနှင့်။", "ရေအနည်းငယ်သာရှိသည်ဟုထင်ပြီး ဘေးကင်းသည်ဟု မယူဆပါနှင့်။"]},
    },
    "infrastructure_damage": {
        "display_name": "Home and infrastructure damage",
        "urgency": "medium",
        "summary": "Safety around damaged homes, utilities, bridges, and buildings.",
        "keywords": ["damage", "building", "bridge", "house", "utility", "collapse"],
        "source_ids": ["cdc_reenter_home", "epa_cleanup", "cdc_cleanup"],
        "answer_templates": {
            "en": "After flooding, buildings, bridges, roads, gas lines, and electrical systems may be damaged. Return home only when authorities say it is safe. Watch for structural cracks, loose wires, gas smells, and contaminated mud or debris.",
            "my": "ရေကြီးပြီးနောက် အဆောက်အအုံ၊ တံတား၊ လမ်း၊ ဓာတ်ငွေ့ပိုက်နှင့် လျှပ်စစ်စနစ်များ ပျက်စီးနိုင်ပါတယ်။ တာဝန်ရှိသူများက ဘေးကင်းကြောင်းပြောမှ အိမ်ပြန်ပါ။ အဆောက်အအုံကွဲခြင်း၊ ဝိုင်ယာကြိုးလွတ်ခြင်း၊ ဓာတ်ငွေ့နံ့၊ မသန့်သောရွှံ့/အမှိုက်များကို သတိထားပါ။",
        },
        "action_steps": {"en": ["Inspect from outside before entering.", "Leave immediately if you smell gas or see major damage.", "Use protective gloves and boots during cleanup."], "my": ["ဝင်မည့်မတိုင်မီ အပြင်ဘက်မှ စစ်ဆေးပါ။", "ဓာတ်ငွေ့နံ့ရပါက သို့မဟုတ် ကြီးမားသောပျက်စီးမှုတွေ့ပါက ချက်ချင်းထွက်ပါ။", "သန့်ရှင်းရေးလုပ်ချိန်တွင် လက်အိတ်နှင့်ဖိနပ်ကာကွယ်ရေးသုံးပါ။"]},
        "avoid": {"en": ["Do not enter badly damaged buildings.", "Do not touch loose wires."], "my": ["အလွန်ပျက်စီးသောအဆောက်အအုံထဲ မဝင်ပါနှင့်။", "လွတ်နေသောဝိုင်ယာကြိုးများကို မထိပါနှင့်။"]},
    },
    "electricity_safety": {
        "display_name": "Electrical safety",
        "urgency": "high",
        "summary": "Electrical hazards during and after floods.",
        "keywords": ["electric", "power", "wire", "switch", "generator", "shock"],
        "source_ids": ["cdc_reenter_home"],
        "answer_templates": {
            "en": "Floodwater and electricity are a deadly combination. Do not touch electrical equipment, switches, outlets, or wires while wet or standing in water. If power must be turned off, ask qualified personnel or the power company when possible.",
            "my": "ရေကြီးရေနှင့် လျှပ်စစ်သည် အသက်အန္တရာယ်ရှိနိုင်ပါတယ်။ ကိုယ်စိုနေချိန် သို့မဟုတ် ရေထဲရပ်နေချိန်တွင် လျှပ်စစ်ကိရိယာ၊ switch၊ socket၊ ဝိုင်ယာကြိုးများကို မထိပါနှင့်။ မီးပိတ်ရန်လိုပါက ဖြစ်နိုင်သမျှ ကျွမ်းကျင်သူ သို့မဟုတ် လျှပ်စစ်ကုမ္ပဏီကို ဆက်သွယ်ပါ။",
        },
        "action_steps": {"en": ["Stay away from downed wires.", "Do not use wet electrical appliances.", "Use generators outdoors only and away from windows."], "my": ["ကျနေသောဝိုင်ယာကြိုးများအနီး မသွားပါနှင့်။", "စိုနေသောလျှပ်စစ်ကိရိယာများကို မသုံးပါနှင့်။", "generator ကို အပြင်ဘက်တွင်သာ သုံးပြီး ပြတင်းပေါက်များမှဝေးဝေးထားပါ။"]},
        "avoid": {"en": ["Never turn power on or off while standing in water."], "my": ["ရေထဲရပ်နေချိန် မီးဖွင့်/ပိတ် မလုပ်ပါနှင့်။"]},
    },
    "after_flood_cleanup": {
        "display_name": "After-flood cleanup and mold prevention",
        "urgency": "medium",
        "summary": "Cleanup, drying, mold prevention, and safe reentry after a flood.",
        "keywords": ["after flood", "cleanup", "mold", "return home", "dry"],
        "source_ids": ["cdc_cleanup", "cdc_reenter_home", "epa_cleanup"],
        "answer_templates": {
            "en": "After a flood, return only when officials say it is safe. Wear boots, gloves, and a mask if cleaning. Remove standing water if safe, air out the building, and dry wet areas as quickly as possible to reduce mold. Throw away items that cannot be cleaned and dried safely.",
            "my": "ရေကြီးပြီးနောက် တာဝန်ရှိသူများက ဘေးကင်းကြောင်းပြောမှ အိမ်ပြန်ပါ။ သန့်ရှင်းရေးလုပ်ပါက ဖိနပ်၊ လက်အိတ်နှင့် mask အသုံးပြုပါ။ ဘေးကင်းပါက ရေတင်ကျန်မှုကို ဖယ်ရှားပြီး အိမ်ကိုလေဝင်လေထွက်ကောင်းအောင်လုပ်ပါ။ မှိုမပေါက်စေရန် စိုနေသောနေရာများကို အမြန်ခြောက်အောင်လုပ်ပါ။ သန့်ရှင်း၍ခြောက်အောင်မလုပ်နိုင်သောပစ္စည်းများကို စွန့်ပစ်ပါ။",
        },
        "action_steps": {"en": ["Photograph damage before cleanup if needed for records.", "Ventilate rooms.", "Dry wet materials quickly.", "Use protective gear around mud and debris."], "my": ["မှတ်တမ်း/အာမခံအတွက်လိုပါက သန့်ရှင်းရေးမလုပ်မီ ပျက်စီးမှုကို ဓာတ်ပုံရိုက်ထားပါ။", "အခန်းများကို လေဝင်လေထွက်ကောင်းစေပါ။", "စိုနေသောပစ္စည်းများကို အမြန်ခြောက်စေပါ။", "ရွှံ့နှင့်အမှိုက်များကို ကိုင်တွယ်ရာတွင် ကာကွယ်ရေးပစ္စည်းသုံးပါ။"]},
        "avoid": {"en": ["Do not enter if there is major structural damage.", "Do not mix cleaning chemicals."], "my": ["အဆောက်အအုံပျက်စီးမှုကြီးပါက မဝင်ပါနှင့်။", "သန့်ရှင်းရေးဓာတုပစ္စည်းများကို မရောပါနှင့်။"]},
    },
    "protect_home": {
        "display_name": "Protect home before flooding",
        "urgency": "medium",
        "summary": "Preparedness steps to reduce damage before flooding.",
        "keywords": ["protect home", "prepare house", "barrier", "before flood", "prevent damage"],
        "source_ids": ["ready_floods", "ready_kit"],
        "answer_templates": {
            "en": "Before flooding, move valuables and documents to higher shelves, clear drains where safe, prepare sandbags or barriers if available, unplug appliances if advised and safe, and keep an emergency kit ready. Know your evacuation route before water rises.",
            "my": "ရေမကြီးမီ တန်ဖိုးရှိပစ္စည်းနှင့်စာရွက်စာတမ်းများကို မြင့်သောနေရာသို့ရွှေ့ပါ။ ဘေးကင်းပါက ရေမြောင်းများရှင်းပါ။ ရရှိနိုင်ပါက sandbag/barrier ပြင်ဆင်ပါ။ ဘေးကင်းပြီး အကြံပြုချက်ရှိပါက လျှပ်စစ်ပစ္စည်းများကို plug ဖြုတ်ပါ။ အရေးပေါ်အိတ်ပြင်ထားပြီး ရေမတက်မီ ထွက်ခွာလမ်းကြောင်းသိထားပါ။",
        },
        "action_steps": {"en": ["Clear gutters and drains before rain.", "Move electronics higher.", "Prepare emergency contacts.", "Check neighbors who may need help."], "my": ["မိုးမရွာမီ gutter နှင့်ရေမြောင်းများကိုရှင်းပါ။", "လျှပ်စစ်ပစ္စည်းများကို မြင့်သောနေရာထားပါ။", "အရေးပေါ်ဆက်သွယ်ရန်နံပါတ်များ ပြင်ဆင်ပါ။", "အကူအညီလိုနိုင်သော အိမ်နီးချင်းများကို စစ်ဆေးပါ။"]},
        "avoid": {"en": ["Do not wait until water reaches your door to prepare."], "my": ["ရေတံခါးဝရောက်မှ ပြင်ဆင်မည်ဟု မစောင့်ပါနှင့်။"]},
    },
    "security_services": {
        "display_name": "Security and official services",
        "urgency": "medium",
        "summary": "Official services, reporting, and staying informed.",
        "keywords": ["police", "security", "official", "report", "service"],
        "source_ids": ["ready_floods", "nws_flood_safety"],
        "answer_templates": {
            "en": "During a flood, follow instructions from emergency services, police, local authorities, and weather agencies. Report blocked roads, trapped people, downed wires, or damaged bridges through official emergency channels. Avoid spreading unverified information.",
            "my": "ရေကြီးချိန်တွင် အရေးပေါ်ဝန်ဆောင်မှု၊ ရဲ၊ ဒေသခံအာဏာပိုင်နှင့် မိုးလေဝသဌာနများ၏ ညွှန်ကြားချက်ကို လိုက်နာပါ။ လမ်းပိတ်ခြင်း၊ ပိတ်မိနေသူ၊ ဝိုင်ယာကြိုးကျခြင်း၊ တံတားပျက်ခြင်းတို့ကို တရားဝင်အရေးပေါ်လမ်းကြောင်းမှ အကြောင်းကြားပါ။ အတည်မပြုနိုင်သောသတင်းများ မဖြန့်ပါနှင့်။",
        },
        "action_steps": {"en": ["Use official emergency numbers.", "Share clear location details.", "Follow evacuation and road closure orders."], "my": ["တရားဝင်အရေးပေါ်ဖုန်းနံပါတ်များကို အသုံးပြုပါ။", "တိကျသောတည်နေရာကို ပြောပါ။", "ထွက်ခွာရန်နှင့်လမ်းပိတ်ညွှန်ကြားချက်များကို လိုက်နာပါ။"]},
        "avoid": {"en": ["Do not spread rumors during emergencies."], "my": ["အရေးပေါ်အချိန်တွင် သတင်းမှား/ကောလဟာလ မဖြန့်ပါနှင့်။"]},
    },
    "general_aid_request": {
        "display_name": "General aid request",
        "urgency": "medium",
        "summary": "General guidance when the user asks for flood help but the exact need is unclear.",
        "keywords": ["help", "aid", "need assistance", "what should i do"],
        "source_ids": ["ready_floods", "ready_kit", "nws_flood_safety"],
        "answer_templates": {
            "en": "I can help with flood safety, evacuation, emergency kits, road safety, medical concerns, and cleanup. If you are in immediate danger, contact local emergency services first. Tell me what is happening: rising water, trapped people, flooded road, medical issue, or preparation question?",
            "my": "ရေကြီးဘေးကင်းရေး၊ ထွက်ခွာခြင်း၊ အရေးပေါ်အိတ်၊ လမ်းဘေးကင်းရေး၊ ဆေးဘက်ဆိုင်ရာပြဿနာနှင့် သန့်ရှင်းရေးအကြောင်း ကူညီနိုင်ပါတယ်။ ချက်ချင်းအန္တရာယ်ရှိပါက ဒေသခံအရေးပေါ်ဝန်ဆောင်မှုကို အရင်ဆက်သွယ်ပါ။ ဘာဖြစ်နေသလဲ ပြောပါ—ရေတက်နေသလား၊ လူပိတ်မိနေသလား၊ လမ်းရေမြုပ်နေသလား၊ ဆေးဘက်ဆိုင်ရာပြဿနာလား၊ ပြင်ဆင်ရေးမေးခွန်းလား။",
        },
        "action_steps": {"en": ["Describe the situation clearly.", "Share location if asking for emergency routing.", "Use emergency services for immediate danger."], "my": ["အခြေအနေကိုရှင်းရှင်းပြောပါ။", "အရေးပေါ်လမ်းညွှန်လိုပါက တည်နေရာပြောပါ။", "ချက်ချင်းအန္တရာယ်ရှိပါက အရေးပေါ်ဝန်ဆောင်မှုသုံးပါ။"]},
        "avoid": {"en": ["Do not rely only on chatbot advice during life-threatening danger."], "my": ["အသက်အန္တရာယ်ရှိသောအခြေအနေတွင် chatbot အကြံပြုချက်တစ်ခုတည်းကို မမှီခိုပါနှင့်။"]},
    },
    "fallback": {
        "display_name": "Fallback clarification",
        "urgency": "low",
        "summary": "Used when the classifier cannot confidently map a question to a topic.",
        "keywords": ["unknown", "fallback"],
        "source_ids": ["ready_floods"],
        "answer_templates": {
            "en": "I may not have understood the question clearly. I can help with flood causes, flood warnings, evacuation, emergency kits, road safety, electricity safety, medical help, and cleanup. Please ask again with a little more detail.",
            "my": "မေးခွန်းကို ရှင်းရှင်းလင်းလင်း မနားလည်နိုင်သေးပါ။ ရေကြီးရခြင်းအကြောင်းရင်း၊ သတိပေးချက်၊ ထွက်ခွာခြင်း၊ အရေးပေါ်အိတ်၊ လမ်းဘေးကင်းရေး၊ လျှပ်စစ်ဘေးကင်းရေး၊ ဆေးဘက်ဆိုင်ရာအကူအညီနှင့် သန့်ရှင်းရေးတို့ကို ကူညီနိုင်ပါတယ်။ နည်းနည်းပိုအသေးစိတ် ပြန်မေးပေးပါ။",
        },
        "action_steps": {"en": ["Ask about one topic at a time."], "my": ["တစ်ကြိမ်လျှင် အကြောင်းအရာတစ်ခုစီ မေးပါ။"]},
        "avoid": {"en": [], "my": []},
    },
}

INTENT_TO_KB_MAPPING = {
    "flood_event": "flood_event",
    "storm_weather": "storm_weather",
    "weather_warning": "weather_warning",
    "water_supply": "water_supply",
    "food_supply": "food_supply",
    "shelter_evacuation": "shelter_evacuation",
    "medical_help": "medical_help",
    "search_and_rescue": "search_and_rescue",
    "road_transport": "road_transport",
    "infrastructure_damage": "infrastructure_damage",
    "security_services": "security_services",
    "general_aid_request": "general_aid_request",
    # Extra direct intents that the future app can route with keyword/LLM/RAG layer.
    "flood_causes": "flood_causes",
    "electricity_safety": "electricity_safety",
    "after_flood_cleanup": "after_flood_cleanup",
    "protect_home": "protect_home",
    "fallback": "fallback",
}


def build_knowledge_base() -> dict:
    return {
        "metadata": {
            "project": "FloodMind AI Flood Assistant",
            "step": "Step 3 - Flood Safety Knowledge Base",
            "version": "1.0.0",
            "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "languages_included": ["en", "my"],
            "intended_use": "Map predicted flood/disaster intents to practical safety responses.",
            "safety_note": "This chatbot provides educational safety guidance. In immediate danger, contact local emergency services and follow official instructions.",
        },
        "source_catalog": SOURCE_CATALOG,
        "intents": KB_INTENTS,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def validate_kb(kb: dict) -> dict:
    errors = []
    warnings = []
    intents = kb.get("intents", {})

    required_intents = set(INTENT_TO_KB_MAPPING.values())
    missing = sorted(required_intents - set(intents.keys()))
    if missing:
        errors.append(f"Missing required KB intents: {missing}")

    for intent, entry in intents.items():
        for field in ["display_name", "urgency", "summary", "source_ids", "answer_templates", "action_steps", "avoid"]:
            if field not in entry:
                errors.append(f"{intent}: missing field {field}")
        for lang in ["en", "my"]:
            answer = entry.get("answer_templates", {}).get(lang, "")
            if len(answer.strip()) < 20:
                errors.append(f"{intent}: answer for {lang} is too short or missing")
            steps = entry.get("action_steps", {}).get(lang, [])
            if intent != "fallback" and len(steps) < 2:
                warnings.append(f"{intent}: fewer than 2 action steps for {lang}")
        for source_id in entry.get("source_ids", []):
            if source_id not in SOURCE_CATALOG:
                errors.append(f"{intent}: unknown source_id {source_id}")

    return {
        "ok": len(errors) == 0,
        "intent_count": len(intents),
        "source_count": len(kb.get("source_catalog", {})),
        "languages": kb.get("metadata", {}).get("languages_included", []),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    kb = build_knowledge_base()
    validation = validate_kb(kb)

    write_json(MODELS_DIR / "flood_safety_knowledge_base.json", kb)
    write_json(MODELS_DIR / "intent_to_kb_mapping.json", INTENT_TO_KB_MAPPING)

    # Backward-compatible simple answer KB for chatbot engines that expect answer_en/answer_my fields.
    simple_kb = {
        intent: {
            "answer_en": entry["answer_templates"]["en"],
            "answer_my": entry["answer_templates"]["my"],
            "urgency": entry["urgency"],
            "source_ids": entry["source_ids"],
        }
        for intent, entry in KB_INTENTS.items()
    }
    write_json(MODELS_DIR / "disaster_answer_kb.json", simple_kb)

    with (DATA_DIR / "flood_safety_sources.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["source_id", "title", "organization", "url", "notes"])
        writer.writeheader()
        for source_id, source in SOURCE_CATALOG.items():
            writer.writerow({"source_id": source_id, **source})

    with (DATA_DIR / "knowledge_base_intent_summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["intent", "display_name", "urgency", "source_ids", "keyword_count"])
        writer.writeheader()
        for intent, entry in KB_INTENTS.items():
            writer.writerow({
                "intent": intent,
                "display_name": entry["display_name"],
                "urgency": entry["urgency"],
                "source_ids": ";".join(entry["source_ids"]),
                "keyword_count": len(entry.get("keywords", [])),
            })

    write_json(REPORTS_DIR / "03_KB_VALIDATION_REPORT.json", validation)

    md_lines = [
        "# Step 3 Knowledge Base Validation Report",
        "",
        f"Generated: {datetime.utcnow().isoformat(timespec='seconds')}Z",
        "",
        f"Validation status: {'PASS' if validation['ok'] else 'FAIL'}",
        f"Intent entries: {validation['intent_count']}",
        f"Source entries: {validation['source_count']}",
        f"Languages included: {', '.join(validation['languages'])}",
        "",
        "## Errors",
    ]
    md_lines += [f"- {error}" for error in validation["errors"]] or ["- None"]
    md_lines += ["", "## Warnings"]
    md_lines += [f"- {warning}" for warning in validation["warnings"]] or ["- None"]
    (REPORTS_DIR / "03_KB_VALIDATION_REPORT.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("Step 3 knowledge base build complete.")
    print(json.dumps(validation, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
