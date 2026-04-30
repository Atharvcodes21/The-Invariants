import os
import json
import streamlit as st
import soundfile as sf       # <-- NEW: For reading/writing audio
import noisereduce as nr     # <-- NEW: For removing background hum
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# --- 1. CONFIG & PROMPTS ---

SYSTEM_PROMPT = """
You are a medical data extraction assistant.
Convert the doctor's English transcript into valid JSON.
Return exactly this JSON structure:
{
  "patient_name": string or null,
  "age": number or null,
  "symptoms": [string],
  "diagnosis": string or null,
  "medicines": [
    {
      "name": string,
      "dosage": string,
      "frequency": string,
      "duration": string
    }
  ],
  "advice": string or null
}
Rules:
- The input transcript will be in English only.
- Output only valid JSON.
- Do not write explanations.
- Do not include markdown.
- Do not include extra keys outside the required JSON structure.
- Use common generic medicine names when possible.
- Keep medicine names in English.
- Keep symptoms and diagnosis in English.
- If patient name is missing, use null.
- If age is missing, use null.
- If symptoms are missing, use an empty list.
- If diagnosis is unclear, use null.
- If no medicines are found, use an empty list.
- If dosage, frequency, or duration is missing for a medicine, use null for that field.
"""

# --- 2. API SETUP ---

def get_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key = None
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Add it to .env or Streamlit secrets.")
    return api_key

def get_groq_client():
    return Groq(api_key=get_api_key())

# --- 3. AUDIO PROCESSING & AI PIPELINE ---

def save_audio_file(audio_file) -> str:
    """Saves Streamlit recorded audio to temp folder."""
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, "raw_recording.wav")
    with open(file_path, "wb") as f:
        f.write(audio_file.getbuffer())
    return file_path

def clean_audio(input_file_path: str) -> str:
    """
    NEW: Reads the raw audio, applies noise reduction, and saves a clean version.
    """
    # 1. Load the raw audio
    audio_data, rate = sf.read(input_file_path)
    
    # 2. Apply spectral gating noise reduction
    reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=rate)
    
    # 3. Save as a new clean file
    clean_file_path = input_file_path.replace("raw_recording", "clean_recording")
    sf.write(clean_file_path, reduced_noise_audio, rate)
    
    return clean_file_path

def transcribe_audio(audio_path: str) -> str:
    """Sends the CLEANED audio file to Groq Whisper and returns text."""
    client = get_groq_client()
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(audio_path, file.read()),
            model="whisper-large-v3",
            response_format="text",
        )
    return transcription

def extract_medical_json(transcript: str) -> dict:
    """Converts transcript into structured prescription JSON using Llama 3."""
    if not transcript or not transcript.strip():
        return {
            "patient_name": None, "age": None, "symptoms": [],
            "diagnosis": None, "medicines": [], "advice": None
        }

    client = get_groq_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    
    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "patient_name": None, "age": None, "symptoms": [],
            "diagnosis": None, "medicines": [], "advice": None
        }

# --- 4. STREAMLIT UI ---

st.set_page_config(page_title="Clinical Co-Pilot", page_icon="🩺", layout="centered")

st.title("🩺 Clinical Co-Pilot")
st.markdown("### Ambient Scribe with Active Noise Cancellation")

# The microphone widget
audio_value = st.audio_input("Record Dictation")

if audio_value:
    with st.spinner("Processing clinical audio..."):
        # Step 1: Save the raw audio
        raw_path = save_audio_file(audio_value)
        
        # Step 2: Clean the audio (Noise Reduction)
        st.toast("Applying noise reduction...")
        clean_path = clean_audio(raw_path)
        
        # Step 3: Send clean audio to Whisper
        st.toast("Transcribing audio...")
        transcription = transcribe_audio(clean_path)
        
        # Optional: Show the doctor what Whisper heard
        with st.expander("View Raw Transcription"):
            st.write(transcription)
        
        # Step 4: Send text to Llama 3 for JSON extraction
        st.toast("Structuring clinical data...")
        json_output = extract_medical_json(transcription)
        
        # Step 5: Display Final Output
        st.subheader("Structured Clinical Data (FHIR Ready)")
        st.json(json_output)