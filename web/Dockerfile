# Copyright (C) 2025 Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


## ---------------------------- Builder Stage --------------------------- ##
FROM python:3.13.8-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy project files
COPY ./pyproject.toml ./pyproject.toml

# Setup uv
COPY --from=ghcr.io/astral-sh/uv:0.6.16 /uv /uvx /bin/

# Install dependencies
RUN uv sync

## ---------------------------- Production Stage --------------------------- ##
FROM python:3.13.8-alpine AS production

# Set metadata
LABEL org.opencontainers.image.title="parts-sorter-web"
LABEL org.opencontainers.image.description="Microservice for user interface"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.authors="Jaime Álvarez Díaz <alvarez.diaz.jaime1@gmail.com>"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.source="https://github.com/Jaimead7/PartsSorter/tree/mainBranch/web"

# Set the working directory
WORKDIR /app

# Copy dependencies
COPY --from=builder /app/.venv /app/.venv

# Copy project files
COPY . .

# Set up environment variables for production
ENV PATH="/app/.venv/bin:$PATH"

# Expose the FastApi port
EXPOSE 5000

# Run the app
CMD ["python3.13", "-m", "app.app"]