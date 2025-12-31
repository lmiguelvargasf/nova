#!/usr/bin/env bash
set -euo pipefail

RULES_DIR=".rules"
CURSOR_RULES_DIR=".cursor/rules"
AGENT_RULES_DIR=".agent/rules"

# Ensure output directories exist
mkdir -p "$CURSOR_RULES_DIR"
mkdir -p "$AGENT_RULES_DIR"

# Function to trim whitespace from start and end of a file (or stdin)
trim() {
    awk '
    /^[[:space:]]*$/ {
        if (printed) {
            blank_lines = blank_lines $0 "\n"
        }
        next
    }
    {
        if (blank_lines) {
            printf "%s", blank_lines
            blank_lines = ""
        }
        print $0
        printed = 1
    }
    '
}

# Main generation loop
for rule_file in "$RULES_DIR"/*.md; do
    [ -e "$rule_file" ] || continue

    filename=$(basename "$rule_file")
    rule_name="${filename%.md}"

    # Temporary files for this iteration
    tmp_cursor_meta=$(mktemp)
    tmp_ag_meta=$(mktemp)
    tmp_body=$(mktemp)

    # Process the file with awk
    # We output to 3 file descriptors.
    # To do this in pure awk inside bash, we can write to distinct files using filenames passed in vars.

    awk -v cursor_out="$tmp_cursor_meta" \
        -v ag_out="$tmp_ag_meta" \
        -v body_out="$tmp_body" '
    BEGIN {
        in_cursor = 0
        in_ag = 0
        found_cursor = 0
        found_ag = 0
    }
    /^<!-- cursor:/ {
        in_cursor = 1
        found_cursor = 1
        next
    }
    /^<!-- antigravity:/ {
        in_ag = 1
        found_ag = 1
        next
    }
    /^-->$/ {
        if (in_cursor) { in_cursor = 0; next }
        if (in_ag) { in_ag = 0; next }
    }
    {
        if (in_cursor) {
            print > cursor_out
        } else if (in_ag) {
            print > ag_out
        } else {
            print > body_out
        }
    }
    END {
        if (found_cursor == 0) exit 1
        if (found_ag == 0) exit 2
    }
    ' "$rule_file"

    rc=$?

    if [ $rc -eq 1 ]; then
        echo "ERROR: Missing 'cursor' metadata block in $filename"
        rm -f "$tmp_cursor_meta" "$tmp_ag_meta" "$tmp_body"
        exit 1
    elif [ $rc -eq 2 ]; then
        echo "ERROR: Missing 'antigravity' metadata block in $filename"
        rm -f "$tmp_cursor_meta" "$tmp_ag_meta" "$tmp_body"
        exit 1
    elif [ $rc -ne 0 ]; then
        echo "ERROR: Failed to parse $filename"
        rm -f "$tmp_cursor_meta" "$tmp_ag_meta" "$tmp_body"
        exit 1
    fi

    # Prepare Body (trim it)
    # We need to read tmp_body, trim it, and store it.
    final_body=$(cat "$tmp_body" | trim)

    # 1. Generate Cursor Rule
    cursor_rule_dir="$CURSOR_RULES_DIR/$rule_name"
    mkdir -p "$cursor_rule_dir"
    {
        echo "---"
        cat "$tmp_cursor_meta" | trim
        echo ""
        echo "---"
        echo ""
        echo "$final_body"
    } > "$cursor_rule_dir/RULE.md"

    # 2. Generate Antigravity Rule
    {
        echo "---"
        cat "$tmp_ag_meta" | trim
        echo ""
        echo "---"
        echo ""
        echo "$final_body"
    } > "$AGENT_RULES_DIR/$filename"

    # Cleanup tmp files
    rm -f "$tmp_cursor_meta" "$tmp_ag_meta" "$tmp_body"

    # echo "Generated rules for $filename"
done

echo "Rules generated successfully."
