# SPAN API Scripts

Command-line tools for discovering and interacting with SPAN panels on your local network.

## Quick Start

```bash
# 1. Discover panels on your network
span-discover

# 2. Set up credentials (waits for door switch press, then registers)
span-auth setup --wait

# 3. Subscribe to panel state via MQTT
span-mqtt-sub -t '@s/$state' -v

# 4. Make authenticated REST API calls
span-curl /api/v2/auth/clients
```

## Prerequisites

- Python 3.10+, with the packages in `scripts/requirements.txt` (`requests`, `zeroconf`)
- `jq` (for JSON processing): `brew install jq` (macOS) or `apt install jq` (Linux)
- `curl` and `openssl` (preinstalled on macOS and most Linux distributions)
- `mosquitto-clients` (for MQTT): `brew install mosquitto` (macOS) or `apt install mosquitto-clients` (Linux)

Install the Python packages from the repository root:

```bash
python3 -m pip install --user -r scripts/requirements.txt
```

Homebrew Python and recent Debian/Ubuntu Python refuse `pip install` into the system interpreter (an "externally-managed-environment" error). Use `--user` where it is allowed, the distribution packages (`apt install python3-requests python3-zeroconf`), or a virtual environment. The Python scripts start with `#!/usr/bin/env python3`, so a virtual environment must be active whenever you run them, unless you install the scripts with `PYTHON` (see Installation).

## Installation

The scripts depend on shared library files in the `lib/` directory of this repository. To make the scripts accessible from your PATH, run from the repository root:

```bash
make -C scripts install     # symlink all six scripts into ~/bin
make -C scripts check       # report each prerequisite and installed link as ok or missing
make -C scripts uninstall   # remove only the links that point into this checkout
```

Set `BINDIR` to install somewhere other than `~/bin`, for example `make -C scripts install BINDIR=/usr/local/bin`. Pass the same `BINDIR` to `check` and `uninstall`.

`install` leaves alone any existing file or link in `BINDIR` that was not installed from this checkout, reports it as skipped, and exits non-zero. Pass `FORCE=1` to replace those entries too.

To run the Python scripts (`span-auth`, `span-discover`, `span-mdns-query`) with a particular interpreter, such as a virtual environment's, pass `PYTHON`, for example `make -C scripts install PYTHON=~/venvs/span/bin/python3`. Those three are then installed as small wrappers that run the script with that interpreter, so the environment does not need to be activated. `git pull` still upgrades them, because the wrappers run the scripts in this checkout. Pass the same `PYTHON` to `check` to check that interpreter's packages.

Alternatively, create the links by hand:

```bash
# Run from anywhere inside the SPAN-API-Client-Docs repository
REPO_ROOT=$(git rev-parse --show-toplevel)
mkdir -p ~/bin
ln -sf "$REPO_ROOT/scripts/span-discover" ~/bin/
ln -sf "$REPO_ROOT/scripts/span-auth" ~/bin/
ln -sf "$REPO_ROOT/scripts/span-curl" ~/bin/
ln -sf "$REPO_ROOT/scripts/span-mqtt-sub" ~/bin/
ln -sf "$REPO_ROOT/scripts/span-mqtt-pub" ~/bin/
ln -sf "$REPO_ROOT/scripts/span-mdns-query" ~/bin/
```

Keep the link name `span-mqtt-pub`: the script chooses between publishing and subscribing from the name it is invoked by.

The scripts resolve symlinks to find their library files, so they will work correctly when invoked via symlink.

**Note:** Ensure `~/bin` is in your PATH. If `which span-discover` returns "not found", add `export PATH="$HOME/bin:$PATH"` to your shell configuration file (`~/.zshrc` or `~/.bashrc`).

**Do not copy the scripts** to another location—they will fail to find the required `lib/` files.

## Scripts

### span-discover

Discover SPAN panels on your local network via mDNS using Python's `zeroconf` library. Panels are found by their `_ebus._tcp` service; the model, firmware version, and hardware version come from the panel's `_device-info._tcp` service, matched by its `serial_number` TXT record. Each of those lines is shown only when the panel advertises it.

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
  Model: MAIN_32
  Firmware: spanos3/r202639/02
  Hardware: 1.2
