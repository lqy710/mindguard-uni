import requests
import json
import re
from config import ZHIPU_API_KEY, ZHIPU_MODEL, ZHIPU_BASE_URL, DEBUG

class EmotionService:
    def __init__(self):
        self.api_key = ZHIPU_API_KEY
        self.model = ZHIPU_MODEL
        self.base_url = ZHIPU_BASE_URL
        
        self.crisis_keywords = {
            'zh': ['自杀', '想死', '不想活', '活着没意思', '结束生命', '自残', '伤害自己', '跳楼', '割腕', '服药'],
            'en': ['suicide', 'kill myself', 'want to die', 'end my life', 'self-harm', 'harm myself', 'jump off', 'cut wrist', 'overdose']
        }
        
        self.negative_keywords = {
            'zh': ['难过', '悲伤', '伤心', '痛苦', '绝望', '抑郁', '焦虑', '恐惧', '害怕', '担心', '压力', '累', '疲惫', '孤独', '寂寞', '无助', '失落', '沮丧', '崩溃', '烦躁'],
            'en': ['sad', 'grief', 'heartbroken', 'painful', 'desperate', 'depressed', 'anxious', 'fear', 'afraid', 'worried', 'stress', 'tired', 'exhausted', 'lonely', 'alone', 'helpless', 'lost', 'depressed', 'crash', 'irritated']
        }
        
        self.positive_keywords = {
            'zh': ['开心', '快乐', '高兴', '幸福', '满足', '愉快', '轻松', '顺利', '美好', '喜欢', '爱', '感谢', '感恩', '希望', '期待', '兴奋', '激动', '欣慰'],
            'en': ['happy', 'joy', 'glad', 'happy', 'satisfied', 'pleased', 'relaxed', 'smooth', 'good', 'like', 'love', 'thank', 'grateful', 'hope', 'expect', 'excited', 'thrilled', 'relieved']
        }
        
        self.emotion_categories = {
            'zh': {
                'angry': ['愤怒', '生气', '恼火', '暴怒', '气愤', '火大'],
                'fear': ['恐惧', '害怕', '担心', '焦虑', '惊恐', '害怕'],
                'sad': ['悲伤', '难过', '伤心', '痛苦', '沮丧', '抑郁'],
                'happy': ['开心', '快乐', '高兴', '幸福', '满足', '愉快'],
                'surprise': ['惊讶', '惊喜', '震惊', '意外', '吃惊', '震撼'],
                'disgust': ['厌恶', '反感', '恶心', '讨厌', '憎恶', '嫌弃']
            },
            'en': {
                'angry': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'rage'],
                'fear': ['fear', 'afraid', 'worried', 'anxious', 'scared', 'terrified'],
                'sad': ['sad', 'sorrow', 'heartbroken', 'grief', 'depressed', 'upset'],
                'happy': ['happy', 'joy', 'glad', 'delighted', 'pleased', 'excited'],
                'surprise': ['surprise', 'amazed', 'shocked', 'astonished', 'astounded', 'stunned'],
                'disgust': ['disgust', 'dislike', 'hate', 'revulsion', 'repulsion', 'aversion']
            }
        }
    
    def analyze(self, text, language='auto'):
        print(f"[DEBUG] analyze called with text: {text}")
        if not text:
            return {
                'sentiment_score': 0.5,
                'emotion_type': 'neutral',
                'emotions': [],
                'emotion_details': {},
                'keywords': [],
                'crisis_detected': False,
                'language': 'unknown'
            }
        
        detected_language = self._detect_language(text) if language == 'auto' else language
        
        crisis_detected = self._detect_crisis(text, detected_language)
        print(f"[DEBUG] crisis_detected: {crisis_detected}")
        
        if crisis_detected:
            return {
                'sentiment_score': 0.1,
                'emotion_type': 'crisis',
                'emotions': ['危机'],
                'emotion_details': {'crisis': 1.0},
                'keywords': self._extract_keywords(text, detected_language),
                'crisis_detected': True,
                'recommendation': '检测到高风险情绪，建议立即寻求专业帮助',
                'language': detected_language
            }
        
        if self.api_key:
            try:
                result = self._analyze_with_zhipu(text, detected_language)
                if result:
                    result['language'] = detected_language
                    return result
            except Exception as e:
                if DEBUG:
                    print(f"智谱AI情感分析失败: {e}")
        
        result = self._analyze_with_rules(text, detected_language)
        result['language'] = detected_language
        return result
    
    def _detect_language(self, text):
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        return 'zh' if chinese_chars > len(text) * 0.3 else 'en'
    
    def _detect_crisis(self, text, language):
        lang = 'zh' if language not in ['zh', 'en'] else language
        for keyword in self.crisis_keywords.get(lang, []):
            if keyword in text.lower():
                return True
        return False
    
    def _extract_keywords(self, text, language):
        keywords = []
        lang = 'zh' if language not in ['zh', 'en'] else language
        all_keywords = self.negative_keywords.get(lang, []) + self.positive_keywords.get(lang, []) + self.crisis_keywords.get(lang, [])
        for keyword in all_keywords:
            if keyword in text:
                keywords.append(keyword)
        return keywords[:5]
    
    def _analyze_with_zhipu(self, text, language):
        url = f"{self.base_url}/chat/completions"
        
        prompt = f"""请分析以下文本的情感，只返回JSON格式结果，不要其他内容：
{{
  "sentiment_score": 0.0-1.0之间的数值,
  "emotion_type": "positive/neutral/negative",
  "emotions": ["具体情绪词1", "具体情绪词2"],
  "emotion_details": {{"情绪类型1": 0.0-1.0, "情绪类型2": 0.0-1.0}},
  "emotion_categories": ["angry", "fear", "sad", "happy", "surprise", "disgust"]
}}

文本：{text}"""
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"[DEBUG] 智谱AI返回内容: {content}")
                try:
                    if '```json' in content:
                        json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                        else:
                            json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                            json_str = json_match.group() if json_match else None
                    else:
                        json_match = re.search(r'\{.*?\}', content, re.DOTALL)
                        json_str = json_match.group() if json_match else None
                    
                    if json_str:
                        parsed = json.loads(json_str)
                        sentiment_score = float(parsed.get('sentiment_score', 0.5))
                        emotion_type = parsed.get('emotion_type', 'neutral')
                        emotions = parsed.get('emotions', [])
                        emotion_details = parsed.get('emotion_details', {})
                        
                        if emotion_type not in ['positive', 'negative', 'neutral']:
                            if sentiment_score > 0.6:
                                emotion_type = 'positive'
                            elif sentiment_score < 0.4:
                                emotion_type = 'negative'
                            else:
                                emotion_type = 'neutral'
                        
                        return {
                            'sentiment_score': round(sentiment_score, 2),
                            'emotion_type': emotion_type,
                            'emotions': emotions[:5],
                            'emotion_details': emotion_details,
                            'keywords': emotions[:5] if emotions else self._extract_keywords(text, language),
                            'crisis_detected': False
                        }
                except (json.JSONDecodeError, ValueError) as e:
                    if DEBUG:
                        print(f"解析智谱AI响应失败: {e}, content: {content}")
        
        return None
    
    def _analyze_with_rules(self, text, language):
        lang = 'zh' if language not in ['zh', 'en'] else language
        positive_count = sum(1 for kw in self.positive_keywords.get(lang, []) if kw in text)
        negative_count = sum(1 for kw in self.negative_keywords.get(lang, []) if kw in text)
        
        total = positive_count + negative_count
        if total == 0:
            return {
                'sentiment_score': 0.5,
                'emotion_type': 'neutral',
                'emotions': [],
                'emotion_details': {},
                'keywords': [],
                'crisis_detected': False
            }
        
        sentiment_score = 0.5 + (positive_count - negative_count) * 0.1
        sentiment_score = max(0.1, min(0.9, sentiment_score))
        
        if sentiment_score > 0.6:
            emotion_type = 'positive'
            emotions = ['开心', '快乐'] if lang == 'zh' else ['happy', 'joy']
        elif sentiment_score < 0.4:
            emotion_type = 'negative'
            emotions = ['难过', '悲伤'] if lang == 'zh' else ['sad', 'upset']
        else:
            emotion_type = 'neutral'
            emotions = ['平静', '中性'] if lang == 'zh' else ['calm', 'neutral']
        
        emotion_details = {}
        for emotion in emotions:
            emotion_details[emotion] = 0.7
        
        return {
            'sentiment_score': round(sentiment_score, 2),
            'emotion_type': emotion_type,
            'emotions': emotions,
            'emotion_details': emotion_details,
            'keywords': self._extract_keywords(text, language),
            'crisis_detected': False
        }
