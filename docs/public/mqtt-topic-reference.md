# SPAN Panel MQTT Topic Reference

This document lists all MQTT topics exposed by the SPAN panel's eBus adapter via the Homie 5 convention, including data types, units, and read/write access.

SPAN API publishes a **parent device** (the panel) and a set of **child devices** (lugs, circuits, and commissioned DERs). Each device organizes its properties into **capability nodes**. See [SPAN Panel MQTT API Capabilities](mqtt-api-overview.md) for the capability-oriented overview.

**Source:** `GET /api/v2/homie/schema` returns the superset of all device classes, capabilities, and property definitions. Individual panels expose a subset based on their hardware configuration and commissioned devices.

**Firmware:** spanos3/r202633
**Homie version:** 5
**Domain:** `ebus`
**Data model version:** 1.0

---

## Topic Structure

All topics follow the Homie 5 convention:

```
ebus/5/<device-id>/$state                          # Device lifecycle state
ebus/5/<device-id>/$description                    # Full device/capability/property schema (JSON)
ebus/5/<device-id>/<capability>/<property>         # Property value (READ)
ebus/5/<device-id>/<capability>/<property>/set     # Property command (WRITE, settable only)
```

- `<device-id>` identifies a single Homie device: the panel, or one of its child devices.
- `<capability>` is a capability node on that device (for example `info`, `meter`, `switch`).
- `<property>` is a property within the capability.

### Devices

The panel is the root (parent) device; its `$description` lists a `children` array of child device IDs. Each child device has its own `$state` and `$description` topics.

| Device class | Device ID form | Notes |
|---|---|---|
| Panel (distribution-enclosure) | `<panel-serial>` | e.g. `nt-2143-c1akc` |
| Lugs | `<panel-serial>-lugs-up`, `<panel-serial>-lugs-dn` | Upstream and downstream lugs |
| Circuit | circuit UUID | e.g. `ac3dccda46a94b98878a227df6fed588` |
| BESS | `<panel-serial>-<bess-serial>` | Proxied; serial normalized to lowercase |
| PV | `<panel-serial>-<pv-identifier>` | Proxied |
| EVSE | `<panel-serial>-<evse-identifier>` | Proxied (SPAN Drive) |
| MID | `<bess-id>-mid` (BESS-integrated) or `<panel-serial>-mid` (panel-integrated) | Microgrid Interconnect Device. SPAN Panel MAIN 32 always emits the BESS-integrated form; the panel-integrated `<panel-serial>-mid` form exists in the eBus data model but is not emitted by current SPAN hardware. |

**Device IDs are opaque.** Classify a device by the `type` field in its `$description`, not by parsing the ID. Vendor serials can contain hyphens, so a device ID cannot be reliably split on `-`.

### Device-Level Topics

| Topic | Payload | Description |
|---|---|---|
| `ebus/5/<device-id>/$state` | `init`, `ready`, `disconnected`, `sleeping`, `lost` | Device lifecycle state |
| `ebus/5/<device-id>/$description` | JSON | Complete schema of the device's capabilities and properties, plus the `children` array on any device that has children (the panel, and a BESS that publishes a MID) |

---

## Device Discovery

The panel publishes a device *tree*, not a flat list, so discovery is recursive:

1. Subscribe to the panel's `$description` and read its `children` array.
2. Subscribe to each child's `$description`. Read its `type` to classify it, and read its own `children` array: a child device can itself be a parent.
3. Repeat step 2 for any newly discovered children until no new devices appear.

A commissioned battery system is the case that matters today: it publishes a MID as its own child, so the MID is a grandchild of the panel and never appears in the panel's `children` array. A consumer that walks only the panel's direct children will not discover the MID or its `grid` capability.

Device types:

- `energy.ebus.device.distribution-enclosure` (the panel; tree root, not listed among its own children)
- `energy.ebus.device.lugs`
- `energy.ebus.device.circuit`
- `energy.ebus.device.bess`
- `energy.ebus.device.pv`
- `energy.ebus.device.evse`
- `energy.ebus.device.mid` (published as a child of the BESS device, not of the panel)

Each capability node in a `$description` carries a `type` of the form `energy.ebus.capability.<name>`.

### DER Topology

