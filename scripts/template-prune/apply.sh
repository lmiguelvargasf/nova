#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/template-prune/common.sh
source "${SCRIPT_DIR}/common.sh"

usage() {
  cat <<USAGE
Usage: scripts/template-prune/apply.sh <profile>

Profiles:
  no-rest
  no-graphql
  no-ios
  rest-only
USAGE
}

require_profile() {
  local profile="$1"
  case "${profile}" in
    no-rest|no-graphql|no-ios|rest-only) ;;
    *) usage; die "Unknown profile: ${profile}" ;;
  esac
}

validate_transitions() {
  local profile="$1"
  local has_rest has_graphql terminal
  has_rest="$(read_state_bool has_rest true)"
  has_graphql="$(read_state_bool has_graphql true)"
  terminal="$(read_state_string terminal_profile "")"

  if [[ "${terminal}" == "rest-only" ]]; then
    case "${profile}" in
      rest-only|no-ios)
        info "rest-only already applied; '${profile}' is a no-op."
        exit 0
        ;;
      no-rest|no-graphql)
        die "Cannot apply '${profile}' after terminal profile 'rest-only'."
        ;;
    esac
  fi

  if [[ "${profile}" == "no-rest" && "${has_graphql}" == "false" ]]; then
    die "Cannot apply no-rest after no-graphql. Profiles are mutually exclusive."
  fi
  if [[ "${profile}" == "no-graphql" && "${has_rest}" == "false" ]]; then
    die "Cannot apply no-graphql after no-rest. Profiles are mutually exclusive."
  fi
}

show_status() {
  ensure_state_file
  cat <<STATUS
State file: ${STATE_FILE}
  applied_profiles: $(read_state_string applied_profiles "")
  terminal_profile: $(read_state_string terminal_profile "")
  has_rest: $(read_state_bool has_rest true)
  has_graphql: $(read_state_bool has_graphql true)
  has_frontend: $(read_state_bool has_frontend true)
  has_ios: $(read_state_bool has_ios true)
  has_celery: $(read_state_bool has_celery true)
  has_redis: $(read_state_bool has_redis true)
STATUS
}

apply_profile() {
  local profile="$1"
  local profile_script="${SCRIPT_DIR}/profiles/${profile}.sh"
  local summary_file

  [[ -f "${profile_script}" ]] || die "Missing profile script: ${profile_script}"

  summary_file="$(mktemp)"

  # shellcheck source=/dev/null
  source "${profile_script}"

  profile_summary "${summary_file}"
  require_confirmation "${profile}" "${summary_file}"

  profile_apply
  append_profile "${profile}"

  rm -f "${summary_file}"
}

main() {
  local profile="${1:-}"
  if [[ -z "${profile}" ]]; then
    usage
    exit 1
  fi

  ensure_state_file
  require_profile "${profile}"

  ensure_clean_git_tree
  ensure_not_main_branch
  validate_transitions "${profile}"

  if has_profile_applied "${profile}"; then
    info "Profile '${profile}' already applied. No changes required."
    show_status
    exit 0
  fi

  apply_profile "${profile}"
  show_status
}

main "$@"
