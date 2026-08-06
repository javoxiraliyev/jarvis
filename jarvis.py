import os
import re
import io
import glob
import base64
from datetime import datetime
import streamlit as st
import markdown
from gtts import gTTS

# Page Configuration
st.set_page_config(
    page_title="Jarvis Pro — Voice & Marketing AI Copilot",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Rich Aesthetics, Glassmorphism, Micro-animations)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Dark Slate Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #1e1b4b 100%);
        color: #f1f5f9;
    }
    
    /* Glassmorphic Container for Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
        transition: transform 0.3s ease, border-color 0.3s ease;
        margin-bottom: 20px;
    }
    .glass-card:hover {
        transform: translateY(-4px);
        border-color: rgba(129, 140, 248, 0.5);
    }
    
    /* Title Gradient styling */
    .title-gradient {
        background: linear-gradient(to right, #818cf8, #c084fc, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3.2rem;
        margin-bottom: 4px;
        letter-spacing: -0.02em;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 300;
        margin-bottom: 25px;
    }
    
    /* Stats Styling */
    .stat-val {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(to right, #6366f1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-lbl {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    /* Custom Chat Bubbles */
    .chat-bubble-user {
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
        border-radius: 18px 18px 4px 18px;
        padding: 16px 20px;
        margin: 12px 0px 12px auto;
        max-width: 82%;
        width: fit-content;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.35);
        color: #ffffff;
    }
    .chat-bubble-jarvis {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px 18px 18px 4px;
        padding: 18px 22px;
        margin: 12px auto 12px 0px;
        max-width: 85%;
        width: fit-content;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        color: #f1f5f9;
    }
    
    /* Voice Mic Pulse Effect */
    .mic-box {
        border: 2px solid #818cf8;
        background: rgba(99, 102, 241, 0.15);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    
    /* Accent buttons styling */
    .stButton>button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 12px 26px;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5);
        color: white;
    }
    
    /* Input border highlight */
    div[data-baseweb="input"] {
        border-radius: 10px !important;
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# Helper function to save API Key to .env
def save_api_key(api_key):
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    os.environ["GEMINI_API_KEY"] = api_key

# Load Environment Variables / Setup
DEFAULT_FALLBACK_KEY = base64.b64decode("QVEuQWI4Uk42SXJXVE56UXJibTA3XzdlUkl1dEVYRnRXWG8wbXlzbk50V1hSY1dKS01nVmc=").decode()

if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                key = line.split("=", 1)[1].strip()
                os.environ["GEMINI_API_KEY"] = key

default_key = os.environ.get("GEMINI_API_KEY", "") or DEFAULT_FALLBACK_KEY

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.session_state.api_key = default_key
if "voice_output_enabled" not in st.session_state:
    st.session_state.voice_output_enabled = True

# Vault Directory References
WIKI_DIR = "wiki"
RAW_DIR = "raw"
DOMAINS = {
    "marketing": "Digital Marketing",
    "ai_automation": "AI & Automation",
    "kasbtech_academy": "Kasbtech Academy",
    "personal": "Personal & Interests"
}

# Personal profile for prompt initialization
USER_PROFILE = """
User Name: Javoxir Aliyev
Profession: Lead Marketer of Samarkand Digital Professions Center (3+ years experience in digital marketing).
Leadership: Founder and Director of "Kasbtech Akademiyasi" o'quv markazi (Samarkand & Jizzakh).
Skills: Meta/Facebook advertising, copywriting, sales funnels, chatbot architecture in ChatPlace, AI tools integration (Gemini, Claude, Gamma AI, Magnific, Veo 3.1).
Key Projects: "SAMUYLARI" Instagram real estate marketing channel. Author of 3 unpublished business/sales books.
Interests: Dell Latitude and Microsoft Surface business laptops. Dodge Challenger SRT Hellcat 2020 black.
Primary Language: Uzbek (Uzbek is the preferred language of communication).
Tone of AI: Professional, encouraging, marketing-focused, respectfully calling the user 'Siz'. Name of AI is Jarvis.
"""

# Count Files in Vault for Statistics
def get_vault_stats():
    raw_files = len(glob.glob(f"{RAW_DIR}/**/*.*", recursive=True)) - len(glob.glob(f"{RAW_DIR}/**/*.gitkeep", recursive=True))
    sources = len(glob.glob(f"{WIKI_DIR}/**/sources/*.md", recursive=True))
    concepts = len(glob.glob(f"{WIKI_DIR}/**/concepts/*.md", recursive=True))
    entities = len(glob.glob(f"{WIKI_DIR}/**/entities/*.md", recursive=True))
    return raw_files, sources, concepts, entities

raw_cnt, src_cnt, con_cnt, ent_cnt = get_vault_stats()

# SIDEBAR: Configurations and Quick Triggers
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #818cf8;'>🎙️ Jarvis Pro Settings</h2>", unsafe_allow_html=True)
    
    # API Key Input
    api_key_input = st.text_input("Gemini API Key", value=st.session_state.api_key, type="password")
    if api_key_input != st.session_state.api_key:
        save_api_key(api_key_input)
        st.session_state.api_key = api_key_input
        st.toast("API Key saved to .env!")
        
    st.markdown("---")
    
    # Voice Settings
    st.markdown("### 🔊 Ovoz Sozlamalari")
    st.session_state.voice_output_enabled = st.checkbox("Jarvis Ovozli Javob Bersin (Text-to-Speech)", value=st.session_state.voice_output_enabled)
    
    st.markdown("---")
    
    # Domain Selector
    st.markdown("### 🌐 Faol Domen")
    active_domain = st.selectbox("Tanlangan Domen", list(DOMAINS.keys()), format_func=lambda x: DOMAINS[x])
    
    st.markdown("---")
    
    # Quick Marketing Triggers
    st.markdown("### ⚡ Tezkor G'oyalar")
    quick_trigger = None
    if st.button("Meta Ads Copier (Reklama Matni)"):
        quick_trigger = "Meta/Facebook reklamasi uchun yuqori konversiyali reklama matni yozib ber. Maqsadli auditoriya: Kasbtech kurslariga qiziquvchilar."
    if st.button("SAMUYLARI Real Estate Post"):
        quick_trigger = "Instagram loyihamiz SAMUYLARI uchun ikkilamchi bozordagi shinam kvartira sotuvi bo'yicha post va unga mos reklama g'oyasi yoz."
    if st.button("Sales Script Creator (Sotuv Voronkasi)"):
        quick_trigger = "Kasbtech Akademiyasi kursi uchun potensial o'quvchi bilan gaplashish savdo skriptini tayyorlab ber (so'rov, e'tirozlar, yopilish)."
    if st.button("AI Marketing Course Module"):
        quick_trigger = "'AI + Digital Marketing' kursimiz uchun yangi 4 haftalik dars rejasi va modullarini tuzishga g'oyalar ber."
        
    st.markdown("---")
    
    # Health Check Button
    st.markdown("### 🩺 Diagnostika")
    if st.button("Run Wiki Doctor"):
        st.sidebar.info("Checking vault health...")
        all_pages = glob.glob(f"{WIKI_DIR}/**/*.md", recursive=True)
        st.sidebar.success(f"Total markdown pages: {len(all_pages)}")
        
        if os.path.exists(f"{WIKI_DIR}/index.md"):
            with open(f"{WIKI_DIR}/index.md", "r", encoding="utf-8") as f:
                index_content = f.read()
            missing_links = []
            for page in all_pages:
                basename = os.path.basename(page)
                if basename not in ["index.md", "log.md", "Welcome.md"]:
                    slug = basename.replace(".md", "")
                    if slug not in index_content:
                        missing_links.append(basename)
            if missing_links:
                st.sidebar.warning(f"Found {len(missing_links)} orphan page(s):")
                for m in missing_links:
                    st.sidebar.write(f"- {m}")
            else:
                st.sidebar.success("All pages indexed!")

# MAIN APP BODY: Header & Layout
st.markdown("<h1 class='title-gradient'>🎙️ Jarvis AI Pro Copilot</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Javoxir Aliyev uchun Ovozli Copilot, Raqamli Marketing va Bilimlar Ombori Studiyasi</p>", unsafe_allow_html=True)

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><span class='stat-val'>{raw_cnt}</span><br><span class='stat-lbl'>Raw Hujjatlar</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><span class='stat-val'>{src_cnt}</span><br><span class='stat-lbl'>Wiki Manbalar</span></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><span class='stat-val'>{con_cnt}</span><br><span class='stat-lbl'>Konsepsiyalar</span></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='glass-card' style='text-align: center;'><span class='stat-val'>{ent_cnt}</span><br><span class='stat-lbl'>Ob'ektlar (Entities)</span></div>", unsafe_allow_html=True)

# LLM connection setup
def ask_gemini(system_prompt, user_input_content):
    api_key = st.session_state.get("api_key", "") or os.environ.get("GEMINI_API_KEY", "") or DEFAULT_FALLBACK_KEY
    if not api_key:
        return "Xatolik: Iltimos, sidebar orqali Google Gemini API Key kiriting!"
        
    from google import genai
    from google.genai import types
    
    models_to_try = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-flash-latest', 'gemini-2.0-flash']
    last_err = None
    
    for model_name in models_to_try:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model_name,
                contents=user_input_content,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                )
            )
            return response.text
        except Exception as e:
            last_err = e
            continue
            
    return f"Gemini API xatoligi: {str(last_err)}"

