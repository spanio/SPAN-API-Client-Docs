# SPAN Panel MQTT API Capabilities

The SPAN panel provides real-time data over MQTT using the Homie 5 convention. Clients connect to the panel's local MQTT broker and receive continuous property updates as they change.

---

## Read vs Write

The vast majority of the API is **read-only**. The panel publishes property values; clients subscribe and receive updates.

Only **3 properties** are writable:

| Property | Where | What It Does |
|---|---|---|
| `dominant-power-source` | Panel (one per panel) | Enables override of grid-state when panel loses communication with the backup system (BESS) |
| `relay` | Circuit (one per breaker) | Opens or closes a circuit breaker relay |
| `shed-priority` | Circuit (one per breaker) | Configures when a circuit sheds load during off-grid operation |

Everything else below is **read-only observation** — the panel publishes it, clients can only listen.

---

## Panel Core

General panel identity and status.

| Property | Type | Description |
|---|---|---|
| `vendor-name` | string | Vendor name |
| `serial-number` | string | Panel serial number |
| `hardware-version` | string | Hardware revision |
| `software-version` | string | Firmware version |
| `door` | enum | Door state: `UNKNOWN`, `OPEN`, `CLOSED` |
| `grid-islandable` | boolean | Capable of operating off-grid |
| `dominant-power-source` | enum | **WRITABLE.** Enables override of grid-state when panel loses communication with the BESS. `GRID`, `BATTERY`, `PV`, `GENERATOR`, `NONE`, `UNKNOWN` |
| `relay` | enum | Main relay: `UNKNOWN`, `OPEN`, `CLOSED` |
| `l1-voltage` | float (V) | Line 1 voltage |
| `l2-voltage` | float (V) | Line 2 voltage |
| `breaker-rating` | integer (A) | Main breaker rating |
| `ethernet` | boolean | Ethernet interface operational |
| `wifi` | boolean | Wi-Fi interface operational |
| `wifi-ssid` | string | Connected Wi-Fi SSID |
| `vendor-cloud` | enum | Cloud connection: `UNKNOWN`, `UNCONNECTED`, `CONNECTED` |
| `postal-code` | string | Postal / ZIP code |
| `time-zone` | string | IANA time zone |

## Lugs (Upstream and Downstream)

Power and energy measurements at the grid connection point (upstream) and sub-panel feed-through point (downstream).

| Property | Type | Description |
|---|---|---|
| `direction` | enum | `UPSTREAM` or `DOWNSTREAM` |
| `feed` | string | Connected device, if known |
| `l1-current` | float (A) | Line 1 current |
| `l2-current` | float (A) | Line 2 current |
| `active-power` | float (W) | Active power |
| `imported-energy` | float (Wh) | Cumulative imported energy |
| `exported-energy` | float (Wh) | Cumulative exported energy |

## Circuit

One node per circuit breaker space in the panel.

| Property | Type | Description |
|---|---|---|
| `name` | string | User-assigned circuit name |
| `relay` | enum | **WRITABLE.** `UNKNOWN`, `OPEN`, `CLOSED` |
| `relay-requester` | enum | Actor that set the relay: `NONE`, `BACKUP`, `USER`, `PCS`, `PCS_FAIL_SAFE`, `ALWAYS_ON`, `NEVER_BACKUP`, `INVERTER`, `FAULT` |
| `breaker-rating` | integer (A) | Breaker rating |
| `current` | float (A) | Measured current |
| `active-power` | float (W) | Measured active power |
| `imported-energy` | float (Wh) | Cumulative imported energy |
| `exported-energy` | float (Wh) | Cumulative exported energy |
| `space` | integer | Breaker space number (1–32) |
| `dipole` | boolean | Two-pole breaker |
| `shed-priority` | enum | **WRITABLE.** `UNKNOWN`, `OFF_GRID`, `SOC_THRESHOLD`, `NEVER` |
| `pcs-managed` | boolean | Managed by Power Control System |
| `pcs-priority` | integer | PCS priority ranking |
| `sheddable` | boolean | Configured as sheddable |
| `never-backup` | boolean | Configured as never-backup |
| `always-on` | boolean | Configured as always-on |

## Aggregate Power Flows

Panel-computed aggregate power across all sources.

| Property | Type | Description |
|---|---|---|
| `pv` | float (W) | Solar PV power |
| `battery` | float (W) | Battery power |
| `grid` | float (W) | Grid power |
| `site` | float (W) | Total site power |

## Power Control System (PCS)

Manages circuit load shedding based on power import limits.

| Property | Type | Description |
|---|---|---|
| `enabled` | boolean | PCS enabled |
| `active` | boolean | Actively controlling loads |
| `import-limit` | float (A) | Current import limit being managed to |
| `feed-import-limit` | float (A) | Feed maximum import limit |
| `feed-import-limit-enablement` | enum | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `feed-import-limit-active` | boolean | Feed limit currently enforced |
| `grid-import-limit` | float (A) | Grid maximum import limit |
| `grid-import-limit-enablement` | enum | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `grid-import-limit-active` | boolean | Grid limit currently enforced |
| `off-grid-import-limit` | float (A) | Off-grid maximum import limit |
| `off-grid-import-limit-enablement` | enum | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `off-grid-import-limit-active` | boolean | Off-grid limit currently enforced |
| `requested-import-limit` | float (A) | Requested maximum import limit |
| `requested-import-limit-enablement` | enum | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `requested-import-limit-active` | boolean | Requested limit currently enforced |

## EVSE (SPAN Drive only)

Present when a SPAN Drive EV charger is commissioned.

| Property | Type | Description |
|---|---|---|
| `vendor-name` | string | EVSE vendor |
| `product-name` | string | Product name |
| `part-number` | string | Part number |
| `serial-number` | string | Serial number |
| `software-version` | string | Firmware version |
| `feed` | enum | Circuit the EVSE is landed on |
| `lock-state` | enum | `UNKNOWN`, `LOCKED`, `UNLOCKED` |
| `status` | enum | `UNKNOWN`, `AVAILABLE`, `PREPARING`, `CHARGING`, `SUSPENDED_EV`, `SUSPENDED_EVSE`, `FINISHING`, `RESERVED`, `FAULTED`, `UNAVAILABLE` |
| `advertised-current` | float (A) | Current advertised to the EV |

## Battery Energy Storage System (BESS)

Present when a battery system is commissioned.

| Property | Type | Description |
|---|---|---|
| `vendor-name` | string | Battery vendor |
| `product-name` | string | Product name |
| `model` | string | Model number |
| `serial-number` | string | Serial number |
| `software-version` | string | Firmware version |
| `nameplate-capacity` | float (kWh) | Nameplate energy capacity |
| `relative-position` | enum | `UPSTREAM`, `DOWNSTREAM`, `IN_PANEL` |
| `feed` | enum | Circuit the battery is landed on |
| `soc` | float (%) | State of charge |
| `soe` | float (kWh) | State of energy |
| `connected` | boolean | Connected to battery system |
| `grid-state` | enum | `UNKNOWN`, `ON_GRID`, `OFF_GRID` |

## Photovoltaic System (PV)

Present when a solar PV system is commissioned.

| Property | Type | Description |
|---|---|---|
| `vendor-name` | string | PV vendor |
| `product-name` | string | Product name |
| `serial-number` | string | Inverter serial number |
| `software-version` | string | Inverter firmware version |
| `nameplate-capacity` | float (kW) | System nameplate capacity |
| `relative-position` | enum | `UPSTREAM`, `DOWNSTREAM`, `IN_PANEL` |
| `feed` | enum | Circuit the PV system is landed on |
