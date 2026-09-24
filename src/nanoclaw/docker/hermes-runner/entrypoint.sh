#!/usr/bin/env bash
set -e

if [ "$(id -u)" = "0" ]; then
    if [ -z "${HERMES_UID:-}" ] && [ -e /output ]; then
        output_uid="$(stat -c %u /output 2>/dev/null || true)"
        if [ -n "${output_uid}" ] && [ "${output_uid}" != "0" ]; then
            export HERMES_UID="${output_uid}"
        fi
    fi
    if [ -z "${HERMES_GID:-}" ] && [ -e /output ]; then
        output_gid="$(stat -c %g /output 2>/dev/null || true)"
        if [ -n "${output_gid}" ] && [ "${output_gid}" != "0" ]; then
            export HERMES_GID="${output_gid}"
        fi
    fi

    target_uid="${HERMES_UID:-$(id -u hermes)}"
    target_gid="${HERMES_GID:-$(id -g hermes)}"
    for path in /output /workspace /state; do
        if [ -e "${path}" ]; then
            chown -R "${target_uid}:${target_gid}" "${path}" 2>/dev/null || \
                echo "Warning: could not chown ${path}; continuing" >&2
        fi
    done
fi

exec /opt/hermes/docker/entrypoint.sh "$@"
