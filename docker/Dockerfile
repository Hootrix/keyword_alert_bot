# 使用官方Python基础镜像
FROM python:3.7-slim

# 设置工作目录
WORKDIR /app

# 将pipenv安装到镜像中
RUN pip install --no-cache-dir pipenv

# 将Pipfile和Pipfile.lock复制到工作目录
COPY Pipfile* /app/

# 安装项目依赖
RUN pipenv install --system --deploy

# 复制项目代码到工作目录
COPY . /app

# 安装supervisor
RUN apt-get update && apt-get install -y supervisor

# 复制supervisor配置文件到适当的位置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 暴露端口，如果需要的话
# EXPOSE <port_number>

# 使用supervisor启动服务
CMD ["/usr/bin/supervisord"]
