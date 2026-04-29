import json
import streamlit as st

from stt import save_audio_file, transcribe_audio
from llm_extract import extract_medical_json
from validator import validate_medicines
from fhir_builder import build_fhir_prescription
from pdf_generator import create_prescription_pdf


st.set_page_config(
    page_title="VoiceRx Sync",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }

    .hero-card {
        background: linear-gradient(135deg, #e0f2fe 0%, #dcfce7 100%);
        padding: 1.5rem;
        border-radius: 22px;
        border: 1px solid #dbeafe;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .small-text {
        font-size: 0.9rem;
        color: #64748b;
    }
    </style>
    """,
    unsafe_allow_html=True
)


def initialize_session_state():
    defaults = {
        "transcript": "",
        "medical_json": None,
        "final_data": None,
        "fhir_json": None,
        "pdf_path": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_safe_age(value):
    try:
        if value is None:
            return 0
        return int(value)
    except Exception:
        return 0


initialize_session_state()


with st.sidebar:
    st.title("🩺 VoiceRx Sync")
    st.caption("Doctor voice to digital prescription")

    st.divider()

    st.subheader("Workflow")
    st.write("1. Record doctor voice")
    st.write("2. Convert speech to text")
    st.write("3. Extract prescription JSON")
    st.write("4. Validate medicine dose")
    st.write("5. Generate PDF + FHIR JSON")

    st.divider()

    st.subheader("Demo Sentence")
    st.info(
        "Ramu, age 25, symptoms of headache and fever. "
        "Give him Paracetamol 500mg twice a day for three days."
    )

    st.subheader("Overdose Test")
    st.warning(
        "Try: Ramu has fever. Give Paracetamol 5000mg twice a day."
    )

    st.divider()

    st.caption(
        "Safety: This is a clinical documentation assistant, "
        "not an autonomous prescribing system."
    )


st.markdown(
    """
    <div class="hero-card">
        <h1>🩺 VoiceRx Sync</h1>
        <p>
        Convert doctor voice notes into structured, validated, editable,
        FHIR-style digital prescriptions.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(
        """
        <div class="metric-card">
            <h3>🎙️ Voice Input</h3>
            <p class="small-text">Doctor speaks naturally.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        """
        <div class="metric-card">
            <h3>🧠 AI Extraction</h3>
            <p class="small-text">Patient, symptoms, medicines.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        """
        <div class="metric-card">
            <h3>🛡️ Safety Check</h3>
            <p class="small-text">Dose validation using CSV.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


left_col, right_col = st.columns([1, 1.25], gap="large")


with left_col:
    st.header("🎙️ Doctor Recording")

    audio_file = st.audio_input(
        "Record voice prescription",
        help="Click microphone, speak, then stop recording."
    )

    if audio_file:
        st.audio(audio_file)

        if st.button("🚀 Process Voice Note", type="primary", use_container_width=True):
            try:
                with st.status("Processing prescription...", expanded=True) as status:
                    st.write("Saving audio...")
                    audio_path = save_audio_file(audio_file)

                    st.write("Transcribing voice...")
                    transcript = transcribe_audio(audio_path)
                    st.session_state.transcript = transcript

                    st.write("Extracting prescription JSON...")
                    extracted_json = extract_medical_json(transcript)

                    st.write("Checking medicine safety...")
                    validated_json = validate_medicines(extracted_json)
                    st.session_state.medical_json = validated_json

                    status.update(
                        label="Prescription processed successfully!",
                        state="complete",
                        expanded=False
                    )

                st.success("Voice note processed successfully!")

            except Exception as e:
                st.error("Something went wrong.")
                st.exception(e)

    st.subheader("📝 Transcript")

    if st.session_state.transcript:
        st.info(st.session_state.transcript)
    else:
        st.caption("Transcript will appear here after processing.")


with right_col:
    st.header("📋 Extracted Prescription")

    if st.session_state.medical_json is None:
        st.info("Record and process a voice note to generate prescription data.")

    else:
        data = st.session_state.medical_json

        with st.form("prescription_form"):
            patient_name = st.text_input(
                "Patient Name",
                value=data.get("patient_name") or ""
            )

            age = st.number_input(
                "Age",
                min_value=0,
                max_value=120,
                value=get_safe_age(data.get("age"))
            )

            diagnosis = st.text_input(
                "Diagnosis",
                value=data.get("diagnosis") or ""
            )

            symptoms_text = st.text_area(
                "Symptoms",
                value=", ".join(data.get("symptoms", []))
            )

            st.subheader("Medicines")

            edited_medicines = []

            medicines = data.get("medicines", [])

            if not medicines:
                st.warning("No medicines detected.")

            for i, med in enumerate(medicines):
                st.markdown(f"### Medicine {i + 1}")

                c1, c2 = st.columns(2)

                with c1:
                    name = st.text_input(
                        f"Medicine Name {i + 1}",
                        value=med.get("name", ""),
                        key=f"med_name_{i}"
                    )

                    dosage = st.text_input(
                        f"Dosage {i + 1}",
                        value=med.get("dosage", ""),
                        key=f"med_dosage_{i}"
                    )

                with c2:
                    frequency = st.text_input(
                        f"Frequency {i + 1}",
                        value=med.get("frequency", ""),
                        key=f"med_frequency_{i}"
                    )

                    duration = st.text_input(
                        f"Duration {i + 1}",
                        value=med.get("duration", ""),
                        key=f"med_duration_{i}"
                    )

                warning = med.get("warning", "")

                if warning == "Validated":
                    st.success("✅ Medicine dose validated")
                else:
                    st.warning(f"⚠️ {warning}")

                edited_medicines.append(
                    {
                        "name": name,
                        "dosage": dosage,
                        "frequency": frequency,
                        "duration": duration,
                        "warning": warning,
                    }
                )

            approved = st.checkbox("Doctor reviewed and approved")

            submit = st.form_submit_button(
                "💾 Save Final Prescription",
                type="primary",
                use_container_width=True
            )

            if submit:
                final_data = {
                    "patient_name": patient_name,
                    "age": age,
                    "diagnosis": diagnosis,
                    "symptoms": [
                        symptom.strip()
                        for symptom in symptoms_text.split(",")
                        if symptom.strip()
                    ],
                    "medicines": edited_medicines,
                    "safety_warnings": data.get("safety_warnings", []),
                    "doctor_approved": approved,
                }

                st.session_state.final_data = final_data
                st.success("Final prescription saved.")

        if st.session_state.final_data:
            st.divider()

            st.subheader("🧾 Final JSON")
            st.json(st.session_state.final_data)

            if not st.session_state.final_data.get("doctor_approved"):
                st.warning("Doctor approval is required before syncing.")

            sync_disabled = not st.session_state.final_data.get("doctor_approved")

            if st.button(
                "🟢 Sync to ABDM / ABHA Demo",
                type="primary",
                disabled=sync_disabled,
                use_container_width=True
            ):
                fhir_json = build_fhir_prescription(st.session_state.final_data)
                pdf_path = create_prescription_pdf(st.session_state.final_data)

                st.session_state.fhir_json = fhir_json
                st.session_state.pdf_path = pdf_path

                print("FHIR-compatible ABDM-ready demo JSON:")
                print(json.dumps(fhir_json, indent=2))

                st.success("Prescription prepared successfully!")
                st.balloons()

            if st.session_state.fhir_json:
                st.subheader("🏥 FHIR-style Demo Payload")
                st.json(st.session_state.fhir_json)

            if st.session_state.pdf_path:
                with open(st.session_state.pdf_path, "rb") as pdf_file:
                    st.download_button(
                        "📄 Download Digital Prescription PDF",
                        data=pdf_file,
                        file_name="digital_prescription.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )