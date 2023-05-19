# 使用官方Python基础镜像
FROM python:3.7-slim

# 设置工作目录
WORKDIR /app

# RUN pip config set global.index-url http://pypi.douban.com/simple/

# 安装项目依赖
# RUN pip install pipenv --trusted-host pypi.douban.com && pipenv install --system
RUN pip install pipenv && pipenv install && pipenv run pip freeze > requirements.txt && pip install -r requirements.txt

# 复制项目文件到容器
COPY . /app
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

CMD ["pipenv", "run", "python", "main.py"]
# ENTRYPOINT ["pipenv shell python"]
# CMD []
