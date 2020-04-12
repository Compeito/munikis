FROM ubuntu

ENV PYTHONUNBUFFERED 1
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# python依存モジュールのインストール
# https://www.python.jp/install/ubuntu/index.html
RUN apt update
RUN apt install -y build-essential libbz2-dev libdb-dev \
    libreadline-dev libffi-dev libgdbm-dev liblzma-dev \
    libncursesw5-dev libsqlite3-dev libssl-dev zlib1g-dev \
    uuid-dev
# mysqlclient依存モジュールのインストール
RUN apt install -y default-libmysqlclient-dev
# python本体のインストール
RUN apt install -y python3.7 python3.7-dev python3.7-distutils python3.7-venv
RUN apt install -y python3-pip
# その他ソフトウェアのインストール
RUN apt install -y ffmpeg git curl

# poetryのインストール
RUN ln -s /usr/bin/python3.7 /usr/bin/python
RUN python -m pip install -U pip
RUN pip install poetry
RUN poetry config virtualenvs.in-project true

# poetryパッケージのインストール
WORKDIR /code
COPY pyproject.toml /code/
COPY poetry.lock /code/
RUN poetry install --no-dev --no-root

COPY . /code/
RUN chmod +x /code/start.sh
ENTRYPOINT ["poetry", "run"]
CMD ["/code/start.sh"]
