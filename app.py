
import streamlit as st
import os
import time
import glob
from gtts import gTTS
from googletrans import Translator
import pandas as pd 

# Create a temporary directory to store audio files
if not os.path.exists("temp"):
    os.mkdir("temp")

st.title("Crop Disease Management Advisor")

# Translator setup
translator = Translator()

disease_data = pd.read_csv("disease_data.csv")
# User inputs for the application
crop = st.selectbox("Select a crop", list(disease_data.keys()))
disease = st.selectbox("Select a disease", list(disease_data[crop].keys()))

# Translate to a selection of African languages
input_language = "en"  # Assuming the data is initially in English
out_lang = st.selectbox(
    "Select your output language",
    ["Amharic", "Swahili", "Hausa", "Yoruba", "Zulu"]
)

output_language = {
    "Amharic": "am",
    "Swahili": "sw",
    "Hausa": "ha",
    "Yoruba": "yo",
    "Zulu": "zu"
}[out_lang]

# Generate text summary of the disease management
text = f"Disease: {disease}\nCauses: {disease_data[crop][disease]['causes']}\nPrevention: {disease_data[crop][disease]['prevention']}\nTreatment: {disease_data[crop][disease]['treatment']}"

def text_to_speech(input_language, output_language, text):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, slow=False)
    file_name = f"{crop}_{disease}.mp3"
    tts.save(f"temp/{file_name}")
    return file_name, trans_text

display_output_text = st.checkbox("Display output text")

if st.button("Convert to Speech"):
    result, output_text = text_to_speech(input_language, output_language, text)
    audio_file = open(f"temp/{result}", "rb")
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format="audio/mp3")
    if display_output_text:
        st.write(output_text)

# Clean up old audio files
def remove_files():
    now = time.time()
    for f in glob.glob("temp/*.mp3"):
        if os.stat(f).st_mtime < now - 7 * 86400:  # 7 days old
            os.remove(f)

remove_files()
