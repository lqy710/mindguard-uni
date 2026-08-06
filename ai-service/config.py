import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv('DEBUG', 'True') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')

ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY', '')
ZHIPU_MODEL = os.getenv('ZHIPU_MODEL', 'glm-4-flash')
ZHIPU_BASE_URL = os.getenv('ZHIPU_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4')

# 硅基流动（SiliconFlow）向量模型配置
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY', '')
SILICONFLOW_EMBEDDING_MODEL = os.getenv('SILICONFLOW_EMBEDDING_MODEL', 'BAAI/bge-large-zh-v1.5')
SILICONFLOW_BASE_URL = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')

# ---------------- Function Calling 配置 ----------------

# 是否启用 GLM function calling。关闭后 ChatService 退回旧的「预检索 RAG」流程，
# 便于线上出问题时快速降级。
ENABLE_FUNCTION_CALLING = os.getenv('ENABLE_FUNCTION_CALLING', 'True') == 'True'

# 单次对话内允许的最大工具调用轮数，防止模型反复调用工具导致死循环。
MAX_TOOL_ROUNDS = int(os.getenv('MAX_TOOL_ROUNDS', '3'))

# 单个工具执行超时（秒）
TOOL_TIMEOUT = int(os.getenv('TOOL_TIMEOUT', '20'))

# 主对话 API 调用超时（秒），便于网络抖动时快速失败降级
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '60'))

# Java 后端地址，trigger_warning 工具需要回调后端写入 warning 表
BACKEND_BASE_URL = os.getenv('BACKEND_BASE_URL', 'http://localhost:8080')

# 内部服务间调用令牌。Python -> Java 的内网接口用它鉴权，
# 避免该接口被外部匿名调用伪造预警。生产环境必须通过环境变量覆盖。
INTERNAL_API_TOKEN = os.getenv('INTERNAL_API_TOKEN', 'mindguard-internal-token')
