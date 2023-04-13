FROM python:3


RUN apt-get update && \
    apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:ja
ENV LC_ALL=ja_JP.UTF-8
ENV TZ=JST-9
ENV TERM=xterm

RUN apt-get install -y vim \
    less \
    poppler-utils \
    poppler-data \
    oathtool

WORKDIR /workspace/
COPY requirements.txt .
COPY set-up-chdriver.sh .
RUN pip install --upgrade pip setuptools && \
    pip install -r ./requirements.txt && \
    chmod +x ./set-up-chdriver.sh && \
    sh ./set-up-chdriver.sh

ARG UID
ARG GID
ARG USERNAME
ARG GROUPNAME
# RUN groupadd -g ${GID} ${GROUPNAME} -f && \
RUN useradd -m -s /bin/bash -u ${UID} -g ${GID} ${USERNAME}
USER ${USERNAME}

# chromedriver用
# RUN apt-get install -y libglib2.0-0=2.50.3-2 \
#     libnss3=2:3.26.2-1.1+deb9u1 \
#     libgconf-2-4=3.2.6-4+b1 \
#     libfontconfig1=2.11.0-6.7+b1



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