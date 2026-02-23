"""Shared utilities for SPAN API credential management."""

import json
import os
import stat
import sys
from pathlib import Path
from typing import Optional


DEFAULT_AUTH_FILE = Path.home() / ".span-auth.json"
DEFAULT_CA_CERT_DIR = Path.home() / ".span-ca-certs"


def get_ca_cert_dir() -> Path:
    """Get the CA certificate directory from env var or default."""
    env_path = os.environ.get("SPAN_CA_CERT_DIR")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_CA_CERT_DIR


def get_auth_file_path() -> Path:
    """Get the credential file path from env var or default."""
    env_path = os.environ.get("SPAN_AUTH_FILE")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_AUTH_FILE


def check_file_permissions(path: Path) -> bool:
    """Check if file has secure permissions (600). Returns True if secure."""
    if not path.exists():
        return True

    mode = path.stat().st_mode
    # Check if group or others have any permissions
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        print(
            f"Warning: {path} has insecure permissions. "
            f"Run 'chmod 600 {path}' to fix.",
            file=sys.stderr
        )
        return False
    return True


def load_auth_file() -> dict:
    """Load the credential file. Returns empty structure if not found."""
    path = get_auth_file_path()

    if not path.exists():
        return {"version": 1, "default_panel": None, "panels": {}}

    check_file_permissions(path)

    with open(path, "r") as f:
        return json.load(f)


def save_auth_file(data: dict) -> None:
    """Save credentials to file with secure permissions."""
    path = get_auth_file_path()

    # Ensure parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write with restricted permissions
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    # Set permissions to 600 (owner read/write only)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def get_panel_credentials(serial_number: Optional[str] = None) -> Optional[dict]:
    """
    Get credentials for a specific panel or the default panel.

    Args:
        serial_number: Panel serial number, or None to use default

    Returns:
        Panel credentials dict, or None if not found
    """
    data = load_auth_file()

    if not data.get("panels"):
        return None

    # Determine which panel to use
    if serial_number:
        target = serial_number
    elif data.get("default_panel"):
        target = data["default_panel"]
    elif len(data["panels"]) == 1:
        # Only one panel, use it
        target = list(data["panels"].keys())[0]
    else:
        return None

    return data["panels"].get(target)


def get_default_panel() -> Optional[str]:
    """Get the default panel serial number."""
    data = load_auth_file()

    if data.get("default_panel"):
        return data["default_panel"]

    # If only one panel, it's the implicit default
    if len(data.get("panels", {})) == 1:
        return list(data["panels"].keys())[0]

    return None


def set_default_panel(serial_number: str) -> bool:
    """Set the default panel. Returns True if successful."""
    data = load_auth_file()

    if serial_number not in data.get("panels", {}):
        print(f"Error: Panel '{serial_number}' not found in credential file.", file=sys.stderr)
        return False

    data["default_panel"] = serial_number
    save_auth_file(data)
    return True


def add_panel_credentials(
    serial_number: str,
    hostname: str,
    hop_passphrase: str,
    ebus_broker_password: str,
    access_token: str,
    access_token_issued_at: int,
    set_as_default: bool = False
) -> None:
    """Add or update credentials for a panel."""
    data = load_auth_file()

    data["panels"][serial_number] = {
        "hostname": hostname,
        "hop_passphrase": hop_passphrase,
        "ebus_broker_password": ebus_broker_password,
        "access_token": access_token,
        "access_token_issued_at": access_token_issued_at
    }

    # Set as default if requested or if it's the only panel
    if set_as_default or len(data["panels"]) == 1:
        data["default_panel"] = serial_number

    save_auth_file(data)


def remove_panel_credentials(serial_number: str) -> bool:
    """Remove a panel from the credential file. Returns True if successful."""
    data = load_auth_file()

    if serial_number not in data.get("panels", {}):
        print(f"Error: Panel '{serial_number}' not found in credential file.", file=sys.stderr)
        return False

    del data["panels"][serial_number]

    # Clear default if it was this panel
    if data.get("default_panel") == serial_number:
        if data["panels"]:
            # Set first remaining panel as default
            data["default_panel"] = list(data["panels"].keys())[0]
        else:
            data["default_panel"] = None

    save_auth_file(data)
    return True


def list_panels() -> list[dict]:
    """List all configured panels with their info."""
    data = load_auth_file()
    default = data.get("default_panel")

    panels = []
    for serial, creds in data.get("panels", {}).items():
        panels.append({
            "serial_number": serial,
            "hostname": creds.get("hostname"),
            "access_token_issued_at": creds.get("access_token_issued_at"),
            "is_default": serial == default
        })

    return panels


def get_ca_cert_path(serial_number: str) -> Path:
    """Get the path to a cached CA certificate for a panel."""
    return get_ca_cert_dir() / f"{serial_number}.crt"


def is_cert_expired(cert_path: Path) -> bool:
    """Check if a certificate file is expired or expiring within 1 day."""
    import subprocess

    try:
        # Use openssl to check if cert expires within 86400 seconds (1 day)
        result = subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-checkend", "86400", "-noout"],
            capture_output=True,
            text=True
        )
        # Exit code 0 = cert is valid for at least 86400 more seconds
        # Exit code 1 = cert will expire within 86400 seconds
        return result.returncode != 0

    except Exception as e:
        print(f"Warning: Could not check certificate expiration: {e}", file=sys.stderr)
        return True  # Assume expired on error


def ensure_ca_cert(serial_number: str, hostname: str) -> Path:
    """
    Ensure CA cert exists for panel, downloading if needed.

    Also checks expiration and re-downloads if the cert is expired.

    Returns the path to the certificate file.
    """
    import requests

    cert_path = get_ca_cert_path(serial_number)

    # Check if cert exists and is not expired
    if cert_path.exists():
        if not is_cert_expired(cert_path):
            return cert_path
        print(f"CA certificate for {serial_number} is expired, re-downloading...", file=sys.stderr)
        cert_path.unlink()

    # Create directory if needed
    get_ca_cert_dir().mkdir(parents=True, exist_ok=True)

    # Download certificate
    url = f"http://{hostname}/api/v2/certificate/ca"
    response = requests.get(url)
    response.raise_for_status()

    cert_path.write_text(response.text)
    print(f"Downloaded CA certificate to {cert_path}", file=sys.stderr)

    return cert_path
