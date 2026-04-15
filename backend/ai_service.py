#!/usr/bin/env python3
"""
AI Service for Vishakha_Notewise
Handles OpenRouter API interactions for AI-powered features.
"""

import requests
import json
import re
from config.config import config
def limit_text(text, max_chars=5000):
    return text[:max_chars]

class AIService:
    """AI service for OpenRouter API interactions."""
    
    def __init__(self):
        self.api_key = config.openrouter_api_key
        self.model_fallbacks = [
            "meta-llama/llama-3.3-70b-instruct:free",
            "google/gemma-3-12b-it:free",
            "mistralai/mistral-small-3.1-24b-instruct:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
        ]
        self.model = self.model_fallbacks[0]
        self.base_url = config.openrouter_base_url
        self.app_name = config.app_name
    
    def is_available(self):
        """Check if AI service is available."""
        return bool(self.api_key)
    
    def generate_completion(self, prompt, max_tokens=1000, temperature=0.7):
        """
        Generate AI completion using OpenRouter.
        
        Args:
            prompt (str): The prompt to send
            max_tokens (int): Maximum tokens in response
            temperature (float): Creativity level (0.0 to 1.0)
            
        Returns:
            dict: Response with success status and content
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'OpenRouter API key not configured',
                'content': ''
            }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/your-username/vishakha-notewise',
            'X-Title': self.app_name
        }
        failures = []

        for index, model_name in enumerate(self.model_fallbacks):
            self.model = model_name

            payload = {
                'model': model_name,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': max_tokens,
                'temperature': temperature,
                'stream': False
            }

            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    content = self._extract_response_text(data)
                    if not content:
                        return {
                            'success': False,
                            'error': self._build_empty_response_error(data),
                            'content': ''
                        }

                    # Strip thinking/reasoning blocks if present
                    content = self._strip_thinking(content)

                    return {
                        'success': True,
                        'content': content,
                        'model': model_name,
                        'tokens_used': data.get('usage', {}).get('total_tokens', 0)
                    }

                error_msg = self._extract_error_message(response)
                failures.append(f"{model_name}: {error_msg}")

                if self._should_retry_with_fallback(response.status_code, error_msg):
                    if index < len(self.model_fallbacks) - 1:
                        continue
                    return {
                        'success': False,
                        'error': self._format_all_model_failures(failures),
                        'content': ''
                    }

                return {
                    'success': False,
                    'error': error_msg,
                    'content': ''
                }

            except requests.exceptions.Timeout:
                return {
                    'success': False,
                    'error': 'Request timeout - please try again',
                    'content': ''
                }
            except requests.exceptions.RequestException as e:
                return {
                    'success': False,
                    'error': f'Network error: {str(e)}',
                    'content': ''
                }
            except Exception as e:
                print("API failed:", e)
                failures.append(f"{model_name}: Unexpected error: {str(e)}")
                if index < len(self.model_fallbacks) - 1:
                    continue
                return {
                    'success': False,
                    'error': self._format_all_model_failures(failures),
                    'content': ''
                }

        return {
            'success': False,
            'error': self._format_all_model_failures(failures),
            'content': ''
        }

    def _should_retry_with_fallback(self, status_code, error_msg):
        """Retry with the next model for rate-limit and endpoint/provider failures."""
        message = (error_msg or "").lower()
        retryable_statuses = {429, 500, 502, 503, 504}
        retryable_markers = (
            'rate limit',
            'rate-limit',
            'too many requests',
            'temporarily unavailable',
            'provider returned error',
            'provider error',
            'no endpoints found',
            'endpoint',
            'unavailable',
        )
        return status_code in retryable_statuses or any(marker in message for marker in retryable_markers)

    def _format_all_model_failures(self, failures):
        """Return a clear aggregated error when every fallback model fails."""
        if not failures:
            return 'All configured fallback models failed, but no detailed error was returned.'
        return "All configured fallback models failed. " + " | ".join(failures)
        

    def _extract_response_text(self, data):
        """Extract text from OpenRouter responses across multiple content shapes."""
        choices = data.get('choices') or []
        if not choices:
            return ""

        choice = choices[0] or {}
        message = choice.get('message') or {}

        text_parts = []
        self._append_text_parts(text_parts, message.get('content'))
        self._append_text_parts(text_parts, choice.get('text'))
        self._append_text_parts(text_parts, message.get('reasoning'))

        return "\n".join(part for part in text_parts if part).strip()

    def _append_text_parts(self, collector, value):
        """Flatten strings, arrays, and nested dicts that may contain model text."""
        if value is None:
            return

        if isinstance(value, str):
            text = value.strip()
            if text:
                collector.append(text)
            return

        if isinstance(value, list):
            for item in value:
                self._append_text_parts(collector, item)
            return

        if isinstance(value, dict):
            for key in ('text', 'content', 'output_text', 'reasoning'):
                nested = value.get(key)
                if nested:
                    self._append_text_parts(collector, nested)
            return

    def _build_empty_response_error(self, data):
        """Provide minimal diagnostics when the model response has no usable text."""
        choices = data.get('choices') or []
        if not choices:
            return 'AI model returned no choices'

        choice = choices[0] or {}
        message = choice.get('message') or {}
        content = message.get('content')

        if content is None:
            return 'AI model returned no message content'

        return f"AI model returned no text content (content type: {type(content).__name__})"

    def _extract_error_message(self, response):
        """Extract the most specific provider error message available."""
        fallback = f"OpenRouter API error: {response.status_code}"

        if not getattr(response, 'text', ''):
            return fallback

        try:
            error_data = response.json()
        except Exception:
            text = response.text.strip()
            return text[:300] if text else fallback

        candidates = []
        error = error_data.get('error')
        if isinstance(error, dict):
            for key in ('message', 'metadata', 'code'):
                value = error.get(key)
                if isinstance(value, str) and value.strip():
                    candidates.append(value.strip())
                elif isinstance(value, dict):
                    for nested_key in ('raw', 'provider_name', 'reason', 'message'):
                        nested_value = value.get(nested_key)
                        if isinstance(nested_value, str) and nested_value.strip():
                            candidates.append(nested_value.strip())
        elif isinstance(error, str) and error.strip():
            candidates.append(error.strip())

        for key in ('message', 'detail'):
            value = error_data.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())

        deduped = []
        for item in candidates:
            if item not in deduped:
                deduped.append(item)

        return " | ".join(deduped) if deduped else fallback

    def _is_placeholder_text(self, value):
        """Detect template placeholders or meta-instructions echoed by the model."""
        if not value:
            return True

        text = value.strip()
        if not text:
            return True

        lowered = text.lower()
        placeholder_patterns = (
            r'^\[[^\]]+\]$',
            r'^\(.*placeholder.*\)$',
        )
        if any(re.match(pattern, text, flags=re.IGNORECASE) for pattern in placeholder_patterns):
            return True

        placeholder_phrases = (
            'the full cleaned text',
            'full cleaned version of the text',
            'format your response exactly',
            'wait, but the user said',
            'since i have to present it',
            'perhaps just present all parts',
            '2-3 sentences.',
            '2-3 sentence summary',
            'bullet points.',
            'bullet points',
            'one word each',
            'tag1, tag2',
            'tag1, tag2, tag3',
            'concise descriptive title'
        )
        return any(phrase in lowered for phrase in placeholder_phrases)

    def _sanitize_extracted_section(self, value):
        """Discard placeholders and trim wrapper punctuation from parsed sections."""
        if not value:
            return ""

        cleaned = value.strip().strip('[]').strip()
        if self._is_placeholder_text(value) or self._is_placeholder_text(cleaned):
            return ""

        alnum_count = sum(1 for char in cleaned if char.isalnum())
        if alnum_count < 6:
            return ""

        if cleaned.lower() in {'summary', 'key points', 'tags', 'insights'}:
            return ""

        return cleaned
    
    def _strip_thinking(self, content):
        """Remove <thought> or <think> blocks from the AI response."""
        import re
        if not content:
            return ""
            
        original = content
        # 1. Remove closed thinking blocks
        content = re.sub(r'<(thought|think)>.*?</\1>', '', content, flags=re.DOTALL)
        # 2. Remove trailing unclosed thinking blocks
        content = re.sub(r'<(thought|think)>.*$', '', content, flags=re.DOTALL)
        
        # If we stripped everything but the original had content, the model likely 
        # put its entire answer inside the thought block.
        if not content.strip() and original.strip():
            # Just remove the tags themselves but keep the inner text
            cleaned = re.sub(r'</?(thought|think)>', '', original, flags=re.IGNORECASE)
            return cleaned.strip()
            
        return content.strip()
    
    def analyze_content(self, text, analysis_type='key_points'):
        text = limit_text(text)
        """
        General content analysis using OpenRouter - replaces manual processing methods.
        
        Args:
            text (str): Text to analyze
            analysis_type (str): Type of analysis (title, key_points, full)
            
        Returns:
            dict: Analysis results
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI service not available',
                'content': ''
            }
        
        if len(text.strip()) < 10:
            return {
                'success': True,
                'content': 'Text too short for analysis.',
                'analysis_type': analysis_type
            }
        
        # Let OpenRouter handle all types of analysis with context-aware prompts
        prompts = {
            'title': f"Generate a clear, descriptive title (under 60 characters) for this text:\n\n{text}\n\nTitle:",
            'key_points': f"Extract at least 10 key points from this text as bullet points. Prefer 10-15 points if the text supports it:\n\n{text}\n\nKey Points:",
            'full': f"""Analyze this text and provide:
1. A descriptive title
2. At least 10 key bullet points

Text: {text}

Analysis:"""
        }
        
        prompt = prompts.get(analysis_type, prompts['key_points'])
        
        # Adjust parameters based on analysis type
        max_tokens = 900 if analysis_type == 'full' else 600
        temperature = 0.3 if analysis_type == 'title' else 0.4
        
        result = self.generate_completion(prompt, max_tokens=max_tokens, temperature=temperature)
        
        if result['success']:
            content = result['content'].strip()
            
            # Clean up response for specific analysis types
            if analysis_type == 'title':
                # Remove common prefixes
                for prefix in ['Title:', 'title:', 'TITLE:', '**Title:**']:
                    if content.startswith(prefix):
                        content = content[len(prefix):].strip()
                content = content.strip('"').strip("'")
            
            return {
                'success': True,
                'content': content,
                'analysis_type': analysis_type,
                'model': result.get('model', ''),
                'tokens_used': result.get('tokens_used', 0)
            }
        else:
            return result
    
    def extract_entities(self, text):
        """
        Extract named entities from text using AI.
        Provides much better accuracy than local spaCy models.
        """
        if not self.is_available() or not text:
            return {}
            
        prompt = f"""You are a precise Entity Extraction engine. Your goal is to extract entities from technical text and categorize them with 100% accuracy.

CATEGORIES:
- PEOPLE: Individual human beings only. (e.g., 'Donald Griffin', 'Reginald Fessenden').
- ORGANIZATIONS: Specific companies, labs, universities, or government agencies. (e.g., 'Pfizer', 'Moderna', 'Sangart Inc').
- LOCATIONS: Specific cities, countries, or geographic regions. (e.g., 'Japan', 'United States', 'Karnataka').
- TECH: Specific inventions, software, hardware, or man-made systems. (e.g., 'Sonar', 'GPS', 'Bionic Leaf', '3D Printer').
- TOPICS: Scientific concepts, biological terms, chemicals, or general subjects. (e.g., 'Carbohydrates', 'Hemoglobin', 'Photosynthesis', 'RNA').
- DATES: Specific calendar dates, years, or time periods.

NEGATIVE CONSTRAINTS (CRITICAL):
1. NEVER put biological terms (like 'Carbohydrates', 'Glucose', 'Hemoglobin') in PEOPLE.
2. NEVER put scientific concepts or bullet points in ORGANIZATIONS.
3. If you are unsure if something is a PERSON or a TOPIC, put it in TOPICS.
4. Clean all strings: remove bullet points (•), dashes (-), and extra whitespace.

Text:
{text[:4000]}

Return ONLY a valid JSON object with keys: people, organizations, locations, tech, topics, dates.
Values must be lists of clean strings."""

        result = self.generate_completion(prompt, max_tokens=1000, temperature=0.0)
        
        if result['success']:
            try:
                content = result['content'].strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                entities = json.loads(content)
                
                # Cleanup: Strip bullet points and junk from AI response
                cleaned_entities = {}
                for key in ['people', 'organizations', 'locations', 'tech', 'topics', 'dates']:
                    raw_list = entities.get(key, [])
                    if not isinstance(raw_list, list): raw_list = []
                    
                    cleaned_list = []
                    for item in raw_list:
                        if isinstance(item, str):
                            # Remove bullets, leading dashes, and trim
                            cleaned = item.replace('•', '').replace('·', '').strip('- ').strip()
                            if cleaned and len(cleaned) > 1:
                                cleaned_list.append(cleaned)
                    cleaned_entities[key] = cleaned_list
                
                return cleaned_entities
            except Exception as e:
                print(f"Error parsing AI entities JSON: {e}")
                return {k: [] for k in ['people', 'organizations', 'locations', 'tech', 'topics', 'dates']}
        else:
            return {}

    def analyze_document(self, text, filename=None):
        """
        Perform comprehensive AI analysis of a document.
        Let OpenRouter handle all the heavy lifting for content analysis.
        
        Args:
            text (str): Document text or basic file info
            filename (str): Optional filename for context
            
        Returns:
            dict: Complete AI analysis results
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'AI service not available',
                'key_points': '',
                'title': filename or 'Untitled Document'
            }
        
        # Let AI do all the heavy lifting - comprehensive document analysis
        comprehensive_prompt = f"""You are analyzing a document. Please provide a comprehensive analysis.

