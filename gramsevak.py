from groq import Groq
from dotenv import load_dotenv
import os
import speech_recognition as sr
from gtts import gTTS
import pygame
import tempfile
import time
import threading
import msvcrt

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LANGUAGES = {
    "1":  {"name": "हिंदी (Hindi)",            "code": "hi", "sr_code": "hi-IN", "dialect_key": "hi"},
    "2":  {"name": "தமிழ் (Tamil)",             "code": "ta", "sr_code": "ta-IN", "dialect_key": "ta"},
    "3":  {"name": "తెలుగు (Telugu)",           "code": "te", "sr_code": "te-IN", "dialect_key": "te"},
    "4":  {"name": "മലയാളം (Malayalam)",        "code": "ml", "sr_code": "ml-IN", "dialect_key": "ml"},
    "5":  {"name": "मराठी (Marathi)",           "code": "mr", "sr_code": "mr-IN", "dialect_key": "mr"},
    "6":  {"name": "বাংলা (Bengali)",           "code": "bn", "sr_code": "bn-IN", "dialect_key": "bn"},
    "7":  {"name": "ગુજરાતી (Gujarati)",        "code": "gu", "sr_code": "gu-IN", "dialect_key": "gu"},
    "8":  {"name": "ਪੰਜਾਬੀ (Punjabi)",          "code": "pa", "sr_code": "pa-IN", "dialect_key": "pa"},
    "9":  {"name": "ಕನ್ನಡ (Kannada)",           "code": "kn", "sr_code": "kn-IN", "dialect_key": "kn"},
    "10": {"name": "اردو (Urdu)",               "code": "ur", "sr_code": "ur-IN", "dialect_key": "ur"},
    "11": {"name": "ओडिआ (Odia)",              "code": "or", "sr_code": "or-IN", "dialect_key": "or"},
    "12": {"name": "অসমীয়া (Assamese)",        "code": "as", "sr_code": "as-IN", "dialect_key": "as"},
    "13": {"name": "संस्कृत (Sanskrit)",        "code": "sa", "sr_code": "sa-IN", "dialect_key": "sa"},
    "14": {"name": "नेपाली (Nepali/Pahadi)",    "code": "ne", "sr_code": "ne-IN", "dialect_key": "ne"},
    "15": {"name": "सिन्धी (Sindhi)",          "code": "sd", "sr_code": "hi-IN", "dialect_key": "sd"},
    "16": {"name": "कोंकणी (Konkani)",         "code": "hi", "sr_code": "hi-IN", "dialect_key": "konkani"},
    "17": {"name": "मैथिली (Maithili)",        "code": "hi", "sr_code": "hi-IN", "dialect_key": "maithili"},
    "18": {"name": "भोजपुरी (Bhojpuri)",       "code": "hi", "sr_code": "hi-IN", "dialect_key": "bhojpuri"},
    "19": {"name": "बघेली (Bagheli)",          "code": "hi", "sr_code": "hi-IN", "dialect_key": "bagheli"},
    "20": {"name": "बुन्देली (Bundeli)",        "code": "hi", "sr_code": "hi-IN", "dialect_key": "bundeli"},
    "21": {"name": "छत्तीसगढ़ी (Chhattisgarhi)","code": "hi", "sr_code": "hi-IN", "dialect_key": "chhattisgarhi"},
    "22": {"name": "हरियाणवी (Haryanvi)",      "code": "hi", "sr_code": "hi-IN", "dialect_key": "haryanvi"},
    "23": {"name": "राजस्थानी (Rajasthani)",   "code": "hi", "sr_code": "hi-IN", "dialect_key": "rajasthani"},
    "24": {"name": "डोगरी (Dogri)",            "code": "hi", "sr_code": "hi-IN", "dialect_key": "dogri"},
    "25": {"name": "मणिपुरी (Manipuri)",       "code": "hi", "sr_code": "hi-IN", "dialect_key": "manipuri"},
    "26": {"name": "বড়ো (Bodo)",               "code": "hi", "sr_code": "hi-IN", "dialect_key": "bodo"},
    "27": {"name": "संताली (Santali)",         "code": "hi", "sr_code": "hi-IN", "dialect_key": "santali"},
    "28": {"name": "তুলু (Tulu)",              "code": "kn", "sr_code": "kn-IN", "dialect_key": "tulu"},
    "29": {"name": "English",                   "code": "en", "sr_code": "en-IN", "dialect_key": "en"},
}

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
    "bagheli":      "जोहार! मैं GramSevak हंव। टाइप करे बर 1 दबाओ। बोले बर 2 दबाओ। बताओ तुम्हार का तकलीफ हय?",
    "bundeli":      "राम राम! मैं GramSevak हौं। टाइप करबे को 1 दबाओ। बोलबे को 2 दबाओ। बताओ तुम्हारी का समस्या है?",
    "chhattisgarhi":"जोहार! मैं GramSevak अंव। टाइप करे बर 1 दबावव। बोले बर 2 दबावव। बताव तुंहर का तकलीफ हे?",
    "haryanvi":     "खम्मा घणी! मैं GramSevak हूं। टाइप करण खातर 1 दबा। बोलण खातर 2 दबा। बता तेरी के समस्या सै?",
    "rajasthani":   "खम्मा घणी! हूं GramSevak हूं। टाइप करबा सारू 1 दबाओ। बोलबा सारू 2 दबाओ। बताओ थारी के समस्या है?",
    "dogri":        "नमस्कार! मैं GramSevak हां। टाइप करने लई 1 दबाओ। बोलने लई 2 दबाओ। दस्सो तुसाडी की समस्या ऐ?",
    "manipuri":     "নমস্কার! ঐ GramSevak নি। টাইপ তৌবগী দা 1 থাজিল্লু। ৱারোল থৌদোকপগী দা 2 থাজিল্লু। নংগী মথৌ কদাইনো?",
    "bodo":         "नमस्कार! आं GramSevak। टाइप करनाय लाय 1 दाब। बोलनाय लाय 2 दाब। नों मा समस्या आव?",
    "santali":      "जोहार! आं GramSevak काना। टाइप करते 1 दबाव। बोलते 2 दबाव। दो तोहोर समस्या एटाक?",
    "tulu":         "ನಮಸ್ಕಾರ! ಯಾನ್ GramSevak. ಟೈಪ್ ಮಲ್ಪೆರೆ 1, ಪಾತೆರೆರೆ 2 ಒತ್ತುಲೆ. ನಿಕ್ಕ ಎಂಚಿನ ತೊಂದರೆ ಉಂಡು?",
    "en":           "Hello! I am GramSevak. Press 1 to type, Press 2 to speak, Press S to stop voice. Tell me your problem and I will find the right government scheme for you!",
}

