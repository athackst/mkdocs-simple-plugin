FROM python:3.11

RUN apt-get update && apt-get -y install --no-install-recommends \
  bats \
  gcc \
  git \
  git-lfs \
  libcairo2-dev \
  libffi-dev \
  libfreetype6-dev \
  libjpeg-dev \
  libpng-dev \
  libz-dev \
  python3-pip \
  vim

WORKDIR /tmp
COPY mkdocs_simple_plugin mkdocs_simple_plugin
COPY README.md README.md
COPY VERSION VERSION
COPY setup.py setup.py
COPY pyproject.toml pyproject.toml

RUN pip install --upgrade pip \
 && pip install --no-cache-dir . \
 && pip install --no-cache-dir mkdocs-material mike pillow cairosvg

WORKDIR /docs

EXPOSE 8000

RUN mkdir -p /home/mkdocs && chmod 777 /home/mkdocs
ENV HOME=/home/mkdocs
ENV PATH=/home/mkdocs/.local/bin:${PATH}

COPY docker/deploy.sh /usr/local/bin/
COPY docker/entrypoint.sh /usr/local/bin/
ENTRYPOINT ["entrypoint.sh"]

CMD ["mkdocs_simple_gen", "--serve", "--", "-a", "0.0.0.0:8000", "--dirtyreload"]
