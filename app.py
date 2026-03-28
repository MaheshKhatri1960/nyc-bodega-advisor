import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import os
import datetime
import time
from dotenv import load_dotenv

# --- CONFIGURATION ---
load_dotenv() # Load local .env for development

NYC_PERSONA = """
You are 'Tony', a savvy, street-smart NYC retail consultant for local bodegas. 
Your tone is funny, local, and encouraging. Use NYC slang (e.g., 'Deadass', 'The real deal', 'Bodega style'). 
You help small shops beat big stores like Costco and Walmart by being 'agile' and 'community-first'.

When you see a product or shelf display captured via camera:
1. **Identify**: List the product categories and names. Identify any 'hidden gems' or high-margin items (like tropical fruits or artisanal snacks).
2. **Strategy**: Suggest one 'High-Margin Placement' (where to put it to sell faster). Use NYC 'street smarts' for placement (e.g., 'Right by the BEC counter, deadass!').
3. **Offers**: Suggest a 'NYC Bundle' (e.g., 'The 5 AM Commuter special' or 'The Bodega Breakfast of Champions').
4. **Marketing**: 
   - A funny, catchy tagline for WhatsApp (Maximum 5 words).
   - A simple recipe for the item (if fruit/veg).
   - A 1-minute 'Street Pitch' in both English and Spanish (Sabor Local).
5. **Shelf Tag**: Generate a short, punchy description for a printable shelf tag.

**Output Format Requirement**:
Start your output with [TAGLINE]: "Your tagline here"
Followed by [ENGLISH_PITCH]: "Your 1-minute English pitch"
Followed by [SPANISH_PITCH]: "Your 1-minute Spanish pitch"
Then provide the rest of the strategic advice.
Be creative, not offensive, and very entertaining.
"""

st.set_page_config(page_title="🍎 NYC Bodega Advisor AI", layout="wide")

# --- SIDEBAR: Settings ---
with st.sidebar:
    st.header("🏪 Shop Settings")
    
    # Secret Logic: Try to get API key from environment first
    env_key = os.getenv("GOOGLE_API_KEY", "")
    api_key_input = st.text_input("Enter Google Gemini API Key", value=env_key, type="password")
    
    # Final API key used in the app
    api_key = api_key_input if api_key_input else env_key
    
    shop_name = st.text_input("Shop Name", "My NYC Grocery")
    shop_phone = st.text_input("WhatsApp Number", "+1 (212) - 123 4567")
    shop_hours = st.text_input("Timings", "8:00 AM - 8:00 PM")
    shop_vibe = st.radio("Shop Vibe", ["Community Friendly", "Deals Focused", "Premium Quality"])
    
    st.markdown("---")
    if api_key:
        st.success("✅ Gemini API Secret Loaded")
    else:
        st.warning("⚠️ No API Key Detected")

# --- FUNCTIONS ---
def get_retail_advice(image, problem, api_key, vibe):
    genai.configure(api_key=api_key)
    
    # DYNAMIC SELECTION: Find the best available Flash model (Prioritizing 2.5)
    model_name = "gemini-1.5-flash" # Fallback
    try:
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods 
                           and 'flash' in m.name.lower()]
        if available_models:
            # Sorting reverse gives us 2.5 > 2.0 > 1.5
            model_name = sorted(available_models, reverse=True)[0]
    except:
        pass
        
    model = genai.GenerativeModel(model_name, system_instruction=NYC_PERSONA)
    
    prompt = f"""
    Business Problem: {problem or 'Help me sell this more effectively for the upcoming holidays!'}
    Current Date: {datetime.date.today()}
    Shop Vibe: {vibe}
    
    Tasks: 
    - Analyze the attached image.
    - Provide identification, strategy, offers, and marketing copy (English & Spanish).
    - Suggest a catchy WhatsApp tagline and printable shelf tag text.
    """
    
    response = model.generate_content([prompt, image])
    return response.text

