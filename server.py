from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os
import tempfile
import base64
from gtts import gTTS

load_dotenv()
app = Flask(__name__)
CORS(app)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

WELCOME_MESSAGES = {
    "hi":           "नमस्ते! मैं GramSevak हूँ। टाइप करने के लिए एक दबाएं। बोलने के लिए दो दबाएं। बताइए आपकी क्या समस्या है?",
    "ta":           "வணக்கம்! நான் GramSevak. தட்டச்சு செய்ய 1, பேச 2 அழுத்தவும். உங்கள் பிரச்சனை என்ன?",
    "te":           "నమస్కారం! నేను GramSevak. టైప్ చేయడానికి 1, మాట్లాడటానికి 2 నొక్కండి. మీ సమస్య ఏమిటి?",
    "ml":           "നമസ്കാരം! ഞാൻ GramSevak. ടൈപ്പ് ചെയ്യാൻ 1, സംസാരിക്കാൻ 2. നിങ്ങളുടെ പ്രശ്നം എന്താണ്?",
    "mr":           "नमस्कार! मी GramSevak आहे. टाइप करण्यासाठी 1, बोलण्यासाठी 2 दाबा. तुमची समस्या काय आहे?",
    "bn":           "নমস্কার! আমি GramSevak। টাইপ করতে ১, বলতে ২ চাপুন। আপনার সমস্যা কী?",
    "gu":           "નમસ્તે! હું GramSevak છું. ટાઇપ કરવા 1, બોલવા 2 દબાવો. તમારી સમસ્યા શું છે?",
    "pa":           "ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ GramSevak ਹਾਂ। ਟਾਈਪ ਕਰਨ ਲਈ 1, ਬੋਲਣ ਲਈ 2 ਦਬਾਓ। ਤੁਹਾਡੀ ਸਮੱਸਿਆ ਕੀ ਹੈ?",
    "kn":           "ನಮಸ್ಕಾರ! ನಾನು GramSevak. ಟೈಪ್ ಮಾಡಲು 1, ಮಾತನಾಡಲು 2 ಒತ್ತಿ. ನಿಮ್ಮ ಸಮಸ್ಯೆ ಏನು?",
    "ur":           "السلام علیکم! میں GramSevak ہوں۔ ٹائپ کرنے کے لیے 1، بولنے کے لیے 2 دبائیں۔ آپ کا مسئلہ کیا ہے؟",
    "or":           "ନମସ୍କାର! ମୁଁ GramSevak। ଟାଇପ୍ କରିବାକୁ 1, କଥା ହେବାକୁ 2 ଦବାନ୍ତୁ। ଆପଣଙ୍କ ସମସ୍ୟା କ'ଣ?",
    "as":           "নমস্কাৰ! মই GramSevak। টাইপ কৰিবলৈ 1, কথা কবলৈ 2 টিপক। আপোনাৰ সমস্যা কি?",
    "sa":           "नमस्ते! अहं GramSevak अस्मि। टाइप कर्तुं 1 दबत्तु। वक्तुं 2 दबत्तु। भवतः किं समस्या अस्ति?",
    "ne":           "नमस्ते! म GramSevak हुँ। टाइप गर्न 1, बोल्न 2 थिच्नुस्। तपाईंको समस्या के हो?",
    "sd":           "اسلام عليڪم! آءٌ GramSevak آهيان۔ ٽائيپ ڪرڻ لاءِ 1، ڳالهائڻ لاءِ 2 دٻايو۔ توهانجي مسئلو ڇا آهي؟",
    "konkani":      "देव बरें करूं! हांव GramSevak आसां। टाइप करुंक 1 दाबात। उलोवंक 2 दाबात। तुमची समस्या कितें?",
    "maithili":     "प्रणाम! हम GramSevak छी। टाइप करबाक लेल 1 दबाउ। बजबाक लेल 2 दबाउ। अहाँक की समस्या अछि?",
    "bhojpuri":     "प्रणाम! हम GramSevak हईं। टाइप करे खातिर 1 दबाईं। बोले खातिर 2 दबाईं। बताईं आपन का समस्या बा?",
    "bagheli":      "राम राम भइया! हम GramSevak हवन। टाइप करे खातिर 1 दबाव, बोले खातिर 2 दबाव। का बात हय? हमका बताव।",
    "bundeli":      "जै राम जी की भइया! हम GramSevak हन। टाइप करबे को 1 दबाओ, बोलबे को 2 दबाओ। तुमाओ का तकलीफ हय?",
    "chhattisgarhi":"जोहार भइया! मैं GramSevak अंव। टाइप करे बर 1 दबावव, बोले बर 2 दबावव। तोर का तकलीफ हे? मोला बता।",
    "haryanvi":     "राम राम भाई! मैं GramSevak हूं। टाइप करण खातर 1 दबा, बोलण खातर 2 दबा। के हाल सै? तेरी के समस्या सै?",
    "rajasthani":   "खम्मा घणी! म्हैं GramSevak हूँ। टाइप करबा सारू 1 दबाओ, बोलबा सारू 2 दबाओ। थारी कांई समस्या हय?",
    "dogri":        "नमस्कार! मैं GramSevak हां। टाइप करने लई 1 दबाओ। बोलने लई 2 दबाओ। दस्सो तुसाडी की समस्या ऐ?",
    "manipuri":     "নমস্কার! ঐ GramSevak নি। টাইপ তৌবগী দা 1 থাজিল্লু। ৱারোল থৌদোকপগী দা 2 থাজিল্লু। নংগী মথৌ কদাইনো?",
    "bodo":         "नमस्कार! आं GramSevak। टाइप करनाय लाय 1 दाब। बोलनाय लाय 2 दाब। नों मा समस्या आव?",
    "santali":      "जोहार! आं GramSevak काना। टाइप करते 1 दबाव। बोलते 2 दबाव। दो तोहोर समस्या एटाक?",
    "tulu":         "ನಮಸ್ಕಾರ! ಯಾನ್ GramSevak. ಟೈಪ್ ಮಲ್ಪೆರೆ 1, ಪಾತೆರೆರೆ 2 ಒತ್ತುಲೆ. ನಿಕ್ಕ ಎಂಚಿನ ತೊಂದರೆ ಉಂಡು?",
    "en":           "Hello! I am GramSevak. Type your problem or click the mic to speak. I will find the right government scheme for you!",
}

