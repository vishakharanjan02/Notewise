# Vishakha_Notewise

Vishakha_Notewise is a Flask + vanilla JavaScript note-taking app with:

- text note creation
- file upload support for `PDF`, `TXT`, `DOC`, and `DOCX`
- OpenRouter-powered title generation and key-point extraction
- local spaCy-based NLP insights
- local machine-learning spam detection using scikit-learn
- note search, dark mode, and PDF export

The app stores notes locally in SQLite and keeps most of the UI in a single frontend built with Bootstrap 5.

## Features

- Create notes from typed text
- Upload documents and save extracted text as notes
- Auto-generate note titles with OpenRouter
- Generate key points / note insights with OpenRouter
- View local NLP insights such as:
  - keywords
  - key phrases
  - reading statistics
- Run local spam detection with 4 ML models:
  - Naive Bayes
  - Logistic Regression
  - Support Vector Machine
  - Random Forest
- Search notes in real time by title or content
- Toggle dark mode with saved preference
- Export note details as PDF
- Delete single notes or clear all notes

## Project Structure

```text
Vishakha_Notewise/
├── backend/
│   ├── ai_service.py
│   ├── db.py
│   ├── document_processor.py
│   ├── nlp_service.py
│   └── spam_detector.py
├── config/
│   └── config.py
├── frontend/
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── src/
│   └── main.py
├── tests/
│   └── test_ai_service.py
├── .env.example
├── README.md
├── requirements.txt
└── notewise_simple.db
```

## How It Works

### Text Notes

1. The user enters note text in the frontend.
2. Flask receives the note through `POST /api/notes`.
3. If AI is enabled:
   - a title can be generated
   - key points can be generated
4. Local spaCy NLP extracts keywords, phrases, and statistics.
5. The note is stored in SQLite.

### File Upload Notes

1. The user uploads a file through the frontend.
2. Flask saves it temporarily and reads it with `document_processor.py`.
3. The extracted plain text is used as the note content.
4. If AI is enabled, OpenRouter can generate title/key-point analysis.
5. The note is saved in SQLite and can later be checked for spam on demand.

### Spam Detection

Spam detection is fully local and does not use OpenRouter.

1. `backend/spam_detector.py` downloads the SMS Spam Collection dataset once and saves it as `spam.tsv` in the project root.
2. It trains four scikit-learn models using one shared `TfidfVectorizer`.
3. The models are loaded once when Flask starts.
4. The frontend calls `POST /api/spam-check` when the user clicks `Spam Check`.
5. Results are shown in a Bootstrap modal with model-by-model verdicts.

## Tech Stack

### Backend

- Python
- Flask
- Flask-CORS
- SQLite
- requests
- python-dotenv

### NLP / ML

- OpenRouter API
- spaCy
- scikit-learn
- pandas
- numpy

### Frontend

- HTML
- CSS
- Vanilla JavaScript
- Bootstrap 5
- Font Awesome
- jsPDF

## Requirements

- Python 3.10+ recommended
- `pip`
- Optional but recommended: OpenRouter API key for AI features

## Environment Variables

Create a `.env` file in the project root from `.env.example`.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free
DEBUG=True
SECRET_KEY=your-secret-key-here
AUTO_SUMMARIZE=True
AUTO_GENERATE_TITLE=True
```

Notes:

- If `OPENROUTER_API_KEY` is missing or invalid, local features still work.
- Spam detection does not depend on OpenRouter.

## Installation

From Warp or any terminal:

```bash
cd "/Users/visha/Documents/Vishakha_Notewise 2"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
```

Then edit `.env` and add your real OpenRouter API key if you want AI features.

## How To Run

Start the app with:

```bash
cd "/Users/visha/Documents/Vishakha_Notewise 2"
source .venv/bin/activate
python src/main.py
```

Open:

```text
http://localhost:5001
```

Notes:

- The app runs on port `5001`.
- On first startup with spam detection enabled, the app may take longer because `spam.tsv` is downloaded once and the ML models are trained.
- After the first run, `spam.tsv` is reused locally.

## Main Files

- [src/main.py](src/main.py)  
  Main Flask app, routes, and orchestration

- [backend/ai_service.py](backend/ai_service.py)  
  OpenRouter integration for titles, key points, and file analysis

- [backend/nlp_service.py](backend/nlp_service.py)  
  Local spaCy NLP for keywords, phrases, and entity extraction

- [backend/spam_detector.py](backend/spam_detector.py)  
  Local spam detection pipeline using TF-IDF + 4 ML models

- [backend/document_processor.py](backend/document_processor.py)  
  Reads TXT, PDF, DOC, and DOCX files

- [backend/db.py](backend/db.py)  
  SQLite schema and note CRUD

- [frontend/index.html](frontend/index.html)  
  Main UI layout

- [frontend/app.js](frontend/app.js)  
  Client-side app logic, modals, API calls, dark mode, spam modal, PDF export

- [frontend/styles.css](frontend/styles.css)  
  App styling including dark mode

## API Endpoints

- `GET /`
  Serve the app UI

- `GET /api/status`
  App status and AI availability

- `GET /api/notes`
  Fetch all notes

- `POST /api/notes`
  Create a text note

- `POST /api/upload`
  Upload a file and create a note from extracted text

- `POST /api/analyze`
  Run AI analysis on text

- `POST /api/spam-check`
  Run local spam detection

- `POST /api/nlp/entities`
  Extract entities using AI or local spaCy fallback

- `GET /api/notes/<id>`
  Get one note

- `DELETE /api/notes/<id>`
  Delete one note

- `DELETE /api/notes/clear`
  Delete all notes

- `GET /health`
  Health check

## Testing

Current unit test:

```bash
source .venv/bin/activate
python -m unittest tests/test_ai_service.py
```

## Security Notes

- Do not commit `.env` or `.env.save`
- Keep API keys only in local environment files
- `spam.tsv` is generated locally and should not be committed

## License

Educational / personal project.