```

With `-j`, every panel object has the same keys (`serial_number`, `hostname`, `addresses`, `model`, `firmware_version`, `hardware_version`), with `null` for a value the panel does not advertise.

### span-auth

Manage credentials for SPAN panels. Credentials are stored in `~/.span-auth.json`.

#### Setup credentials

Three authentication methods are supported:

**Method 1: Door bypass with `--wait` (recommended)**

Start the command first, then go press the door switch — no timing pressure:

```bash
span-auth setup --wait                    # Discover panel, wait for door press
span-auth setup --wait ab-1234-c5d67      # Wait for specific panel
span-auth setup --wait --wait-timeout 60  # Custom timeout (default: 900s = 15 min)
```

The script polls the panel's status endpoint every few seconds. Once proximity is proven, it automatically proceeds with registration.

**Method 2: Door bypass (manual timing)**

1. Press the panel's door switch 3 times rapidly
2. Within 15 minutes, run:

   ```bash
   span-auth setup
   ```

**Method 3: With passphrase**

```bash
span-auth setup -p YOUR_PASSPHRASE
span-auth setup ab-1234-c5d67 -p YOUR_PASSPHRASE  # Specific panel
```

#### About door bypass (proof-of-proximity)

The panel's door switch is a magnetic reed switch. Opening the panel door counts as the first press, so from a closed door you only need **2 additional presses** to trigger proximity proof. When proximity is proven, the breaker-space LED strip flashes approximately twice to confirm.

The proof-of-proximity window lasts ~15 minutes and is **single-use** — the first API registration consumes it. If registration fails for any reason (e.g., a client name collision), the proof is spent and you must press the door switch again.

#### Token privilege

Registering with the `hopPassphrase` (Method 3) yields a full-privilege token. Registering by proof of proximity (Methods 1 and 2) yields a reduced-privilege token, for which some endpoints, such as `/api/v2/auth/clients`, return HTTP 403. `span-auth` records which kind each panel's token is, and `span-auth list` shows it as `full`, `reduced`, or `unknown` (credentials saved by an earlier version of `span-auth`).

The registration response includes the `hopPassphrase`, so `--full` turns a proof-of-proximity setup into a full-privilege one by registering a second time, with that passphrase, under a distinct client name:

```bash
span-auth setup --wait --full             # Door press, then a full-privilege token
```

Without `--full`, `span-auth setup` registers once. When a `hopPassphrase` is stored, `span-auth refresh` registers with it, so it also yields a full-privilege token. When `span-auth` or `span-curl` receives HTTP 403, it prints a hint on getting a full-privilege token.

#### Other commands

```bash
span-auth list                     # List configured panels, with token privilege
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

# Subscribe to the panel's meter properties
span-mqtt-sub -t '@s/meter/#' -v

# Get device description (JSON schema)
span-mqtt-sub -C 1 -t '@s/$description' | jq

# Override default panel
span-mqtt-sub -u nt-2236-000jv -t '@s/$state' -v
```

The `@s` macro expands to `ebus/5/<serial-number>`.

The broker host, MQTTS port, and username are the `ebusBrokerHost`, `ebusBrokerMqttsPort`, and `ebusBrokerUsername` values saved from the registration response. For credentials saved by an earlier version of `span-auth`, which lack them, the defaults are the saved panel hostname (`span-<serial-number>.local` if none), `8883`, and the serial number.

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

   # Start the wait, then go press the door switch 3x:
   span-auth setup --wait
   ```

2. **Daily use:**

   ```bash
   # Check panel state
   span-mqtt-sub -C 1 -t '@s/$state'

   # Monitor grid power in real time (upstream lugs; positive = importing)
   span-mqtt-sub -t '@s-lugs-up/meter/active-power' -v

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
- Verify the prerequisites: `make -C scripts check`

**"No default panel configured"**

- Run `span-auth setup` to configure credentials
- Or specify panel explicitly: `-u SERIAL`

**"Connection refused" on MQTT**

- Verify credentials: `span-auth list`
- Try refreshing token: `span-auth refresh`
- Check panel is online: `ping span-SERIAL.local`

**Permission denied on credential file**

- File should be readable only by owner: `chmod 600 ~/.span-auth.json`
