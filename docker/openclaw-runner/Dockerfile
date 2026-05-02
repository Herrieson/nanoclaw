ARG OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:latest
FROM ${OPENCLAW_IMAGE}

ARG NPM_CONFIG_REGISTRY=
ARG NANOCLAW_OPENCLAW_PREWARM_INTERVAL=30

LABEL org.opencontainers.image.title="nanoclaw OpenClaw runner"
LABEL org.opencontainers.image.description="OpenClaw image extended with the nanoclaw Docker runner adapter"

USER root

RUN install -d -m 0755 -o node -g node /opt/nanoclaw-adapter /opt/nanoclaw-openclaw-home

USER node

RUN set -eu; \
    watcher=""; \
    cleanup_watcher() { \
      if [ -n "$watcher" ]; then \
        kill "$watcher" 2>/dev/null || true; \
        wait "$watcher" 2>/dev/null || true; \
      fi; \
    }; \
    trap cleanup_watcher EXIT; \
    if [ -n "${NPM_CONFIG_REGISTRY}" ]; then \
      npm config set registry "${NPM_CONFIG_REGISTRY}"; \
      pnpm config set registry "${NPM_CONFIG_REGISTRY}"; \
    fi; \
    echo "[nanoclaw-openclaw-prewarm] npm registry: $(npm config get registry)"; \
    echo "[nanoclaw-openclaw-prewarm] checking bundled plugin runtime deps"; \
    openclaw plugins deps --json > /tmp/openclaw-plugin-deps-before.json; \
    node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('/tmp/openclaw-plugin-deps-before.json','utf8')); console.log('[nanoclaw-openclaw-prewarm] missing deps before repair:', (data.missing||[]).length, 'installRoot:', data.installRoot);"; \
    ( \
      while true; do \
        root=/home/node/.openclaw/plugin-runtime-deps; \
        size=$(du -sh "$root" 2>/dev/null | awk '{print $1}' || true); \
        files=$(find "$root" -type f 2>/dev/null | wc -l | tr -d ' ' || true); \
        echo "[nanoclaw-openclaw-prewarm] $(date -u +%Y-%m-%dT%H:%M:%SZ) runtime_deps_size=${size:-0} files=${files:-0}"; \
        sleep "${NANOCLAW_OPENCLAW_PREWARM_INTERVAL}"; \
      done \
    ) & watcher="$!"; \
    openclaw plugins deps --repair --json > /tmp/openclaw-plugin-deps-repair.json; \
    cleanup_watcher; \
    watcher=""; \
    trap - EXIT; \
    cat /tmp/openclaw-plugin-deps-repair.json; \
    openclaw plugins deps --json > /tmp/openclaw-plugin-deps-after.json; \
    node -e "const fs=require('fs'); const data=JSON.parse(fs.readFileSync('/tmp/openclaw-plugin-deps-after.json','utf8')); const missing=(data.missing||[]).length; console.log('[nanoclaw-openclaw-prewarm] missing deps after repair:', missing); if (missing) process.exit(1);"; \
    echo "[nanoclaw-openclaw-prewarm] staging embedded agent runtime deps"; \
    node -e "const fs=require('fs'); const config={agents:{defaults:{workspace:'/tmp',model:{primary:'custom-nanoclaw-build/nanoclaw-build-prewarm'},models:{'custom-nanoclaw-build/nanoclaw-build-prewarm':{}}}},gateway:{mode:'local',auth:{mode:'token',token:'nanoclaw-build-prewarm'},port:18789,bind:'loopback',tailscale:{mode:'off',resetOnExit:false}},session:{dmScope:'per-channel-peer'},tools:{profile:'coding'},models:{mode:'merge',providers:{'custom-nanoclaw-build':{baseUrl:'http://127.0.0.1:9/v1',api:'openai-completions',apiKey:{source:'env',provider:'default',id:'CUSTOM_API_KEY'},models:[{id:'nanoclaw-build-prewarm',name:'nanoclaw build prewarm',contextWindow:4000,maxTokens:16,input:['text'],cost:{input:0,output:0,cacheRead:0,cacheWrite:0},reasoning:false}]}}}}; fs.writeFileSync('/tmp/openclaw-prewarm-config.json', JSON.stringify(config,null,2)+'\n');"; \
    trap cleanup_watcher EXIT; \
    ( \
      while true; do \
        root=/home/node/.openclaw/plugin-runtime-deps; \
        size=$(du -sh "$root" 2>/dev/null | awk '{print $1}' || true); \
        files=$(find "$root" -type f 2>/dev/null | wc -l | tr -d ' ' || true); \
        echo "[nanoclaw-openclaw-prewarm] $(date -u +%Y-%m-%dT%H:%M:%SZ) agent_runtime_deps_size=${size:-0} files=${files:-0}"; \
        sleep "${NANOCLAW_OPENCLAW_PREWARM_INTERVAL}"; \
      done \
    ) & watcher="$!"; \
    CUSTOM_API_KEY=nanoclaw-build-prewarm \
      OPENCLAW_CONFIG_PATH=/tmp/openclaw-prewarm-config.json \
      OPENCLAW_STATE_DIR=/home/node/.openclaw \
      OPENCLAW_PLUGIN_STAGE_DIR=/home/node/.openclaw/plugin-runtime-deps \
      openclaw agent --local --message "nanoclaw build dependency prewarm" --json --session-id nanoclaw-build-prewarm --timeout 1 --model custom-nanoclaw-build/nanoclaw-build-prewarm \
        > /tmp/openclaw-agent-prewarm-stdout.log \
        2> /tmp/openclaw-agent-prewarm-stderr.log || true; \
    cleanup_watcher; \
    watcher=""; \
    trap - EXIT; \
    node -e "const fs=require('fs'); const path=require('path'); const base='/home/node/.openclaw/plugin-runtime-deps'; const roots=fs.existsSync(base)?fs.readdirSync(base).filter((name)=>name.startsWith('openclaw-')).map((name)=>path.join(base,name)):[]; const required=['@mariozechner/pi-agent-core','@anthropic-ai/sdk','@google/genai','@aws-sdk/client-bedrock','@openai/codex']; const root=roots.find((candidate)=>required.every((dep)=>fs.existsSync(path.join(candidate,'node_modules',dep,'package.json')))); console.log('[nanoclaw-openclaw-prewarm] agent runtime deps root:', root||'<missing>'); if(!root){ try{ console.error(fs.readFileSync('/tmp/openclaw-agent-prewarm-stderr.log','utf8')); }catch{} process.exit(1); }"; \
    rm -f /tmp/openclaw-prewarm-config.json /tmp/openclaw-agent-prewarm-stdout.log /tmp/openclaw-agent-prewarm-stderr.log; \
    rm -f /home/node/.openclaw/openclaw.json; \
    rm -rf /home/node/.openclaw/agents /home/node/.openclaw/logs /home/node/.openclaw/tasks; \
    rm -f /tmp/openclaw-plugin-deps-before.json /tmp/openclaw-plugin-deps-repair.json /tmp/openclaw-plugin-deps-after.json; \
    cp -a /home/node/.openclaw /opt/nanoclaw-openclaw-home/.openclaw

USER root

RUN chown -R node:node /opt/nanoclaw-openclaw-home

COPY --chown=node:node --chmod=0755 adapter/run_task /opt/nanoclaw-adapter/run_task
COPY --chown=node:node --chmod=0644 adapter/run_task.mjs /opt/nanoclaw-adapter/run_task.mjs

ENV NANOCLAW_OPENCLAW_HOME_TEMPLATE=/opt/nanoclaw-openclaw-home \
    CI=true \
    NPM_CONFIG_CONFIRM_MODULES_PURGE=false \
    PNPM_CONFIG_CONFIRM_MODULES_PURGE=false \
    npm_config_confirm_modules_purge=false

USER node
WORKDIR /workspace

HEALTHCHECK NONE

CMD ["/opt/nanoclaw-adapter/run_task", "--task", "/input/task.md", "--resolved-task", "/input/resolved_task.json", "--workspace", "/workspace", "--output", "/output", "--state", "/state"]
