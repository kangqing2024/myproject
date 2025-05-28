3.1 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate  # 对于 Linux/macOS
.venv\Scripts\activate  # 对于 Windows

3.2 安装依赖
pip install -r requirements.txt  # 如果没有 requirements.txt 文件，可根据 pyproject.toml 手动安装依赖
pip install anthropic>=0.40.0 fastapi>=0.115.6 jinja2>=3.1.5 litellm>=1.61.8 pydantic>=2.10.3 python-dotenv>=1.0.1 uvicorn>=0.33.0

3.3 在 PyCharm 中打开项目
打开 PyCharm，选择 File -> Open，然后选择 bpmn-assistant 项目文件夹。
配置 Python 解释器为刚才创建的虚拟环境。

3.4 运行应用
在终端中运行以下命令启动 bpmn_assistant：
uvicorn bpmn_assistant.app:app --reload --port 8000