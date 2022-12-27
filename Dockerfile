FROM python:3.11-alpine

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN \
  apk add --no-cache \
  git \
  git-fast-import \
  git-lfs \
  openssh \
  cairo-dev \
  freetype-dev \
  libffi-dev \
  jpeg-dev \
  libpng-dev \
  zlib-dev \
  && apk add --no-cache --virtual .build gcc musl-dev \
  && apk add --no-cache --upgrade bash \
  && pip install --upgrade pip \
  && pip install --no-cache-dir mkdocs-material mike pillow cairosvg

WORKDIR /tmp
COPY mkdocs_simple_plugin mkdocs_simple_plugin
COPY README.md README.md
COPY VERSION VERSION
COPY setup.py setup.py
COPY pyproject.toml pyproject.toml

RUN pip install --no-cache-dir . \
  && rm -rf /tmp/*

WORKDIR /docs

EXPOSE 8000

RUN mkdir -p /home/mkdocs && chmod 777 /home/mkdocs
ENV HOME=/home/mkdocs
ENV PATH=/home/mkdocs/.local/bin:${PATH}

COPY docker/deploy.sh /usr/local/bin/
COPY docker/entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]

CMD ["mkdocs_simple_gen", "--serve", "--", "-a", "0.0.0.0:8000", "--dirtyreload"]
