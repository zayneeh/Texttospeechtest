import streamlit as st
import os
import time
import glob
import pandas as pd
from gtts import gTTS
from googletrans import Translator

# Create a temporary directory to store audio files if it doesn't exist
if not os.path.exists("temp"):
    os.mkdir("temp")

st.title("Crop Disease Management Advisor")

# Load the dataset

@st.cache_data
def load_data():
    try:
        data = pd.read_csv("disease_data.csv")
        # Clean column names by stripping whitespace and ensuring proper capitalization
        data.columns = [col.strip().title() for col in data.columns]
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data()

if data.empty:
    st.stop()
# Initialize Translator
translator = Translator()

# Define African languages supported by Google Translate
african_languages = [
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

# Map language names to language codes
language_codes = {
    "Afrikaans": "af",
    "Amharic": "am",
    "Chichewa": "ny",
    "Hausa": "ha",
    "Igbo": "ig",
    "Kinyarwanda": "rw",
    "Malagasy": "mg",
    "Oromo": "om",
    "Shona": "sn",
    "Somali": "so",
    "Sotho": "st",
    "Swahili": "sw",
    "Tswana": "tn",
    "Xhosa": "xh",
    "Yoruba": "yo",
    "Zulu": "zu"
}

# Define English accents relevant to Africa
english_accents = [
    "Default",
    "United Kingdom",
    "South Africa"
]

# User selects the crop
crops = data["Crop"].unique()
crop = st.selectbox("Select Crop", crops)

# Filter diseases based on selected crop
diseases = data["Crop Disease"].unique()
disease = st.selectbox("Select Disease", diseases)

# Select output language
out_lang = st.selectbox(
    "Select your output language",
    african_languages
)

output_language = language_codes.get(out_lang, "en")  # Default to English if not found

# Select English accent if English is chosen
if out_lang == "English":
    english_accent = st.selectbox(
        "Select your English accent",
        english_accents
    )
    if english_accent == "Default":
        tld = "com"
    elif english_accent == "United Kingdom":
        tld = "co.uk"
    elif english_accent == "South Africa":
        tld = "co.za"
else:
    tld = "com"  # Default tld for non-English languages

# Retrieve disease information
disease_info = data[(data["Crop"] == crop) & (data["Crop Disease"] == disease)]

if not disease_info.empty:
    causes = disease_info.iloc[0]["Causes"]
    prevention = disease_info.iloc[0]["Prevention"]
    treatment = disease_info.iloc[0]["Treatment"]

    # Generate the text to be converted to speech
    text = f"Disease: {disease}\nCauses: {causes}\nPrevention: {prevention}\nTreatment: {treatment}"

    # Define the TTS function
    def text_to_speech(output_language, text, tld):
        try:
            # Translate the text
            translation = translator.translate(text, dest=output_language)
            trans_text = translation.text
            # Convert to speech
            tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
            # Generate a safe filename
            safe_filename = f"{crop}_{disease}".replace(" ", "_").replace("/", "_")[:20] + ".mp3"
            tts.save(f"temp/{safe_filename}")
            return safe_filename, trans_text
        except Exception as e:
            st.error(f"Error in text-to-speech conversion: {e}")
            return None, None

    # Button to trigger TTS conversion
    if st.button("🔊 Convert to Speech"):
        result, output_text = text_to_speech(output_language, text, tld)
        if result:
            try:
                with open(f"temp/{result}", "rb") as audio_file:
                    audio_bytes = audio_file.read()
                st.markdown(f"## 🎧 Your Audio:")
                st.audio(audio_bytes, format="audio/mp3", start_time=0)

                # Optionally display the translated text
                if st.checkbox("📝 Display Output Text"):
                    st.markdown(f"## 📝 Output Text:")
                    st.write(output_text)
            except Exception as e:
                st.error(f"Error playing audio: {e}")
else:
    st.error("❌ No information available for the selected crop and disease.")

# Function to remove old audio files
def remove_files(n_days=7):
    now = time.time()
    for f in glob.glob("temp/*.mp3"):
        try:
            if os.stat(f).st_mtime < now - n_days * 86400:
                os.remove(f)
                print(f"Deleted {f}")
        except Exception as e:
            print(f"Error deleting file {f}: {e}")

# Clean up old files
remove_files()
