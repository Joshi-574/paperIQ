import spacy
import re
from collections import Counter

class AIAnalyzer:
    def __init__(self):
        self.nlp = None
        self._initialize_nlp()
    
    def _initialize_nlp(self):
        """Initialize spaCy NLP with fallback"""
        try:
            self.nlp = spacy.load('en_core_web_sm')
            print("spaCy model loaded successfully")
        except OSError:
            print("spaCy model not found. Using fallback text processing...")
            self.nlp = None
    
    def analyze_document(self, text):
        """
        Analyze document text and return insights
        """
        if self.nlp:
            return self._analyze_with_spacy(text)
        else:
            return self._analyze_with_fallback(text)
    
    def _analyze_with_spacy(self, text):
        """Advanced analysis using spaCy"""
        doc = self.nlp(text[:1000000])  # Limit text length
        
        # Extract entities
        entities = [ent.text for ent in doc.ents][:10]
        
        # Extract key phrases (noun chunks)
        key_phrases = [chunk.text for chunk in doc.noun_chunks][:10]
        
        # Analyze sentences
        sentences = [sent.text for sent in doc.sents]
        
        analysis = {
            "summary": self._generate_summary(sentences),
            "key_points": key_phrases,
            "entities": entities,
            "sentiment": self._analyze_sentiment(doc),
            "word_count": len(doc),
            "sentence_count": len(sentences)
        }
        
        return analysis
    
    def _analyze_with_fallback(self, text):
        """Fallback analysis without spaCy"""
        # Simple text processing
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple entity extraction (capitalized words)
        entities = list(set([word for word in words if word.istitle() and len(word) > 2]))[:10]
        
        # Simple key phrases (frequent words)
        word_freq = Counter([word.lower() for word in words if len(word) > 3])
        key_phrases = [word for word, count in word_freq.most_common(10)]
        
        analysis = {
            "summary": self._generate_simple_summary(sentences),
            "key_points": key_phrases,
            "entities": entities,
            "sentiment": "neutral",  # Fallback
            "word_count": len(words),
            "sentence_count": len(sentences),
            "note": "Using fallback analysis (install spaCy model for better results)"
        }
        
        return analysis
    
    def _generate_summary(self, sentences, max_sentences=3):
        """Generate summary from sentences"""
        return ' '.join(sentences[:max_sentences])
    
    def _generate_simple_summary(self, sentences, max_sentences=3):
        """Simple summary without spaCy"""
        return ' '.join(sentences[:max_sentences])
    
    def _analyze_sentiment(self, doc):
        """Simple sentiment analysis"""
        positive_words = {'good', 'great', 'excellent', 'positive', 'successful', 'effective'}
        negative_words = {'bad', 'poor', 'negative', 'limited', 'challenging', 'problem'}
        
        text_lower = doc.text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def generate_questions(self, text, num_questions=5):
        """
        Generate questions based on the document content
        """
        if self.nlp:
            return self._generate_questions_with_spacy(text, num_questions)
        else:
            return self._generate_questions_with_fallback(text, num_questions)
    
    def _generate_questions_with_spacy(self, text, num_questions):
        """Generate questions using spaCy"""
        doc = self.nlp(text[:50000])  # Limit for performance
        sentences = [sent.text for sent in doc.sents][:10]
        
        questions = []
        for sentence in sentences:
            if len(sentence) > 50:  # Substantial sentences
                questions.append(f"What does this mean: '{sentence}'?")
        
        return self._fill_default_questions(questions, num_questions)
    
    def _generate_questions_with_fallback(self, text, num_questions):
        """Generate questions without spaCy"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 50][:10]
        
        questions = []
        for sentence in sentences:
            questions.append(f"Can you explain: '{sentence}'?")
        
        return self._fill_default_questions(questions, num_questions)
    
    def _fill_default_questions(self, questions, num_questions):
        """Fill with default questions if needed"""
        default_questions = [
            "What is the main argument presented?",
            "How does the author support their claims?",
            "What methodology was used in this research?",
            "What are the key findings?",
            "What limitations are mentioned?",
            "What future work is suggested?",
            "How does this relate to existing research?",
            "What are the practical implications?"
        ]
        
        while len(questions) < num_questions:
            questions.extend(default_questions)
        
        return questions[:num_questions]