# Chinese Translator 🇨🇳 ➡️ 🇮🇩

**Chinese Translator** is a real-time speech translation system designed to translate spoken Mandarin (Chinese) to Indonesian (Bahasa Indonesia).

---

## 📖 Background & Motivation

In our company, we frequently collaborate with a team based in Beijing, China. We conduct regular online sharing sessions using **VOOV Meeting** (Tencent Meeting). Because the Beijing team members are not always fluent in English, they prefer using Mandarin to elaborate and present during these sessions.

To bridge this language barrier and facilitate smooth collaboration, this project was developed. It captures system/meeting audio (or microphone input) in real time, transcribes the Mandarin speech, translates it into Indonesian, and displays it instantly in a clean web interface.

Additionally, this project serves as a practical codebase to learn, expand, and improve my knowledge of **Artificial Intelligence (AI)**—specifically exploring real-time Speech-to-Text (STT) APIs, building custom voice activity detection (VAD), and orchestrating Large Language Model (LLM) translation endpoints.

---

## 🛠️ Tech Stack & Architecture

This application uses a modern, lightweight, and high-performance tech stack:

### 1. Backend (Python & FastAPI)

- **[FastAPI](https://fastapi.tiangolo.com/)**: A modern, fast web framework for building APIs with Python. It handles WebSocket connections for real-time binary audio streaming.
- **[uv](https://github.com/astral-sh/uv)**: An extremely fast Python package manager and resolver used to manage virtual environments and dependencies.
- **[NumPy](https://numpy.org/)**: Used on the server-side to calculate RMS (Root Mean Square) energy of audio frames for custom Voice Activity Detection (VAD).
- **[Uvicorn](https://www.uvicorn.org/)**: ASGI server to run the FastAPI application.

### 2. AI Services (Cloud APIs)

- **[Groq API (Whisper-large-v3)](https://groq.com/)**: Used for lightning-fast, highly accurate Speech-to-Text (STT) transcription of Mandarin.
- **[OpenRouter API (openai/gpt-4o-mini)](https://openrouter.ai/)**: Used as the Translation Engine. It translates the Mandarin transcripts to natural Indonesian. The prompt is strictly optimized to only translate and not answer questions.

### 3. Frontend (Web Audio API & WebSockets)

- **HTML5 / JavaScript (Vanilla CSS)**: A premium glassmorphism dark-themed UI that manages audio capturing, logs, and translation bubbles.
- **Web Audio API**: Captures native browser microphone or system loopback audio.
- **Client-side Downsampler**: Automatically downsamples native browser audio (usually 44.1kHz or 48kHz on macOS) to **16000Hz mono 16-bit PCM** before sending it, ensuring perfect pitch and speed compatibility with the Whisper model.

---

## 🚀 Setup & Installation

### Prerequisites

Make sure you have `uv` installed. If you don't have it, install it using Homebrew on macOS:

```bash
brew install uv
```

### 1. Clone the Project

```bash
git clone <repository-url>
cd chinese-translator
```

### 2. Configure Environment Variables

Copy the `.env.example` file to `.env`:

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
GROQ_API_KEY=gsk_your_key_here
OPENROUTER_API_KEY=sk-or-your_key_here
OPENROUTER_MODEL=openai/gpt-4o-mini
```

### 3. Install Dependencies

Sync and download dependencies using `uv` (or `make`):

```bash
make install
```

_This will create a `.venv` virtual environment and install all packages locked in `uv.lock`._

---

## 💻 How to Run & Use

### Step 1: Start the Translation Server

Run the FastAPI backend:

```bash
make run-server
```

The server will start on **`http://127.0.0.1:9099`**.

### Step 2: Open the Web UI

Open your browser and navigate to:

```
http://127.0.0.1:9099
```

### Step 3: Capture VOOV Meeting Audio

1. Open **VOOV Meeting** and join your session.
2. In the Chinese Translator Web UI, click **"Hubungkan"** to open the WebSocket connection.
3. Click **"Mulai Desktop Audio"**.
4. A browser prompt will ask you to share a screen, window, or tab.
   - **On Chrome (macOS/Windows)**: Select the VOOV Meeting window or your entire screen.
   - ⚠️ **IMPORTANT**: Make sure to check the **"Share system audio"** (or **"Share audio"**) checkbox at the bottom left of the selection dialog.
5. Once shared, any Mandarin audio spoken during the VOOV Meeting will automatically stream to the backend, translate to Indonesian, and print on your screen!

---

## 🧪 Testing with Dummy Audio

If you want to test the translation pipeline without a live meeting:

1. Generate a dummy Mandarin audio file:
   ```bash
   make dummy
   ```
2. Run the test client which streams the generated WAV file directly to the running server:
   ```bash
   make test-client
   ```
3. Check the client logs or Web UI to verify the transcribed and translated Indonesian output.

---

## 📁 Project Structure

- `server.py`: FastAPI server containing WebSocket endpoints and VAD/API client logic.
- `index.html`: Web interface for recording audio and viewing translations.
- `generate_dummy.py`: Script to generate dummy Chinese speech for testing.
- `test_client.py`: Python CLI client to simulate audio streaming.
- `client.py`: Windows-specific audio capturing client (using WASAPI).
- `Makefile`: Quick shortcuts for developer workflows.
- `pyproject.toml` & `uv.lock`: Dependency definitions managed by `uv`.

## Demo

https://github.com/user-attachments/assets/aeed8d73-90e2-4428-b410-0bb269643c06
