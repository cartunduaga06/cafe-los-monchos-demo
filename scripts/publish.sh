#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -n "$(git status --porcelain)" ]]; then
  echo "Hay cambios sin commit. Revisa y guarda un commit antes de publicar." >&2
  exit 1
fi
branch=$(git symbolic-ref --short HEAD)
if [[ "$branch" == main ]]; then
  echo "Trabaja y publica desde develop o una rama de cambios." >&2
  exit 1
fi
git fetch origin main
git merge-base --is-ancestor origin/main HEAD || {
  echo "Integra origin/main en tu rama y resuelve los conflictos antes de publicar." >&2
  exit 1
}
make build
if git diff --quiet origin/main HEAD; then
  echo "No hay cambios nuevos para publicar."
  exit 0
fi
git push -u origin "$branch"
# GitHub rejects this push if main advanced meanwhile; never force-push.
git push origin HEAD:refs/heads/main
printf 'Enviado a main. Consulta el despliegue con: gh run list --workflow pages.yml\n'
