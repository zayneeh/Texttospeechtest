import streamlit as st
import os
import time
import glob
import pandas as pd
from gtts import gTTS
from googletrans import Translator

# Create a temporary directory to store audio files
if not os.path.exists("temp"):
    os.mkdir("temp")

st.title("Crop Disease Management Advisor")

@st.cache_data
def load_data():
    try:
        data = pd.read_csv("disease_data.csv")
        data.columns = [col.strip().title() for col in data.columns]
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data()

if data.empty:
    st.stop()

translator = Translator()

# Languages
supported_languages = [
    "English",   
    "Amharic",
    "Swahili",
    "Hausa",
    "Yoruba",
    "Zulu",
    "Igbo",
    "Kinyarwanda",
    "Shona",
    "Somali",
    "Xhosa",
    "Sotho",
    "Tswana",
    "Chichewa",
    "Oromo",
    "Afrikaans",
    "Malagasy"
]

# Map language names to their codes for translation
language_codes = {
    "English": "en",     
    "Afrikaans": "af",
    "Amharic": "am",
    "Chichewa": "ny",
    "Hausa": "ha",
    "Igbo": "ig",
    "Kinyarwanda": "rw",
    #"Malagasy": "mg",
    "Oromo": "om",
    "Shona": "sn",
    "Somali": "so",
    "Sotho": "st",
    "Swahili": "sw",
    "Tswana": "tn",
    "Xhosa": "xh",
    #"Yoruba": "yo",
    "Zulu": "zu"
}

# Define English accents relevant to Africa
english_accents = [
    "Default",
    "United Kingdom",
    "South Africa"
]

# 1. Let the user pick a crop
crops = data["Crop"].unique()
crop = st.selectbox("Select Crop", crops)

# 2. Let the user pick a disease
filtered_diseases = data[data["Crop"] == crop]["Crop Disease"].unique()
disease = st.selectbox("Select Disease", filtered_diseases)

# 3. Let the user pick an output language
out_lang = st.selectbox("Select your output language", supported_languages)
output_language = language_codes.get(out_lang, "en")  # Default to English if not found

# 4. If English is chosen, let the user pick an English accent
if out_lang == "English":
    english_accent = st.selectbox("Select your English accent", english_accents)
    if english_accent == "Default":
        tld = "com"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "South Africa":
        tld = "co.za"
else:
    tld = "com"  # Default TLD for non-English languages

# Retrieve disease information
disease_info = data[(data["Crop"] == crop) & (data["Crop Disease"] == disease)]
if not disease_info.empty:
    causes = disease_info.iloc[0]["Causes"]
    prevention = disease_info.iloc[0]["Prevention"]
    treatment = disease_info.iloc[0]["Treatment"]

    # Here is the original text in English (from your dataset):
    original_text = (
        f"Disease: {disease}\n"
        f"Causes: {causes}\n"
        f"Prevention: {prevention}\n"
        f"Treatment: {treatment}"
    )

    # 5. Translate the text right away, so user can see the text
    try:
        translation_result = translator.translate(original_text, dest=output_language)
        display_text = translation_result.text
    except Exception as e:
        st.error(f"Error translating text: {e}")
        display_text = original_text

    # Display the text (translated or original if out_lang == "English")
    st.markdown("### Text Output:")
    st.write(display_text)

    # 6. TTS conversion
    def text_to_speech(display_text, lang_code, tld):
        try:
            tts = gTTS(display_text, lang=lang_code, tld=tld, slow=False)
            safe_filename = f"{crop}_{disease}".replace(" ", "_").replace("/", "_")[:20] + ".mp3"
            tts.save(f"temp/{safe_filename}")
            return safe_filename
        except Exception as e:
            st.error(f"Error in text-to-speech conversion: {e}")
            return None

    # Button for speech
    if st.button("🔊 Convert to Speech"):
        result = text_to_speech(display_text, output_language, tld)
        if result:
            try:
                with open(f"temp/{result}", "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.markdown(f"## 🎧 Your Audio:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)
            except Exception as e:
                st.error(f"Error playing audio: {e}")
else:
    st.error("❌ No information available for the selected crop and disease.")

# Cleanup old audio files
def remove_files(n_days=7):
    now = time.time()
    for f in glob.glob("temp/*.mp3"):
        try:
            if os.stat(f).st_mtime < now - n_days * 86400:
                os.remove(f)
                print(f"Deleted {f}")
        except Exception as e:
            print(f"Error deleting file {f}: {e}")

remove_files()
