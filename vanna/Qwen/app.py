import openai

# ✅ Monkey patch：强制关闭 enable_thinking，避免 400 报错
original_create = openai.ChatCompletion.create
def patched_create(*args, **kwargs):
    kwargs["enable_thinking"] = False
    return original_create(*args, **kwargs)
openai.ChatCompletion.create = patched_create


from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from vanna.qianwen import QianWenAI_Chat
from vanna.flask import VannaFlaskApp

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ✅ 组合类：Chroma + 通义千问
class MyVanna(ChromaDB_VectorStore, QianWenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        QianWenAI_Chat.__init__(self, config=config)

# ✅ 配置模型
config = {
    "api_key": "sk-74b2aa50e99c43c38d88aace97f7c705",  # ✅ 替换为你自己的 API Key
    "model": "qwen3-235b-a22b"  # ✅ 替换为你使用的 Qwen 模型名称
}

vn = MyVanna(config=config)

# ✅ MySQL 数据库连接
vn.connect_to_mysql(
    host="10.17.0.21",
    dbname="lit_db_base",
    user="root",
    password="lit-Info-Dev",
    port=3306
)

# ✅ 开始训练
vn.train(documentation="请注意，在我们公司一般将1作为是，0作为否。")

# ✅ 初始化 Flask App（不运行）
flask_app = VannaFlaskApp(
    vn,
    debug=False,
    allow_llm_to_see_data=True,
    title="数据库问答系统"
)

# ✅ 正确地启动服务
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=8084, debug=True)

