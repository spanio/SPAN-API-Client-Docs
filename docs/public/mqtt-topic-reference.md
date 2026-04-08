# SPAN Panel MQTT Topic Reference

This document lists all MQTT topics exposed by the SPAN panel's eBus adapter
via the Homie 5 convention, including data types, units, and read/write access.

**Source:** `GET /api/v2/homie/schema` — returns the superset of all property
definitions across node types. Individual panels expose a subset based on their
hardware configuration and commissioned devices.

**Firmware:** spanos2/r202603
**Homie version:** 5
**Domain:** `ebus`

---

## Topic Structure

All topics follow the Homie 5 convention:

```
ebus/5/<device-id>/$state                          # Device lifecycle state
ebus/5/<device-id>/$description                    # Full device/node/property schema (JSON)
ebus/5/<device-id>/<node-id>/<property-id>         # Property value (READ)
ebus/5/<device-id>/<node-id>/<property-id>/set     # Property command (WRITE, settable only)
```

- `<device-id>` — panel serial number (e.g., `nt-2143-c1akc`)
- `<node-id>` — identifies the node: `core`, `lugs-upstream`, `lugs-downstream`,
  `power-flows`, `pcs`, `bess`, `pv`, `evse`, or a circuit UUID
- `<property-id>` — property name within the node

### Device-Level Topics

| Topic | Payload | Description |
|---|---|---|
| `ebus/5/<device-id>/$state` | `init`, `ready`, `disconnected`, `sleeping`, `lost` | Device lifecycle state |
| `ebus/5/<device-id>/$description` | JSON | Complete schema of all nodes and properties for this device |

---

## Node Types and Properties

Properties are **read-only** unless marked **SETTABLE**. Settable properties
accept commands on the `/set` subtopic.

### Panel Core

**Node type:** `energy.ebus.device.distribution-enclosure.core`
**Node ID:** `core`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `vendor-name` | string | — | read | Vendor name |
| `serial-number` | string | — | read | Panel serial number |
| `hardware-version` | string | — | read | Hardware revision |
| `software-version` | string | — | read | Firmware version |
| `door` | enum | — | read | `UNKNOWN`, `OPEN`, `CLOSED` |
| `grid-islandable` | boolean | — | read | Capable of operating off-grid |
| `dominant-power-source` | enum | — | **SETTABLE** | `GRID`, `BATTERY`, `PV`, `GENERATOR`, `NONE`, `UNKNOWN` — current dominant power source and load-shedding trigger |
| `relay` | enum | — | read | Main relay: `UNKNOWN`, `OPEN`, `CLOSED` |
| `l1-voltage` | float | V | read | Line 1 voltage |
| `l2-voltage` | float | V | read | Line 2 voltage |
| `breaker-rating` | integer | A | read | Main breaker rating |
| `ethernet` | boolean | — | read | Ethernet interface operational |
| `wifi` | boolean | — | read | Wi-Fi interface operational |
| `wifi-ssid` | string | — | read | Connected Wi-Fi SSID |
| `vendor-cloud` | enum | — | read | `UNKNOWN`, `UNCONNECTED`, `CONNECTED` |
| `postal-code` | string | — | read | Postal / ZIP code |
| `time-zone` | string | — | read | IANA time zone (e.g., `America/Los_Angeles`) |

### Lugs (Upstream and Downstream)

**Node type:** `energy.ebus.device.lugs`
**Node IDs:** `lugs-upstream`, `lugs-downstream`

The upstream lugs measure power at the grid/utility connection point. The
downstream lugs measure power at the sub-panel feed-through point. Not all
panels have downstream lugs.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `direction` | enum | — | read | `UPSTREAM`, `DOWNSTREAM` |
| `feed` | string | — | read | Device the lugs connect to, if known |
| `l1-current` | float | A | read | Line 1 current |
| `l2-current` | float | A | read | Line 2 current |
| `active-power` | float | W | read | Active power through lugs |
| `imported-energy` | float | Wh | read | Cumulative energy imported (into panel from this direction) |
| `exported-energy` | float | Wh | read | Cumulative energy exported (out of panel in this direction) |

### Circuit

