#!/bin/bash
# Shared utilities for SPAN API credential management (Bash version)

# Default paths (can be overridden by environment variables)
SPAN_AUTH_FILE_DEFAULT="${HOME}/.span-auth.json"
SPAN_CA_CERT_DIR="${SPAN_CA_CERT_DIR:-${HOME}/.span-ca-certs}"

# Get the credential file path
get_auth_file_path() {
    echo "${SPAN_AUTH_FILE:-$SPAN_AUTH_FILE_DEFAULT}"
}

# Warn if the file is accessible by group or others (mode & 077)
check_file_permissions() {
    local path="$1"
    if [[ ! -f "$path" ]]; then
        return 0
    fi

    local perms
    perms=$(stat -c "%a" "$path" 2>/dev/null) || perms=$(stat -f "%Lp" "$path" 2>/dev/null) || perms=""
    if [[ ! "$perms" =~ ^[0-7]+$ ]]; then
        echo "Warning: could not read permissions of $path; skipping permission check" >&2
        return 0
    fi

    if (( 8#$perms & 8#077 )); then
        echo "Warning: $path has insecure permissions ($perms). Run 'chmod 600 $path' to fix." >&2
        return 1
    fi
    return 0
}

# Lowercase a panel serial number
normalize_serial() {
    printf '%s\n' "$1" | tr '[:upper:]' '[:lower:]'
}

# Load a value from the auth file using jq; extra arguments go to jq
# Usage: load_auth_value ".default_panel"
#        load_auth_value '.panels[$s]' --arg s "$serial"
load_auth_value() {
    local jq_path="$1"
    shift
    local auth_file
    auth_file=$(get_auth_file_path)

    if [[ ! -f "$auth_file" ]]; then
        echo ""
        return 1
    fi

    check_file_permissions "$auth_file"
    jq -r "$@" "$jq_path // empty" "$auth_file"
}

# Get the default panel serial number
get_default_panel() {
    local default
    default=$(load_auth_value ".default_panel")

    if [[ -n "$default" ]]; then
        normalize_serial "$default"
        return 0
    fi

    # Check if there's only one panel
    local panel_count
    panel_count=$(load_auth_value ".panels | keys | length")

    if [[ "$panel_count" == "1" ]]; then
        normalize_serial "$(load_auth_value ".panels | keys[0]")"
        return 0
    fi

    return 1
}

# Get a field of a panel's credentials, matching the serial case-insensitively
# Usage: get_panel_field "serial-number" "hostname"
get_panel_field() {
    load_auth_value \
        '[.panels // {} | to_entries[] | select(.key | ascii_downcase == ($s | ascii_downcase)) | .value[$f]][0]' \
        --arg s "$1" --arg f "$2"
}

get_panel_hostname() {
    get_panel_field "$1" hostname
}

get_panel_password() {
    get_panel_field "$1" ebus_broker_password
}

get_panel_access_token() {
    get_panel_field "$1" access_token
}

# Explain an HTTP 403 and how to obtain a full-privilege token
print_reduced_privilege_hint() {
    local serial="$1"
    local remedy
    if [[ -n "$(get_panel_field "$serial" hop_passphrase)" ]]; then
        remedy="'span-auth refresh $serial' (uses the stored hopPassphrase) or 'span-auth setup --full $serial'"
    else
        remedy="'span-auth setup --full $serial' or 'span-auth setup -p PASSPHRASE $serial'"
    fi
    echo "Hint: if the token for $serial is reduced-privilege (registered by proof of proximity)," >&2
    echo "registering with the hopPassphrase gives a full-privilege token: $remedy" >&2
}

# Resolve panel serial number (use provided or get default)
resolve_panel_serial() {
    local provided="$1"

    if [[ -n "$provided" ]]; then
        normalize_serial "$provided"
        return 0
    fi

    local default
    default=$(get_default_panel)

    if [[ -z "$default" ]]; then
        echo "Error: No panel specified and no default panel configured." >&2
        echo "Run 'span-auth setup' to configure credentials or specify -u SERIAL." >&2
        return 1
    fi

    echo "$default"
}

# Check if a certificate is expired or expiring within 1 day
is_cert_expired() {
    local cert_path="$1"

    if [[ ! -f "$cert_path" ]]; then
        return 0  # No cert = treat as expired
    fi

    # Use openssl to check if cert expires within 86400 seconds (1 day)
    if openssl x509 -in "$cert_path" -checkend 86400 -noout >/dev/null 2>&1; then
        return 1  # Not expired (exit code 1 = false in shell)
    else
        return 0  # Expired or expiring soon (exit code 0 = true in shell)
    fi
}

# Download a panel's CA certificate to dest, replacing dest only with a PEM certificate
# Usage: download_ca_cert "hostname" "dest"
download_ca_cert() {
    local hostname="$1"
    local dest="$2"
    local tmp
    tmp=$(mktemp "$(dirname "$dest")/.$(basename "$dest").XXXXXX") || return 1

    if ! curl -sf --connect-timeout 5 --max-time 15 "http://${hostname}/api/v2/certificate/ca" -o "$tmp"; then
        rm -f "$tmp"
        echo "Error: could not download the CA certificate from ${hostname}" >&2
        return 1
    fi
    if ! grep -q -e '-----BEGIN CERTIFICATE-----' "$tmp"; then
        rm -f "$tmp"
        echo "Error: response from ${hostname} is not a PEM certificate" >&2
        return 1
    fi
    chmod 644 "$tmp" && mv -f "$tmp" "$dest" || { rm -f "$tmp"; return 1; }
}

# Get or download CA certificate
ensure_ca_cert() {
    local serial="$1"
    local hostname="$2"
    local cert_path="${SPAN_CA_CERT_DIR}/${serial}.crt"

    # Check if cert exists and is not expired
    if [[ -f "$cert_path" ]]; then
        if ! is_cert_expired "$cert_path"; then
            echo "$cert_path"
            return 0
        fi
        echo "CA certificate for $serial is expired, re-downloading..." >&2
    fi

    # Create directory if needed
    mkdir -p "$SPAN_CA_CERT_DIR"

    echo "Downloading CA certificate for $serial..." >&2
    download_ca_cert "$hostname" "$cert_path" || return 1
    echo "Certificate saved to $cert_path" >&2
    echo "$cert_path"
}
