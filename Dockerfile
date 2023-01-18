FROM python:3.11

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && apt-get -y install --no-install-recommends bats gcc \
  git \
  git-lfs \
  python3-pip \
  libcairo2-dev \
  libfreetype6-dev \
  libffi-dev \
  libjpeg-dev \
  libpng-dev \
  libz-dev \
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

RUN git config --global --add safe.directory /docs

WORKDIR /docs

EXPOSE 8000

RUN mkdir -p /home/mkdocs && chmod 777 /home/mkdocs
ENV HOME=/home/mkdocs
ENV PATH=/home/mkdocs/.local/bin:${PATH}

COPY docker/deploy.sh /usr/local/bin/
COPY docker/entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]

CMD ["mkdocs_simple_gen", "--serve", "--", "-a", "0.0.0.0:8000", "--dirtyreload"]
