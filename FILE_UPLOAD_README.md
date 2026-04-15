# Vishakha_Notewise - File Upload Functionality

## Overview
This is a simplified clone of the note-taking app with enhanced AI features and robust file upload capabilities.

## File Upload Features
- **Drag & Drop**: Drag files directly onto the upload area
- **Click to Browse**: Click the upload area to open file selector
- **File Type Validation**: Supports PDF, TXT, DOC, DOCX files
- **Size Validation**: Maximum 10MB file size
- **Visual Feedback**: Drag-over effects and file selection display
- **AI Processing**: Automatic content extraction and analysis using OpenRouter API

## How to Test File Upload

### Method 1: Using the Main Application
1. Start the Flask server:
   ```bash
   cd /Users/rahul/Desktop/repos/Vishakha_Notewise
   python src/main.py
   ```

2. Open your browser and go to `http://localhost:5000`

3. Test file upload:
   - Select "File Upload" radio button
   - Either drag and drop a file or click to browse
   - Enter a title and click "Save Note"

### Method 2: Using the Simple Test Page
1. Start the Flask server (same as above)

2. Open the test page: `http://localhost:5000/test_simple.html`

3. This page includes:
   - Debug logging for troubleshooting
   - Both text and file upload testing
   - Real-time status updates
   - Detailed error reporting

### Method 3: Using the Dedicated Debug Test
1. Start the Flask server

2. Open: `http://localhost:5000/test_upload.html`

3. This provides:
   - Comprehensive debug information
   - Step-by-step logging
   - File validation testing
   - Direct upload testing

## Troubleshooting

### Common Issues
1. **File upload area not responding**:
   - Check browser console for JavaScript errors
   - Ensure Flask server is running
   - Verify file types are supported

2. **Files not being processed**:
   - Check file size (must be < 10MB)
   - Verify file extensions (.pdf, .txt, .doc, .docx)
   - Check server logs for backend errors

3. **Drag and drop not working**:
   - Try clicking the upload area instead
   - Check if files are being dropped on the correct element
   - Verify browser supports drag and drop

### Debug Information
- Open browser Developer Tools (F12)
- Check Console tab for JavaScript logs
- Network tab shows upload requests and responses
- Server console shows backend processing logs

## File Upload Implementation Details

### Frontend (JavaScript)
- `setupFileUpload()`: Initializes all event listeners
- `handleFileSelection()`: Validates and processes selected files
- `displaySelectedFile()`: Updates UI to show selected file
- Comprehensive drag and drop event handling
- Real-time file validation

### Backend (Python/Flask)
- `/api/upload` endpoint handles file uploads
- Werkzeug secure_filename for security
- Temporary file processing
- AI-powered content extraction
- Database storage with metadata

### AI Integration
- OpenRouter API for content analysis
- Automatic title generation
- Text extraction from documents
- Content summarization and analysis

## Supported File Types
- **PDF**: Portable Document Format
- **TXT**: Plain text files
- **DOC**: Microsoft Word (legacy)
- **DOCX**: Microsoft Word (modern)

## File Size Limits
- Maximum file size: 10MB
- Files larger than 10MB will be rejected with an error message

## AI Features
- **Title Generation**: AI suggests titles based on content
- **Content Analysis**: Extracts and analyzes document content
- **Smart Processing**: Handles different document formats intelligently
- **Error Recovery**: Graceful fallback when AI is unavailable

## Configuration
Check `config/config.py` for:
- OpenRouter API configuration
- File upload settings
- Database configuration
- Debug options

## Success Indicators
When file upload works correctly, you should see:
1. File selection feedback in the UI
2. Progress indicator during upload
3. Success message after processing
4. New note created in the notes list
5. AI analysis included (if enabled)

## Error Handling
The system provides detailed error messages for:
- Invalid file types
- Files too large
- Network issues
- Server processing errors
- AI service unavailability