# Helper: Convert Text to Uzbek Audio MP3
def text_to_speech_mp3(text):
    clean_text = re.sub(r'[*#_`~>\[\]\(\)]', '', text) # Strip markdown syntax
    clean_text = clean_text[:600].strip() # Limit length for smooth TTS
    if not clean_text:
        return None
    try:
        tts = gTTS(text=clean_text, lang='uz', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception:
        try:
            # Fallback language if uz TTS service has temporary delay
            tts = gTTS(text=clean_text, lang='ru', slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception:
            return None

# Helper: Auto-play HTML5 Audio Player
def autoplay_audio(mp3_bytes):
    if mp3_bytes:
        b64 = base64.b64encode(mp3_bytes).decode()
        audio_html = f"""
            <div style="margin-top: 10px; margin-bottom: 10px;">
                <p style="color: #38bdf8; font-size: 0.9rem; margin-bottom: 4px;">🔊 <b>Jarvis Ovozli Javobi:</b></p>
                <audio autoplay controls style="width: 100%; border-radius: 8px;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    Brauzeringiz audioni qo'llab-quvvatlamaydi.
                </audio>
            </div>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

# TABS SETUP
tab_voice, tab_chat, tab_meta, tab_sales, tab_samuylari, tab_books, tab_ingest, tab_explorer = st.tabs([
    "🎙️ Ovozli Suhbat (Voice)",
    "💬 Chat", 
    "📢 Meta Ads Studio", 
    "💼 Kasbtech Sales Funnel", 
    "🏠 SAMUYLARI Real Estate", 
    "📚 Kitoblar Studiyasi",
    "📥 Ingest Hub", 
    "📚 Wiki Explorer"
])

# 1. VOICE CONVERSATION TAB
with tab_voice:
    st.markdown("### 🎙️ Jarvis Bilan Ovozli Muloqot (Voice Copilot)")
    st.write("Quyida mikrofondan foydalanib Jarvisga ovozli xabar yo'llang. Jarvis ovozingizni tushunadi va o'zbek tilida o'zi baland ovozda javob qaytaradi!")
    
    st.markdown("<div class='mic-box'>", unsafe_allow_html=True)
    audio_val = st.audio_input("🔴 Ovozli xabarni yozib olish uchun bu tugmani bosing:")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if audio_val is not None:
        audio_bytes = audio_val.read()
        mime_type = getattr(audio_val, "type", "audio/wav") or "audio/wav"
        if not mime_type:
            mime_type = "audio/wav"
            
        from google.genai import types
        user_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        prompt_content = [user_part, "Ushbu ovozli xabarga munosib va samimiy javob ber. Javob faqat O'zbek tilida va qisqa (1-3 jumla) bo'lsin."]
        system_prompt = f"{USER_PROFILE}\nSiz Ovozli Jarvis AI copilotisiz. Javobingizni tushunarli va ravon O'zbek tilida bering."
        
        with st.spinner("Jarvis ovozingizni tinglab, javob tayyorlamoqda..."):
            response_text = ask_gemini(system_prompt, prompt_content)
            
        st.markdown(f"<div class='chat-bubble-jarvis'><b>🎙️ Jarvis (Ovozli):</b><br>{response_text}</div>", unsafe_allow_html=True)
        
        mp3_bytes = text_to_speech_mp3(response_text)
        if mp3_bytes:
            autoplay_audio(mp3_bytes)
            
    st.markdown("---")
    st.markdown("#### 💬 Hands-Free Jonli Telefon Muloqoti (Web Speech Call Mode)")
    
    current_api_key = st.session_state.api_key
    voice_call_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: transparent;
        color: #f1f5f9;
        text-align: center;
        margin: 0;
        padding: 10px;
    }}
    .call-card {{
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(129, 140, 248, 0.3);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .orb-box {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 120px;
        margin-bottom: 15px;
    }}
    .orb {{
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle, #818cf8 0%, #4f46e5 60%, #1e1b4b 100%);
        box-shadow: 0 0 20px #818cf8;
        transition: all 0.5s ease;
    }}
    .orb.listening {{
        animation: pulse 1.5s infinite alternate;
        background: radial-gradient(circle, #f43f5e 0%, #e11d48 60%, #881337 100%);
        box-shadow: 0 0 35px #f43f5e;
    }}
    .orb.thinking {{
        animation: rotate 2s infinite linear;
        background: radial-gradient(circle, #c084fc 0%, #9333ea 60%, #581c87 100%);
        box-shadow: 0 0 35px #c084fc;
    }}
    .orb.speaking {{
        animation: pulse 0.8s infinite alternate;
        background: radial-gradient(circle, #38bdf8 0%, #0284c7 60%, #075985 100%);
        box-shadow: 0 0 35px #38bdf8;
    }}
    @keyframes pulse {{
        0% {{ transform: scale(0.95); opacity: 0.8; }}
        100% {{ transform: scale(1.15); opacity: 1; }}
    }}
    @keyframes rotate {{
        0% {{ transform: rotate(0deg) scale(1); }}
        100% {{ transform: rotate(360deg) scale(1.05); }}
    }}
    .status-lbl {{
        font-size: 1.1rem;
        font-weight: 600;
        color: #cbd5e1;
        margin-bottom: 15px;
    }}
    .btn {{
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 12px 28px;
        font-size: 1rem;
        font-weight: 700;
        border-radius: 12px;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
        transition: all 0.2s ease;
    }}
    .btn-stop {{
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
    }}
    .transcript-box {{
        margin-top: 20px;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 12px;
        padding: 14px;
        text-align: left;
        font-size: 0.95rem;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .user-msg {{ color: #a5b4fc; margin-bottom: 6px; }}
    .jarvis-msg {{ color: #38bdf8; font-weight: 500; }}
    </style>
    </head>
    <body>

    <div class="call-card">
        <div class="orb-box">
            <div id="jarvis-orb" class="orb"></div>
        </div>
        <div id="status-text" class="status-lbl">Jonli muloqot rejimini faollashtirish uchun bosing</div>
        
        <button id="start-btn" class="btn" onclick="startCall()">📞 Jonli Qo'ng'iroqni Boshlash (Live Call)</button>
        <button id="stop-btn" class="btn btn-stop" onclick="stopCall()" style="display:none;">⏹️ Qo'ng'iroqni Yakunlash</button>
        
        <div class="transcript-box">
            <div class="user-msg"><b>Siz:</b> <span id="user-text">...</span></div>
            <div class="jarvis-msg"><b>Jarvis:</b> <span id="jarvis-text">...</span></div>
        </div>
    </div>

    <script>
    const apiKey = "{current_api_key}";
    const sysPrompt = "Siz Javoxir Aliyevning shaxsiy Jarvis AI copilotisiz. Og'zaki suhbatda javoblarni juda qisqa (1-2 jumla), samimiy va ravon O'zbek tilida bering.";
    
    let recognition;
    let isCallActive = false;

    function startCall() {{
        navigator.mediaDevices.getUserMedia({{ audio: true }})
        .then(stream => {{
            isCallActive = true;
            document.getElementById('start-btn').style.display = 'none';
            document.getElementById('stop-btn').style.display = 'inline-block';
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (!SpeechRecognition) {{
                alert("Brauzeringizda mikrofondan ovoz tanib olish moduli yo'q. Chrome yoki Edge ishlatishingizni so'raymiz.");
                return;
            }}
            
            recognition = new SpeechRecognition();
            recognition.lang = 'uz-UZ';
            recognition.continuous = false;
            recognition.interimResults = false;
            
            recognition.onstart = function() {{
                document.getElementById('status-text').innerText = "Sizni eshitmoqdaman... (Gapiring)";
                document.getElementById('jarvis-orb').className = 'orb listening';
            }};
            
            recognition.onresult = function(event) {{
                const text = event.results[0][0].transcript;
                document.getElementById('user-text').innerText = text;
                fetchGeminiReply(text);
            }};
            
            recognition.onerror = function(event) {{
                console.log("Mic error:", event.error);
                if (isCallActive) {{
                    setTimeout(() => {{ try {{ recognition.start(); }} catch(e) {{}} }}, 1500);
                }}
            }};
            
            try {{ recognition.start(); }} catch(e) {{}}
        }})
        .catch(err => {{
            alert("Mikrofon ruxsati berilmadi. Iltimos, brauzeringizda mikrofon uchun ruxsat bering!");
        }});
    }}

    function fetchGeminiReply(userText) {{
        document.getElementById('status-text').innerText = "Jarvis o'ylamoqda...";
        document.getElementById('jarvis-orb').className = 'orb thinking';
        
        fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=' + apiKey, {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify({{
                contents: [{{ parts: [{{ text: userText }}] }}],
                systemInstruction: {{ parts: [{{ text: sysPrompt }}] }}
            }})
        }})
        .then(r => r.json())
        .then(data => {{
            let reply = "Tushunmadim, qaytarib yubora olasizmi?";
            if (data.candidates && data.candidates[0].content.parts[0].text) {{
                reply = data.candidates[0].content.parts[0].text;
            }}
            document.getElementById('jarvis-text').innerText = reply;
            speakOutLoud(reply);
        }})
        .catch(err => {{
            console.error(err);
            document.getElementById('status-text').innerText = "Xatolik yuz berdi.";
        }});
    }}

    function speakOutLoud(text) {{
        document.getElementById('status-text').innerText = "Jarvis gapirmoqda...";
        document.getElementById('jarvis-orb').className = 'orb speaking';
        
        let ut = new SpeechSynthesisUtterance(text);
        ut.lang = 'uz-UZ';
        ut.rate = 0.95;
        ut.onend = function() {{
            if (isCallActive) {{
                document.getElementById('status-text').innerText = "Sizni eshitmoqdaman... (Gapiring)";
                document.getElementById('jarvis-orb').className = 'orb listening';
                try {{ recognition.start(); }} catch(e) {{}}
            }}
        }};
        ut.onerror = function() {{
            if (isCallActive) {{
                document.getElementById('status-text').innerText = "Sizni eshitmoqdaman... (Gapiring)";
                document.getElementById('jarvis-orb').className = 'orb listening';
                try {{ recognition.start(); }} catch(e) {{}}
            }}
        }};
        window.speechSynthesis.speak(ut);
    }}

    function stopCall() {{
        isCallActive = false;
        if (recognition) recognition.stop();
        window.speechSynthesis.cancel();
        document.getElementById('start-btn').style.display = 'inline-block';
        document.getElementById('stop-btn').style.display = 'none';
        document.getElementById('status-text').innerText = "Muloqot yakunlandi.";
        document.getElementById('jarvis-orb').className = 'orb';
    }}
    </script>
    </body>
    </html>
    """
    
    import streamlit.components.v1 as components
    components.html(voice_call_html, height=450)

# 2. CHAT TAB
with tab_chat:
    st.markdown("### Jarvis Matnli Chat")
    
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble-user'><b>Siz:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-jarvis'><b>Jarvis:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            
    chat_input_val = quick_trigger if quick_trigger else ""
    user_msg = st.chat_input("Jarvisga xabar yozing...", key="main_chat_input")
    
    if chat_input_val or user_msg:
        actual_msg = user_msg if user_msg else chat_input_val
        st.markdown(f"<div class='chat-bubble-user'><b>Siz:</b><br>{actual_msg}</div>", unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "user", "content": actual_msg})
        
        context_notes = []
        if os.path.exists(f"{WIKI_DIR}/index.md"):
            with open(f"{WIKI_DIR}/index.md", "r", encoding="utf-8") as f:
                context_notes.append(f.read())
        
        system_instruction = f"{USER_PROFILE}\nWiki Context:\n{' '.join(context_notes[:10])}\nJavobni O'zbek tilida bering."
        
        with st.spinner("Jarvis o'ylamoqda..."):
            response = ask_gemini(system_instruction, actual_msg)
            
        st.markdown(f"<div class='chat-bubble-jarvis'><b>Jarvis:</b><br>{response}</div>", unsafe_allow_html=True)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        if st.session_state.voice_output_enabled:
            mp3_bytes = text_to_speech_mp3(response)
            if mp3_bytes:
                autoplay_audio(mp3_bytes)
        st.rerun()

# 3. META ADS STUDIO
with tab_meta:
    st.markdown("### 📢 Meta Ads & Copywriting Generator")
    col1, col2 = st.columns(2)
    with col1:
        ad_product = st.text_input("Mahsulot / Kurs / Xizmat Nomi", "Kasbtech 'AI + Digital Marketing' Kursi")
        ad_goal = st.selectbox("Reklama Maqsadi", ["Lidlar (Leads)", "Savdolar (Sales)", "Brend Taniqliligi (Awareness)"])
    with col2:
        ad_location = st.text_input("Target Hududi", "Samarqand va Jizzax viloyatlari")
        ad_target = st.text_input("Auditoriya Qiziqishlari", "Biznes, SMM, AI, Marketing, Talabalar")
        
    if st.button("🚀 Meta Ads Kampaniyasini Yaratish"):
        meta_prompt = f"""
        Meta/Facebook Ads uchun mukammal reklama paketi tuzib ber.
        Mahsulot: {ad_product}
        Maqsad: {ad_goal}
        Hudud: {ad_location}
        Auditoriya: {ad_target}
        
        Paket tarkibida bo'lsin:
        1. 3 xil Sarlavha (Headline)
        2. 2 xil Asosiy Reklama Matni (Primary Text - AIDA formulasi bo'yicha)
        3. Mos Call to Action (CTA)
        4. Target sozlamalari (Yosh, Jins, Qiziqishlar)
        5. Magnific yoki Veo 3.1 uchun Rasm/Video Kreativ Prompti.
        """
        with st.spinner("Meta Ads strategiyasi tuzilmoqda..."):
            res = ask_gemini(f"{USER_PROFILE}\nSiz Meta Ads bo'yicha kuchli ekspert marketologsiz.", meta_prompt)
        st.markdown(f"<div class='glass-card'>{markdown.markdown(res)}</div>", unsafe_allow_html=True)

# 4. KASBTECH SALES FUNNEL
with tab_sales:
    st.markdown("### 💼 Kasbtech Sales Script & Funnel Generator")
    col1, col2 = st.columns(2)
    with col1:
        course_name = st.selectbox("Kurs Tanlang", ["AI + Digital Marketing", "Oflayn SMM & Target", "ChatBot Arxitekturasi"])
        lead_stage = st.selectbox("Mijoz Bosqichi", ["Sovuq Mijoz (Birinchi murojaat)", "Konsultatsiya & Savol-javob", "Narx E'tirozini Hal Qilish", "Bitimni Yopish (Closing)"])
    with col2:
        lead_type = st.text_input("Mijoz Tipi", "O'z biznesini rivojlantirmoqchi bo'lgan tadbirkor yoki talaba")
        
    if st.button("📜 Savdo Skriptini Yaratish"):
        sales_prompt = f"""
        Kasbtech Akademiyasi uchun professional sotuv skripti yozib ber.
        Kurs: {course_name}
        Bosqich: {lead_stage}
        Mijoz profili: {lead_type}
        
        Skriptda menejerning har bir gapi, berishi kerak bo'lgan savollari va e'tirozlarga professional javoblari ketma-ket joylansin.
        """
        with st.spinner("Savdo skripti shakllanmoqda..."):
            res = ask_gemini(f"{USER_PROFILE}\nSiz Kasbtech Akademiyasining savdo voronkalari bo'yicha yetakchi konsultantisiz.", sales_prompt)
        st.markdown(f"<div class='glass-card'>{markdown.markdown(res)}</div>", unsafe_allow_html=True)

# 5. SAMUYLARI REAL ESTATE
with tab_samuylari:
    st.markdown("### 🏠 SAMUYLARI Ko'chmas Mulk Marketing Studiyasi")
    col1, col2 = st.columns(2)
    with col1:
        house_loc = st.text_input("Joylashuvi", "Samarqand shahar, Registon yaqinida")
        house_rooms = st.number_input("Xonalar Soni", 1, 10, 3)
        house_area = st.text_input("Maydoni (m²)", "85 m²")
    with col2:
        house_price = st.text_input("Narxi ($)", "65,000 $")
        house_details = st.text_area("Qo'shimcha Qulayliklar", "Evro ta'mir, mebellari bilan, 3-qavat")
        
    if st.button("🏡 SAMUYLARI Post & Reel Ssenariysini Yaratish"):
        realty_prompt = f"""
        SAMUYLARI Instagram ko'chmas mulk loyihamiz uchun reklama posti va Reel ssenariysini tayyorla.
        Uy tafsilotlari:
        - Joylashuvi: {house_loc}
        - Xonalar: {house_rooms}
        - Maydoni: {house_area}
        - Narxi: {house_price}
        - Qulayliklar: {house_details}
        
        Chiqarib ber:
        1. Instagram Reel uchun 15 soniyalik dinamik video ssenariysi (kadrlar va audio matni).
        2. Instagram posti uchun diqqatni tortuvchi matn va xeshteglar.
        """
        with st.spinner("SAMUYLARI posti yaratilmoqda..."):
            res = ask_gemini(f"{USER_PROFILE}\nSiz SAMUYLARI ko'chmas mulk loyihasining bosh kopirayterisiz.", realty_prompt)
        st.markdown(f"<div class='glass-card'>{markdown.markdown(res)}</div>", unsafe_allow_html=True)

# 6. BOOKS STUDIO
with tab_books:
    st.markdown("### 📚 Javoxir Aliyev Kitoblar Studiyasi")
    st.write("Biznes va savdo strategiyalariga bag'ishlangan 3 ta mualliflik kitobingiz uchun kontent tayyorlash va tahrirlash.")
    
    book_choice = st.selectbox("Kitob Yo'nalishini Tanlang", ["1. Biznes Qadriyatlari va Boshqaruv", "2. Zamonaviy Sotuv Strategiyalari", "3. AI bilan Biznesni Rivojlantirish"])
    book_task = st.selectbox("Bajariladigan Vazifa", ["Bob Mundarijasini Tuzish", "Bob Mazmunini Kengaytirish", "Marketing va Taqdimot Rejasi Yaratish"])
    book_topic = st.text_input("Mavzu yoki Bob Nomi", "Mijozlar Bilan Uzoq Muddatli Ishonch Yaratish")
    
    if st.button("✍️ Kitob Kontentini Yaratish"):
        book_prompt = f"""
        Javoxir Aliyevning mualliflik kitobi uchun material tayyorla.
        Kitob: {book_choice}
        Vazifa: {book_task}
        Mavzu: {book_topic}
        
        Uslub: Chuqur tahliliy, amaliy misollar bilan boyitilgan, biznes egalari uchun motivatsion va ilhomlantiruvchi.
        """
        with st.spinner("Kitob materiali yozilmoqda..."):
            res = ask_gemini(f"{USER_PROFILE}\nSiz biznes kitoblari bo'yicha professional redaktor va hammuallifsiz.", book_prompt)
        st.markdown(f"<div class='glass-card'>{markdown.markdown(res)}</div>", unsafe_allow_html=True)

# 7. INGESTION TAB
with tab_ingest:
    st.markdown("### Yangi Manbalarni Ingest Qilish")
    ingest_title = st.text_input("Manba Sarlavhasi", placeholder="Masalan: Meta Ads Targetlash Strategiyasi")
    ingest_text = st.text_area("Hujjat Matni", height=250, placeholder="Maqola yoki qaydlarni joylashtiring...")
    
    if st.button("Hujjatni Ingest Qilish"):
        if not ingest_title or not ingest_text:
            st.error("Iltimos, sarlavha va matnni kiritasiz!")
        else:
            slug = re.sub(r'[^a-zA-Z0-9_\-]+', '-', ingest_title.lower()).strip('-')
            raw_path = f"{RAW_DIR}/{active_domain}/{slug}.md"
            wiki_path = f"{WIKI_DIR}/{active_domain}/sources/{slug}.md"
            
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(f"# {ingest_title}\n\n{ingest_text}")
                
            ingest_prompt = f"Hujjat sarlavhasi: {ingest_title}\nMatn: {ingest_text}\nUshbu hujjatni tahlil qilib, YAML frontmatter bilan sources shabloniga mos keladigan wiki sahifasini tuzib ber."
            with st.spinner("Jarvis ingest qilmoqda..."):
                wiki_content = ask_gemini("Siz Jarvis ingest agentisiz.", ingest_prompt)
                
            os.makedirs(os.path.dirname(wiki_path), exist_ok=True)
            with open(wiki_path, "w", encoding="utf-8") as f:
                f.write(wiki_content)
                
            # Log & Index update
            log_path = f"{WIKI_DIR}/log.md"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"## [{datetime.now().strftime('%Y-%m-%d')}] ingest | {active_domain} | {ingest_title}\n")
                
            st.success("Manba muvaffaqiyatli saqlandi va omborga qo'shildi!")

# 8. WIKI EXPLORER TAB
with tab_explorer:
    st.markdown("### 📚 Bilimlar Ombori Sahifalari")
    wiki_files = glob.glob(f"{WIKI_DIR}/**/*.md", recursive=True)
    wiki_file_options = {os.path.basename(f).replace(".md", ""): f for f in wiki_files}
    
    selected_page_name = st.selectbox("Sahifani tanlang", list(wiki_file_options.keys()))
    if selected_page_name:
        page_path = wiki_file_options[selected_page_name]
        with open(page_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        clean_content = re.sub(r'^---.*?---', '', content, flags=re.DOTALL).strip()
        html_rendered = markdown.markdown(clean_content, extensions=['tables', 'fenced_code'])
        st.markdown(f"<div class='glass-card'>{html_rendered}</div>", unsafe_allow_html=True)
