import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import os
import datetime

# --- CONFIGURATION ---
MODEL_ID = "gemini-1.5-flash"  # Low latency for hackathon

NYC_PERSONA = """
You are 'Tony', a savvy, street-smart NYC retail consultant for local bodegas. 
Your tone is funny, local, and encouraging. Use NYC slang (e.g., 'Deadass', 'The real deal', 'Bodega style'). 
You help small shops beat big stores like Costco and Walmart by being 'agile' and 'community-first'.

When you see a product or shelf display captured via camera:
1. **Identify**: List the product categories and names.
2. **Strategy**: Suggest one 'High-Margin Placement' (where to put it to sell faster).
3. **Offers**: Suggest a 'NYC Bundle' (e.g., 'The 5 AM Commuter special').
4. **Marketing**: 
   - A funny, catchy tagline for WhatsApp (Maximum 5 words).
   - A simple recipe for the item (if fruit/veg).
   - A 1-minute 'Street Pitch' in both English and Spanish.
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
    api_key = st.text_input("Enter Google Gemini API Key", type="password")
    shop_name = st.text_input("Shop Name", "My NYC Grocery")
    shop_phone = st.text_input("WhatsApp Number", "+1 (212) - 123 4567")
    shop_hours = st.text_input("Timings", "8:00 AM - 8:00 PM")
    shop_vibe = st.radio("Shop Vibe", ["Community Friendly", "Deals Focused", "Premium Quality"])
    
    st.markdown("---")
    st.info("💡 Pro Tip: Snap a photo of your shelves to get placement advice!")

# --- FUNCTIONS ---
def get_retail_advice(image, problem, api_key, vibe):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(MODEL_ID, system_instruction=NYC_PERSONA)
    
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
    # Resize image for standard card size if needed
    base = img.convert("RGBA")
    txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    
    # Overlay semi-transparent box at the bottom
    w, h = base.size
    box_height = h // 4
    draw.rectangle([0, h - box_height, w, h], fill=(0, 0, 0, 160))
    
    # Text Drawing logic (simplified for hackathon)
    # Note: In a real hackathon, you'd load a local font file. 
    # Here we use default for speed, though results vary.
    try:
        font = ImageFont.load_default()
    except:
        font = None
        
    draw.text((w//10, h - box_height + 20), f"🔥 {tagline}", fill="white", font=font)
    draw.text((w//10, h - 40), f"📞 {phone} | ⏰ {hours}", fill="yellow", font=font)
    
    out = Image.alpha_composite(base, txt)
    return out.convert("RGB")

def generate_audio_pitch(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    filename = f"pitch_{lang}.mp3"
    tts.save(filename)
    return filename

# --- MAIN UI ---
st.title("🍎 NYC Bodega Advisor AI")
st.write("Helping Main Street beat the big stores one snap at a time.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📸 Snap your Display")
    img_file = st.camera_input("Take a photo of a product or shelf")
    voice_msg = st.text_input("Tell Tony your problem (e.g. 'Easter is coming and my chocolate isn't moving!')")

# Initialize session state for persistence
if "advice" not in st.session_state:
    st.session_state.advice = None
if "card" not in st.session_state:
    st.session_state.card = None
if "en_audio" not in st.session_state:
    st.session_state.en_audio = None
if "es_audio" not in st.session_state:
    st.session_state.es_audio = None
if "tagline" not in st.session_state:
    st.session_state.tagline = None

if img_file and api_key:
    img = Image.open(img_file)
    
    if st.button("🚀 Generate Boost Package"):
        with st.spinner("Talking to Tony..."):
            try:
                # 1. Get AI Advice
                advice_text = get_retail_advice(img, voice_msg, api_key, shop_vibe)
                st.session_state.advice = advice_text
                
                # 2. Extract Tagline & Pitches
                tagline = "Fresh & Local Bodega Vibes!"
                en_pitch = "Come check out our fresh deals today at the shop!"
                es_pitch = "¡Vengan a ver nuestras ofertas hoy en la tienda!"
                
                if "[TAGLINE]:" in advice_text:
                    tagline = advice_text.split("[TAGLINE]:")[1].split("\n")[0].strip().strip('"')
                if "[ENGLISH_PITCH]:" in advice_text:
                    en_pitch = advice_text.split("[ENGLISH_PITCH]:")[1].split("\n")[0].strip().strip('"')
                if "[SPANISH_PITCH]:" in advice_text:
                    es_pitch = advice_text.split("[SPANISH_PITCH]:")[1].split("\n")[0].strip().strip('"')
                
                # 3. Create Visuals
                st.session_state.card = create_whatsapp_card(img, tagline, shop_phone, shop_hours)
                st.session_state.tagline = tagline
                
                # 4. Generate Audio
                st.session_state.en_audio = generate_audio_pitch(en_pitch, 'en')
                st.session_state.es_audio = generate_audio_pitch(es_pitch, 'es')
                
            except Exception as e:
                st.error(f"Error: {e}")

    # Display results if they exist in session state
    if st.session_state.advice:
        st.success("✅ Boost Package Ready!")
        tabs = st.tabs(["📊 Retail Strategy", "📱 WhatsApp Card", "🔊 Audio Pitch", "📄 Shelf Tag"])
        
        with tabs[0]:
            st.markdown(st.session_state.advice)
        
        with tabs[1]:
            st.image(st.session_state.card, caption="Send this to your WhatsApp Status!")
            # Save and provide download
            st.session_state.card.save("whatsapp_status.jpg")
            with open("whatsapp_status.jpg", "rb") as file:
                st.download_button("Download Image", file, "whatsapp_status.jpg", "image/jpeg")
        
        with tabs[2]:
            st.subheader("English Pitch")
            st.audio(st.session_state.en_audio)
            st.subheader("Spanish Pitch (Sabor Local)")
            st.audio(st.session_state.es_audio)
        
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
            st.button("🖨️ Print (Mock)")

elif not api_key:
    st.warning("Please enter your Google Gemini API Key in the sidebar to start.")
