FROM python:3
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=JST-9
ENV TERM=xterm

RUN apt-get install -y vim less
RUN pip install --upgrade pip setuptools

RUN apt-get install -y poppler-utils poppler-data
WORKDIR /workspace/
COPY requirements.txt .
RUN pip install -r ./requirements.txt



# # git最新バージョンをインストール
# ARG GIT_VERSION=2.38.1
# # git最新バージョンをインストールするための必要なライブラリ
# RUN apt-get install -y gettext \
#     libcurl4-gnutls-dev \
#     libexpat1-dev \
#     libghc-zlib-dev \
#     libssl-dev \
#     make \
#     wget
    
# # Gitをソースからコンパイルしてインストール
# RUN wget https://github.com/git/git/archive/v${GIT_VERSION}.tar.gz \
#     && tar -xzf v${GIT_VERSION}.tar.gz \
#     && cd git-* \
#     && make prefix=/usr/local all \
#     && make prefix=/usr/local install