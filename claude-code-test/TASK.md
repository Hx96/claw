# 任务：创建一个简单的Python Web API

创建一个基于 FastAPI 的 REST API，包含以下功能：

1. GET /health - 健康检查
2. GET /items - 获取所有项目
3. POST /items - 创建新项目
4. GET /items/{id} - 获取单个项目

要求：
- 使用 Python 3.12
- 使用 FastAPI + Uvicorn
- 使用 SQLite 作为数据库
- 包含完整的错误处理
- 代码结构清晰

项目文件：
- main.py - 主入口
- models.py - 数据模型
- database.py - 数据库配置
- requirements.txt - 依赖
