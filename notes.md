To run **AURA Studio 4.3** on your local Windows machine, follow these steps exactly.

### ✅ Step 1: Pre-Flight Check

Before running the code, ensure these two things are ready:

1. **API Keys:**
Make sure you have a file named `.env` in your root folder (`C:\Users\AshutoshKumar\AURA_4.0\`) with your keys:
```ini
OPENAI_API_KEY="sk-..."
EURIAI_API_KEY="sk-..."
PEXELS_API_KEY="..."

```


2. **Music Library:**
Ensure you have MP3 files in `assets/music/` named exactly:
* `chill.mp3`
* `upbeat.mp3`
* `dramatic.mp3`
* `phonk.mp3`
* `corporate.mp3`



---

### 🚀 Step 2: Launch Command

Open your **Command Prompt (cmd)** or Terminal and run these commands one by one:

1. **Navigate to your folder:**
```bash
cd C:\Users\AshutoshKumar\AURA_4.0

```


2. **Activate your Virtual Environment:**
*(You should see `(venv)` appear at the start of your line)*
```bash
venv\Scripts\activate

```


3. **Install/Update Libraries:**
*(Do this just to be sure you have the latest `moviepy` fix)*
```bash
pip install -r requirements.txt

```


4. **Run the App:**
```bash
streamlit run src/app.py

```



---

### 🖥️ Step 3: Usage

Once you see the message **"You can now view your Streamlit app in your browser"**:

1. Your browser should auto-open to `http://localhost:8501`.
2. Go to **Creative Studio** on the sidebar.
3. Enter a Topic (e.g., "The Future of AI").
4. Select a Language (e.g., "Hindi") and Music Vibe.
5. Click **🚀 LAUNCH PRODUCTION**.

