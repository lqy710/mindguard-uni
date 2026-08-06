import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.risk_assessment import RiskService
import pytest

class TestRiskService:
    
    def setup_method(self):
        self.service = RiskService()
    
    def test_assess_high_risk_score(self):
        user_data = {
            'score': 25,
            'history': [
                {'risk_level': 'high', 'score': 22},
                {'risk_level': 'high', 'score': 20},
                {'risk_level': 'high', 'score': 18}
            ]
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'high'
        assert result['need_immediate_attention'] == True
    
    def test_assess_medium_risk_score(self):
        user_data = {
            'score': 15,
            'history': [
                {'risk_level': 'medium', 'score': 10},
                {'risk_level': 'medium', 'score': 8},
                {'risk_level': 'medium', 'score': 6}
            ]
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'medium'
        assert result['need_immediate_attention'] == False
    
    def test_assess_low_risk_score(self):
        user_data = {
            'score': 3,
            'history': [{'risk_level': 'low', 'score': 2}]
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'low'
        assert result['need_immediate_attention'] == False
    
    def test_assess_with_crisis_keywords(self):
        user_data = {
            'score': 15,
            'history': [],
            'recent_texts': ['我不想活了，想自杀']
        }
        
        result = self.service.assess(user_data)
        
        assert result['risk_level'] == 'high'
        assert result['need_immediate_attention'] == True
    
    def test_assess_with_emotion_scores(self):
        user_data = {
            'score': 5,
            'history': [],
            'emotion_scores': [0.2, 0.25, 0.3]
        }
        
        result = self.service.assess(user_data)
        
        assert 'risk_factors' in result
        assert any('情绪' in factor for factor in result['risk_factors'])
    
    def test_quick_assess_crisis_keyword(self):
        result = self.service.quick_assess("我不想活了，想自杀")
        
        assert result['risk_level'] == 'high'
        assert result['need_immediate_attention'] == True
    
    def test_quick_assess_high_risk_keyword(self):
        result = self.service.quick_assess("我感到绝望，崩溃了")
        
        assert result['risk_level'] == 'medium'
        assert result['need_immediate_attention'] == False
    
    def test_quick_assess_medium_risk_keyword(self):
        result = self.service.quick_assess("最近很焦虑，压力很大")
        
        assert result['risk_level'] == 'low'
        assert result['need_immediate_attention'] == False
    
    def test_quick_assess_normal_text(self):
        result = self.service.quick_assess("今天天气不错")
        
        assert result['risk_level'] == 'low'
        assert result['need_immediate_attention'] == False
    
    def test_assess_empty_data(self):
        result = self.service.assess({})
        
        assert result['risk_level'] == 'low'
        assert 'recommendation' in result
    
    def test_recommendation_content(self):
        low_result = self.service.assess({'score': 0})
        high_result = self.service.assess({
            'score': 25, 
            'history': [
                {'risk_level': 'high'},
                {'risk_level': 'high'},
                {'risk_level': 'high'}
            ]
        })
        
        assert '继续保持' in low_result['recommendation']
        assert '心理援助热线' in high_result['recommendation']
