FROM python:3.7-slim

# pythonのuオプションと等しい
ENV PYTHONUNBUFFERED 1

# 依存パッケージのインストール
# gcc,default-libmysqlclient-devはmysqlclientのため
RUN apt update && apt install -y ffmpeg git gcc default-libmysqlclient-dev

# poetryのインストール
RUN python -m pip install -U pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true

# poetryパッケージのインストール
WORKDIR /code
COPY pyproject.toml /code/
COPY poetry.lock /code/
RUN poetry install --no-dev --no-root

# gccの削除
RUN apt purge gcc -y --auto-remove

COPY . /code/
RUN chmod +x /code/start.sh
ENTRYPOINT ["poetry", "run"]
CMD ["/code/start.sh"]
