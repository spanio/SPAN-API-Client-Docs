"""Shared utilities for SPAN API credential management."""

import json
import os
import stat
import sys
import tempfile
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
    """Warn if group or others have any access (mode & 0o077). Returns True if secure."""
    if not path.exists():
        return True

    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        print(
            f"Warning: {path} has insecure permissions ({mode:o}). "
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
        data = json.load(f)

    # Serial numbers are lowercase; normalize files written with mixed-case keys
    data["panels"] = {k.lower(): v for k, v in (data.get("panels") or {}).items()}
    if data.get("default_panel"):
        data["default_panel"] = data["default_panel"].lower()
    return data


def save_auth_file(data: dict) -> None:
    """Save credentials to file with secure permissions."""
    # Resolve a symlinked credential file so the link itself is preserved
    path = Path(os.path.realpath(get_auth_file_path()))

    path.parent.mkdir(parents=True, exist_ok=True)

    data = dict(data)
    data["panels"] = {k.lower(): v for k, v in (data.get("panels") or {}).items()}
    if data.get("default_panel"):
        data["default_panel"] = data["default_panel"].lower()

    # mkstemp creates the file 0600, so the tokens are never readable by others,
    # and os.replace leaves the new file's 0600 in place of any looser old mode.
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


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
        target = serial_number.lower()
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
    serial_number = serial_number.lower()
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
    set_as_default: bool = False,
    privilege: Optional[str] = None,
    ebus_broker_username: Optional[str] = None,
    ebus_broker_host: Optional[str] = None,
    ebus_broker_mqtts_port: Optional[int] = None,
) -> None:
    """Add or update credentials for a panel.

    privilege is "full" (registered with the hopPassphrase) or "reduced"
    (registered by proof of proximity); None leaves it unrecorded.
    """
    serial_number = serial_number.lower()
    data = load_auth_file()

    entry = {
        "hostname": hostname,
        "hop_passphrase": hop_passphrase,
        "ebus_broker_password": ebus_broker_password,
        "access_token": access_token,
        "access_token_issued_at": access_token_issued_at
    }
    optional = {
        "privilege": privilege,
        "ebus_broker_username": ebus_broker_username,
        "ebus_broker_host": ebus_broker_host,
        "ebus_broker_mqtts_port": ebus_broker_mqtts_port,
    }
    entry.update({k: v for k, v in optional.items() if v is not None})
    data["panels"][serial_number] = entry

    # Set as default if requested or if it's the only panel
    if set_as_default or len(data["panels"]) == 1:
        data["default_panel"] = serial_number

    save_auth_file(data)


def remove_panel_credentials(serial_number: str) -> bool:
    """Remove a panel from the credential file. Returns True if successful."""
    serial_number = serial_number.lower()
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
            "privilege": creds.get("privilege") or "unknown",
            "is_default": serial == default
        })

    return panels


def reduced_privilege_hint(serial_number: str, has_passphrase: bool) -> str:
    """Explain an HTTP 403 and how to obtain a full-privilege token."""
    serial_number = serial_number.lower()
    if has_passphrase:
        remedy = (f"'span-auth refresh {serial_number}' (uses the stored hopPassphrase) "
                  f"or 'span-auth setup --full {serial_number}'")
    else:
        remedy = f"'span-auth setup --full {serial_number}' or 'span-auth setup -p PASSPHRASE {serial_number}'"
    return (
        f"Hint: if the token for {serial_number} is reduced-privilege "
        f"(registered by proof of proximity),\n"
        f"registering with the hopPassphrase gives a full-privilege token: {remedy}"
    )


def get_ca_cert_path(serial_number: str) -> Path:
    """Get the path to a cached CA certificate for a panel."""
    return get_ca_cert_dir() / f"{serial_number.lower()}.crt"


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
    try:
        import requests
    except ImportError as e:
        requirements = Path(__file__).resolve().parent.parent / "scripts" / "requirements.txt"
        sys.exit(
            f"Error: missing Python package '{e.name}' for {sys.executable}\n"
            f"Install with: {sys.executable} -m pip install -r {requirements}\n"
            f"or run the scripts with a Python that has it: make -C scripts install PYTHON=/path/to/python3"
        )

    cert_path = get_ca_cert_path(serial_number)

    # Check if cert exists and is not expired
    if cert_path.exists():
        if not is_cert_expired(cert_path):
            return cert_path
        print(f"CA certificate for {serial_number} is expired, re-downloading...", file=sys.stderr)

    # Create directory if needed
    get_ca_cert_dir().mkdir(parents=True, exist_ok=True)

    # Download to a temporary file and replace the cached cert only with a PEM certificate
    url = f"http://{hostname}/api/v2/certificate/ca"
    response = requests.get(url, timeout=(5, 15))
    if response.status_code != 200:
        sys.exit(f"Error: could not download the CA certificate from {hostname}: HTTP {response.status_code}")
    if "-----BEGIN CERTIFICATE-----" not in response.text:
        sys.exit(f"Error: response from {hostname} is not a PEM certificate")

    fd, tmp_path = tempfile.mkstemp(dir=cert_path.parent, prefix=f".{cert_path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(response.text)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, cert_path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise
    print(f"Downloaded CA certificate to {cert_path}", file=sys.stderr)

    return cert_path