def create_whatsapp_card(img, tagline, phone, hours):
    base = img.convert("RGBA")
    txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    w, h = base.size
    box_height = h // 4
    draw.rectangle([0, h - box_height, w, h], fill=(0, 0, 0, 160))
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((w//10, h - box_height + 20), f"🔥 {tagline}", fill="white", font=font)
    draw.text((w//10, h - 40), f"📞 {phone} | ⏰ {hours}", fill="yellow", font=font)
    
    out = Image.alpha_composite(base, txt)
    return out.convert("RGB")

def generate_audio_pitch(text, lang='en', is_sample=False):
    ts = int(time.time())
    filename = f"pitch_{lang}_{ts}.mp3"
    
    # MASTER DEMO FALLBACK: Use pre-generated files for the sample photo
    sample_file = f"sample_{lang}.mp3"
    if is_sample and os.path.exists(sample_file):
        return sample_file

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(filename)
        return filename
    except Exception as e:
        # If gTTS 429 occurs, return None so UI can show a fallback message
        return None

# --- MAIN UI ---
st.title("🍎 NYC Bodega Advisor AI")
st.write("Helping Main Street beat the big stores one snap at a time.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Snap or Upload Display")
    img_file = st.camera_input("Take a photo of a product or shelf")
    up_file = st.file_uploader("Or upload an image for testing", type=["jpg", "jpeg", "png"])
    voice_msg = st.text_input("Tell Tony your problem (e.g. 'Easter is coming and my chocolate isn't moving!')")

# Initialize session state for persistence
for key in ["advice", "card", "en_audio", "es_audio", "tagline"]:
    if key not in st.session_state:
        st.session_state[key] = None

# MASTER LOGIC: Show both, but prioritize live for analysis
input_file = img_file if img_file else up_file
sample_img_path = "sample_shelf.png"
working_img = None

st.markdown("---")
img_col1, img_col2 = st.columns(2)

with img_col1:
    if os.path.exists(sample_img_path):
        st.image(sample_img_path, caption="🏙️ Tony's Prototype Reference")
        working_img = Image.open(sample_img_path) # Default to prototype

with img_col2:
    if input_file:
        live_img = Image.open(input_file)
        st.image(live_img, caption="📸 Your Live Shop Snap")
        working_img = live_img # Live takes priority for analysis
    else:
        st.info("💡 Pro Tip: Upload your own photo to see Tony analyze your shop!")

if working_img and api_key:
    if st.button("🚀 Generate Boost Package"):
        with st.spinner("Talking to Tony..."):
            try:
                advice_text = get_retail_advice(working_img, voice_msg, api_key, shop_vibe)
                st.session_state.advice = advice_text
                
                tagline = "Fresh & Local Bodega Vibes!"
                en_pitch = "Come check out our fresh deals today!"
                es_pitch = "¡Vengan a ver nuestras ofertas hoy!"
                
                if "[TAGLINE]:" in advice_text:
                    tagline = advice_text.split("[TAGLINE]:")[1].split("\n")[0].strip().strip('"')
                if "[ENGLISH_PITCH]:" in advice_text:
                    en_pitch = advice_text.split("[ENGLISH_PITCH]:")[1].split("\n")[0].strip().strip('"')
                if "[SPANISH_PITCH]:" in advice_text:
                    es_pitch = advice_text.split("[SPANISH_PITCH]:")[1].split("\n")[0].strip().strip('"')
                
                st.session_state.card = create_whatsapp_card(working_img, tagline, shop_phone, shop_hours)
                st.session_state.tagline = tagline
                
                # Identify if we are in demo mode for audio fallback
                is_demo = not input_file and os.path.exists(sample_img_path)
                
                st.session_state.en_audio = generate_audio_pitch(en_pitch, 'en', is_sample=is_demo)
                st.session_state.es_audio = generate_audio_pitch(es_pitch, 'es', is_sample=is_demo)
            except Exception as e:
                st.error(f"Error: {e}")

    # Display results
    if st.session_state.advice:
        st.success("✅ Boost Package Ready!")
        tabs = st.tabs(["📊 Retail Strategy", "📱 WhatsApp Card", "🔊 Audio Pitch", "📄 Shelf Tag"])
        
        with tabs[0]:
            st.markdown(st.session_state.advice)
        with tabs[1]:
            st.image(st.session_state.card, caption="Send this to your WhatsApp Status!")
            temp_path = "whatsapp_status_final.jpg"
            st.session_state.card.save(temp_path)
            with open(temp_path, "rb") as file:
                st.download_button("Download Image", file, temp_path, "image/jpeg")
        with tabs[2]:
            st.subheader("English Pitch")
            if st.session_state.en_audio:
                st.audio(st.session_state.en_audio)
            else:
                st.warning("⚠️ Tony's voice is resting (API limit). Read the English pitch in the Retail Strategy tab!")
                
            st.subheader("Spanish Pitch (Sabor Local)")
            if st.session_state.es_audio:
                st.audio(st.session_state.es_audio)
            else:
                st.warning("⚠️ El audio está en pausa. ¡Lea el discurso en español arriba!")
        with tabs[3]:
            st.info("Print this and stick it to your shelf!")
            st.markdown(f"""
            <div style="border: 5px solid black; padding: 20px; text-align: center; border-radius: 10px; background-color: #f9f9f9;">
                <h1 style="color: #FF4B4B; margin: 0;">{st.session_state.tagline}</h1>
                <hr>
                <p style="font-size: 24px; font-weight: bold;">{shop_name}</p>
                <p style="font-size: 18px;">{shop_phone}</p>
            </div>
            """, unsafe_allow_html=True)

elif not api_key:
    st.warning("Please enter your Google Gemini API Key in the sidebar to start (or set it in Cloud Envs).")
elif not working_img:
    st.warning("Please upload a photo or camera snap to get started.")
