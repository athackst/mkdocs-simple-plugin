FROM python:3.8.1-alpine3.11

WORKDIR /tmp
COPY mkdocs_simple_plugin mkdocs_simple_plugin
COPY README.md README.md
COPY setup.py setup.py

RUN \
  apk add --no-cache \
    git \
    git-fast-import \
    openssh \
  && apk add --no-cache --virtual .build gcc musl-dev \
  && pip install --no-cache-dir . \
  && apk del .build gcc musl-dev \
  && rm -rf /tmp/*

WORKDIR /docs

EXPOSE 8000

ENTRYPOINT ["mkdocs_simple_gen"]

CMD ["--install", "--serve"]
