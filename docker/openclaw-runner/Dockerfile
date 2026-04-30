ARG OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:latest
FROM ${OPENCLAW_IMAGE}

LABEL org.opencontainers.image.title="nanoclaw OpenClaw runner"
LABEL org.opencontainers.image.description="OpenClaw image extended with the nanoclaw Docker runner adapter"

USER root

RUN install -d -m 0755 -o node -g node /opt/nanoclaw-adapter

COPY --chown=node:node --chmod=0755 adapter/run_task /opt/nanoclaw-adapter/run_task
COPY --chown=node:node --chmod=0644 adapter/run_task.mjs /opt/nanoclaw-adapter/run_task.mjs

USER node
WORKDIR /workspace

HEALTHCHECK NONE

CMD ["/opt/nanoclaw-adapter/run_task", "--task", "/input/task.md", "--resolved-task", "/input/resolved_task.json", "--workspace", "/workspace", "--output", "/output", "--state", "/state"]
