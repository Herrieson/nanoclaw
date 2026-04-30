ARG HERMES_IMAGE=nousresearch/hermes-agent:latest
FROM ${HERMES_IMAGE}

LABEL org.opencontainers.image.title="nanoclaw Hermes runner"
LABEL org.opencontainers.image.description="Hermes Agent image extended with the nanoclaw Docker runner adapter"

USER root

ENV HERMES_HOME=/state

RUN install -d -m 0775 -o hermes -g hermes /state /workspace \
    && install -d -m 0755 -o hermes -g hermes /opt/nanoclaw-adapter

COPY --chown=hermes:hermes --chmod=0755 adapter/run_task /opt/nanoclaw-adapter/run_task
COPY --chown=hermes:hermes --chmod=0644 adapter/run_task.py /opt/nanoclaw-adapter/run_task.py

WORKDIR /workspace

HEALTHCHECK NONE

CMD ["/opt/nanoclaw-adapter/run_task", "--task", "/input/task.md", "--resolved-task", "/input/resolved_task.json", "--workspace", "/workspace", "--output", "/output", "--state", "/state"]
