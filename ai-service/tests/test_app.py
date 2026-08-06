import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import pytest
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestApp:
    
    def test_health_check(self, client):
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
    
    def test_emotion_analyze_success(self, client):
        response = client.post('/api/emotion/analyze',
            json={'text': '今天心情很好'},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert 'emotion_type' in data['data']
        assert 'sentiment_score' in data['data']
    
    def test_emotion_analyze_empty_text(self, client):
        response = client.post('/api/emotion/analyze',
            json={'text': ''},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 400
    
    def test_risk_assess_success(self, client):
        response = client.post('/api/risk/assess',
            json={'userData': {'score': 15, 'history': []}},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert 'risk_level' in data['data']
    
    def test_risk_quick_assess_success(self, client):
        response = client.post('/api/risk/quick-assess',
            json={'text': '今天心情不错'},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
        assert 'risk_level' in data['data']
    
    def test_risk_quick_assess_empty_text(self, client):
        response = client.post('/api/risk/quick-assess',
            json={'text': ''},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 400
    
    def test_chat_reply_success(self, client):
        response = client.post('/api/chat/reply',
            json={'message': '你好'},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 200
    
    def test_chat_reply_empty_message(self, client):
        response = client.post('/api/chat/reply',
            json={'message': ''},
            content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['code'] == 400