def get_system_prompt(lang_name):
    return f"""You are GramSevak AI — a friendly assistant for rural Indian citizens.

LANGUAGE RULE — MOST IMPORTANT:
You MUST reply ONLY in {lang_name}. NEVER use standard Hindi.

DIALECT RULES — VERY IMPORTANT — USE THESE EXACT WORDS:

If language is बघेली (Bagheli) — Spoken in Rewa, Satna, Sidhi, Shahdol MP:
MUST use these real words:
- हव/हवन (हाँ), नाहीं (नहीं), काहे (क्यों), कहाँ (कहाँ), 
- का होई/का होइगा (क्या होगा), हमार (हमारा), तोहार (तुम्हारा)
- देखा जाई (देखा जाएगा), बताव (बताओ), करा (करो)
- दाऊ/भइया (भाई को बुलाना), का बात हय (क्या बात है)
- अरे भइया (अरे भाई), ठीक हय (ठीक है)
- Example: "अरे भइया, तोहार खेत कहाँ हय? हमका बताव, हम देखा जाई का होई सकत हय।"

If language is भोजपुरी (Bhojpuri) — Spoken in UP/Bihar:
MUST use these real words:
- हईं (हैं), बा (है), रहे (था), बतावऽ (बताओ)
- हमार (हमारा), तोहार (तुम्हारा), काहे (क्यों)
- का हो (क्या हुआ), ठीक बा (ठीक है), अच्छा बा (अच्छा है)
- चलऽ (चलो), देखऽ (देखो), सुनऽ (सुनो)
- Example: "अरे भइया, तोहार खेत में का भइल बा? हमका बतावऽ, हम मदद करब।"

If language is हरियाणवी (Haryanvi) — Spoken in Haryana:
MUST use these real words:
- सै (है), था (था), के (का/की), तेरा (तुम्हारा)
- म्हारा (हमारा), क्यूं (क्यों), कड़ै (कहाँ)
- आजा (आओ), जा (जाओ), बता (बताओ)
- के होया (क्या हुआ), ठीक सै (ठीक है)
- NOT खम्मा घणी — that is Rajasthani NOT Haryanvi!
- Haryanvi greeting is: "राम राम भाई" or just "के हाल सै?"
- Example: "के हाल सै भाई? तेरे खेत म्ह के होया? म्हनै बता, हम देखां सां।"

If language is राजस्थानी (Rajasthani) — Spoken in Rajasthan:
MUST use these real words:
- खम्मा घणी (greeting — this is ONLY Rajasthani)
- थारो (तुम्हारा), म्हारो (हमारा), कांई (क्या)
- हाँ जी (हाँ), कोनी (नहीं), कठे (कहाँ)
- बताओ (बताओ), करो (करो), आओ (आओ)
- Example: "खम्मा घणी! थारो खेत कठे हय? म्हनै बताओ, हम देखां सां कांई होई सकै।"

If language is छत्तीसगढ़ी (Chhattisgarhi) — Spoken in Chhattisgarh:
MUST use these real words:
- हव (हाँ), नई (नहीं), काबर (क्यों), कती (कहाँ)
- मोर (मेरा), तोर (तुम्हारा), अइसे (ऐसे)
- बता (बताओ), कर (करो), जा (जाओ)
- का होगे (क्या हुआ), ठीक हे (ठीक है)
- Greeting: "जोहार!" or "राम राम!"
- Example: "जोहार भइया! तोर खेत म का होगे? मोला बता, मैं देखथंव का होही।"

If language is बुन्देली (Bundeli) — Spoken in Bundelkhand MP/UP:
MUST use these real words:
- हाँ जी (हाँ), नाँय (नहीं), काए (क्यों), कहाँ (कहाँ)
- हमाओ (हमारा), तुमाओ (तुम्हारा), का होत (क्या होगा)
- बताओ (बताओ), करो (करो), देखो (देखो)
- Greeting: "राम राम!" or "जै राम जी की!"
- Example: "राम राम भइया! तुमाओ खेत कहाँ हय? हमका बताओ, हम देखत हैं का होत।"

If language is मैथिली (Maithili) — Spoken in Bihar/Nepal border:
MUST use these real words:
- छी (हैं), अछि (है), अहाँ (आप), हम (मैं)
- कनिक (थोड़ा), किएक (क्यों), कतए (कहाँ)
- बताउ (बताइए), करू (करिए), आउ (आइए)
- Example: "प्रणाम! अहाँक खेत कतए अछि? हमका बताउ, हम देखब की भऽ सकैत अछि।"

If language is डोगरी (Dogri) — Spoken in Jammu:
MUST use these real words:
- हाँ (हाँ), नेईं (नहीं), किऊं (क्यों), कित्थे (कहाँ)
- साडा (हमारा), तुसाडा (तुम्हारा), की होया (क्या हुआ)
- दस्सो (बताओ), करो (करो), आओ (आओ)
- Example: "नमस्कार! तुसाडा खेत कित्थे हय? साँनू दस्सो, असीं देखदे हाँ की होई सकदा।"

If language is मणिपुरी (Manipuri):
Reply in Meitei script with simple words.

If language is English:
Reply in simple clear English. Not formal. Like talking to a friend.

For Tamil, Telugu, Malayalam, Kannada, Bengali, Gujarati, Punjabi, Odia, Assamese, Urdu, Marathi, Nepali:
Reply COMPLETELY in that language script. Natural conversational style.

YOUR PROCESS:
STEP 1 - Ask 2-3 simple questions ONE AT A TIME:
- Their village/district/state
- Their income (monthly or yearly)  
- Their family situation

STEP 2 - Check eligibility:
- Tell exactly which schemes they qualify for
- Explain why they qualify

STEP 3 - Explain scheme simply:
- What they get, how much money, for how long

STEP 4 - Documents needed:
- Simple list, tell where to get each one

STEP 5 - Application — BOTH options:
ONLINE: Which website, which button, what to fill
OFFLINE: Which office, which day, what to say, what to carry

STEP 6 - Follow up with one question

RULES:
- SHORT replies — 4 to 5 lines max
- ONE follow up question at end
- Simple words only
- Warm like elder brother or sister
- NEVER switch language
- If confused, explain differently
- If illiterate, guide to CSC center"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get('messages', [])
    lang_name = data.get('lang_name', 'हिंदी (Hindi)')
    system_prompt = get_system_prompt(lang_name)
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=full_messages
    )
    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    text = data.get('text', '')
    lang_code = data.get('lang_code', 'hi')
    try:
        clean_text = text.replace('*', '').replace('#', '').replace('-', ' ')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            temp_file = f.name
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(temp_file)
        with open(temp_file, 'rb') as f:
            audio_data = f.read()
        os.unlink(temp_file)
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({"audio": audio_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/welcome', methods=['POST'])
def get_welcome():
    data = request.json
    dialect_key = data.get('dialect_key', 'hi')
    msg = WELCOME_MESSAGES.get(dialect_key, WELCOME_MESSAGES['hi'])
    return jsonify({"welcome": msg})

@app.route('/')
def home():
    return open('index.html', encoding='utf-8').read()

if __name__ == '__main__':
    print("=" * 55)
    print("🌾 GramSevak Server — Apna Haq, Apni Bhasha 🇮🇳")
    print("=" * 55)
    print("✅ Server starting on http://localhost:5000")
    print("✅ Open index.html in Chrome to use GramSevak")
    print("=" * 55)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
