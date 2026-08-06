from flask import Flask, request, jsonify
from flask_cors import CORS
from services.emotion_analysis import EmotionService
from services.chat_service import ChatService
from services.risk_assessment import RiskService
from services.knowledge_service import knowledge_service

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})

emotion_service = EmotionService()
chat_service = ChatService()
risk_service = RiskService()

@app.route('/api/emotion/analyze', methods=['POST'])
def analyze_emotion():
    data = request.json
    text = data.get('text', '')
    language = data.get('language', 'auto')
    
    if not text:
        return jsonify({'code': 400, 'message': '文本不能为空'})
    
    try:
        result = emotion_service.analyze(text, language)
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/chat/reply', methods=['POST'])
def chat_reply():
    data = request.json
    message = data.get('message', '')
    context = data.get('context', [])
    user_id = data.get('user_id', None)
    language = data.get('language', 'auto')
    session_id = data.get('session_id', None)
    
    if not message:
        return jsonify({'code': 400, 'message': '消息不能为空'})
    
    try:
        result = chat_service.reply(
            message, context, user_id, language, session_id=session_id
        )
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/chat/reply_with_context', methods=['POST'])
def chat_reply_with_context():
    data = request.json
    message = data.get('message', '')
    context = data.get('context', [])
    user_id = data.get('user_id', None)
    language = data.get('language', 'auto')
    session_id = data.get('session_id', None)
    
    if not message:
        return jsonify({'code': 400, 'message': '消息不能为空'})
    
    if not context:
        context = []
    
    try:
        result = chat_service.reply_with_context(
            message, context, user_id, language, session_id=session_id
        )
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/chat/stage', methods=['GET'])
def chat_stage():
    """查询会话当前所处阶段。调试与前端初始化恢复阶段展示时使用。"""
    user_id = request.args.get('user_id', type=int)
    session_id = request.args.get('session_id', type=int)

    try:
        return jsonify({
            'code': 200,
            'data': chat_service.get_stage(user_id=user_id, session_id=session_id),
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/chat/stage/reset', methods=['POST'])
def chat_stage_reset():
    """重置会话阶段，回到评估阶段。开启新对话时调用。"""
    data = request.json or {}
    user_id = data.get('user_id')
    session_id = data.get('session_id')

    try:
        removed = chat_service.reset_stage(user_id=user_id, session_id=session_id)
        return jsonify({'code': 200, 'data': {'reset': removed}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})


@app.route('/api/risk/assess', methods=['POST'])
def assess_risk():
    data = request.json
    user_data = data.get('userData', {})
    
    try:
        result = risk_service.assess(user_data)
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/risk/quick-assess', methods=['POST'])
def quick_assess_risk():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'code': 400, 'message': '文本不能为空'})
    
    try:
        result = risk_service.quick_assess(text)
        return jsonify({'code': 200, 'data': result})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/knowledge/retrieve', methods=['POST'])
def retrieve_knowledge():
    """RAG 检索：返回与 query 最相关的知识片段。"""
    data = request.json or {}
    query = data.get('query', '')
    top_k = data.get('top_k', 3)

    if not query:
        return jsonify({'code': 400, 'message': '查询内容不能为空'})

    try:
        top_k = max(1, min(int(top_k), 10))
    except (TypeError, ValueError):
        top_k = 3

    try:
        results = knowledge_service.retrieve(query, top_k=top_k)
        return jsonify({'code': 200, 'data': {'query': query, 'references': results}})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/knowledge/reindex', methods=['POST'])
def reindex_knowledge():
    """
    由 Java 后端推送文章全量语料，重建向量索引。
    articles: [{id, title, summary, content, category}]
    """
    data = request.json or {}
    articles = data.get('articles', [])

    if not isinstance(articles, list):
        return jsonify({'code': 400, 'message': 'articles 必须是数组'})

    try:
        chunk_count = knowledge_service.build_index(articles)
        return jsonify({
            'code': 200,
            'data': {'articleCount': len(articles), 'chunkCount': chunk_count}
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/api/knowledge/stats', methods=['GET'])
def knowledge_stats():
    """查看当前索引状态，便于排查 RAG 是否生效。"""
    try:
        return jsonify({'code': 200, 'data': knowledge_service.stats()})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'python-ai-service'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
