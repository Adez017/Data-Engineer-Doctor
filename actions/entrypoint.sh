#!/usr/bin/env bash
#
# Entry point for the reusable Data Engineer Doctor GitHub Action.
# Inputs arrive as DEDOC_* environment variables (see action.yml) so that no
# untrusted value is ever interpolated directly into the script.
#
# Exit codes:
#   0  success (or a finding that policy does not fail on)
#   1  fail-on policy triggered
#   2  usage error (no input files matched)

set -euo pipefail

input_path="${DEDOC_INPUT_PATH:-}"
format="${DEDOC_FORMAT:-markdown}"
output="${DEDOC_OUTPUT:-}"
fail_on="${DEDOC_FAIL_ON:-never}"
color="${DEDOC_COLOR:-never}"
diagnoses_path="${DEDOC_DIAGNOSES_PATH:-}"

if [ -z "${input_path}" ]; then
  echo "::error::dedoc: input 'path' is required"
  exit 2
fi

tmpdir="$(mktemp -d)"
trap 'rm -rf "${tmpdir}"' EXIT

collect_files() {
  local target="$1"
  if [ -d "${target}" ]; then
    find "${target}" -type f | sort
  else
    # Expand a glob (or pass through a single file path). Intentional word split.
    local candidate
    # shellcheck disable=SC2086
    for candidate in ${target}; do
      if [ -f "${candidate}" ]; then
        printf '%s\n' "${candidate}"
      fi
    done
  fi
}

mapfile -t files < <(collect_files "${input_path}")
if [ "${#files[@]}" -eq 0 ]; then
  echo "::error::dedoc: no input files matched '${input_path}'"
  exit 2
fi

summary_target="${output}"
if [ -z "${summary_target}" ] && [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  summary_target="${GITHUB_STEP_SUMMARY}"
fi

diag_args=(--format "${format}" --color "${color}")
if [ -n "${diagnoses_path}" ]; then
  diag_args+=(--diagnoses "${diagnoses_path}")
fi

json_args=(--format json)
if [ -n "${diagnoses_path}" ]; then
  json_args+=(--diagnoses "${diagnoses_path}")
fi

saw_diagnosed=0
saw_error=0
index=0

# The JSON pass is only needed to detect status (fail-on=diagnosed) or to render
# the report itself (format=json); avoid a second run otherwise.
need_status=0
if [ "${format}" = "json" ] || [ "${fail_on}" = "diagnosed" ]; then
  need_status=1
fi

for file in "${files[@]}"; do
  index=$((index + 1))
  echo "::group::dedoc diagnose ${file}"
  json_file="${tmpdir}/report-${index}.json"
  json_rc=0
  status=""
  if [ "${need_status}" -eq 1 ]; then
    set +e
    dedoc diagnose "${file}" "${json_args[@]}" > "${json_file}"
    json_rc=$?
    set -e
    if [ "${json_rc}" -eq 0 ]; then
      status="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "${json_file}")"
    fi
  fi

  display=""
  display_rc=0
  if [ "${format}" = "json" ]; then
    display="$(cat "${json_file}")"
  else
    set +e
    display="$(dedoc diagnose "${file}" "${diag_args[@]}")"
    display_rc=$?
    set -e
  fi
  rc="${json_rc}"
  [ "${format}" != "json" ] && rc="${display_rc}"

  if [ -n "${summary_target}" ]; then
    {
      echo "### \`${file}\`"
      echo
      echo "${display}"
      echo
    } >> "${summary_target}"
    echo "${display}"
  else
    echo "${display}"
  fi

  case "${rc}" in
    0) : ;;
    1)
      saw_error=1
      echo "::error::dedoc: ${file} could not be parsed (input error)"
      ;;
    *)
      saw_error=1
      echo "::error::dedoc: ${file} failed with exit code ${rc}"
      ;;
  esac

  if [ "${status}" = "diagnosed" ]; then
    saw_diagnosed=1
  fi
  echo "::endgroup::"
done

exit_code=0
case "${fail_on}" in
  never) : ;;
  diagnosed)
    if [ "${saw_diagnosed}" -eq 1 ]; then
      exit_code=1
      echo "::error::dedoc: at least one input was diagnosed (fail-on=diagnosed)"
    fi
    ;;
  error)
    if [ "${saw_error}" -eq 1 ]; then
      exit_code=1
      echo "::error::dedoc: at least one input failed to parse (fail-on=error)"
    fi
    ;;
  *)
    echo "::warning::dedoc: unknown fail-on value '${fail_on}'; treating as 'never'"
    ;;
esac

if [ "${need_status}" -eq 1 ]; then
  echo "dedoc: diagnosed ${saw_diagnosed} of ${#files[@]} input file(s)"
else
  echo "dedoc: processed ${#files[@]} input file(s)"
fi
exit "${exit_code}"