**Node type:** `energy.ebus.device.circuit`
**Node ID:** circuit UUID (e.g., `ac3dccda46a94b98878a227df6fed588`)

Each circuit breaker space in the panel is represented as a separate node.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `name` | string | — | read | User-assigned circuit name |
| `relay` | enum | — | **SETTABLE** | `UNKNOWN`, `OPEN`, `CLOSED` — circuit relay state |
| `relay-requester` | enum | — | read | Actor that requested current relay state: `UNKNOWN`, `NONE`, `BACKUP`, `USER`, `PCS`, `PCS_FAIL_SAFE`, `ALWAYS_ON`, `NEVER_BACKUP`, `INVERTER`, `FAULT` |
| `breaker-rating` | integer | A | read | Breaker rating |
| `current` | float | A | read | Measured current |
| `active-power` | float | kW | read | Measured active power (see note below) |
| `imported-energy` | float | Wh | read | Cumulative energy imported (from circuit back to panel) |
| `exported-energy` | float | Wh | read | Cumulative energy exported (from panel to circuit) |
| `space` | integer | — | read | Breaker space number (format: `1:32:1`) |
| `dipole` | boolean | — | read | Two-pole breaker |
| `shed-priority` | enum | — | **SETTABLE** | `UNKNOWN`, `OFF_GRID`, `SOC_THRESHOLD`, `NEVER` — load shedding priority when off-grid |
| `pcs-managed` | boolean | — | read | Managed by Power Control System |
| `pcs-priority` | integer | — | read | PCS priority ranking |
| `sheddable` | boolean | — | read | Configured as sheddable |
| `never-backup` | boolean | — | read | Configured as never-backup |
| `always-on` | boolean | — | read | Configured as always-on |

> **Note:** The schema declares `active-power` unit as `kW`, but actual values
> are reported in **watts**. This is a known firmware discrepancy.

### Battery Energy Storage System (BESS)

**Node type:** `energy.ebus.device.bess`
**Node ID:** `bess`

Present when a battery system (e.g., Tesla Powerwall) is commissioned.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `vendor-name` | string | — | read | Battery vendor (e.g., `Tesla`) |
| `product-name` | string | — | read | Product name (e.g., `Powerwall 2 AC`) |
| `model` | string | — | read | Model number |
| `serial-number` | string | — | read | Battery serial number |
| `software-version` | string | — | read | Battery firmware version |
| `nameplate-capacity` | float | kWh | read | Nameplate energy capacity |
| `relative-position` | enum | — | read | `UPSTREAM`, `DOWNSTREAM`, `IN_PANEL` — position relative to the panel |
| `feed` | enum | — | read | Circuit ID the battery is landed on |
| `soc` | float | % | read | State of charge |
| `soe` | float | kWh | read | State of energy |
| `connected` | boolean | — | read | Connected to battery system |
| `grid-state` | enum | — | read | `UNKNOWN`, `ON_GRID`, `OFF_GRID` |

### Photovoltaic System (PV)

**Node type:** `energy.ebus.device.pv`
**Node ID:** `pv`

Present when a solar PV system is commissioned.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `vendor-name` | string | — | read | PV vendor (e.g., `Enphase Energy`) |
| `product-name` | string | — | read | Product name (e.g., `IQ7PLUS-72-x-US`) |
| `serial-number` | string | — | read | Inverter serial number |
| `software-version` | string | — | read | Inverter firmware version |
| `nameplate-capacity` | float | kW | read | System nameplate capacity (see note below) |
| `relative-position` | enum | — | read | `UPSTREAM`, `DOWNSTREAM`, `IN_PANEL` — position relative to the panel |
| `feed` | enum | — | read | Circuit ID the PV system is landed on |

> **Note:** The schema declares `nameplate-capacity` unit as `kW`, but actual
> values are reported in **watts** (e.g., `4640` = 4.64 kW). This is a known
> firmware discrepancy.

### Electric Vehicle Supply Equipment (EVSE)

**Node type:** `energy.ebus.device.evse`
**Node ID:** `evse`