Document filename: {filename or 'Unknown'}

Document content:
{text[:4000]}

Based on this content, provide:

1. TITLE: Generate a clear, descriptive title for this document (under 60 characters)
2. KEY POINTS: List 3-5 main points or topics covered (as bullet points with •)

Format your response exactly like this:
TITLE: [your title here]
KEY POINTS:
• [first point]
• [second point]
• [third point]"""

        result = self.generate_completion(comprehensive_prompt, max_tokens=500, temperature=0.4)
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Analysis failed'),
                'key_points': '',
                'title': filename or 'Untitled Document'
            }
        
        # Parse AI response to extract components
        analysis_text = result['content']
        
        # Extract title (try both formats)
        title = filename or 'Untitled Document'
        for title_marker in ['TITLE:', '**TITLE:**', 'Title:']:
            if title_marker in analysis_text:
                try:
                    title_section = analysis_text.split(title_marker)[1]
                    title_match = title_section.split('\n')[0].strip()
                    if title_match and len(title_match) > 5 and not title_match.startswith('['):
                        title = title_match
                        break
                except:
                    pass
        
        # Extract key points (try both formats)
        key_points = ''
        for points_marker in ['KEY POINTS:', '**KEY POINTS:**', 'Key Points:']:
            if points_marker in analysis_text:
                try:
                    points_section = analysis_text.split(points_marker)[1]
                    lines = points_section.strip().split('\n')
                    bullet_lines = [line for line in lines[:5] if line.strip() and ('•' in line or line.strip().startswith('-'))]
                    key_points = '\n'.join(bullet_lines)
                    if key_points and not key_points.startswith('['):
                        break
                except:
                    pass
        
        # Compile comprehensive analysis
        analysis_parts = []
        if key_points:
            analysis_parts.append(f"**Key Points:**\n{key_points}")
        
        # Fallback: if no meaningful content was extracted, use the raw response
        final_analysis = '\n\n'.join(analysis_parts) if analysis_parts else analysis_text
        
        # Check if we got placeholder text (template wasn't filled)
        if '[' in final_analysis and ']' in final_analysis:
            # AI returned template format, use simpler format
            final_analysis = f"Document Analysis:\n\n{analysis_text}"
        
        return {
            'success': True,
            'title': title,
            'key_points': key_points,
            'analysis': final_analysis,
            'raw_response': analysis_text,
            'model': result.get('model', ''),
            'tokens_used': result.get('tokens_used', 0)
        }
    
    def extract_and_analyze_file_content(self, raw_content, filename):
        """
        Streamlined: Merged extraction and analysis into one efficient call.
        """
        if not self.is_available():
            return {'success': False, 'error': 'AI service not available', 'content': raw_content}
        
        # Combined prompt for efficiency and better context
        prompt = f"""You are a professional document analyst. Please process this document:
