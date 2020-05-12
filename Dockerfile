FROM squidfunk/mkdocs-material:latest

WORKDIR /tmp
COPY mkdocs_simple_plugin mkdocs_simple_plugin
COPY README.md README.md
COPY setup.py setup.py

RUN  pip install --no-cache-dir . \
  && rm -rf /tmp/*

WORKDIR /docs
ENTRYPOINT []

CMD ["mkdocs", "serve", "--dev-addr=0.0.0.0:8000"]