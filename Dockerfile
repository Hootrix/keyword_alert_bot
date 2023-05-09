# 使用官方Python基础镜像
FROM python:3.7-slim

# 设置工作目录
WORKDIR /app

# RUN pip config set global.index-url http://pypi.douban.com/simple/

# 安装项目依赖
# RUN pip install pipenv --trusted-host pypi.douban.com && pipenv install --system --deploy
RUN pip install pipenv && pipenv install --system --deploy

# 复制项目文件到容器
# COPY . /app
COPY Pipfile /app/Pipfile

# CMD ["python", "main.py"]
ENTRYPOINT ["python"]
CMD []
