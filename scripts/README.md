# SPAN API Scripts

Command-line tools for discovering and interacting with SPAN panels on your local network.

## Quick Start

```bash
# 1. Discover panels on your network
span-discover

# 2. Set up credentials (press door switch 3x first, or have your passphrase ready)
span-auth setup

# 3. Subscribe to panel state via MQTT
span-mqtt-sub -t '@s/$state' -v

# 4. Make authenticated REST API calls
span-curl /api/v2/auth/clients
```

## Prerequisites

- Python 3.10+
- Python packages: `pip install requests zeroconf`
- `jq` (for JSON processing): `brew install jq` (macOS) or `apt install jq` (Linux)
- `mosquitto-clients` (for MQTT): `brew install mosquitto` (macOS) or `apt install mosquitto-clients` (Linux)

## Installation

The scripts depend on shared library files in the `lib/` directory of this repository. To make the scripts accessible from your PATH:

```bash
# Run from anywhere inside the SPAN-API-Client-Docs repository
REPO_ROOT=$(git rev-parse --show-toplevel)
mkdir -p ~/bin
ln -s "$REPO_ROOT/scripts/span-discover" ~/bin/
ln -s "$REPO_ROOT/scripts/span-auth" ~/bin/
ln -s "$REPO_ROOT/scripts/span-curl" ~/bin/
ln -s "$REPO_ROOT/scripts/span-mqtt-sub" ~/bin/
```

The scripts resolve symlinks to find their library files, so they will work correctly when invoked via symlink.

**Note:** Ensure `~/bin` is in your PATH. If `which span-discover` returns "not found", add `export PATH="$HOME/bin:$PATH"` to your shell configuration file (`~/.zshrc` or `~/.bashrc`).

**Do not copy the scripts** to another location—they will fail to find the required `lib/` files.

## Scripts

### span-discover

Discover SPAN panels on your local network via mDNS using Python's `zeroconf` library.

```bash
span-discover              # List all panels
span-discover -j           # JSON output
span-discover -t 5         # 5 second timeout
```

Example output:

```bash
Found 1 SPAN panel(s):

  Serial: ab-1234-c5d67
  Hostname: span-ab-1234-c5d67.local
  Addresses: 192.0.2.100
  Model: SPAN32
  Firmware: spanos2/r202546/03
```

### span-auth

Manage credentials for SPAN panels. Credentials are stored in `~/.span-auth.json`.

#### Setup credentials

Two authentication methods are supported:

**Method 1: Door bypass (proof-of-proximity)**

1. Press the panel's door switch 3 times rapidly
2. Within 15 minutes, run:

   ```bash
   span-auth setup
   ```

**Method 2: With passphrase**

```bash
span-auth setup -p YOUR_PASSPHRASE
span-auth setup ab-1234-c5d67 -p YOUR_PASSPHRASE  # Specific panel
```

#### Other commands

```bash
span-auth list                     # List configured panels
span-auth default                  # Show default panel
span-auth default ab-1234-c5d67    # Set default panel
span-auth refresh                  # Refresh access token
span-auth refresh --all            # Refresh all panels
span-auth regenerate               # Regenerate passphrase (invalidates old one)
span-auth regenerate -y            # Skip confirmation prompt
span-auth remove ab-1234-c5d67     # Remove a panel
```

### span-mqtt-sub / span-mqtt-pub

Subscribe to or publish MQTT messages. After running `span-auth setup`, credentials are loaded automatically.

```bash
# Subscribe to panel state
span-mqtt-sub -t '@s/$state' -v

# Subscribe to all topics (continuous stream)
span-mqtt-sub -t '@s/#' -v

# Subscribe to core node properties
span-mqtt-sub -t '@s/core/#' -v

# Get device description (JSON schema)
span-mqtt-sub -C 1 -t '@s/$description' | jq

# Override default panel
span-mqtt-sub -u nt-2236-000jv -t '@s/$state' -v
```

The `@s` macro expands to `ebus/5/<serial-number>`.

**Backward compatible mode** (explicit credentials):

```bash
span-mqtt-sub -u SERIAL -P PASSWORD --cafile /path/to/ca.crt -t '@s/$state' -v
```

### span-curl

Make authenticated REST API calls. Uses credentials from `~/.span-auth.json`.

```bash
# List registered clients
span-curl /api/v2/auth/clients

# Get FQDN configuration
span-curl /api/v2/dns/fqdn

# Delete a client
span-curl -X DELETE /api/v2/auth/clients/myapp

# Set FQDN
span-curl -X POST -d '{"ebusTlsFqdn":"panel.home.local"}' /api/v2/dns/fqdn

# Use a different panel
span-curl -u nt-2236-000jv /api/v2/auth/clients

# Verbose output
span-curl -v /api/v2/auth/clients

# Use HTTP instead of HTTPS
span-curl --http /api/v2/auth/clients
```

### span-mdns-query

Query specific mDNS service advertisements (lower-level than span-discover).

```bash
span-mdns-query ab-1234-c5d67 _http
span-mdns-query ab-1234-c5d67 _ebus
span-mdns-query ab-1234-c5d67 _device-info
```

## Configuration

### Credential File

Credentials are stored in `~/.span-auth.json` with permissions `600`.

To use a different location, set the `SPAN_AUTH_FILE` environment variable:

```bash
export SPAN_AUTH_FILE=/path/to/my-credentials.json
```

### CA Certificates

CA certificates are cached in `~/.span-ca-certs/` (one file per panel).

To use a different location, set the `SPAN_CA_CERT_DIR` environment variable:

```bash
export SPAN_CA_CERT_DIR=/path/to/ca-certs
```

## Typical Workflow

1. **First-time setup:**

   ```bash
   # Discover your panel
   span-discover

   # Press door switch 3x, then within 15 minutes:
   span-auth setup
   ```

2. **Daily use:**

   ```bash
   # Check panel state
   span-mqtt-sub -C 1 -t '@s/$state'

   # Monitor power in real-time
   span-mqtt-sub -t '@s/core/instant-grid-power-w' -v

   # List API clients
   span-curl /api/v2/auth/clients
   ```

3. **If token expires:**

   ```bash
   span-auth refresh
   ```

## Troubleshooting

**"No SPAN panels found"**

- Ensure your computer is on the same network as the panel
- Try increasing timeout: `span-discover -t 10`
- Verify zeroconf is installed: `pip install zeroconf`

**"No default panel configured"**

- Run `span-auth setup` to configure credentials
- Or specify panel explicitly: `-u SERIAL`

**"Connection refused" on MQTT**

- Verify credentials: `span-auth list`
- Try refreshing token: `span-auth refresh`
- Check panel is online: `ping span-SERIAL.local`

**Permission denied on credential file**

- File should be readable only by owner: `chmod 600 ~/.span-auth.json`
