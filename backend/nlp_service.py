#!/usr/bin/env python3
"""
Local NLP Service for Vishakha_Notewise
Handles manual NLP tasks like Named Entity Recognition using spaCy.
"""

import spacy
import os
import sys

class NLPService:
    """Manual NLP service for local entity extraction and processing."""
    
    def __init__(self, model_name="en_core_web_sm"):
        """Initialize the spaCy model."""
        self.model_name = model_name
        self.nlp = None
        self._load_model()
    
    def _load_model(self):
        """Lazy-load or download the spaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
            self._add_custom_rules()
        except (OSError, ImportError):
            print(f"Model '{self.model_name}' not found. Attempting to download...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "spacy", "download", self.model_name])
                self.nlp = spacy.load(self.model_name)
                self._add_custom_rules()
            except Exception as e:
                print(f"Error downloading spaCy model: {e}")
                self.nlp = None

    def _add_custom_rules(self):
        """Add custom rules to improve technical entity recognition."""
        if not self.nlp:
            return
            
        # Create an EntityRuler to handle technical terms correctly
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            
            # Define common technical terms that are often misidentified
            tech_patterns = [
                {"label": "TECH", "pattern": [{"LOWER": "hypervisor"}]},
                {"label": "TECH", "pattern": [{"LOWER": "vm"}]},
                {"label": "TECH", "pattern": [{"LOWER": "vms"}]},
                {"label": "TECH", "pattern": [{"LOWER": "virtual"}, {"LOWER": "machine"}]},
                {"label": "TECH", "pattern": [{"LOWER": "docker"}]},
                {"label": "TECH", "pattern": [{"LOWER": "kubernetes"}]},
                {"label": "TECH", "pattern": [{"LOWER": "k8s"}]},
                {"label": "TECH", "pattern": [{"LOWER": "api"}]},
                {"label": "TECH", "pattern": [{"LOWER": "frontend"}]},
                {"label": "TECH", "pattern": [{"LOWER": "backend"}]},
                {"label": "TECH", "pattern": [{"LOWER": "database"}]},
                {"label": "TECH", "pattern": [{"LOWER": "linux"}]},
                {"label": "TECH", "pattern": [{"LOWER": "cloud"}]},
                {"label": "TECH", "pattern": [{"LOWER": "server"}]},
                {"label": "TECH", "pattern": [{"LOWER": "python"}]},
                {"label": "TECH", "pattern": [{"LOWER": "javascript"}]},
            ]
            ruler.add_patterns(tech_patterns)
    
    def is_available(self):
        """Check if local NLP service is available."""
        return self.nlp is not None
    
    def extract_entities(self, text):
        """
        Extract named entities from text locally.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Categorized entities (PERSON, ORG, GPE, DATE, etc.)
        """
        if not self.is_available() or not text:
            return {}
            
        doc = self.nlp(text)
        entities = {
            'people': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'tech': []
        }
        
        # Mapping spaCy labels to our categories
        label_map = {
            'PERSON': 'people',
            'ORG': 'organizations',
            'GPE': 'locations',
            'LOC': 'locations',
            'DATE': 'dates',
            'TECH': 'tech',
            'PRODUCT': 'tech'
        }
        
        # Use set to avoid duplicates within a category
        seen = {cat: set() for cat in entities.keys()}
        
        for ent in doc.ents:
            category = label_map.get(ent.label_)
            if category and ent.text.strip() not in seen[category]:
                entities[category].append(ent.text.strip())
                seen[category].add(ent.text.strip())
        
        return entities

    def get_text_insights(self, text):
        """
        Extract structural insights, key phrases, and statistics locally.
        """
        if not self.is_available() or not text:
            return {}
            
        doc = self.nlp(text)
        
        # 1. Extract Single Keywords (Nouns)
        keywords = []
        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
                keywords.append(token.text.lower())
        
        from collections import Counter
        top_keywords = [item[0] for item in Counter(keywords).most_common(8)]

        # 2. NEW: Extract Key Phrases (Noun Chunks)
        # Filters out chunks that are just stop words or too short
        noun_chunks = [chunk.text.lower().strip() for chunk in doc.noun_chunks 
                      if len(chunk.text.split()) > 1 and not all(t.is_stop for t in chunk)]
        top_phrases = [item[0] for item in Counter(noun_chunks).most_common(5)]
        
        # 3. Text Statistics
        tokens = [token for token in doc if not token.is_punct]
        word_count = len(tokens)
        sent_count = len(list(doc.sents))
        
        # 4. NEW: Readability (Simple Flesch-like heuristic)
        # Average words per sentence
        avg_sent_len = word_count / max(1, sent_count)
        readability = "Easy"
        if avg_sent_len > 25: readability = "Complex"
        elif avg_sent_len > 15: readability = "Intermediate"
        
        # 5. Estimated Reading Time
        reading_time_seconds = max(1, int((word_count / 200) * 60))
        
        return {
            'keywords': top_keywords,
            'phrases': top_phrases,
            'statistics': {
                'word_count': word_count,
                'sentence_count': sent_count,
                'reading_time_seconds': reading_time_seconds,
                'complexity': readability
            }
        }

    def format_entities_for_db(self, entities):
        """Convert entities dict to a comma-separated string for DB storage."""
        if not entities:
            return ""
        
        all_ents = []
        for cat, items in entities.items():
            if items:
                # Add category prefix for clarity
                prefix = f"[{cat.upper()}] "
                all_ents.append(prefix + ", ".join(items))
                
        return " | ".join(all_ents)

# Global local NLP service instance
nlp_service = NLPService()
