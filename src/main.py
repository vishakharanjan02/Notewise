#!/usr/bin/env python3
"""
Vishakha_Notewise - Simple Note-Taking App
A simplified version of NoteWise with basic functionality and file upload support.
"""

import sys
import os
import tempfile
import json
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Add backend and config to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.config import config
from backend.db import db
from backend.document_processor import doc_processor
from backend.ai_service import ai_service
from backend.nlp_service import nlp_service
from backend.spam_detector import predict_all as spam_predict_all

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
            static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app.config['SECRET_KEY'] = config.get_secret_key()
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Enable CORS
CORS(app)

@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')

@app.route('/styles.css')
def serve_css():
    """Serve CSS file."""
    return send_from_directory(app.static_folder, 'styles.css')

@app.route('/app.js')
def serve_js():
    """Serve JavaScript file."""
    return send_from_directory(app.static_folder, 'app.js')

@app.route('/api/notes', methods=['GET'])
def get_notes():
    """Get all notes."""
    try:
        notes = db.get_all_notes()
        return jsonify(notes)
    except Exception as e:
        print(f"Error getting notes: {e}")
        return jsonify({'error': 'Failed to retrieve notes'}), 500

@app.route('/api/notes', methods=['POST'])
def create_note():
    """Create a new note."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({'error': 'Title and content are required'}), 400
        
        title = data['title'].strip()
        content = data['content'].strip()
        summary = data.get('summary', '')
        source_type = data.get('source_type', 'text')
        auto_analyze = data.get('auto_analyze', False)
        
        if not title or not content:
            return jsonify({'error': 'Title and content cannot be empty'}), 400
        
        # Auto-generate title if requested and AI is available
        if title == "AUTO_GENERATE" and ai_service.is_available():
            title_result = ai_service.analyze_content(content, 'title')
            if title_result['success']:
                title = title_result['content']
            else:
                title = "Untitled Note"
        
        # Auto-generate key points if requested and AI is available
        if auto_analyze and ai_service.is_available():
            analysis_result = ai_service.analyze_content(content, 'key_points')
            if analysis_result['success']:
                if not summary:
                    summary = analysis_result.get('content', '')
        
        # LOCAL INSIGHTS: Always get basic structural insights locally
        insights_json = ""
        if nlp_service.is_available():
            insights = nlp_service.get_text_insights(content)
            insights_json = json.dumps(insights)
        
        note_id = db.save_note(title, content, ai_analysis=summary, source_type=source_type, tags="", entities="", insights=insights_json)
        
        return jsonify({
            'success': True,
            'message': 'Note saved successfully',
            'note_id': note_id,
            'ai_generated_title': title if data.get('title', '').strip() == "AUTO_GENERATE" else None,
            'ai_generated_key_points': summary if auto_analyze else None,
            'local_insights': json.loads(insights_json) if insights_json else None
        })
        
    except Exception as e:
        print(f"Error creating note: {e}")
        return jsonify({'error': 'Failed to save note'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """Analyze text using AI."""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text'].strip()
        analysis_type = data.get('type', 'key_points')  # title, key_points, full
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        if not ai_service.is_available():
            return jsonify({'error': 'AI service not available. Please configure OpenRouter API key.'}), 503
        
        # Use simplified AI analysis - let OpenRouter handle all the complexity
        result = ai_service.analyze_content(text, analysis_type)
        
        # Format response based on analysis type for compatibility
        if analysis_type == 'title':
            return jsonify({
                'success': result['success'],
                'title': result.get('content', ''),
                'content': result.get('content', ''),
                'model': result.get('model', ''),
                'tokens_used': result.get('tokens_used', 0)
            })
        elif analysis_type == 'key_points':
            return jsonify({
                'success': result['success'],
                'key_points': result.get('content', ''),
                'content': result.get('content', ''),
                'model': result.get('model', ''),
                'tokens_used': result.get('tokens_used', 0)
            })
        elif analysis_type == 'full':
            return jsonify({
                'success': result['success'],
                'analysis': result.get('content', ''),
                'content': result.get('content', ''),
                'model': result.get('model', ''),
                'tokens_used': result.get('tokens_used', 0)
            })
        else:
            return jsonify(result)
            
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return jsonify({'error': 'Failed to analyze text'}), 500

@app.route('/api/spam-check', methods=['POST'])
def spam_check():
    """Run local machine-learning spam detection on text input."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400

        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400

        prediction = spam_predict_all(text)
        return jsonify({
            'success': True,
            'overall_verdict': prediction['overall_verdict'],
            'results': prediction['results'],
            'text_preview': text[:100]
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error running spam detection: {e}")
        return jsonify({'error': 'Failed to run spam detection'}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and create note."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        title = request.form.get('title', '').strip()
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Check file type
        allowed_extensions = {'.pdf', '.txt', '.doc', '.docx'}
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'Unsupported file type'}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Basic file reading - let AI do the heavy lifting
            result = doc_processor.process_file(temp_path)
            
            if not result.get('success', False):
                return jsonify({'error': result.get('error', 'Failed to process file')}), 400
            
            # Get basic file content and metadata
            raw_content = result['content']
            metadata = result['metadata']
            
            # Use AI for all content processing and analysis
            final_title = title
            ai_analysis = ''
            processed_content = raw_content
            
            if ai_service.is_available():
                # Let AI extract, clean, and analyze the content
                ai_result = ai_service.extract_and_analyze_file_content(raw_content, filename)
                if ai_result['success']:
                    ai_analysis = ai_result.get('analysis', '')
                    # Use AI-generated title if the provided title is generic
                    if title.lower() in ['untitled', 'document', 'file'] or len(title) < 5:
                        final_title = ai_result.get('title', title)
            
            # LOCAL INSIGHTS: Always get basic structural insights locally
            insights_json = ""
            if nlp_service.is_available():
                insights = nlp_service.get_text_insights(processed_content)
                insights_json = json.dumps(insights)
                
            # Save note to database - simplified schema
            note_id = db.save_note(
                title=final_title,
                content=processed_content,
                ai_analysis=ai_analysis,
                source_type='file',
                filename=filename,
                tags="",
                entities="",
                insights=insights_json
            )
            
            return jsonify({
                'success': True,
                'message': 'File uploaded and processed successfully',
                'note_id': note_id,
                'filename': filename,
                'file_type': metadata.get('file_type', 'unknown'),
                'content_length': len(processed_content),
                'ai_enhanced': ai_service.is_available(),
                'ai_generated_title': final_title if final_title != title else None,
                'ai_analysis_included': bool(ai_analysis),
                'local_insights': json.loads(insights_json) if insights_json else None
            })
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except:
                pass
                
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500

@app.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """Get a specific note by ID."""
    try:
        note = db.get_note_by_id(note_id)
        if note:
            return jsonify(note)
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error getting note: {e}")
        return jsonify({'error': 'Failed to retrieve note'}), 500

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note by ID."""
    try:
        if db.delete_note(note_id):
            return jsonify({'success': True, 'message': 'Note deleted successfully'})
        else:
            return jsonify({'error': 'Note not found'}), 404
    except Exception as e:
        print(f"Error deleting note: {e}")
        return jsonify({'error': 'Failed to delete note'}), 500

@app.route('/api/notes/clear', methods=['DELETE'])
def clear_all_notes():
    """Delete all notes."""
    try:
        deleted_count = db.clear_all_notes()
        return jsonify({
            'success': True, 
            'message': f'Successfully deleted {deleted_count} notes',
            'deleted_count': deleted_count
        })
    except Exception as e:
        print(f"Error clearing notes: {e}")
        return jsonify({'error': 'Failed to clear notes'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'app': 'Vishakha_Notewise'})

@app.route('/api/nlp/entities', methods=['POST'])
def extract_entities():
    """Extract entities using AI or local spaCy model."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text'].strip()
        entities = {}
        method = ""
        
        if ai_service.is_available():
            entities = ai_service.extract_entities(text)
            if entities:
                method = "OpenRouter AI"
            else:
                # Fallback to local
                if nlp_service.is_available():
                    entities = nlp_service.extract_entities(text)
                    method = "Local spaCy (AI fallback)"
        elif nlp_service.is_available():
            entities = nlp_service.extract_entities(text)
            method = "Local spaCy"
        else:
            return jsonify({'error': 'No NER service available (AI or Local)'}), 503
            
        formatted = nlp_service.format_entities_for_db(entities)
        
        return jsonify({
            'success': True,
            'entities': entities,
            'formatted': formatted,
            'method': method
        })
    except Exception as e:
        print(f"Error in entity extraction: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """Get API and AI service status."""
    ai_available = ai_service.is_available()
    nlp_available = nlp_service.is_available()
    
    status = {
        'app': 'Vishakha_Notewise',
        'status': 'healthy',
        'ai_enabled': ai_available,
        'local_nlp_enabled': nlp_available,
        'features': {
            'text_notes': True,
            'file_upload': True,
            'ai_summarization': ai_available,
            'local_entity_extraction': nlp_available
        }
    }
    
    if ai_available:
        status['ai_model'] = config.openrouter_model
    else:
        status['ai_message'] = 'Configure OPENROUTER_API_KEY to enable AI features'
    
    return jsonify(status)

if __name__ == '__main__':
    print("Starting Vishakha_Notewise...")
    print("Access the app at: http://localhost:5001")
    app.run(debug=config.debug, host='0.0.0.0', port=5001)