The wiring relationship between a DER and the panel is published on the panel-side device that owns the connection point (a circuit or a lugs device) via the `connection` capability. To find what feeds a DER, scan the circuit and lugs children:

- `connection/feeds-device-id == <der-id>`: the matching circuit feeds the DER. Only circuits publish this property; SPAN Panel does not populate `feeds-*` on either lugs device.
- `connection/fed-by-device-id == <der-id>`: the matching (upstream) lugs is fed by the DER (the common case for an upstream BESS).

Mixed-load and unsurveyed circuits publish no `connection` records. The MID does not publish a `connection` record.

Scan for **0, 1, or N** matches per DER class: this is the forward-compatible pattern, and the eBus data model permits N children of a class. SPAN firmware r202633 proxies at most **one** BESS, one PV, and one EVSE, so a scan today returns at most one per class; consumers should still be written to handle N. `connection` records are best-effort: a commissioned DER whose feeding circuit or lugs is not resolved may be published as a child with no `connection` record pointing at it, in which case its wiring position and panel-side link health are not derivable.

---

## Device Lifecycle and State

Device state follows the [Homie 5 Specification](https://homieiot.github.io/specification/). If the panel (root) device's `$state` is `lost`, every child device is effectively `lost` regardless of the child's own `$state`, because the panel's Last Will and Testament sets only the root `$state`. Subscribe to both a device's `$state` and its root's `$state` to determine effective state. A device's `$description` may change only while its `$state` is `init`, `disconnected`, or `lost`; consumers may cache `$description` while a device is `ready`.

---

## Panel: Distribution Enclosure

**Device type:** `energy.ebus.device.distribution-enclosure`
**Device ID:** panel serial number

Properties are **read-only** unless marked **SETTABLE**.

### `info`

**Capability type:** `energy.ebus.capability.info`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `vendor-name` | string | - | read | Vendor name |
| `model` | enum | - | read | `MAIN_16`, `MLO_24`, `MAIN_32`, `MAIN_40`, `MLO_48` |
| `serial-number` | string | - | read | Panel serial number |
| `hardware-version` | string | - | read | Hardware revision |
| `firmware-version` | string | - | read | Firmware version |
| `data-model-version` | string | - | read | eBus data-model version (`1.0`) |

### `door`

**Capability type:** `energy.ebus.capability.door`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `state` | enum | - | read | `UNKNOWN`, `OPEN`, `CLOSED` |

### `status`

**Capability type:** `energy.ebus.capability.status`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `relay` | enum | - | read | Main relay: `UNKNOWN`, `OPEN`, `CLOSED` |
| `ethernet` | boolean | - | read | Ethernet interface operational |
| `wifi` | boolean | - | read | Wi-Fi interface operational |
| `wifi-ssid` | string | - | read | Connected Wi-Fi SSID |
| `cloud-connection` | enum | - | read | `UNKNOWN`, `UNCONNECTED`, `CONNECTED` |
| `postal-code` | string | - | read | Postal / ZIP code |
| `time-zone` | string | - | read | IANA time zone (e.g. `America/Los_Angeles`) |

### `meter`

**Capability type:** `energy.ebus.capability.meter`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `voltage-a` | float | V | read | Line 1 voltage |
| `voltage-b` | float | V | read | Line 2 voltage |

### `breaker`

**Capability type:** `energy.ebus.capability.breaker`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `rating` | integer | A | read | Main breaker rating |

### `pcs`

**Capability type:** `energy.ebus.capability.pcs`

Power Control System (SPAN PowerUp). Manages circuit load based on power import limits.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `enabled` | boolean | - | read | PCS system enabled |
| `active` | boolean | - | read | Actively controlling loads |
| `import-limit` | float | A | read | Current import limit being managed to |
| `binding-constraint` | enum | - | read | Which constraint sets the import limit: `FSR`, `DOE`, `VOLTAGE`, `OFF_GRID`, `REQUESTED`, `OPERATOR`, `NONE`, `UNKNOWN` |
| `feed-import-limit` | float | A | read | Feed maximum import power limit |
| `feed-import-limit-enablement` | enum | - | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `feed-import-limit-active` | boolean | - | read | Feed limit currently enforced |
| `operator-import-limit` | float | A | read | Operator maximum import power limit |
| `operator-import-limit-enablement` | enum | - | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `operator-import-limit-active` | boolean | - | read | Operator limit currently enforced |
| `off-grid-import-limit` | float | A | read | Off-grid maximum import power limit |
| `off-grid-import-limit-enablement` | enum | - | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `off-grid-import-limit-active` | boolean | - | read | Off-grid limit currently enforced |
| `requested-import-limit` | float | A | read | Requested maximum import power limit |
| `requested-import-limit-enablement` | enum | - | read | `UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED` |
| `requested-import-limit-active` | boolean | - | read | Requested limit currently enforced |

### `power-flows`

**Capability type:** `energy.ebus.capability.power-flows`

Panel-computed aggregate power flows across all sources.

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `pv` | float | W | read | Solar PV power flow |
| `battery` | float | W | read | Battery / BESS power flow |
| `grid` | float | W | read | Grid power flow |
| `site` | float | W | read | Total site power flow |

### `shed-forecast`

**Capability type:** `energy.ebus.capability.shed-forecast`

Battery Time Remaining (BTR) forecast. Published only when a BESS is commissioned. All properties read-only.

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `total-time-remaining` | integer | min | read | At current aggregate SOE, time before backed-up circuits drop |
| `time-to-priority-shed` | integer | min | read | At current aggregate SOE, time until the next priority tier is shed |
| `full-charge-total-time-remaining` | integer | min | read | Total backup duration assuming the BESS starts at full charge |
| `full-charge-time-to-priority-shed` | integer | min | read | Time to the next priority shed assuming the BESS starts at full charge |
| `confidence` | enum | - | read | `LOW`, `MEDIUM`, `HIGH` |

### `shed`

**Capability type:** `energy.ebus.capability.shed`

Panel-wide shed controls. Published only when a BESS is commissioned.

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `asserted-islanding-state` | enum | - | **SETTABLE** (`ON_GRID` / `OFF_GRID` only) | `NONE`, `ON_GRID`, `OFF_GRID`. Consumer-asserted islanding-state that overrides the sensed grid-state for load-shedding, accepted only during MID/BESS communication loss. A consumer writes `ON_GRID` or `OFF_GRID`; `NONE` is the panel-authored default that defers to the MID's sensed `islanding-state`, and the panel restores it itself once communication returns. |
| `policy` | json | - | read | Active shed policy. On SPAN panels this is a `soc-priority.v1` object carrying `soc-threshold-shed` and `soc-threshold-release`; the property's `$format` is the policy JSONSchema. |

---

## Lugs

**Device type:** `energy.ebus.device.lugs`
**Device IDs:** `<panel-serial>-lugs-up`, `<panel-serial>-lugs-dn`

The upstream lugs measure power at the grid/utility connection point. The downstream lugs measure power at the sub-panel feed-through point. Not all panels have downstream lugs.

Both lugs devices publish the same `meter` property set, but only `active-power`, `imported-energy`, and `exported-energy` are specific to the lugs device you read them from. The `current-a` and `current-b` values are the panel's service-entrance measurement, republished unchanged on both devices.

> **Deviation from the eBus specification.** The specification defines a `meter` node's `current-{a,b}` as the RMS current on the publishing device's own measured conductors. SPAN Panel publishes its service-entrance current on both lugs devices instead, so on `<panel-serial>-lugs-dn` these two properties do not describe the conductors that device represents.

### `info`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `direction` | enum | - | read | `UPSTREAM`, `DOWNSTREAM` |

### `meter`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `current-a` | float | A | read | Line 1 (leg A) RMS current measured at the panel's service entrance. Not measured per lugs device: the same panel-level value is published on both `<panel-serial>-lugs-up` and `<panel-serial>-lugs-dn`, so it does not describe feedthrough current on the downstream lugs. |
| `current-b` | float | A | read | Line 2 (leg B) RMS current measured at the panel's service entrance. Published identically on both lugs devices, as for `current-a`. |
| `active-power` | float | W | read | Active power through lugs. Unlike `current-a` and `current-b`, this is measured per lugs device. |
| `imported-energy` | float | Wh | read | Cumulative energy imported |
| `exported-energy` | float | Wh | read | Cumulative energy exported |

### `connection`

Panel-side wiring facts. The lugs device class declares both the upstream (`fed-by-*`) and downstream (`feeds-*`) sides, but SPAN Panel populates only the upstream triplet, and only on `<panel-serial>-lugs-up`. The `feeds-*` triplet is declared and left unpublished on both lugs devices, and `<panel-serial>-lugs-dn` publishes no `connection` values at all. Do not treat the absence of a `feeds-*` value on the downstream lugs as evidence that nothing is wired there.

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `fed-by-device-id` | string | - | read | Device ID wired upstream of this lugs |
| `fed-by-device-type` | string | - | read | `$description.type` of the upstream device |
| `fed-by-device-status` | enum | - | read | Panel's view of link health to the upstream device: `OK`, `LOST`, `DEGRADED`. Reflects real link health when the upstream device is a BESS. On a multi-panel cascade, where the upstream device is a sister panel, this is always `OK`, because link-health detection in that direction is not implemented; do not read it as a liveness signal. |
| `feeds-device-id` | string | - | read | Device ID wired downstream of this lugs |
| `feeds-device-type` | string | - | read | `$description.type` of the downstream device |
| `feeds-device-status` | enum | - | read | Panel's view of link health to the downstream device: `OK`, `LOST`, `DEGRADED` |
| `count` | integer | - | read | Number of physical units aggregated as the connected device. Declared in the schema but not published by SPAN Panel in this release, so no value ever appears on the topic. |

---

## Circuit

**Device type:** `energy.ebus.device.circuit`
**Device ID:** circuit UUID

Each circuit breaker space is a separate child device.

### `info`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `name` | string | - | read | User-assigned circuit name |
| `spaces` | string | - | read | Physical panel position(s) the circuit occupies, as a comma-separated list (for example `17,19` for a 2-pole breaker, `5` for a single-pole). Together with `breaker/poles` this identifies every occupied slot without assuming a numbering convention. |

### `switch`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `relay` | enum | - | **SETTABLE** | `UNKNOWN`, `OPEN`, `CLOSED`. Circuit relay state. Settable only when `relay-controllable = true`; otherwise the `$settable` attribute is `false`. |
| `relay-requester` | enum | - | read | Actor that requested the current relay state: `UNKNOWN`, `NONE`, `LOAD_SHED`, `USER`, `PCS`, `CONFIGURATION`, `FAULT` (vendor-extendable via `$format`) |
| `relay-controllable` | boolean | - | read | Whether the relay can be commanded at all |

### `breaker`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `rating` | integer | A | read | Breaker rating |
| `poles` | integer | - | read | Number of breaker poles (format `1:4:1`) |

### `meter`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `current` | float | A | read | Measured current |
| `active-power` | float | W | read | Measured active power |
| `imported-energy` | float | Wh | read | Cumulative energy imported |
| `exported-energy` | float | Wh | read | Cumulative energy exported |

**Circuit direction.** These follow the enclosure-frame convention: a normal load reads **negative** `active-power` and accumulates **`exported-energy`** (power delivered enclosure to circuit); a backfeeding circuit (for example a PV inverter on that breaker) reads positive `active-power` and accumulates `imported-energy`. The reference point is the enclosure busbar, not the branch load, which is the reverse of what the property names alone suggest. See [Power and Energy Conventions](power-and-energy-conventions.md).

### `load-shed`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `priority` | enum | - | **SETTABLE** | `UNKNOWN`, `OFF_GRID`, `SOC_THRESHOLD`, `NEVER`. Load-shed priority when off-grid. Writable values are `OFF_GRID`, `SOC_THRESHOLD`, and `NEVER`: the panel may publish `UNKNOWN`, but a write of `UNKNOWN` is silently ignored and the published value does not change. `$settable` is `false` on a circuit commissioned as never-backup, whose priority is locked at `OFF_GRID`. |

### `pcs`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `managed` | boolean | - | read | Managed by the Power Control System |
| `priority` | integer | - | read | PCS priority ranking |

### `connection`

Circuits publish the downstream (`feeds-*`) side only. The `connection` capability node itself is declared on **every** circuit device, so its presence carries no information: it is the `feeds-*` property values that are populated only when the circuit is dedicated to a specifically-commissioned downstream DER. Test for a value, not for the node, when deciding whether a circuit feeds a known device. (The eBus data model treats an absent `connection` node as "topology unknown"; SPAN Panel does not use that signal, so absence of a value is what carries the meaning here.)

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `feeds-device-id` | string | - | read | Device ID wired downstream of this circuit |
| `feeds-device-type` | string | - | read | `$description.type` of the downstream device |
| `feeds-device-status` | enum | - | read | Panel's view of link health: `OK`, `LOST`, `DEGRADED` |
| `count` | integer | - | read | Number of physical units aggregated as the connected device. Declared in the schema but not published by SPAN Panel in this release, so no value ever appears on the topic. |

---

## Battery Energy Storage System (BESS)

**Device type:** `energy.ebus.device.bess`
**Device ID:** `<panel-serial>-<bess-serial>` (proxied)

Present when a battery system (for example a Tesla Powerwall) is commissioned. A commissioned BESS is proxied by the panel, which also publishes an associated MID. The MID is published as a child of this BESS device, making it a grandchild of the panel, so it does not appear in the panel's own `children` array (see MID below).

### `info`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `vendor-name` | string | - | read | Battery vendor (e.g. `Tesla`) |
| `model` | string | - | read | Human-facing product designation (e.g. `Powerwall 2 AC`) |
| `part-number` | string | - | read | Vendor orderable part / SKU code (e.g. `1232100-00-E`) |
| `serial-number` | string | - | read | Battery serial number |
| `firmware-version` | string | - | read | Battery firmware version |
| `nameplate-capacity` | float | kWh | read | Nameplate energy capacity |

### `soc`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `soc` | float | % | read | State of charge |
| `soe` | float | kWh | read | State of energy |

### `meter`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `active-power` | float | W | read | Battery active power |

### `status`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `communication-state` | enum | - | read | `OK`, `DEGRADED`, `LOST`, `UNKNOWN`. The publisher's self-reported communication state |

---

## Photovoltaic System (PV)

**Device type:** `energy.ebus.device.pv`
**Device ID:** `<panel-serial>-<pv-identifier>` (proxied)

Present when a solar PV system is commissioned.

### `info`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `vendor-name` | string | - | read | PV vendor (e.g. `Enphase Energy`) |
| `model` | string | - | read | Human-facing product designation (e.g. `IQ7PLUS-72-x-US`) |
| `serial-number` | string | - | read | Inverter serial number |
| `firmware-version` | string | - | read | Inverter firmware version |
| `nominal-power` | float | W | read | Rated power (rated DC array power for a PV system) |

---

## Electric Vehicle Supply Equipment (EVSE)

**Device type:** `energy.ebus.device.evse`
**Device ID:** `<panel-serial>-<evse-identifier>` (proxied)

Present when an EV charger (SPAN Drive) is commissioned.

### `info`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `vendor-name` | string | - | read | EVSE vendor |
| `model` | string | - | read | Human-facing product designation |
| `part-number` | string | - | read | Vendor orderable part / SKU code |
| `serial-number` | string | - | read | Serial number |
| `firmware-version` | string | - | read | Firmware version |

### `switch`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `lock-state` | enum | - | read | `UNLOCKED`, `LOCKED` |

### `status`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `status` | enum | - | read | `AVAILABLE`, `PREPARING`, `CHARGING`, `UNAVAILABLE` |

### `meter`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `advertised-current` | float | A | read | Current advertised to the EV |

### `config`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `max-charge-current` | integer | A | read | Installer-configured maximum charge current (breaker rating and J1772 derating) |
| `user-max-charge-current` | integer | A | **SETTABLE** | User-configured charge-current ceiling. Accepted range is 6 A (the J1772 minimum charge rate) up to `max-charge-current`, and the panel publishes that range as this property's `$format`. A value outside the range is not rejected: it is silently clamped to the nearest bound. A payload that is not an integer is discarded, and the published value does not change. |

Because a clamped write is not reported back as an error, read the property after writing it to learn what was actually applied. Before the panel has learned the commissioned maximum (a brief window at startup), only the lower bound is enforced.

> **Deviation from the eBus specification.** The specification constrains the user ceiling to be less than or equal to the installer maximum and defines no lower bound. SPAN Panel additionally enforces the 6 A J1772 floor, and it satisfies both bounds by clamping rather than by rejecting the write.

---

## Microgrid Interconnect Device (MID)

**Device type:** `energy.ebus.device.mid`
**Device ID:** `<bess-id>-mid` (BESS-integrated) or `<panel-serial>-mid` (panel-integrated)

Manages the electrical boundary between the grid and the home during islanding. For SPAN Panel MAIN 32, every commissioned (and therefore proxied) BESS publishes a MID in the BESS-integrated form (`<bess-id>-mid`); the panel-integrated `<panel-serial>-mid` form exists in the eBus data model but is not emitted by current SPAN hardware. The MID is a child of the BESS device, not of the panel, so reach it by walking the BESS device's `children` array rather than the panel's.

### `info`

| Property | Type | Unit | Access | Description |
|---|---|---|---|---|
| `vendor-name` | string | - | read | Vendor name |
| `serial-number` | string | - | read | Serial number |
| `model` | string | - | read | Human-facing product designation |
| `firmware-version` | string | - | read | Firmware version |
| `hardware-version` | string | - | read | Hardware version |

### `grid`

| Property | Type | Unit | Access | Format / Description |
|---|---|---|---|---|
| `islanding-state` | enum | - | read | `ON_GRID`, `OFF_GRID`, `UNKNOWN`. The MID's relay position (electrically connected to the utility?) |
| `grid-state` | enum | - | read | `UP`, `DOWN`, `DEGRADED`, `UNKNOWN`. Sensed condition of the utility supply, independent of `islanding-state`. On SPAN Panel this property is always `UNKNOWN`: the panel has no upstream-grid sensor on the MID it synthesizes, so it cannot observe the utility supply independently of the battery system's own connection state. Do not write logic that branches on `UP` or `DOWN` here; use `islanding-state` for the relay position. |
| `grid-forming-entity` | string | - | read | Device establishing the AC voltage/frequency reference: `"GRID"` when grid-tied, or the Homie device ID of the grid-forming DER when islanded |

---

## Summary: Settable (Writable) Properties

Exactly **4 properties** accept `/set` commands:

| Device | Capability | Property | Values | Effect |
|---|---|---|---|---|
| Circuit | `switch` | `relay` | `OPEN`, `CLOSED` | Opens or closes a circuit relay (when `relay-controllable = true`) |
| Circuit | `load-shed` | `priority` | `OFF_GRID`, `SOC_THRESHOLD`, `NEVER` | Changes when a circuit sheds load during off-grid operation |
| Panel | `shed` | `asserted-islanding-state` | `ON_GRID`, `OFF_GRID` | Consumer override of the sensed islanding-state, accepted only during MID/BESS comm loss (`NONE` is panel-authored and cannot be set) |
| EVSE | `config` | `user-max-charge-current` | integer (A), 6 to `max-charge-current` | Sets the user charge-current ceiling; out-of-range values are clamped to the nearest bound, and non-integer payloads are discarded |

All other properties are read-only.

### Write Topic Examples

```
ebus/5/<circuit-uuid>/switch/relay/set                 → "OPEN"
ebus/5/<circuit-uuid>/load-shed/priority/set           → "NEVER"
ebus/5/<panel-serial>/shed/asserted-islanding-state/set → "ON_GRID"
ebus/5/<evse-id>/config/user-max-charge-current/set    → "24"
```

---

## Energy and Power Sign Conventions

All `imported-energy`, `exported-energy`, and `active-power` properties follow a single panel-perspective convention. See [Power and Energy Conventions](power-and-energy-conventions.md) for the full reference: per-context meaning, sign rules, and a worked example.

---

## Schema Endpoint

```
GET /api/v2/homie/schema
```

Returns the full superset of device classes, capabilities, and property definitions as JSON. No authentication required. The response includes `dataModelVersion` (`1.0`), `homieDomain` (`ebus`), `homieVersion` (`5`), `firmwareVersion`, the `deviceClasses` schema (device class to capability to property), and a `deviceClassesSchemaHash` for cache validation. Individual panels expose a subset of these device classes and capabilities based on hardware configuration and commissioned devices. The per-device `$description` topic provides the actual schema for each specific device.
