#!/usr/bin/env bash
set -euo pipefail

fail=0
if [[ ! -f /sys/fs/cgroup/cgroup.controllers ]] || [[ "$(stat -fc %T /sys/fs/cgroup)" != "cgroup2fs" ]]; then
  echo "FAIL cgroup_mode: unified cgroup v2 is not active"
  exit 3
fi

uid="$(id -u)"
user_slice="/sys/fs/cgroup/user.slice/user-${uid}.slice"
manager_scope="${user_slice}/user@${uid}.service"
control_file="${manager_scope}/cgroup.subtree_control"

echo "PASS cgroup_mode: unified v2"
echo "INFO root_controllers: $(tr '\n' ' ' < /sys/fs/cgroup/cgroup.controllers)"
if [[ ! -r "${control_file}" ]]; then
  echo "FAIL delegation: cannot read ${control_file}"
  exit 3
fi

delegated="$(tr '\n' ' ' < "${control_file}")"
echo "INFO delegated_controllers: ${delegated}"
for controller in memory cpu io; do
  if grep -qw "${controller}" "${control_file}"; then
    echo "PASS controller_${controller}: delegated"
  else
    echo "FAIL controller_${controller}: not delegated"
    fail=1
  fi
done

home_source="$(findmnt -n -o SOURCE --target "${HOME}")"
home_type="$(findmnt -n -o FSTYPE --target "${HOME}")"
echo "INFO home_mount: source=${home_source} fstype=${home_type}"
if [[ "${HOME}" == /mnt/* ]] || [[ "${home_type}" == "9p" ]] || [[ "${home_type}" == "drvfs" ]]; then
  echo "FAIL io_workspace: HOME is not on the WSL ext4 filesystem"
  fail=1
elif [[ "${home_source}" != /dev/* ]] || [[ ! -b "${home_source}" ]]; then
  echo "FAIL io_workspace: HOME source is not a directly addressable block device"
  fail=1
else
  echo "PASS io_workspace: HOME is backed by block device ${home_source}"
fi

if (( fail != 0 )); then
  echo "VERDICT: delegation is not ready; model-bearing runs remain blocked"
  exit 3
fi
echo "VERDICT: controllers are delegated; cap probes are still required before a model-bearing run"
