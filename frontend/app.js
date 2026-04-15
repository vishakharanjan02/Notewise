// Vishakha_Notewise Enhanced Frontend with AI Features
class SimpleNotewise {
    constructor() {
        this.baseURL = window.location.origin;
        this.allNotes = [];
        this.currentNoteId = null;
        this.selectedFile = null;
        this.inputType = 'text';
        this.aiAvailable = false;
        this.searchQuery = '';
        this.speechRecognition = null;
        this.isListening = false;
        this.supportsSpeechRecognition = false;
        this.keepSpeechStatus = false;
        
        this.init();
    }
    
    init() {
        this.applySavedTheme();

        // Ensure DOM is ready before setting up event listeners
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.setupEventListeners();
                this.loadAllNotes();
                this.checkAIStatus();
            });
        } else {
            this.setupEventListeners();
            this.loadAllNotes();
            this.checkAIStatus();
        }
    }
    
    setupEventListeners() {
        // Form submission
        document.getElementById('noteForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveNote();
        });
        
        // Input type selector
        document.querySelectorAll('input[name="inputType"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.switchInputType(radio.value);
            });
        });
        
        // AI feature buttons
        document.getElementById('generateTitleBtn').addEventListener('click', () => {
            this.generateTitle();
        });
        
        document.getElementById('analyzeBtn').addEventListener('click', () => {
            this.analyzeText();
        });

        document.getElementById('speechToTextBtn').addEventListener('click', () => {
            this.toggleSpeechRecognition();
        });

        document.getElementById('noteSearch').addEventListener('input', (event) => {
            this.searchQuery = event.target.value.trim().toLowerCase();
            this.displayNotes();
        });

        document.getElementById('darkModeToggle').addEventListener('click', () => {
            this.toggleDarkMode();
        });
        
        // File upload setup
        this.setupFileUpload();
        
        // Delete note button
        document.getElementById('deleteNoteBtn').addEventListener('click', () => {
            this.deleteNote();
        });

        document.getElementById('exportPdfBtn').addEventListener('click', () => {
            this.exportCurrentNoteAsPdf();
        });

        this.setupSpeechRecognition();
        this.updateDarkModeButton();
    }

    applySavedTheme() {
        const savedTheme = localStorage.getItem('notewise-theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    }

    toggleDarkMode() {
        document.body.classList.toggle('dark-mode');
        const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('notewise-theme', theme);
        this.updateDarkModeButton();
    }

    updateDarkModeButton() {
        const darkModeIcon = document.getElementById('darkModeIcon');
        const darkModeToggle = document.getElementById('darkModeToggle');
        const isDarkMode = document.body.classList.contains('dark-mode');

        if (darkModeIcon) {
            darkModeIcon.textContent = isDarkMode ? '☀️' : '🌙';
        }

        if (darkModeToggle) {
            darkModeToggle.setAttribute('title', isDarkMode ? 'Switch to light mode' : 'Switch to dark mode');
        }
    }

    setupSpeechRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const speechButton = document.getElementById('speechToTextBtn');

        if (!SpeechRecognition) {
            speechButton.disabled = true;
            speechButton.title = 'Speech recognition is not supported in this browser';
            this.updateSpeechUI('Speech-to-text is not supported in this browser.', true);
            return;
        }

        this.supportsSpeechRecognition = true;
        this.speechRecognition = new SpeechRecognition();
        this.speechRecognition.continuous = false;
        this.speechRecognition.interimResults = false;
        this.speechRecognition.lang = 'en-US';

        this.speechRecognition.onstart = () => {
            this.isListening = true;
            this.updateSpeechUI('Listening...');
        };

        this.speechRecognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(result => result[0] ? result[0].transcript : '')
                .join(' ')
                .trim();

            if (!transcript) {
                return;
            }

            const noteContent = document.getElementById('noteContent');
            const existingText = noteContent.value.trim();
            noteContent.value = existingText ? `${existingText} ${transcript}` : transcript;
            noteContent.dispatchEvent(new Event('input', { bubbles: true }));
        };

        this.speechRecognition.onerror = (event) => {
            this.isListening = false;

            if (event.error === 'no-speech') {
                this.updateSpeechUI('No speech detected. Try again.', true);
                return;
            }

            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
                this.updateSpeechUI('Microphone access was blocked.', true);
                this.showAlert('Please allow microphone access to use speech-to-text.', 'warning');
                return;
            }

            this.updateSpeechUI('Speech recognition failed.', true);
            this.showAlert(`Speech-to-text error: ${event.error}`, 'danger');
        };

        this.speechRecognition.onend = () => {
            this.isListening = false;
            if (this.supportsSpeechRecognition && !this.keepSpeechStatus) {
                this.updateSpeechUI('');
            }
        };
    }

    toggleSpeechRecognition() {
        if (this.inputType === 'file') {
            this.showAlert('Speech-to-text is available only for text notes.', 'info');
            return;
        }

        if (!this.supportsSpeechRecognition || !this.speechRecognition) {
            this.showAlert('Speech-to-text is not supported in this browser.', 'warning');
            return;
        }

        if (this.isListening) {
            this.speechRecognition.stop();
            return;
        }

        try {
            this.speechRecognition.start();
        } catch (error) {
            console.error('Error starting speech recognition:', error);
            this.updateSpeechUI('Could not start listening.', true);
            this.showAlert('Could not start speech-to-text. Please try again.', 'danger');
        }
    }

    updateSpeechUI(message, persist = false) {
        const speechStatus = document.getElementById('speechStatus');
        const speechButton = document.getElementById('speechToTextBtn');
        this.keepSpeechStatus = persist;

        if (speechStatus) {
            speechStatus.textContent = message;
        }

        if (speechButton) {
            speechButton.classList.toggle('listening', this.isListening);
            speechButton.innerHTML = this.isListening
                ? '<i class="fas fa-stop-circle"></i><span class="ms-1">Stop</span>'
                : '<i class="fas fa-microphone"></i><span class="ms-1">Speak</span>';
        }
    }
    
    async checkAIStatus() {
        try {
            const response = await fetch('/api/status');
            if (response.ok) {
                const status = await response.json();
                this.aiAvailable = status.ai_enabled;
                this.updateAIInterface();
            }
        } catch (error) {
            console.error('Error checking AI status:', error);
            this.aiAvailable = false;
            this.updateAIInterface();
        }
    }
    
    updateAIInterface() {
        const aiPanel = document.getElementById('aiPanel');
        const generateTitleBtn = document.getElementById('generateTitleBtn');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const titleInput = document.getElementById('noteTitle');
        
        if (this.aiAvailable) {
            aiPanel.style.display = 'block';
            generateTitleBtn.disabled = false;
            analyzeBtn.style.display = 'inline-block';
            titleInput.placeholder = 'Enter note title or leave empty for AI generation';
            titleInput.required = false;
        } else {
            aiPanel.style.display = 'none';
            generateTitleBtn.disabled = true;
            analyzeBtn.style.display = 'none';
            titleInput.placeholder = 'Enter note title';
            titleInput.required = true;
        }
    }
    
    async generateTitle() {
        const content = document.getElementById('noteContent').value.trim();
        const titleInput = document.getElementById('noteTitle');
        
        // Check if in file mode
        if (this.inputType === 'file') {
            this.showAlert('Title generation from uploaded files happens automatically during upload', 'info');
            return;
        }
        
        if (!content) {
            this.showAlert('Please enter some content first', 'warning');
            return;
        }
        
        if (!this.aiAvailable) {
            this.showAlert('AI features not available', 'warning');
            return;
        }
        
        const generateBtn = document.getElementById('generateTitleBtn');
        const originalHTML = generateBtn.innerHTML;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        generateBtn.disabled = true;
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: content,
                    type: 'title'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    titleInput.value = result.title;
                    this.showAlert('Title generated successfully!', 'success');
                } else {
                    throw new Error(result.error || 'Failed to generate title');
                }
            } else {
                throw new Error('Failed to generate title');
            }
        } catch (error) {
            console.error('Error generating title:', error);
            this.showAlert(`Failed to generate title: ${error.message}`, 'danger');
        } finally {
            generateBtn.innerHTML = originalHTML;
            generateBtn.disabled = false;
        }
    }
    
    async analyzeText() {
        // Check if in file mode
        if (this.inputType === 'file') {
            this.showAlert('AI analysis for uploaded files happens automatically during upload', 'info');
            return;
        }
        
        const content = document.getElementById('noteContent').value.trim();
        
        if (!content) {
            this.showAlert('Please enter some content first', 'warning');
            return;
        }
        
        if (!this.aiAvailable) {
            this.showAlert('AI features not available', 'warning');
            return;
        }
        
        const analyzeBtn = document.getElementById('analyzeBtn');
        const originalHTML = analyzeBtn.innerHTML;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        analyzeBtn.disabled = true;
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: content,
                    type: 'key_points'
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.showAnalysisModal(result);
                } else {
                    throw new Error(result.error || 'Failed to analyze text');
                }
            } else {
                throw new Error('Failed to analyze text');
            }
        } catch (error) {
            console.error('Error analyzing text:', error);
            this.showAlert(`Failed to analyze text: ${error.message}`, 'danger');
        } finally {
            analyzeBtn.innerHTML = originalHTML;
            analyzeBtn.disabled = false;
        }
    }
    
    showAnalysisModal(analysis) {
        const modalHTML = `
            <div class="modal fade" id="analysisModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">
                                <i class="fas fa-list-ul me-2"></i>Key Points
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${analysis.analysis ? `
                                <div class="mb-3">
                                    <div class="border rounded p-3" style="background-color: #f0f8ff;">
                                        ${this.escapeHtml(analysis.analysis).replace(/\n/g, '<br>')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('analysisModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
        modal.show();
    }
    
    setupFileUpload() {
        console.log('Setting up file upload...');
        
        // Wait a bit for DOM to be fully ready
        setTimeout(() => {
            const fileUploadArea = document.getElementById('fileUploadArea');
            const fileInput = document.getElementById('fileUpload');
            
            console.log('fileUploadArea:', fileUploadArea);
            console.log('fileInput:', fileInput);
            
            if (!fileUploadArea || !fileInput) {
                console.error('File upload elements not found! Retrying in 500ms...');
                // Retry once more
                setTimeout(() => this.setupFileUpload(), 500);
                return;
            }
            
            console.log('File upload elements found successfully');
            
            // Remove any existing listeners to avoid duplicates
            const newFileUploadArea = fileUploadArea.cloneNode(true);
            fileUploadArea.parentNode.replaceChild(newFileUploadArea, fileUploadArea);
            
            // Re-get the element after cloning
            const freshFileUploadArea = document.getElementById('fileUploadArea');
            const freshFileInput = document.getElementById('fileUpload');
            
            // Click to browse files
            freshFileUploadArea.addEventListener('click', (e) => {
                console.log('File upload area clicked');
                e.preventDefault();
                e.stopPropagation();
                if (!this.selectedFile) {
                    console.log('Triggering file input click');
                    freshFileInput.click();
                } else {
                    console.log('File already selected, not triggering click');
                }
            });
            
            // File input change handler
            freshFileInput.addEventListener('change', (e) => {
                console.log('File input changed, files:', e.target.files.length);
                if (e.target.files.length > 0) {
                    console.log('Selected file:', e.target.files[0].name);
                    this.handleFileSelection(e.target.files[0]);
                }
            });
            
            // Drag and drop handlers
            freshFileUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drag over detected');
                freshFileUploadArea.classList.add('dragover');
            });
            
            freshFileUploadArea.addEventListener('dragenter', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drag enter detected');
                freshFileUploadArea.classList.add('dragover');
            });
            
            freshFileUploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drag leave detected');
                // Only remove dragover if we're leaving the dropzone itself
                if (!freshFileUploadArea.contains(e.relatedTarget)) {
                    freshFileUploadArea.classList.remove('dragover');
                }
            });
            
            freshFileUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Drop detected');
                freshFileUploadArea.classList.remove('dragover');
                
                const files = e.dataTransfer.files;
                console.log('Dropped files count:', files.length);
                if (files.length > 0) {
                    console.log('Processing dropped file:', files[0].name);
                    this.handleFileSelection(files[0]);
                }
            });
            
            // File removal button - setup with event delegation
            document.addEventListener('click', (e) => {
                if (e.target && e.target.id === 'removeFileBtn') {
                    console.log('Remove file button clicked');
                    e.preventDefault();
                    e.stopPropagation();
                    this.clearFile();
                }
            });
            
            console.log('File upload setup completed successfully');
        }, 100);
    }
    
    switchInputType(type) {
        this.inputType = type;
        const textSection = document.getElementById('textInputSection');
        const fileSection = document.getElementById('fileInputSection');
        
        if (type === 'text') {
            textSection.style.display = 'block';
            fileSection.style.display = 'none';
            document.getElementById('noteContent').required = true;
        } else {
            textSection.style.display = 'none';
            fileSection.style.display = 'block';
            document.getElementById('noteContent').required = false;
        }
        
        this.clearFile();
    }
    
    handleFileSelection(file) {
        // Check file type
        const allowedTypes = [
            'text/plain',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            this.showAlert('Unsupported file type. Please upload PDF, TXT, DOC, or DOCX files.', 'warning');
            return;
        }
        
        // Check file size (10MB limit)
        if (file.size > 10 * 1024 * 1024) {
            this.showAlert('File too large. Please upload files smaller than 10MB.', 'warning');
            return;
        }
        
        this.selectedFile = file;
        this.displaySelectedFile();
    }
    
    displaySelectedFile() {
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const fileUploadPrompt = document.getElementById('fileUploadPrompt');
        const fileSelected = document.getElementById('fileSelected');
        
        fileName.textContent = this.selectedFile.name;
        fileSize.textContent = this.formatFileSize(this.selectedFile.size);
        
        fileUploadPrompt.style.display = 'none';
        fileSelected.style.display = 'block';
    }
    
    clearFile() {
        this.selectedFile = null;
        document.getElementById('fileUpload').value = '';
        document.getElementById('fileUploadPrompt').style.display = 'block';
        document.getElementById('fileSelected').style.display = 'none';
    }
    
    async saveNote() {
        let title = document.getElementById('noteTitle').value.trim();
        const autoAnalyze = document.getElementById('autoAnalyze').checked;
        
        console.log('saveNote called, inputType:', this.inputType);
        console.log('selectedFile:', this.selectedFile);
        
        // Handle AI title generation
        if (!title && this.aiAvailable) {
            title = "AUTO_GENERATE";
        }
        
        if (this.inputType === 'text') {
            const content = document.getElementById('noteContent').value.trim();
            
            if (!content) {
                this.showAlert('Please enter some content', 'warning');
                return;
            }
            
            if (!title && !this.aiAvailable) {
                this.showAlert('Please provide a title', 'warning');
                return;
            }
            
            try {
                const response = await fetch('/api/notes', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title || "Untitled Note",
                        content: content,
                        source_type: 'text',
                        auto_analyze: autoAnalyze && this.aiAvailable
                    })
                });
                
                if (response.ok) {
                    const result = await response.json();
                    let message = 'Note saved successfully!';
                    
                    if (result.ai_generated_title) {
                        message += ` AI generated title: "${result.ai_generated_title}"`;
                    }
                    if (result.ai_generated_key_points) {
                        message += ' AI key points included.';
                    }
                    
                    this.showAlert(message, 'success');
                    this.clearForm();
                    this.loadAllNotes();
                } else {
                    throw new Error('Failed to save note');
                }
            } catch (error) {
                console.error('Error saving note:', error);
                this.showAlert('Failed to save note. Please try again.', 'danger');
            }
        } else {
            // File upload logic remains the same
            if (!this.selectedFile) {
                this.showAlert('Please select a file to upload', 'warning');
                return;
            }
            
            if (!title && !this.aiAvailable) {
                this.showAlert('Please provide a title for the note', 'warning');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            formData.append('title', title || 'Untitled Document');
            
            try {
                this.showAlert('Processing file...', 'info');
                
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    let message = 'File uploaded and note saved successfully!';
                    
                    if (result.ai_enhanced) {
                        message += ' AI key points included.';
                    }
                    
                    this.showAlert(message, 'success');
                    this.clearForm();
                    this.loadAllNotes();
                } else {
                    let errorMessage = `Failed to upload file (${response.status})`;
                    try {
                        const error = await response.json();
                        errorMessage = error.error || errorMessage;
                    } catch {
                        try {
                            const errorText = await response.text();
                            if (errorText) {
                                errorMessage = errorText;
                            }
                        } catch {
                            // Keep the status-based fallback.
                        }
                    }
                    throw new Error(errorMessage);
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                const isNetworkError = error instanceof TypeError && /fetch|network/i.test(error.message);
                const message = isNetworkError
                    ? 'Failed to upload file: could not reach the backend server. Check that Flask is still running and reload the page.'
                    : `Failed to upload file: ${error.message}`;
                this.showAlert(message, 'danger');
            }
        }
    }
    
    async loadAllNotes() {
        try {
            const response = await fetch('/api/notes');
            if (response.ok) {
                this.allNotes = await response.json();
                this.displayNotes();
            } else {
                throw new Error('Failed to load notes');
            }
        } catch (error) {
            console.error('Error loading notes:', error);
            this.showAlert('Failed to load notes.', 'danger');
        }
    }
    
    displayNotes() {
        const notesList = document.getElementById('notesList');
        const filteredNotes = this.getFilteredNotes();
        
        if (this.allNotes.length === 0) {
            notesList.innerHTML = '<p class="text-muted">No notes yet. Create your first note!</p>';
            return;
        }

        if (filteredNotes.length === 0) {
            notesList.innerHTML = '<p class="text-muted">No matching notes found.</p>';
            return;
        }
        
        notesList.innerHTML = filteredNotes.map(note => {
            const sourceIcon = note.source_type === 'file' 
                ? '<i class="fas fa-file-alt me-1"></i>' 
                : '<i class="fas fa-sticky-note me-1"></i>';
            
            const sourceInfo = note.source_type === 'file' && note.filename
                ? `<small class="text-muted"><i class="fas fa-paperclip me-1"></i>${note.filename}</small><br>`
                : '';
            
            return `
                <div class="note-item" onclick="noteWise.showNoteModal(${note.id})">
                    <div class="note-title">${sourceIcon}${this.escapeHtml(note.title)}</div>
                    ${sourceInfo}
                    <div class="note-excerpt">${this.truncateText(this.escapeHtml(note.content), 100)}</div>
                    <div class="note-date">
                        <i class="fas fa-calendar-alt me-1"></i>
                        ${this.formatDate(note.created_at)}
                    </div>
                </div>
            `;
        }).join('');
    }

    getFilteredNotes() {
        if (!this.searchQuery) {
            return this.allNotes;
        }

        return this.allNotes.filter(note => {
            const title = (note.title || '').toLowerCase();
            const content = (note.content || '').toLowerCase();
            return title.includes(this.searchQuery) || content.includes(this.searchQuery);
        });
    }

    displayInsights(insightsJson) {
        if (!insightsJson) return '';
        try {
            const insights = typeof insightsJson === 'string' ? JSON.parse(insightsJson) : insightsJson;
            if (!insights) return '';
            
            let html = '<div class="small">';
            
            // Display Statistics
            if (insights.statistics) {
                const stats = insights.statistics;
                let badgeClass = 'bg-success';
                if (stats.complexity === 'Complex') badgeClass = 'bg-danger';
                else if (stats.complexity === 'Intermediate') badgeClass = 'bg-warning text-dark';
                
                html += `
                    <div class="mb-3">
                        <i class="fas fa-chart-bar me-1 text-muted"></i>
                        <strong>Stats:</strong> ${stats.word_count} words, ${stats.sentence_count} sentences
                        <span class="badge ${badgeClass} ms-2">${stats.complexity}</span>
                        <span class="ms-2 text-muted">(~${stats.reading_time_seconds}s read)</span>
                    </div>
                `;
            }

            // Display Key Phrases
            if (insights.phrases && insights.phrases.length > 0) {
                html += `
                    <div class="mb-3">
                        <i class="fas fa-quote-left me-1 text-muted"></i>
                        <strong>Key Phrases:</strong><br>
                        ${insights.phrases.map(ph => `<span class="badge bg-light text-dark border me-1 mt-1">${this.escapeHtml(ph)}</span>`).join('')}
                    </div>
                `;
            }
            
            // Display Keywords
            if (insights.keywords && insights.keywords.length > 0) {
                html += `
                    <div>
                        <i class="fas fa-key me-1 text-muted"></i>
                        <strong>Top Nouns:</strong><br>
                        ${insights.keywords.map(kw => `<span class="badge rounded-pill border text-muted me-1 mt-1" style="background-color: #fafafa; font-weight: normal;">${this.escapeHtml(kw)}</span>`).join('')}
                    </div>
                `;
            }
            
            html += '</div>';
            return html;
        } catch (e) {
            console.error('Error parsing insights:', e);
            return '';
        }
    }
    
    async showNoteModal(noteId) {
        const note = this.allNotes.find(n => n.id === noteId);
        if (!note) return;
        
        this.currentNoteId = noteId;
        
        document.getElementById('noteModalTitle').textContent = note.title;
        
        const fileInfo = note.source_type === 'file' && note.filename
            ? `
                <div class="mb-3">
                    <h6><i class="fas fa-file-alt me-1"></i>File Information:</h6>
                    <div class="border rounded p-3" style="background-color: #f0f8ff;">
                        <strong>Filename:</strong> ${this.escapeHtml(note.filename)}<br>
                        <strong>Source:</strong> File Upload
                    </div>
                </div>
            `
            : '';
        
        const insightsHTML = note.insights ? `
            <div class="mb-3">
                <h6><i class="fas fa-microscope me-1"></i>Local Insights:</h6>
                <div class="border rounded p-2" style="background-color: #f8f9fa;">
                    ${this.displayInsights(note.insights)}
                </div>
            </div>
        ` : '';
        
        document.getElementById('noteModalContent').innerHTML = `
            ${fileInfo}
            ${insightsHTML}
            <div class="mb-3">
                <h6>Content:</h6>
                <div class="border rounded p-3" style="background-color: #f8f9fa; max-height: 400px; overflow-y: auto;">
                    ${this.escapeHtml(note.content).replace(/\n/g, '<br>')}
                </div>
            </div>
            ${note.ai_analysis ? `
                <div class="mb-3">
                    <h6><i class="fas fa-list-ul me-1"></i>Key Points:</h6>
                    <div class="border rounded p-3" style="background-color: #e8f4f8; max-height: 400px; overflow-y: auto;">
                        ${this.escapeHtml(note.ai_analysis).replace(/\n/g, '<br>')}
                    </div>
                </div>
            ` : ''}
            <div class="text-muted">
                <small>Created: ${this.formatDate(note.created_at)}</small>
            </div>
        `;
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('noteModal'));
        modal.show();
    }
    
    async deleteNote() {
        if (!this.currentNoteId) return;
        
        if (!confirm('Are you sure you want to delete this note?')) {
            return;
        }
        
        try {
            const response = await fetch(`/api/notes/${this.currentNoteId}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                this.showAlert('Note deleted successfully!', 'success');
                this.loadAllNotes();
                
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('noteModal'));
                if (modal) modal.hide();
                
                this.currentNoteId = null;
            } else {
                throw new Error('Failed to delete note');
            }
        } catch (error) {
            console.error('Error deleting note:', error);
            this.showAlert('Failed to delete note. Please try again.', 'danger');
        }
    }

    exportCurrentNoteAsPdf() {
        if (!this.currentNoteId) {
            this.showAlert('Open a note before exporting it as PDF.', 'warning');
            return;
        }

        if (!window.jspdf || !window.jspdf.jsPDF) {
            this.showAlert('PDF export library is not available. Please reload the page.', 'danger');
            return;
        }

        const note = this.allNotes.find(item => item.id === this.currentNoteId);
        if (!note) {
            this.showAlert('Could not find the selected note for export.', 'danger');
            return;
        }

        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
            unit: 'pt',
            format: 'a4'
        });

        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const margin = 48;
        const maxWidth = pageWidth - (margin * 2);
        let y = margin;

        const ensurePageSpace = (neededHeight = 20) => {
            if (y + neededHeight > pageHeight - margin) {
                doc.addPage();
                y = margin;
            }
        };

        const addWrappedText = (text, fontSize = 12, gapAfter = 16) => {
            const safeText = text || '';
            doc.setFontSize(fontSize);
            const lines = doc.splitTextToSize(safeText, maxWidth);
            const lineHeight = fontSize * 1.45;

            lines.forEach(line => {
                ensurePageSpace(lineHeight);
                doc.text(line, margin, y);
                y += lineHeight;
            });

            y += gapAfter;
        };

        const addSection = (heading, text) => {
            if (!text) return;
            ensurePageSpace(28);
            doc.setFont('helvetica', 'bold');
            addWrappedText(heading, 15, 8);
            doc.setFont('helvetica', 'normal');
            addWrappedText(text, 11, 18);
        };

        doc.setFont('helvetica', 'bold');
        addWrappedText(note.title || 'Untitled Note', 20, 10);

        doc.setFont('helvetica', 'normal');
        addWrappedText(`Created: ${this.formatDate(note.created_at)}`, 11, 20);

        addSection('Content', note.content || 'No content available.');
        addSection('Key Points', note.ai_analysis || 'No key points available.');

        const sanitizedTitle = (note.title || 'note')
            .replace(/[<>:"/\\|?*\x00-\x1F]/g, '')
            .trim()
            .replace(/\s+/g, '_');

        doc.save(`${sanitizedTitle || 'note'}.pdf`);
    }
    
    showAllNotes() {
        this.loadAllNotes();
    }
    
    async confirmClearAllNotes() {
        if (this.allNotes.length === 0) {
            this.showAlert('No notes to clear', 'info');
            return;
        }
        
        const confirmed = confirm(`Are you sure you want to delete all ${this.allNotes.length} notes? This action cannot be undone!`);
        
        if (confirmed) {
            await this.clearAllNotes();
        }
    }
    
    async clearAllNotes() {
        try {
            this.showAlert('Deleting all notes...', 'info');
            
            const response = await fetch('/api/notes/clear', {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showAlert(`Successfully deleted ${result.deleted_count} notes!`, 'success');
                this.loadAllNotes();
            } else {
                throw new Error('Failed to clear notes');
            }
        } catch (error) {
            console.error('Error clearing notes:', error);
            this.showAlert('Failed to clear notes. Please try again.', 'danger');
        }
    }
    
    clearForm() {
        document.getElementById('noteTitle').value = '';
        document.getElementById('noteContent').value = '';
        this.clearFile();
        
        // Reset to text input
        document.getElementById('textInput').checked = true;
        this.switchInputType('text');
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        alertContainer.innerHTML = alertHTML;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                const alert = bootstrap.Alert.getInstance(alertElement);
                if (alert) alert.close();
            }
        }, 5000);
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    }
}

// Global functions for HTML onclick events
function showAllNotes() {
    noteWise.showAllNotes();
}

// Initialize the app
const noteWise = new SimpleNotewise();