Present when an EV charger is commissioned.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `vendor-name` | string | — | read | EVSE vendor |
| `product-name` | string | — | read | Product name |
| `part-number` | string | — | read | Part number |
| `serial-number` | string | — | read | Serial number |
| `software-version` | string | — | read | Firmware version |
| `feed` | enum | — | read | Circuit ID the EVSE is landed on |
| `lock-state` | enum | — | read | `UNKNOWN`, `LOCKED`, `UNLOCKED` |
| `status` | enum | — | read | `UNKNOWN`, `AVAILABLE`, `PREPARING`, `CHARGING`, `SUSPENDED_EV`, `SUSPENDED_EVSE`, `FINISHING`, `RESERVED`, `FAULTED`, `UNAVAILABLE` |
| `advertised-current` | float | A | read | Current advertised to the EV |

### Power Control System (PCS)

**Node type:** `energy.ebus.device.pcs`
**Node ID:** `pcs`

Manages circuit load shedding based on power import limits.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `enabled` | boolean | — | read | PCS system enabled |
| `active` | boolean | — | read | Actively controlling loads |
| `import-limit` | float | A | read | Current import limit being managed to |
| `feed-import-limit` | float | A | read | Feed maximum import power limit |
| `feed-import-limit-enablement` | enum | — | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `feed-import-limit-active` | boolean | — | read | Feed limit currently enforced |
| `grid-import-limit` | float | A | read | Grid maximum import power limit |
| `grid-import-limit-enablement` | enum | — | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `grid-import-limit-active` | boolean | — | read | Grid limit currently enforced |
| `off-grid-import-limit` | float | A | read | Off-grid maximum import power limit |
| `off-grid-import-limit-enablement` | enum | — | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `off-grid-import-limit-active` | boolean | — | read | Off-grid limit currently enforced |
| `requested-import-limit` | float | A | read | Requested maximum import power limit |
| `requested-import-limit-enablement` | enum | — | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `requested-import-limit-active` | boolean | — | read | Requested limit currently enforced |

### Aggregate Power Flows

**Node type:** `energy.ebus.device.power-flows`
**Node ID:** `power-flows`

Panel-computed aggregate power flows across all sources.

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `pv` | float | W | read | Solar PV power flow |
| `battery` | float | W | read | Battery/BESS power flow |
| `grid` | float | W | read | Grid power flow |
| `site` | float | W | read | Total site power flow |

---

## Summary: Settable (Writable) Properties

Only **3 properties** accept `/set` commands:

| Node Type | Property | Values | Effect |
|---|---|---|---|
| Core | `dominant-power-source` | `GRID`, `BATTERY`, `PV`, `GENERATOR`, `NONE`, `UNKNOWN` | Changes the load-shedding trigger source |
| Circuit | `relay` | `OPEN`, `CLOSED` | Opens or closes a circuit breaker relay |
| Circuit | `shed-priority` | `OFF_GRID`, `SOC_THRESHOLD`, `NEVER` | Changes when a circuit sheds load during off-grid operation |

All other properties are **read-only** and published by the panel.

### Write Topic Examples

```
ebus/5/<device-id>/core/dominant-power-source/set    → "BATTERY"
ebus/5/<device-id>/<circuit-uuid>/relay/set           → "OPEN"
ebus/5/<device-id>/<circuit-uuid>/shed-priority/set   → "NEVER"
```

---

## Energy Direction Convention

Energy direction is defined from the **panel's perspective**:

| Context | `imported-energy` | `exported-energy` |
|---|---|---|
| Upstream lugs | Energy from grid into panel | Energy from panel to grid |
| Downstream lugs | Energy from sub-panel into panel | Energy from panel to sub-panel |
| Circuit | Energy from circuit back to panel (backfeed/generation) | Energy from panel to circuit (consumption) |

For `active-power` on circuits: negative values indicate consumption,
positive values indicate generation (e.g., a PV-feeding circuit).

---

## Schema Endpoint

```
GET /api/v2/homie/schema
```

Returns the full superset of all node types and property definitions as JSON.
No authentication required. Individual panels expose a subset of these node
types based on their hardware configuration and commissioned devices (battery,
PV, EVSE). The per-panel `$description` topic provides the actual node/property
schema for that specific device.

Response includes a `typesSchemaHash` field (e.g., `sha256:d347556a07d98f40`)
for cache validation.
