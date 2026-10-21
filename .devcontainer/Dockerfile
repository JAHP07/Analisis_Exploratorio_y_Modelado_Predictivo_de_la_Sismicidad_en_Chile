FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

# Desactivar únicamente la fuente APT de Yarn con
# clave GPG inválida. Mantener la verificación de
# firmas de los repositorios Debian.
RUN set -eu; \
    for file in /etc/apt/sources.list /etc/apt/sources.list.d/*.list; do \
        if [ -f "$file" ]; then \
            sed -i '/dl\.yarnpkg\.com/d' "$file"; \
        fi; \
    done; \
    for file in /etc/apt/sources.list.d/*.sources; do \
        if [ -f "$file" ] && grep -q 'dl.yarnpkg.com' "$file"; then \
            rm "$file"; \
        fi; \
    done