def get_system_prompt(lang_name):
    return f"""You are GramSevak AI — a friendly assistant for rural Indian citizens.

LANGUAGE RULE — MOST IMPORTANT:
You MUST reply ONLY in {lang_name}. NEVER switch to another language.
If language is English — reply in clear simple English only.
If language is भोजपुरी — use words like "हईं, बा, रहल बा, बतावऽ, हमार, तोहार"
If language is बघेली — use words like "हंव, हय, बताओ, तकलीफ, मोर, तोर"
If language is राजस्थानी — use words like "हूं, थारो, म्हारो, कांई, बताओ"
If language is हरियाणवी — use words like "सै, तेरी, मेरी, बता, आजा, चाल"
If language is छत्तीसगढ़ी — use words like "हे, अंव, तुंहर, मोर, बताव, करव"
If language is बुन्देली — use words like "हौं, तुम्हार, मोय, बताओ, करो"
If language is मैथिली — use words like "छी, अछि, अहाँ, हम, बताउ"
If language is डोगरी — use words like "हां, तुसाडी, साडी, दस्सो, करो"
For Tamil, Telugu, Malayalam, Kannada etc — reply COMPLETELY in that language script.

YOUR PROCESS:
1. Ask 2-3 simple questions to understand situation (location, income, family size)
2. Tell which government schemes they qualify for
3. Explain scheme simply — what benefit, how much money
4. List documents needed — tell where to get missing ones
5. Give ONLINE steps like they never used internet — which website, which button, what to fill
6. Give OFFLINE steps — which office, what to say, what to carry, which day to go
7. Always end with one follow up question

RULES:
- Keep replies SHORT — 4 to 5 lines max
- Always ask one follow up question at end
- Simple words only — no difficult terms
- Be warm like a helpful elder brother or sister
- NEVER switch language mid conversation"""

pygame.mixer.init()
skip_speaking = False
currently_speaking = False

def key_watcher():
    global skip_speaking, currently_speaking
    while True:
        if currently_speaking:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ('s', 'S'):
                    skip_speaking = True
                    try:
                        pygame.mixer.music.stop()
                    except:
                        pass
                    print("\n⏭️ Voice stopped.")
        time.sleep(0.05)

watcher_thread = threading.Thread(target=key_watcher, daemon=True)
watcher_thread.start()

def speak(text, lang_code):
    global skip_speaking, currently_speaking
    skip_speaking = False
    currently_speaking = True
    try:
        clean_text = text.replace('*', '').replace('#', '').replace('-', ' ')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            temp_file = f.name
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        tts.save(temp_file)
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            if skip_speaking:
                pygame.mixer.music.stop()
                break
            time.sleep(0.1)
        pygame.mixer.music.unload()
        try:
            os.unlink(temp_file)
        except:
            pass
    except Exception as e:
        print(f"(Voice error: {e})")
    finally:
        currently_speaking = False

