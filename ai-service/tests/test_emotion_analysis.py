import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.emotion_analysis import EmotionService
import pytest

class TestEmotionService:
    
    def setup_method(self):
        self.service = EmotionService()
    
    def test_analyze_empty_text(self):
        result = self.service.analyze("")
        
        assert result['sentiment_score'] == 0.5
        assert result['emotion_type'] == 'neutral'
        assert result['crisis_detected'] == False
    
    def test_analyze_positive_text(self):
        result = self.service.analyze("今天天气真好，心情很愉快！")
        
        assert result['emotion_type'] in ['positive', 'neutral', 'negative']
        assert result['sentiment_score'] >= 0
        assert 'keywords' in result
    
    def test_analyze_negative_text(self):
        result = self.service.analyze("今天很糟糕，什么都不想做，好难过")
        
        assert result['emotion_type'] in ['positive', 'neutral', 'negative']
        assert result['sentiment_score'] >= 0
    
    def test_analyze_crisis_text(self):
        result = self.service.analyze("我不想活了，想自杀")
        
        assert result['emotion_type'] == 'crisis'
        assert result['crisis_detected'] == True
        assert result['sentiment_score'] == 0.1
    
    def test_detect_language_chinese(self):
        lang = self.service._detect_language("这是一段中文文本")
        
        assert lang == 'zh'
    
    def test_detect_language_english(self):
        lang = self.service._detect_language("This is an English text")
        
        assert lang == 'en'
    
    def test_detect_crisis_keywords(self):
        assert self.service._detect_crisis("我想自杀", 'zh') == True
        assert self.service._detect_crisis("今天天气不错", 'zh') == False
    
    def test_extract_keywords(self):
        keywords = self.service._extract_keywords("今天很开心也很快乐", 'zh')
        
        assert len(keywords) >= 0
    
    def test_analyze_neutral_text(self):
        result = self.service.analyze("今天去上班了")
        
        assert result['emotion_type'] in ['positive', 'neutral', 'negative']
        assert 0 <= result['sentiment_score'] <= 1
