FROM python:3.11-slim

WORKDIR /workspace

# Copy only pyproject.toml to install dependencies
COPY pyproject.toml /tmp/pyproject.toml

RUN pip install --upgrade pip && \
    cd /tmp && \
    pip install .[dev] && \
    rm -rf /tmp/*

# Files will be mounted at /workspace
CMD ["./reformat/reformat.sh"]
