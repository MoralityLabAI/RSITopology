#!/usr/bin/env bash
set -euo pipefail

CONFIRMATION="I_UNDERSTAND_THIS_CHANGES_SHARED_WSL"
TARGET="/etc/systemd/system/user@.service.d/delegate.conf"
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/config/wsl-user-delegate.conf"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Refusing: run as root inside the intended WSL distribution." >&2
  exit 2
fi
if [[ "${1:-}" != "--confirm-host-change" || "${2:-}" != "${CONFIRMATION}" ]]; then
  echo "Refusing without explicit confirmation." >&2
  echo "Usage: sudo $0 --confirm-host-change ${CONFIRMATION}" >&2
  exit 2
fi
if [[ ! -f /sys/fs/cgroup/cgroup.controllers ]]; then
  echo "Refusing: unified cgroup v2 is not active." >&2
  exit 3
fi
if [[ "$(stat -fc %T /sys/fs/cgroup)" != "cgroup2fs" ]]; then
  echo "Refusing: /sys/fs/cgroup is not a cgroup2 filesystem." >&2
  exit 3
fi
if [[ ! -f "${SOURCE}" ]]; then
  echo "Missing tracked delegation template: ${SOURCE}" >&2
  exit 4
fi

if [[ -e "${TARGET}" ]] && ! cmp -s "${SOURCE}" "${TARGET}"; then
  backup="${TARGET}.bak.$(date -u +%Y%m%dT%H%M%SZ)"
  cp -a -- "${TARGET}" "${backup}"
  echo "Backed up existing drop-in to ${backup}"
fi

install -D -m 0644 -- "${SOURCE}" "${TARGET}"
systemctl daemon-reload

echo "Installed ${TARGET}."
echo "No WSL restart was performed. From Windows, explicitly run: wsl.exe --shutdown"
echo "After re-entering WSL, run scripts/verify_wsl_cgroup_delegation.sh."
