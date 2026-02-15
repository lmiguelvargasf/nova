#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
STATE_DIR="${ROOT_DIR}/.nova"
STATE_FILE="${STATE_DIR}/template-prune-state.toml"

info() { printf "\033[1;34m[template-prune]\033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m[template-prune]\033[0m %s\n" "$*"; }
err() { printf "\033[1;31m[template-prune]\033[0m %s\n" "$*" >&2; }
die() { err "$*"; exit 1; }

ensure_state_file() {
  mkdir -p "${STATE_DIR}"
  if [[ -f "${STATE_FILE}" ]]; then
    return 0
  fi

  cat > "${STATE_FILE}" <<'STATE'
version = 1
applied_profiles = ""
terminal_profile = ""
has_rest = true
has_graphql = true
has_frontend = true
has_ios = true
has_celery = true
has_redis = true
STATE
}

read_state_raw() {
  local key="$1"
  awk -F' = ' -v key="$key" '$1 == key {print $2}' "${STATE_FILE}" | tail -n1
}

read_state_string() {
  local key="$1"
  local default="${2:-}"
  local raw
  raw="$(read_state_raw "$key")"
  if [[ -z "${raw}" ]]; then
    printf "%s" "$default"
    return 0
  fi
  raw="${raw#\"}"
  raw="${raw%\"}"
  printf "%s" "$raw"
}

read_state_bool() {
  local key="$1"
  local default="${2:-false}"
  local raw
  raw="$(read_state_raw "$key")"
  if [[ -z "${raw}" ]]; then
    printf "%s" "$default"
    return 0
  fi
  if [[ "${raw}" == "true" || "${raw}" == "false" ]]; then
    printf "%s" "$raw"
    return 0
  fi
  printf "%s" "$default"
}

set_state_raw() {
  local key="$1"
  local value="$2"
  local tmp
  tmp="$(mktemp)"
  awk -F' = ' -v key="$key" -v value="$value" '
    BEGIN {updated=0}
    $1 == key {print key " = " value; updated=1; next}
    {print $0}
    END {if (!updated) print key " = " value}
  ' "${STATE_FILE}" > "${tmp}"
  mv "${tmp}" "${STATE_FILE}"
}

set_state_string() {
  local key="$1"
  local value="$2"
  set_state_raw "$key" "\"${value}\""
}

set_state_bool() {
  local key="$1"
  local value="$2"
  if [[ "${value}" != "true" && "${value}" != "false" ]]; then
    die "Invalid boolean for ${key}: ${value}"
  fi
  set_state_raw "$key" "$value"
}

has_profile_applied() {
  local profile="$1"
  local applied
  applied="$(read_state_string "applied_profiles" "")"
  [[ ",${applied}," == *",${profile},"* ]]
}

append_profile() {
  local profile="$1"
  local applied
  applied="$(read_state_string "applied_profiles" "")"
  if [[ -z "${applied}" ]]; then
    set_state_string "applied_profiles" "${profile}"
    return 0
  fi
  if [[ ",${applied}," == *",${profile},"* ]]; then
    return 0
  fi
  set_state_string "applied_profiles" "${applied},${profile}"
}

ensure_clean_git_tree() {
  local status
  status="$(git -C "${ROOT_DIR}" status --porcelain)"
  if [[ -n "${status}" ]]; then
    die "Working tree is not clean. Commit/stash changes before pruning."
  fi
}

ensure_not_main_branch() {
  local branch
  branch="$(git -C "${ROOT_DIR}" branch --show-current)"
  if [[ "${branch}" == "main" ]]; then
    die "Refusing to run on main branch. Create a feature branch first."
  fi
}

require_confirmation() {
  local profile="$1"
  local summary_file="$2"

  info "Profile: ${profile}"
  info "Planned changes:"
  sed 's/^/  - /' "${summary_file}"

  if [[ "${CONFIRM:-}" == "yes" ]]; then
    info "CONFIRM=yes provided, skipping interactive confirmation."
    return 0
  fi

  printf "\nType 'yes' to continue: "
  local answer
  read -r answer
  if [[ "${answer}" != "yes" ]]; then
    die "Aborted by user."
  fi
}

remove_path() {
  local rel="$1"
  local abs="${ROOT_DIR}/${rel}"
  if [[ ! -e "${abs}" ]]; then
    info "No-op (missing): ${rel}"
    return 0
  fi
  rm -rf "${abs}"
  info "Removed: ${rel}"
}

copy_template_file() {
  local profile="$1"
  local rel="$2"
  local src="${ROOT_DIR}/scripts/template-prune/templates/${profile}/${rel}"
  local dst="${ROOT_DIR}/${rel}"

  [[ -f "${src}" ]] || die "Template not found for ${profile}: ${rel}"
  mkdir -p "$(dirname "${dst}")"
  cp "${src}" "${dst}"
  info "Updated from template: ${rel}"
}

remove_root_task_block() {
  local rel_file="$1"
  local task_name="$2"
  local file="${ROOT_DIR}/${rel_file}"
  [[ -f "${file}" ]] || return 0

  local tmp
  tmp="$(mktemp)"
  awk -v task="  ${task_name}:" '
    BEGIN {skip=0}
    {
      if (!skip && $0 == task) {
        skip=1
        next
      }
      if (skip) {
        if ($0 ~ /^  [a-zA-Z0-9:_-]+:[[:space:]]*$/) {
          skip=0
        } else {
          next
        }
      }
      print
    }
  ' "${file}" > "${tmp}"
  mv "${tmp}" "${file}"
  info "Removed task block '${task_name}' from ${rel_file}"
}

replace_in_file() {
  local rel_file="$1"
  local from="$2"
  local to="$3"
  local file="${ROOT_DIR}/${rel_file}"
  [[ -f "${file}" ]] || return 0
  perl -0pi -e "s/${from}/${to}/g" "${file}"
}

remove_regex_lines() {
  local rel_file="$1"
  local regex="$2"
  local file="${ROOT_DIR}/${rel_file}"
  [[ -f "${file}" ]] || return 0

  local tmp
  tmp="$(mktemp)"
  awk -v r="$regex" '$0 !~ r {print}' "${file}" > "${tmp}"
  mv "${tmp}" "${file}"
}

run_task() {
  local args=("$@")
  (cd "${ROOT_DIR}" && task "${args[@]}")
}
