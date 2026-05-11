
# 🎓 EduComic – Generative AI-Based Lecture-to-Comic Learning System

EduComic is an AI-powered educational platform that converts lecture videos into interactive, visual, and engaging learning content.  
It integrates speech recognition, natural language processing, retrieval-augmented generation (RAG), and comic-style visualization to improve student comprehension, retention, and engagement.

The system is designed as an offline-first, privacy-focused AI solution suitable for academic, research, and institutional environments.

---

## 🚀 Key Features

- 🎥 Video-to-Text Conversion  
  Upload lecture videos or provide YouTube links. Audio is extracted and transcribed using Whisper ASR.

- 🧠 NLP-Based Lecture Understanding  
  Performs topic segmentation, educational summarization, and keyword/concept extraction.

- 💬 RAG-Based Chatbot  
  Enables context-aware question answering using FAISS-based semantic retrieval and a local language model.

- 🎨 Comic-Style Visualization  
  Converts summarized lecture content into comic-style visual panels using diffusion-based generative models.

- 🔐 Offline & Privacy-Focused  
  All processing is done locally without dependency on cloud APIs.

---

## 🏗️ System Architecture (High-Level)

```

User
↓
Video Upload / YouTube Link
↓
Audio Extraction (yt-dlp)
↓
Whisper ASR → Transcript
↓
NLP Processing (Segmentation, Summarization)
↓
├── FAISS Vector Store → RAG Chatbot
└── Comic Visualization (Stable Diffusion)
↓
Database & Media Storage

```

---

## 🛠️ Technology Stack

### Backend
- Python
- Django
- FastAPI (AI orchestration – research reference)

### AI / ML
- Whisper ASR
- BERT-based embeddings
- BART / PEGASUS (Summarization)
- Retrieval-Augmented Generation (RAG)
- Stable Diffusion / ComfyUI

### Frontend
- Django Templates (HTML/CSS)
- React.js (research architecture reference)

### Database & Storage
- SQLite (development)
- MongoDB (research reference)
- FAISS (vector similarity search)
- Local media storage

---

## 📁 Project Structure

```

comic_generator/
│
├── comic_web/          # Django project configuration
├── core/               # Core application logic (AI + views)
├── media/              # Uploaded videos & generated comics
├── db.sqlite3          # Local database
│
├── manage.py           # Django entry point
├── debug_import.py     # Dependency checks
├── debug_whisper.py    # Whisper & Torch validation
├── test_sr.py          # Speech recognition tests

````

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/omgupta2004/comic_generator.git
cd comic_generator
````

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Ensure FFmpeg is installed and available in system PATH.

### 4. Run the Application

```bash
python manage.py migrate
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

---

## 🧪 Testing Utilities

* `debug_import.py` – Dependency and environment verification
* `debug_whisper.py` – Whisper and Torch setup validation
* `test_sr.py` – Speech recognition testing

---

## 📊 Experimental Results (Research)

| Module        | Metric                   | Performance |
| ------------- | ------------------------ | ----------- |
| ASR           | Word Error Rate Accuracy | 92.8%       |
| Summarization | ROUGE-L Score            | 0.86        |
| Chatbot       | Context Match Accuracy   | 88.5%       |

---

## 📄 Research Reference

**Title:** Generative AI-Based EduComic System for Lecture Visualization and Chat Interaction

This project implements a research framework integrating:

* Whisper-based lecture transcription
* NLP-driven semantic analysis
* RAG-powered conversational AI
* Diffusion-based comic visualization

---

## 🎯 Use Cases

* University lecture revision
* Self-paced learning
* Visual learning enhancement
* Offline academic environments
* AI-assisted teaching support

---

## 🔮 Future Enhancements

* Multi-language support (Hindi and regional languages)
* Mobile applications (Android / iOS)
* Voice-based chatbot interaction
* Adaptive learning analytics
* Real-time lecture processing

---

## 👨‍💻 Authors

* Om Gupta – Department of CSE, Delhi Technical Campus


## 📜 License

This project is intended for academic and research purposes.
You may reuse or extend it with proper attribution.
