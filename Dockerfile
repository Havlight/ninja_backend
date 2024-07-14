# 使用官方的 Python 镜像作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y libgl1

# 复制当前目录内容到工作目录
COPY . /app

# 更新 pip 和安装所需的依赖项
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# 暴露应用运行的端口
EXPOSE 8000

# 运行数据库迁移和启动应用
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
