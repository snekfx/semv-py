#!/bin/bash
# validate-docs.sh - Documentation validation for SEMV Python Meta Process v2
# Silent success, noisy failure validation
# Only output problems - hide successful validations

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

missing=()
warnings=()

current_time=$(date +%s)
one_week=$((7 * 24 * 60 * 60))
one_month=$((30 * 24 * 60 * 60))
two_weeks=$((14 * 24 * 60 * 60))

get_mtime() {
    stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo ""
}

check_exists() {
    local path="$1"
    local label="$2"
    if [[ ! -e "$path" ]]; then
        missing+=("❌ missing: $label ($path)")
        return 1
    fi
    return 0
}

check_file_age() {
    local path="$1"
    local label="$2"
    local threshold="$3"
    local mtime
    mtime=$(get_mtime "$path")
    if [[ -z "$mtime" ]]; then
        warnings+=("⚠️ cannot read timestamp for $label ($path)")
        return
    fi
    local age=$((current_time - mtime))
    if (( age > threshold )); then
        local days=$((age / 86400))
        if [[ $threshold -eq $one_week ]]; then
            missing+=("❌ critical doc stale: $label ($path) - ${days}d old (max: 7d)")
        else
            warnings+=("⚠️ stale: $label ($path) last updated ${days}d ago")
        fi
    fi
}

# Required directories
check_exists "docs/procs" "process directory"
check_exists "docs/ref" "reference directory"
check_exists ".analysis" "analysis directory"
check_exists "bin" "scripts directory"

# Ensure no legacy process docs linger at the repo root
for legacy in ROADMAP.txt TASKS.txt IDEAS.txt TODO.md; do
    if [[ -e "$legacy" ]]; then
        warnings+=("⚠️ legacy file not migrated: $legacy (should be in docs/)")
    fi
done

# Critical process docs (7-day freshness - errors if stale)
critical_docs=(
    "START.txt:START entry point"
    "docs/procs/PROCESS.md:workflow guide"
    "docs/procs/CONTINUE.md:session log"
    "docs/procs/QUICK_REF.md:quick reference"
    "docs/procs/SPRINT.md:active sprint plan"
)

for entry in "${critical_docs[@]}"; do
    IFS=":" read -r path label <<<"$entry"
    if check_exists "$path" "$label"; then
        check_file_age "$path" "$label" "$one_week"
    fi
done

# Supporting process docs (30-day freshness - warnings if stale)
support_docs=(
    "docs/procs/TASKS.md:task backlog"
    "docs/procs/ROADMAP.md:roadmap"
    "docs/procs/DONE.md:done log"
)

for entry in "${support_docs[@]}"; do
    IFS=":" read -r path label <<<"$entry"
    if check_exists "$path" "$label"; then
        check_file_age "$path" "$label" "$one_month"
    fi
done

# SEMV-specific reference docs that should exist
ref_docs=(
    "docs/ref/semv_concepts.md:SEMV concepts guide"
    "docs/ref/plan/semv_prd.md:product requirements"
    "docs/ref/plan/semv_python_buildout_plan.md:implementation plan"
    "docs/ref/plan/semv_roadmap.md:original roadmap"
    "docs/ref/pypi_publishing_guide.md:publishing guide"
    "README.md:project README"
    "META_PROCESS.md:Meta Process documentation"
)

for entry in "${ref_docs[@]}"; do
    IFS=":" read -r path label <<<"$entry"
    check_exists "$path" "$label" > /dev/null || true
done

# Check integration and detection directories exist and have content
if [[ -d "docs/ref/integration" ]]; then
    integration_count=$(find docs/ref/integration -name "*.md" 2>/dev/null | wc -l)
    if [[ $integration_count -eq 0 ]]; then
        warnings+=("⚠️ empty: integration directory has no .md files")
    fi
else
    missing+=("❌ missing: integration directory (docs/ref/integration/)")
fi

if [[ -d "docs/ref/detection" ]]; then
    detection_count=$(find docs/ref/detection -name "*.md" 2>/dev/null | wc -l)
    if [[ $detection_count -eq 0 ]]; then
        warnings+=("⚠️ empty: detection directory has no .md files")
    fi
else
    missing+=("❌ missing: detection directory (docs/ref/detection/)")
fi

# Check license structure
if [[ -d "docs/lics" ]]; then
    license_count=$(find docs/lics -name "*.txt" 2>/dev/null | wc -l)
    if [[ $license_count -eq 0 ]]; then
        warnings+=("⚠️ empty: license directory has no .txt files")
    fi
else
    missing+=("❌ missing: license directory (docs/lics/)")
fi

# Analysis artifacts (14-day freshness)
analysis_docs=(
    ".analysis/consolidated_wisdom.txt:consolidated wisdom"
    ".analysis/technical_debt.txt:technical debt snapshot"
)
for entry in "${analysis_docs[@]}"; do
    IFS=":" read -r path label <<<"$entry"
    if check_exists "$path" "$label"; then
        check_file_age "$path" "$label" "$two_weeks"
        if [[ ! -s "$path" ]]; then
            warnings+=("⚠️ empty: $label ($path)")
        fi
    fi
done

# Check that validate script exists and is executable
if [[ ! -x "bin/validate-docs.sh" ]]; then
    missing+=("❌ validation script not executable: bin/validate-docs.sh")
fi

# Summary and exit
total_issues=$(( ${#missing[@]} + ${#warnings[@]} ))

if (( total_issues == 0 )); then
    # Silent success - no output for healthy state
    exit 0
fi

printf '🔍 SEMV Python Meta Process v2 Documentation Validation\n'
printf '========================================================\n'

for err in "${missing[@]}"; do
    printf '%s\n' "$err"
done
for warn in "${warnings[@]}"; do
    printf '%s\n' "$warn"
done

printf '\n📊 Summary:\n'
printf '   - Errors: %d\n' "${#missing[@]}"
printf '   - Warnings: %d\n' "${#warnings[@]}"

if (( ${#missing[@]} > 0 )); then
    printf '\n❌ VALIDATION FAILED - Fix errors before proceeding\n'
    exit 1
else
    printf '\n⚠️  VALIDATION PASSED WITH WARNINGS\n'
    exit 0
fi
