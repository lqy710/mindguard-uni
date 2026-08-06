class RiskService:
    def __init__(self):
        self.crisis_keywords = [
            '自杀', '想死', '不想活', '活着没意思', '结束生命',
            '自残', '伤害自己', '跳楼', '割腕', '服药'
        ]
        
        self.high_risk_keywords = [
            '绝望', '崩溃', '无法承受', '撑不下去', '没有希望',
            '抑郁', '严重失眠', '幻觉', '幻听'
        ]
        
        self.medium_risk_keywords = [
            '焦虑', '压力大', '失眠', '孤独', '无助',
            '难过', '悲伤', '恐惧', '害怕'
        ]
    
    def assess(self, user_data):
        score = user_data.get('score', 0)
        history = user_data.get('history', [])
        recent_texts = user_data.get('recent_texts', [])
        emotion_scores = user_data.get('emotion_scores', [])
        
        risk_level = 'low'
        risk_factors = []
        risk_score = 0
        
        if score >= 20:
            risk_score += 40
            risk_factors.append(f'测评得分较高({score}分)')
        elif score >= 10:
            risk_score += 20
            risk_factors.append(f'测评得分中等({score}分)')
        
        high_risk_count = 0
        medium_risk_count = 0
        for record in history:
            if record.get('risk_level') == 'high':
                high_risk_count += 1
            elif record.get('risk_level') == 'medium':
                medium_risk_count += 1
        
        if high_risk_count >= 3:
            risk_score += 30
            risk_factors.append(f'历史记录显示多次高风险({high_risk_count}次)')
        elif high_risk_count >= 1:
            risk_score += 15
            risk_factors.append(f'历史记录有高风险({high_risk_count}次)')
        
        if medium_risk_count >= 3:
            risk_score += 10
            risk_factors.append(f'历史记录多次中等风险({medium_risk_count}次)')
        
        if recent_texts:
            crisis_detected = self._detect_crisis_keywords(recent_texts)
            if crisis_detected:
                risk_score += 50
                risk_factors.append('近期表达中检测到危机关键词')
            else:
                high_risk_detected = self._detect_keywords(recent_texts, self.high_risk_keywords)
                medium_risk_detected = self._detect_keywords(recent_texts, self.medium_risk_keywords)
                
                if high_risk_detected:
                    risk_score += 20
                    risk_factors.append('近期表达中存在高风险情绪词')
                if medium_risk_detected:
                    risk_score += 10
                    risk_factors.append('近期表达中存在中等风险情绪词')
        
        if emotion_scores:
            avg_emotion = sum(emotion_scores) / len(emotion_scores)
            if avg_emotion < 0.3:
                risk_score += 25
                risk_factors.append(f'近期情绪持续低落(平均{round(avg_emotion, 2)})')
            elif avg_emotion < 0.4:
                risk_score += 15
                risk_factors.append(f'近期情绪偏低(平均{round(avg_emotion, 2)})')
        
        if risk_score >= 60:
            risk_level = 'high'
        elif risk_score >= 30:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'risk_score': min(risk_score, 100),
            'risk_factors': risk_factors,
            'recommendation': self._get_recommendation(risk_level),
            'need_immediate_attention': risk_level == 'high'
        }
    
    def _detect_crisis_keywords(self, texts):
        for text in texts:
            for keyword in self.crisis_keywords:
                if keyword in text:
                    return True
        return False
    
    def _detect_keywords(self, texts, keywords):
        for text in texts:
            for keyword in keywords:
                if keyword in text:
                    return True
        return False
    
    def _get_recommendation(self, level):
        recommendations = {
            'low': '继续保持良好的心理状态。建议：\n• 保持规律作息\n• 适度运动\n• 与亲友保持联系\n• 定期自我反思',
            'medium': '建议关注心理健康。建议：\n• 寻求专业心理咨询\n• 与家人朋友保持沟通\n• 关注自我情绪变化\n• 学习压力管理技巧\n• 如有需要可拨打心理热线：400-161-9995',
            'high': '⚠️ 强烈建议尽快寻求专业心理帮助！\n\n紧急联系方式：\n• 24小时心理援助热线：400-161-9995\n• 北京心理危机干预中心：010-82951332\n• 生命热线：400-821-1215\n\n请立即：\n1. 联系专业心理咨询师或精神科医生\n2. 告知家人或信任的朋友你的情况\n3. 避免独处，寻求陪伴'
        }
        return recommendations.get(level, recommendations['low'])
    
    def quick_assess(self, text):
        for keyword in self.crisis_keywords:
            if keyword in text:
                return {
                    'risk_level': 'high',
                    'need_immediate_attention': True,
                    'recommendation': '检测到危机信号，请立即寻求专业帮助！\n24小时心理援助热线：400-161-9995'
                }
        
        high_risk = any(kw in text for kw in self.high_risk_keywords)
        medium_risk = any(kw in text for kw in self.medium_risk_keywords)
        
        if high_risk:
            return {
                'risk_level': 'medium',
                'need_immediate_attention': False,
                'recommendation': '检测到一些负面情绪，建议关注心理健康，必要时寻求专业帮助。'
            }
        elif medium_risk:
            return {
                'risk_level': 'low',
                'need_immediate_attention': False,
                'recommendation': '保持关注自己的情绪状态，适当放松和休息。'
            }
        
        return {
            'risk_level': 'low',
            'need_immediate_attention': False,
            'recommendation': '继续保持良好的心理状态。'
        }