Filename: {filename}

Content (may contain raw text artifacts):
{raw_content[:4500]}

TASK:
1. Clean the text (remove artifacts/noise).
2. Provide a descriptive TITLE (max 60 chars).
3. List at least 10 KEY POINTS (use • bullets). Prefer 10-15 points if the content supports it.

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
TITLE: concise descriptive title
KEY POINTS: • bullet 1
• bullet 2
• bullet 3
• bullet 4
CLEANED TEXT: full cleaned text in plain text

Do not use brackets like [title] or placeholder words.
Do not repeat instructions like "bullet points" or "concise descriptive title".
Each section must contain document-specific content taken from the provided file."""

        result = self.generate_completion(prompt, max_tokens=1200, temperature=0.2)
        
        if not result['success']:
            return {
                'success': True,
                'content': raw_content,
                'analysis': f"File: {filename}\n\n(AI analysis unavailable: {result.get('error')})\n\nPreview:\n{raw_content[:500]}...",
                'title': filename,
                'ai_extracted': False
            }

        response_text = result['content']
        if not response_text or len(response_text.strip()) < 5:
            return {
                'success': True,
                'content': raw_content,
                'analysis': f"File: {filename}\n\n(AI returned an empty response for this file.)\n\nPreview:\n{raw_content[:500]}...",
                'title': filename,
                'ai_extracted': False
            }
        
        # Robust Parsing Engine
        def extract_section(marker, next_markers):
            try:
                start = response_text.find(marker)
                if start == -1: return ""
                start += len(marker)
                
                # Find the earliest occurrence of any next marker
                end = len(response_text)
                for nm in next_markers:
                    pos = response_text.find(nm, start)
                    if pos != -1 and pos < end:
                        end = pos
                
                return response_text[start:end].strip()
            except:
                return ""

        title = self._sanitize_extracted_section(
            extract_section("TITLE:", ["KEY POINTS:", "CLEANED TEXT:"])
        ) or filename
        key_points = self._sanitize_extracted_section(
            extract_section("KEY POINTS:", ["CLEANED TEXT:"])
        )
        cleaned_text = self._sanitize_extracted_section(
            extract_section("CLEANED TEXT:", [])
        ) or raw_content

        # Build formatted analysis string
        analysis_parts = []
        if key_points: analysis_parts.append(f"**Key Points:**\n{key_points}")
        
        # If we failed to parse sections but the response has content, show the content
        if not analysis_parts and response_text and not self._is_placeholder_text(response_text):
            final_analysis = f"AI Analysis:\n\n{response_text}"
        else:
            final_analysis = "\n\n".join(analysis_parts) if analysis_parts else (
                f"File: {filename}\n\n(AI returned placeholder content instead of a usable analysis.)\n\nPreview:\n{raw_content[:500]}..."
            )

        return {
            'success': True,
            'content': raw_content,
            'analysis': final_analysis,
            'title': title,
            'key_points': key_points,
            'ai_extracted': True,
            'tokens_used': result.get('tokens_used', 0)
        }

# Global AI service instance
ai_service = AIService()
