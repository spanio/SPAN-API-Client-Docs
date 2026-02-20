#!/bin/bash
# Shared utilities for SPAN API credential management (Bash version)

# Default paths (can be overridden by environment variables)
SPAN_AUTH_FILE_DEFAULT="${HOME}/.span-auth.json"
SPAN_CA_CERT_DIR="${SPAN_CA_CERT_DIR:-${HOME}/.span-ca-certs}"

# Get the credential file path
get_auth_file_path() {
    echo "${SPAN_AUTH_FILE:-$SPAN_AUTH_FILE_DEFAULT}"
}

# Check if file has secure permissions
check_file_permissions() {
    local path="$1"
    if [[ ! -f "$path" ]]; then
        return 0
    fi

    local perms
    perms=$(stat -f "%Lp" "$path" 2>/dev/null || stat -c "%a" "$path" 2>/dev/null)

    if [[ "$perms" != "600" ]]; then
        echo "Warning: $path has insecure permissions ($perms). Run 'chmod 600 $path' to fix." >&2
        return 1
    fi
    return 0
}

# Load a value from the auth file using jq
# Usage: load_auth_value ".default_panel"
load_auth_value() {
    local jq_path="$1"
    local auth_file
    auth_file=$(get_auth_file_path)

    if [[ ! -f "$auth_file" ]]; then
        echo ""
        return 1
    fi

    check_file_permissions "$auth_file"
    jq -r "$jq_path // empty" "$auth_file"
}

# Get the default panel serial number
get_default_panel() {
    local default
    default=$(load_auth_value ".default_panel")

    if [[ -n "$default" ]]; then
        echo "$default"
        return 0
    fi

    # Check if there's only one panel
    local panel_count
    panel_count=$(load_auth_value ".panels | keys | length")

    if [[ "$panel_count" == "1" ]]; then
        load_auth_value ".panels | keys[0]"
        return 0
    fi

    return 1
}

# Get panel credentials
# Usage: get_panel_hostname "serial-number"
get_panel_hostname() {
    local serial="$1"
    load_auth_value ".panels[\"$serial\"].hostname"
}

get_panel_password() {
    local serial="$1"
    load_auth_value ".panels[\"$serial\"].ebus_broker_password"
}

get_panel_access_token() {
    local serial="$1"
    load_auth_value ".panels[\"$serial\"].access_token"
}

# Resolve panel serial number (use provided or get default)
resolve_panel_serial() {
    local provided="$1"

    if [[ -n "$provided" ]]; then
        echo "$provided"
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
        rm -f "$cert_path"
    fi

    # Create directory if needed
    mkdir -p "$SPAN_CA_CERT_DIR"

    # Download certificate
    echo "Downloading CA certificate for $serial..." >&2
    if curl -sf "http://${hostname}/api/v2/certificate/ca" -o "$cert_path"; then
        echo "Certificate saved to $cert_path" >&2
        echo "$cert_path"
        return 0
    else
        echo "Error: Failed to download CA certificate from $hostname" >&2
        return 1
    fi
}
