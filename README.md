# 📘 Vishakha_Notewise - AI-Powered Note-Taking App

A lightweight, intelligent note-taking application built with Flask and enhanced with OpenRouter AI capabilities.

**Features:**
- 📝 Create and save notes with title and content
- 📄 Upload and process files (PDF, TXT, DOC, DOCX)
- 🤖 **AI-Powered Features with OpenRouter:**
  - Auto-generate titles from content
  - Smart summarization of notes and documents
  - Key points extraction
  - Full document analysis
- 🔍 View all saved notes with file indicators
- 🗑️ Delete notes
- 💾 Local SQLite database storage
- 🎨 Clean, responsive interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenRouter API key (free at [openrouter.ai](https://openrouter.ai)) - Optional but recommended for AI features

### Installation

1. **Navigate to the project:**
   ```bash
   cd Vishakha_Notewise
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AI features (optional):**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenRouter API key
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

5. **Open your browser:**
   Visit `http://localhost:5000`

## 🤖 OpenRouter AI-Powered Architecture

**Heavy Lifting Done by AI:** This app leverages OpenRouter's powerful AI models to handle complex tasks that would traditionally require multiple libraries and manual processing:

### What OpenRouter Handles:
- 📄 **Document Content Extraction** - AI reads and cleans messy file content
- 🧠 **Text Analysis** - Smart summarization, key point extraction, insights
- 🏷️ **Title Generation** - Contextual, descriptive titles from content
- 🔍 **Content Understanding** - Semantic analysis vs. simple text processing
- 🎯 **Smart Organization** - AI categorizes and structures information
- 🧹 **Content Cleanup** - Removes formatting artifacts, fixes garbled text

### What We Removed (Let AI Handle):
- ❌ Complex PDF parsing libraries and logic
- ❌ Manual text preprocessing and cleaning
- ❌ Custom summarization algorithms  
- ❌ Keyword extraction logic
- ❌ File metadata complex calculations
- ❌ Manual content categorization

### Simplified Architecture:
```
File Upload → Basic Read → OpenRouter AI → Intelligent Analysis → Save
Text Input → OpenRouter AI → Smart Processing → Enhanced Content → Save
```

## 📝 Usage

### Text Notes:
1. **Create Notes:** Enter content, optionally add a title (or let AI generate one)
2. **AI Enhancement:** Toggle "Auto-analyze" for AI summaries
3. **Manual AI:** Use "Analyze" or "Summarize" buttons for instant AI insights

### File Upload:
1. **Upload Files:** Switch to "File Upload" mode
2. **Drag & Drop:** Drop PDF, TXT, DOC, or DOCX files
3. **AI Processing:** Files are automatically analyzed with AI (if enabled)

### Viewing Notes:
- Recent notes appear on the right with file indicators
- Click any note to see full content, analysis, and file information
- File-based notes show original filename and processing details

## 📁 Project Structure

```
Vishakha_Notewise/
├── src/
│   └── main.py              # Main Flask application with AI routes
├── backend/
│   ├── db.py               # Enhanced database with file metadata
│   ├── ai_service.py       # OpenRouter AI integration
│   └── document_processor.py # File processing utilities
├── config/
│   └── config.py           # Configuration with AI settings
├── frontend/
│   ├── index.html          # Enhanced HTML with AI controls
│   ├── styles.css          # Updated styles with AI elements
│   └── app.js              # Frontend with AI features
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🛠️ Technical Details

- **Backend:** Flask (Python) - Minimal processing, AI does the work
- **AI Engine:** OpenRouter API - Handles all content analysis and processing
- **Frontend:** HTML, CSS, JavaScript with Bootstrap
- **Database:** SQLite with simplified schema (no complex metadata)
- **File Handling:** Basic reading + AI content extraction and analysis
- **Architecture:** AI-first design - OpenRouter handles complexity

### Minimal Dependencies Strategy:
- **Core only:** Flask, requests, python-dotenv
- **No heavy libraries:** Let OpenRouter handle PDF parsing, text analysis, etc.
- **Optional libraries:** Only install if you want enhanced local file reading
- **AI-powered:** Complex processing delegated to advanced AI models

## � Configuration

### Environment Variables (.env):
```env
# AI Features
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free

# App Settings
DEBUG=True
SECRET_KEY=your-secret-key
AUTO_SUMMARIZE=True
AUTO_GENERATE_TITLE=True
```

### Optional Document Processing Libraries:
```bash
# For enhanced PDF support
pip install PyPDF2

# For Word document support  
pip install python-docx
```

## 📊 API Endpoints

- `GET /api/status` - Check AI service availability
- `POST /api/notes` - Create note with optional AI enhancement
- `POST /api/upload` - Upload file with AI analysis
- `POST /api/analyze` - Analyze text with AI (summary, title, key points, full)
- `GET /api/notes` - Get all notes
- `DELETE /api/notes/<id>` - Delete note

## 📄 License

This is an educational project created for learning purposes. Enhanced with AI capabilities via OpenRouter.