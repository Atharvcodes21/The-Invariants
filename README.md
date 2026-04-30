# 🩺 VoiceRx Sync

> AI-powered voice-to-prescription system for doctors — with FHIR output, MongoDB storage, and Google OAuth login.

---

## Features

- 🎙️ **Voice Recording** → Doctor speaks naturally
- 🧠 **AI Extraction** → Groq (Whisper + LLaMA) converts speech to structured prescription JSON
- 🛡️ **Safety Validation** → Dose checking against medicine reference CSV
- 🏥 **FHIR Output** → FHIR-compatible Bundle (Patient, Condition, MedicationRequest)
- 📄 **PDF Generation** → Downloadable digital prescription
- 🔐 **Google OAuth Login** → Doctor authentication via Google account
- 📊 **Analytics Dashboard** → Consultations over time, top medicines, diagnosis distribution
- 🗄️ **MongoDB Storage** → All prescriptions + FHIR JSON stored in MongoDB Atlas

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend / UI | Streamlit (multi-page) |
| Speech-to-Text | Groq Whisper Large v3 |
| LLM Extraction | Groq LLaMA 3.3 70B |
| Database | MongoDB Atlas (pymongo + certifi) |
| Auth | Google OAuth 2.0 (PKCE) via google-auth-oauthlib |
| Charts | Plotly |
| PDF | fpdf2 |

---

## Project Structure

```
voicerx-sync/
├── app.py                        # Entry point — login page + st.navigation()
├── auth.py                       # Google OAuth PKCE flow
├── database.py                   # MongoDB operations
├── fhir_builder.py               # FHIR Bundle builder
├── llm_extract.py                # Groq LLM prescription extraction
├── stt.py                        # Groq Whisper transcription
├── validator.py                  # Medicine dose safety checker
├── pdf_generator.py              # Prescription PDF generator
├── medications.csv               # Medicine reference data
├── pages/
│   ├── 1_Dashboard.py            # Analytics dashboard
│   ├── 2_New_Consultation.py     # Voice recording + prescription form
│   └── 3_All_Consultations.py    # Search + drill-down consultation viewer
├── .env.example                  # Environment variable template
├── requirements.txt
└── .gitignore
```

---

## Setup

### 1. Clone & install

```bash
git clone https://github.com/your-username/voicerx-sync.git
cd voicerx-sync
python -m venv venv
.\venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Where to get it |
|----------|----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `MONGO_URI` | [cloud.mongodb.com](https://cloud.mongodb.com) → Connect → Drivers |
| `GOOGLE_CLIENT_ID` | Google Cloud Console → APIs & Services → Credentials |
| `GOOGLE_CLIENT_SECRET` | Same OAuth 2.0 client → Client Secret |

> **MongoDB URI note:** URL-encode special characters in your password:  
> `#` → `%23`, `*` → `%2A`, `@` → `%40`

### 3. Google Cloud Console setup

1. Go to [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
2. Create or use an existing **OAuth 2.0 Client ID** (type: **Desktop app**)
3. Add `http://localhost:8501` to **Authorized Redirect URIs**
4. Go to **OAuth consent screen** → **Publish App** (allows any Google account to log in)

### 4. MongoDB Atlas setup

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. Go to **Network Access** → Add IP `0.0.0.0/0` (allow all, for dev)
3. Create a database user and copy the connection URI

### 5. Run

```bash
.\venv\Scripts\streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Usage

1. **Login** with your Google account
2. Go to **New Consultation** → record your voice
3. AI extracts the prescription → review & edit → approve → sync to MongoDB
4. View **Dashboard** for analytics (today / week / month / year / all time)
5. Browse **All Consultations** → click any record to see full Medical JSON + FHIR JSON

---

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for Whisper + LLaMA | ✅ |
| `MONGO_URI` | MongoDB Atlas connection string | ✅ |
| `MONGO_DB_NAME` | Database name (default: `voicerx`) | ✅ |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Client Secret | ✅ |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI (default: `http://localhost:8501`) | ✅ |
| `OAUTHLIB_INSECURE_TRANSPORT` | Set `1` for localhost HTTP (dev only) | ✅ dev |

---

## Security Notes

- `.env` is gitignored — never commit real credentials
- PKCE (S256) is used for Google OAuth — no auth code interception risk
- `OAUTHLIB_INSECURE_TRANSPORT=1` is **dev only** — remove this for HTTPS production deployment
- Doctors only see their own consultations (scoped by `doctor_email`)

---

## License

MIT