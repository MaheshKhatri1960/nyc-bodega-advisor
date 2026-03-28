# 🍎 NYC Bodega AI Retail Advisor

A "Main Street AI" tool designed for small grocery owners in NYC to increase loyalty and sales through multimodal AI.

## 🚀 Features
- **Visual Shelf Analysis**: point your camera at a shelf to get placement and bundle advice.
- **WhatsApp Marketing**: Automatically generated image cards with your shop's branding.
- **Bilingual Pitch**: 1-minute audio pitches in English and Spanish (Sabor Local) to attract customers.
- **Printable Shelf Tags**: Instant, punchy tags for your store displays.
- **NYC Persona**: Strategy advice from 'Tony', a savvy NYC retail consultant.

## 🛠️ Tech Stack
- **AI**: Gemini 1.5 Flash (Multimodal Vision & Reasoning)
- **UI**: Streamlit
- **Image**: Pillow (PIL)
- **Audio**: gTTS

## 🏃 How to Run
1. Install dependencies:
   ```bash
   pip install google-generativeai streamlit pillow gTTS
   ```
2. Set up your Gemini API Key from [Google AI Studio](https://aistudio.google.com/).
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📝 Hackathon Notes
- Created in 120 minutes for a "Main Street AI" hackathon.
- Uses a Storyboard approach for visual planning.
- Prioritizes low-latency and "Live" feel using Gemini 1.5 Flash.
