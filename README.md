. # 🍎 NYC Bodega AI Retail Advisor

**Live Demo**: [https://nyc-bodega-advisor-1039268545039.us-east1.run.app](https://nyc-bodega-advisor-1039268545039.us-east1.run.app)

A "Main Street AI" tool designed for small grocery owners in NYC to increase loyalty and sales through multimodal AI.

Small grocery owners globally as in New York are facing tremendous challenges to their businesses. Online, large competitors, next generation family members refusing to join the business, etc. These small store owners serve important needs in serving the local population (many times the marginal income earners). 

These owners have mobile phones which have powerful cameras but many of them are completely unware of the tools and technologies to help them boost their sales and retain customer loyalty. They also cannot afford to hire expensive consultants. 

Hence, an AI digital assistant app to help them boost sales. 

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

---

## 👨‍💻 Developer
**Mahesh Khatri**  
📧 [mahesh@kaytek.in](mailto:mahesh@kaytek.in)  
📧 [khatrimahesh@gmail.com](mailto:khatrimahesh@gmail.com)