def listen(sr_code):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if selected_lang["code"] == "en":
            print("\n🎤 Speak now...")
        else:
            print(f"\n🎤 बोलिए... ({selected_lang['name']})")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            if selected_lang["code"] == "en":
                print("⏳ Understanding...")
            else:
                print("⏳ समझ रहा हूँ...")
            text = recognizer.recognize_google(audio, language=sr_code)
            if selected_lang["code"] == "en":
                print(f"You said: {text}")
            else:
                print(f"आपने कहा: {text}")
            return text
        except sr.WaitTimeoutError:
            print("❌ No voice detected, try again" if selected_lang["code"] == "en" else "❌ कोई आवाज़ नहीं आई")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand, speak again" if selected_lang["code"] == "en" else "❌ समझ नहीं आया, दोबारा बोलिए")
            return None
        except sr.RequestError:
            print("❌ Check internet connection" if selected_lang["code"] == "en" else "❌ इंटरनेट चेक करें")
            return None

def show_menu():
    if selected_lang["code"] == "en":
        print("\n1=Type | 2=Speak | L=Change Language | S=Stop Voice | exit=Quit")
    else:
        print("\n1=टाइप | 2=बोलें | L=भाषा बदलें | S=आवाज़ बंद | exit=बंद")

def select_language():
    global selected_lang, current_system_prompt
    print("\n" + "=" * 55)
    print("🌍 भाषा चुनें / Choose Your Language:")
    print("=" * 55)
    keys = list(LANGUAGES.keys())
    for i in range(0, len(keys), 2):
        left = f"{keys[i]:>2} = {LANGUAGES[keys[i]]['name']}"
        if i+1 < len(keys):
            right = f"{keys[i+1]:>2} = {LANGUAGES[keys[i+1]]['name']}"
            print(f"{left:<35} {right}")
        else:
            print(left)
    print("=" * 55)
    choice = input("Enter number (Press Enter for Hindi): ").strip()
    if choice in LANGUAGES:
        selected_lang = LANGUAGES[choice]
    else:
        selected_lang = LANGUAGES["1"]
    current_system_prompt = get_system_prompt(selected_lang["name"])
    print(f"✅ Language: {selected_lang['name']}")

# Global variables
selected_lang = LANGUAGES["1"]
current_system_prompt = get_system_prompt("हिंदी (Hindi)")
conversation_history = []

# Startup
print("=" * 55)
print("🙏 GramSevak AI — Apna Haq, Apni Bhasha 🇮🇳")
print("=" * 55)

select_language()
conversation_history = []

lang_key = selected_lang.get("dialect_key", selected_lang["code"])
welcome = WELCOME_MESSAGES.get(lang_key, WELCOME_MESSAGES["hi"])
print(f"\n🤖 GramSevak: {welcome}\n")
speak(welcome, selected_lang["code"])

while True:
    show_menu()
    choice = input(">>> ").strip()

    if choice.lower() == 'exit':
        bye = "Thank you! Goodbye!" if selected_lang["code"] == "en" else "धन्यवाद! जय हिंद!"
        print(bye)
        speak(bye, selected_lang["code"])
        time.sleep(3)
        break

    elif choice.lower() == 'l':
        select_language()
        conversation_history = []  # Reset conversation for new language
        lang_key = selected_lang.get("dialect_key", selected_lang["code"])
        welcome = WELCOME_MESSAGES.get(lang_key, WELCOME_MESSAGES["hi"])
        print(f"\n🤖 GramSevak: {welcome}")
        speak(welcome, selected_lang["code"])
        continue

    elif choice.lower() == 's':
        skip_speaking = True
        try:
            pygame.mixer.music.stop()
        except:
            pass
        print("⏭️ Voice stopped." if selected_lang["code"] == "en" else "⏭️ आवाज़ बंद की।")
        continue

    elif choice == "1":
        prompt = "You: " if selected_lang["code"] == "en" else "आप: "
        user_input = input(prompt)

    elif choice == "2":
        user_input = listen(selected_lang["sr_code"])
        if not user_input:
            continue

    else:
        print("Please choose correct option" if selected_lang["code"] == "en" else "सही option चुनें")
        continue

    conversation_history.append({
        "role": "user",
        "content": user_input
    })

    messages = [{"role": "system", "content": current_system_prompt}] + conversation_history

    print("\n⏳ Thinking..." if selected_lang["code"] == "en" else "\n⏳ सोच रहा हूँ...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": assistant_reply
    })

    print("\n🤖 GramSevak:")
    print(assistant_reply)
    print("-" * 55)
    print("(S = Stop voice)" if selected_lang["code"] == "en" else "(S = आवाज़ बंद)")

    speak(assistant_reply, selected_lang["code"])