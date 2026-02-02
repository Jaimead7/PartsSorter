# MIT License

# Copyright (c) 2025 Jaime Álvarez Díaz
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## ---------------------------- Builder Stage --------------------------- ##
FROM python:3.12.11-slim AS builder

# Set the working directory
WORKDIR /api

# Copy project files
COPY ./pyproject.toml ./pyproject.toml

# Setup uv
COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

# Install dependencies
RUN uv sync --extra postgres

## ---------------------------- Production Stage --------------------------- ##
FROM python:3.12.11-slim AS production

# Set metadata
LABEL org.opencontainers.image.title="parts-sorter-api"
LABEL org.opencontainers.image.description="Microservice for API"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/Jaimead7/PartsSorter/tree/mainBranch/api"

# Set the working directory
WORKDIR /api

# Instal opencv dependencies.
    # libgl1, libglib2.0-0 for opencv
    # curl for healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY --from=builder /api/.venv /api/.venv

# Copy project files
COPY . .

# Create folders
RUN mkdir -p /mnt/static/images/production /mnt/static/models /mnt/static/datasets /mnt/static/logs

# Set up environment variables for production
ENV PATH="/api/.venv/bin:$PATH"

# Expose the FastApi port
EXPOSE 8000

# Run the app
CMD ["python3.12", "-m", "parts_sorter_api.src.api"]