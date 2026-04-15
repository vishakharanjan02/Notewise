#!/usr/bin/env python3
"""
Simple Database Module for Vishakha_Notewise
A simplified version of the original NoteWise database.
"""

import sqlite3
import json
from datetime import datetime

class SimpleDatabase:
    """Simplified database handler for Vishakha_Notewise application."""
    
    def __init__(self, db_path="notewise_simple.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize simplified database tables - let AI handle the complex analysis."""
        with self.get_connection() as conn:
            # Simplified notes table - AI handles metadata and analysis
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    ai_analysis TEXT,
                    source_type TEXT DEFAULT 'text',
                    filename TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migration: Add ai_analysis column if it doesn't exist
            try:
                cursor = conn.execute("PRAGMA table_info(notes)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'ai_analysis' not in columns:
                    print("Migrating database: Adding ai_analysis column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN ai_analysis TEXT')
                    print("Migration complete!")
                    
                if 'source_type' not in columns:
                    print("Migrating database: Adding source_type column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN source_type TEXT DEFAULT "text"')
                    print("Migration complete!")
                    
                if 'filename' not in columns:
                    print("Migrating database: Adding filename column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN filename TEXT')
                    print("Migration complete!")

                if 'tags' not in columns:
                    print("Migrating database: Adding tags column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN tags TEXT')
                    print("Migration complete!")

                if 'entities' not in columns:
                    print("Migrating database: Adding entities column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN entities TEXT')
                    print("Migration complete!")
                
                if 'insights' not in columns:
                    print("Migrating database: Adding insights column...")
                    conn.execute('ALTER TABLE notes ADD COLUMN insights TEXT')
                    print("Migration complete!")
                    
            except Exception as e:
                print(f"Migration error (may be safe to ignore): {e}")
            
            conn.commit()
    
    def save_note(self, title, content, ai_analysis='', source_type='text', filename=None, tags='', entities='', insights=''):
        """
        Save a note - simplified schema, local and AI NLP.
        
        Args:
            title (str): Note title
            content (str): Note content 
            ai_analysis (str): AI-generated analysis/summary
            source_type (str): 'text' or 'file'
            filename (str): Original filename if uploaded
            tags (str): Comma-separated tags (AI)
            entities (str): Locally extracted entities (spaCy)
            insights (str): JSON string of local NLP insights
            
        Returns:
            int: ID of the created note
        """
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO notes (title, content, ai_analysis, source_type, filename, tags, entities, insights, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, content, ai_analysis, source_type, filename, tags, entities, insights, datetime.now().isoformat()))
            return cursor.lastrowid
    
    def get_all_notes(self):
        """Get all notes."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM notes ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_note_by_id(self, note_id):
        """Get note by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM notes WHERE id = ?
            ''', (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_note(self, note_id):
        """Delete note by ID."""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                DELETE FROM notes WHERE id = ?
            ''', (note_id,))
            return cursor.rowcount > 0
    
    def clear_all_notes(self):
        """Delete all notes and return count of deleted notes."""
        with self.get_connection() as conn:
            # Get count before deletion
            count_cursor = conn.execute('SELECT COUNT(*) FROM notes')
            count = count_cursor.fetchone()[0]
            
            # Delete all notes
            conn.execute('DELETE FROM notes')
            
            return count

# Global database instance
db = SimpleDatabase()