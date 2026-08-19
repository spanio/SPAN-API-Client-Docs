# SPAN Panel MQTT API Capabilities

The SPAN panel provides real-time data over MQTT using the Homie 5 convention. Clients connect to the panel's local MQTT broker and receive continuous property updates as they change.

SPAN API publishes a **parent device** (the panel) plus a set of **child devices** (lugs, circuits, and commissioned DERs). Each device organizes its properties into **capability nodes** (for example `info`, `meter`, `switch`). Identify a device by the `type` field in its `$description`; device IDs are opaque. See [SPAN Panel MQTT Topic Reference](mqtt-topic-reference.md) for exact topic paths and device-ID forms.

This page catalogs what each device class exposes. A given panel publishes a subset based on its hardware and commissioned devices.

---

## Read vs Write

The vast majority of the API is **read-only**: the panel publishes property values; clients subscribe and receive updates.

Only **4 properties** are writable:

| Device | Capability | Property | What It Does |
|---|---|---|---|
| Circuit | `switch` | `relay` | Opens or closes a circuit relay (when `relay-controllable` is true) |
| Circuit | `load-shed` | `priority` | Configures when a circuit sheds load during off-grid operation (only where this property's `$settable` is `true`; it is `false` on circuits commissioned as never-backup) |
| Panel | `shed` | `asserted-islanding-state` | Overrides the sensed islanding-state when the panel loses communication with the MID or BESS |
| EVSE | `config` | `user-max-charge-current` | Sets the user charge-current ceiling for the SPAN Drive |

Everything else below is read-only observation.

---

## Panel (Distribution Enclosure)

Device type `energy.ebus.device.distribution-enclosure`. Panel identity, status, metering, and control-system state.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `vendor-name` | string | Vendor name |
| `info` | `model` | enum | `MAIN_16`, `MLO_24`, `MAIN_32`, `MAIN_40`, `MLO_48` |
| `info` | `serial-number` | string | Panel serial number |
| `info` | `hardware-version` | string | Hardware revision |
| `info` | `firmware-version` | string | Firmware version |
| `info` | `data-model-version` | string | eBus data-model version (`1.0`) |
| `door` | `state` | enum | Door state: `UNKNOWN`, `OPEN`, `CLOSED` |
| `status` | `relay` | enum | Main relay: `UNKNOWN`, `OPEN`, `CLOSED` |
| `status` | `ethernet` | boolean | Ethernet interface operational |
| `status` | `wifi` | boolean | Wi-Fi interface operational |
| `status` | `wifi-ssid` | string | Connected Wi-Fi SSID |
| `status` | `cloud-connection` | enum | `UNKNOWN`, `UNCONNECTED`, `CONNECTED` |
| `status` | `postal-code` | string | Postal / ZIP code |
| `status` | `time-zone` | string | IANA time zone |
| `meter` | `voltage-a` | float (V) | Line 1 voltage |
| `meter` | `voltage-b` | float (V) | Line 2 voltage |
| `breaker` | `rating` | integer (A) | Main breaker rating |
| `pcs` | `enabled` | boolean | Power Control System enabled |
| `pcs` | `active` | boolean | Actively controlling loads |
| `pcs` | `import-limit` | float (A) | Current import limit being managed to |
| `pcs` | `binding-constraint` | enum | Which constraint sets the import limit: `FSR`, `DOE`, `VOLTAGE`, `OFF_GRID`, `REQUESTED`, `OPERATOR`, `NONE`, `UNKNOWN` |
| `pcs` | `feed-import-limit` | float (A) | Feed import limit. Each import limit has an `-enablement` (enum) and `-active` (boolean) companion. |
| `pcs` | `operator-import-limit` | float (A) | Operator import limit |
| `pcs` | `off-grid-import-limit` | float (A) | Off-grid import limit |
| `pcs` | `requested-import-limit` | float (A) | Requested import limit |
| `power-flows` | `pv` | float (W) | Solar PV power flow |
| `power-flows` | `battery` | float (W) | Battery / BESS power flow |
| `power-flows` | `grid` | float (W) | Grid power flow |
| `power-flows` | `site` | float (W) | Total site power flow |
| `shed-forecast` | `total-time-remaining` | integer (min) | Time before backed-up circuits drop at current SOE |
| `shed-forecast` | `time-to-priority-shed` | integer (min) | Time until the next priority tier is shed at current SOE |
| `shed-forecast` | `full-charge-total-time-remaining` | integer (min) | Total backup duration assuming a full charge |
| `shed-forecast` | `full-charge-time-to-priority-shed` | integer (min) | Time to the next priority shed assuming a full charge |
| `shed-forecast` | `confidence` | enum | `LOW`, `MEDIUM`, `HIGH` |
| `shed` | `asserted-islanding-state` | enum | **WRITABLE, `ON_GRID` / `OFF_GRID` only.** Consumer override of the sensed islanding-state, accepted only during MID/BESS comm loss. `NONE` is the panel-authored default and cannot be set by a consumer |
| `shed` | `policy` | json | Active shed policy (`soc-priority.v1` with shed/release thresholds) |

The `shed-forecast` and `shed` capabilities are published only when a BESS is commissioned.

## Lugs

Device type `energy.ebus.device.lugs`. Power and energy at the grid connection point (upstream lugs) and the sub-panel feed-through point (downstream lugs).

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `direction` | enum | `UPSTREAM` or `DOWNSTREAM` |
| `meter` | `current-a` | float (A) | Line 1 (leg A) RMS current at the panel's service entrance, republished unchanged on both lugs devices rather than measured per lugs |
| `meter` | `current-b` | float (A) | Line 2 (leg B) RMS current at the panel's service entrance, republished unchanged on both lugs devices rather than measured per lugs |
| `meter` | `active-power` | float (W) | Active power |
| `meter` | `imported-energy` | float (Wh) | Cumulative imported energy |
| `meter` | `exported-energy` | float (Wh) | Cumulative exported energy |
| `connection` | `fed-by-device-id` / `-type` / `-status` | string / string / enum | Upstream connection: device wired into this lugs, and the panel's view of its link health (`OK`, `LOST`, `DEGRADED`) |
| `connection` | `feeds-device-id` / `-type` / `-status` | string / string / enum | Downstream connection: device fed by this lugs, and its link health |
| `connection` | `count` | integer | Physical units aggregated as the connected device. Declared in the schema but not published by SPAN Panel in this release, so no value ever appears on the topic. |

## Circuit

Device type `energy.ebus.device.circuit`. One child device per circuit breaker space.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `name` | string | User-assigned circuit name |
| `info` | `spaces` | string | Physical panel position(s) the circuit occupies, comma-separated (e.g. `17,19`); with `breaker/poles` identifies every occupied slot |
| `switch` | `relay` | enum | **WRITABLE** (when `relay-controllable` is true): `UNKNOWN`, `OPEN`, `CLOSED` |
| `switch` | `relay-requester` | enum | Actor that requested the relay state: `UNKNOWN`, `NONE`, `LOAD_SHED`, `USER`, `PCS`, `CONFIGURATION`, `FAULT` |
| `switch` | `relay-controllable` | boolean | Whether the relay can be commanded at all |
| `breaker` | `rating` | integer (A) | Breaker rating |
| `breaker` | `poles` | integer | Number of breaker poles |
| `meter` | `current` | float (A) | Measured current |
| `meter` | `active-power` | float (W) | Measured active power |
| `meter` | `imported-energy` | float (Wh) | Cumulative imported energy |
| `meter` | `exported-energy` | float (Wh) | Cumulative exported energy |
| `load-shed` | `priority` | enum | **WRITABLE** where this property's `$settable` is `true`, which is `false` on circuits commissioned as never-backup. Load-shed priority when off-grid. Writable values are `OFF_GRID`, `SOC_THRESHOLD`, and `NEVER`; the panel may publish `UNKNOWN`, but a write of `UNKNOWN` is silently ignored |
| `pcs` | `managed` | boolean | Managed by the Power Control System |
| `pcs` | `priority` | integer | PCS priority ranking |
| `connection` | `feeds-device-id` / `-type` / `-status` | string / string / enum | Present when the circuit is dedicated to a commissioned downstream DER |
| `connection` | `count` | integer | Physical units aggregated as the connected device. Declared in the schema but not published by SPAN Panel in this release, so no value ever appears on the topic. |

## Battery Energy Storage System (BESS)

Device type `energy.ebus.device.bess`. Present when a battery system is commissioned. A commissioned BESS is proxied by the panel, which also publishes an associated MID as a child of the BESS device, making the MID a grandchild of the panel.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `vendor-name` | string | Battery vendor |
| `info` | `model` | string | Human-facing product designation (e.g. `Powerwall 2 AC`) |
| `info` | `part-number` | string | Vendor orderable part / SKU code (e.g. `1232100-00-E`) |
| `info` | `serial-number` | string | Serial number |
| `info` | `firmware-version` | string | Firmware version |
| `info` | `nameplate-capacity` | float (kWh) | Nameplate energy capacity |
| `soc` | `soc` | float (%) | State of charge |
| `soc` | `soe` | float (kWh) | State of energy |
| `meter` | `active-power` | float (W) | Battery active power |
| `status` | `communication-state` | enum | `OK`, `DEGRADED`, `LOST`, `UNKNOWN` |

## Photovoltaic System (PV)

Device type `energy.ebus.device.pv`. Present when a solar PV system is commissioned.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `vendor-name` | string | PV vendor |
| `info` | `model` | string | Human-facing product designation (e.g. `IQ7PLUS-72-x-US`) |
| `info` | `serial-number` | string | Inverter serial number |
| `info` | `firmware-version` | string | Inverter firmware version |
| `info` | `nominal-power` | float (W) | Rated power (rated DC array power) |

## Electric Vehicle Supply Equipment (EVSE)

Device type `energy.ebus.device.evse`. Present when a SPAN Drive EV charger is commissioned.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `vendor-name` | string | EVSE vendor |
| `info` | `model` | string | Human-facing product designation |
| `info` | `part-number` | string | Vendor orderable part / SKU code |
| `info` | `serial-number` | string | Serial number |
| `info` | `firmware-version` | string | Firmware version |
| `switch` | `lock-state` | enum | `UNLOCKED`, `LOCKED` |
| `status` | `status` | enum | `AVAILABLE`, `PREPARING`, `CHARGING`, `UNAVAILABLE` |
| `meter` | `advertised-current` | float (A) | Current advertised to the EV |
| `config` | `max-charge-current` | integer (A) | Installer-configured maximum charge current |
| `config` | `user-max-charge-current` | integer (A) | **WRITABLE.** User charge-current ceiling, from 6 A (the J1772 minimum charge rate) up to `max-charge-current`. Out-of-range values are clamped to the nearest bound rather than rejected, and a non-integer payload is discarded |

## Microgrid Interconnect Device (MID)

Device type `energy.ebus.device.mid`. Manages the electrical boundary between the grid and the home during islanding. For SPAN Panel MAIN 32, every commissioned (and therefore proxied) BESS publishes a MID.

| Capability | Property | Type | Description |
|---|---|---|---|
| `info` | `vendor-name` | string | Vendor name |
| `info` | `serial-number` | string | Serial number |
| `info` | `model` | string | Human-facing product designation |
| `info` | `firmware-version` | string | Firmware version |
| `info` | `hardware-version` | string | Hardware version |
| `grid` | `islanding-state` | enum | The MID's relay position: `ON_GRID`, `OFF_GRID`, `UNKNOWN` |
| `grid` | `grid-state` | enum | Sensed grid condition: `UP`, `DOWN`, `DEGRADED`, `UNKNOWN`. Always `UNKNOWN` on SPAN Panel (no upstream-grid sensor on the synthesized MID) |
| `grid` | `grid-forming-entity` | string | Device establishing the AC reference: `"GRID"`, or the Homie device ID of the grid-forming DER when islanded |
