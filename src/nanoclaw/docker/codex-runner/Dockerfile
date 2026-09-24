ARG NODE_IMAGE=node:22-bookworm-slim
FROM ${NODE_IMAGE}

LABEL org.opencontainers.image.title="nanoclaw Codex runner"
LABEL org.opencontainers.image.description="OpenAI Codex CLI image extended with the nanoclaw Docker runner adapter"

USER root

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        git \
        ripgrep \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

ARG NPM_CONFIG_REGISTRY=
RUN if [ -n "${NPM_CONFIG_REGISTRY}" ]; then npm config set registry "${NPM_CONFIG_REGISTRY}"; fi \
    && npm install -g @openai/codex

RUN python3 -m pip install --break-system-packages --no-cache-dir \
        beautifulsoup4 \
        cryptography \
        fpdf \
        httpx \
        numpy \
        openai \
        openpyxl \
        pandas \
        pillow \
        PyYAML \
        reportlab \
        requests

RUN install -d -m 0755 -o node -g node /opt/nanoclaw-adapter /workspace /output /state

COPY --chown=node:node --chmod=0755 adapter/run_task /opt/nanoclaw-adapter/run_task
COPY --chown=node:node --chmod=0644 adapter/run_task.py /opt/nanoclaw-adapter/run_task.py

USER node
WORKDIR /workspace

HEALTHCHECK NONE

CMD ["/opt/nanoclaw-adapter/run_task", "--task", "/input/task.md", "--resolved-task", "/input/resolved_task.json", "--workspace", "/workspace", "--output", "/output", "--state", "/state"]
