# SPAN API Migration Guide: Flat to Parent/Child Data Model

**Audience:** Consumers of SPAN API (eBus / Homie 5 over MQTT)
**Data model version:** 1.0
**Firmware:** r202633 and later (fleet rollout projected, not committed, for the first two weeks of September 2026)

## eBus and This Guide

SPAN API adopts the [Electrification Bus (eBus) specification](https://github.com/electrification-bus/specification), an open, vendor-neutral Homie 5 data model for Home Energy Infrastructure (HEI) devices. eBus defines the generic device-class and capability contracts; this guide describes SPAN's concrete implementation of them at `data_model_version 1.0`, including exactly what a SPAN panel publishes.

SPAN API has always tracked the eBus specification: the flat schema was SPAN's faithful implementation of the earlier eBus data model. The eBus data model has since matured to this parent/child and capability structure, and SPAN API v1.0 tracks that evolution, so a client written to the eBus contracts targets an open, community-maintained standard with cross-vendor reach.

SPAN API is an implementation of the eBus [`distribution-enclosure`](https://github.com/electrification-bus/specification/blob/main/devices/distribution-enclosure.md) data model. Its child devices implement the eBus [`circuit`](https://github.com/electrification-bus/specification/blob/main/devices/circuit.md) and [`bess`](https://github.com/electrification-bus/specification/blob/main/devices/bess.md) data models, and the panel uses the eBus [`proxy`](https://github.com/electrification-bus/specification/blob/main/devices/proxy.md) model to publish DERs (BESS, PV, EVSE) on their behalf until each represents itself on eBus. The `energy.ebus.device.*` and `energy.ebus.capability.*` type strings are registered in the eBus [device-types](https://github.com/electrification-bus/specification/blob/main/registries/device-types.md) and [capability-types](https://github.com/electrification-bus/specification/blob/main/registries/capability-types.md) registries.

Each panel and child capability node implements the correspondingly-named eBus capability: [`info`](https://github.com/electrification-bus/specification/blob/main/capabilities/info.md), [`meter`](https://github.com/electrification-bus/specification/blob/main/capabilities/meter.md), [`breaker`](https://github.com/electrification-bus/specification/blob/main/capabilities/breaker.md), [`switch`](https://github.com/electrification-bus/specification/blob/main/capabilities/switch.md), [`load-shed`](https://github.com/electrification-bus/specification/blob/main/capabilities/load-shed.md), [`pcs`](https://github.com/electrification-bus/specification/blob/main/capabilities/pcs.md), [`connection`](https://github.com/electrification-bus/specification/blob/main/capabilities/connection.md), [`door`](https://github.com/electrification-bus/specification/blob/main/capabilities/door.md), [`status`](https://github.com/electrification-bus/specification/blob/main/capabilities/status.md), [`soc`](https://github.com/electrification-bus/specification/blob/main/capabilities/soc.md), [`grid`](https://github.com/electrification-bus/specification/blob/main/capabilities/grid.md), [`power-flows`](https://github.com/electrification-bus/specification/blob/main/capabilities/power-flows.md), [`shed`](https://github.com/electrification-bus/specification/blob/main/capabilities/shed.md), and [`shed-forecast`](https://github.com/electrification-bus/specification/blob/main/capabilities/shed-forecast.md). The EVSE `config` capability is SPAN-specific.

## Summary of Changes

SPAN API eBus representation is being restructured from a **single Homie device with many nodes** to a **parent device with child devices**, and the panel's own properties are reorganized into **capability nodes**. This is a breaking change to the MQTT topic structure. Throughout this guide, the **flat** schema is the single-device model published by SPAN API releases **r202603 through r202627** (it carries no `data-model-version`), and the **v1.0** schema is the new parent/child model introduced in **r202633** (it publishes `data_model_version 1.0`).

**Key changes:**

- Circuits, lugs, BESS, PV, EVSE, and the MID become **devices** in a tree (each with its own Homie device ID) instead of nodes on a single panel device. All of them are direct children of the panel except the MID, which is a child of the BESS and therefore a grandchild of the panel.
- The panel's `core` node is split into **capability nodes** on the panel device: `info`, `door`, `status`, `meter`, `breaker`, and `pcs`. The panel also carries the `power-flows`, `shed-forecast`, and `shed` capabilities.
- Node types are renamed from `energy.ebus.device.*` to `energy.ebus.capability.*` to reflect that nodes represent capabilities, not devices. The panel device type stays `energy.ebus.device.distribution-enclosure`.
- Several property names are standardized (for example `l1-voltage` / `l2-voltage` become `voltage-a` / `voltage-b`; `software-version` becomes `firmware-version`).
- **Wiring relationships move to a new `connection` capability on circuits and lugs.** The `feed` property on lugs and DER children is retired; `relative-position` on DER children is retired (derivable from connection records); the panel's view of communication-link health to a DER (`bess/connected` in the flat schema) becomes a `connection/feeds-device-status` or `connection/fed-by-device-status` enum on the panel-side connection owner.
- **`dominant-power-source` is split.** Its grid-forming-source identity becomes `grid-forming-entity` (string, read-only) on the MID's `grid` capability; its settable override role becomes `asserted-islanding-state` (enum, settable) on the panel's new `shed` capability.
- **Per-circuit shed configuration consolidates.** The flat `shed-priority` enum plus three booleans (`sheddable`, `never-backup`, `always-on`) become the `load-shed/priority` enum (with its Homie `$settable` attribute) plus one `switch/relay-controllable` boolean. The circuit `relay-requester` enum is reframed as source attribution with a canonical value set.
- **New panel `shed-forecast` capability** publishes Battery Time Remaining (BTR) forecast values when a BESS is commissioned.
- **New panel `shed` capability** carries the consumer-asserted islanding-state override and the SoC-based shed policy.
- **EVSE child gains a `config` capability** with `max-charge-current` (read-only, installer cap) and `user-max-charge-current` (settable, user ceiling).
- **Every BESS child publishes a MID child device** carrying the grid / islanding state. When the underlying hardware does not present a separable MID, the panel synthesizes one.

**What stays the same:**

- Homie 5 convention, the `ebus` domain, and the MQTT broker endpoints (ports 8883, 9001, 9002).
- Property datatypes, units, and values except where noted below.
- Authentication and broker permissions model.
- The `$state` and `$description` topic semantics, per the [Homie 5 Specification](https://homieiot.github.io/specification/).
- The panel `power-flows` capability (`pv`, `battery`, `grid`, `site`), with unchanged topics.

---

## Structural Change: Nodes to Child Devices

### Flat schema

Everything is a node on a single device. All topics share one device ID (the panel serial):

```
ebus/5/<panel>/core/<property>
ebus/5/<panel>/lugs-upstream/<property>
ebus/5/<panel>/<circuit-uuid>/<property>
ebus/5/<panel>/bess/<property>
```

### v1.0 schema (parent/child)

Circuits, lugs, and DER devices are separate Homie devices with their own device IDs. Panel properties are organized into capability nodes:

```
ebus/5/<panel>/info/<property>              was core
ebus/5/<panel>/door/<property>              was core
ebus/5/<panel>-lugs-up/meter/<property>     was lugs-upstream
ebus/5/<circuit-uuid>/meter/<property>      was <circuit-uuid>
ebus/5/<bess-id>/soc/<property>             was bess
```

**Token convention for this guide:** `<panel>` is the panel's serial-number device ID (for example `nt-2143-c1akc`). `<panel>-lugs-up` and `<panel>-lugs-dn` are *separate* Homie devices whose IDs are derived from the panel serial by suffix. `<bess-id>`, `<pv-id>`, `<evse-id>`, and the MID device ID are also separate child devices; their ID forms are given in the Device ID Stability section near the end. Anywhere `<panel>-...` or `<...-id>` appears as a topic prefix, that is a distinct child-device topic tree.

### Discovering Child Devices

Previously, all nodes were listed in the panel's `$description`. Now, child devices are listed in the `children` array of the panel's `$description`:

```json
{
  "name": "SPAN Panel",
  "type": "energy.ebus.device.distribution-enclosure",
  "children": [
    "nt-2143-c1akc-lugs-up",
    "nt-2143-c1akc-lugs-dn",
    "nt-2143-c1akc-tg121153003k7g",
    "ac3dccda46a94b98878a227df6fed588",
    "..."
  ],
  "nodes": { "...": "panel capability nodes" }
}
```

Each child device has its own `$state` and `$description` topics. Every child's `$description` includes an authoritative `type` field and a `parent` back-reference:

```json
{
  "type": "energy.ebus.device.circuit",
  "name": "Ovens",
  "root": "nt-2143-c1akc",
  "parent": "nt-2143-c1akc",
  "nodes": { "...": "capability nodes" }
}
```

A child device can itself be a parent. A commissioned energy storage system (BESS) publishes a synthesized **MID** (Microgrid Interconnect Device) as *its own* child, so the MID is a grandchild of the panel: it appears in the BESS's `children` array (with its `parent` back-reference pointing at the BESS), not in the panel's `children` array. The BESS's `$description`:

```json
{
  "type": "energy.ebus.device.bess",
  "name": "Energy Storage System",
  "root": "nt-2143-c1akc",
  "parent": "nt-2143-c1akc",
  "children": [
    "nt-2143-c1akc-tg121153003k7g-mid"
  ],
  "nodes": { "...": "capability nodes" }
}
```

```
ebus/5/ac3dccda46a94b98878a227df6fed588/$state
ebus/5/ac3dccda46a94b98878a227df6fed588/$description
```

**Important:** Identify child device classes by reading the `type` field in each child's `$description`, not by parsing device ID format or naming conventions. All device classes use the same discovery model: subscribe to the child's `$description` and read its `type`. Treat every device ID as opaque. This matters for proxied devices whose IDs embed a vendor serial or product identifier (for example a proxied BESS ID `<panel>-tg121153003k7g`): the ID cannot be reliably split on `-` to recover its components, so classification must come from `$description.type`.

---

## Subscription Pattern Changes

### Subscribing to All Panel Data

**Flat:**

```
ebus/5/<panel>/#
```

This single wildcard captured everything: core, circuits, lugs, BESS, all in one subscription.

**v1.0:**

```
ebus/5/<panel>/#                    panel-level capabilities only
ebus/5/<panel>-lugs-up/#            upstream lugs
ebus/5/<panel>-lugs-dn/#            downstream lugs
ebus/5/<circuit-uuid>/#             per circuit (subscribe individually)
ebus/5/<bess-id>/#                  per DER child
```

To discover all children dynamically, subscribe to the panel's `$description`, parse the `children` array, then subscribe to each child's topics.

### Subscribing to All Circuits

Each circuit is its own device. Subscribe per-circuit, using the `$description` children list to discover circuit device IDs and filtering by `type: "energy.ebus.device.circuit"`.

### Subscribing to a Specific Circuit

**Flat:**

```
ebus/5/<panel>/<circuit-uuid>/+
```

**v1.0:**

```
ebus/5/<circuit-uuid>/+/+
```

The circuit UUID is now the **device ID**, not a node under the panel.

### Subscribing to Settable Property Commands

**Flat:**

```
ebus/5/<panel>/<circuit-uuid>/relay/set
ebus/5/<panel>/<circuit-uuid>/shed-priority/set
ebus/5/<panel>/core/dominant-power-source/set
```

**v1.0:**

```
ebus/5/<circuit-uuid>/switch/relay/set
ebus/5/<circuit-uuid>/load-shed/priority/set
ebus/5/<panel>/shed/asserted-islanding-state/set
ebus/5/<evse-id>/config/user-max-charge-current/set
```

The flat `dominant-power-source/set` topic is removed. Its settable override role is now `<panel>/shed/asserted-islanding-state` (see Shed Controls). Its grid-forming-source identity becomes a read-only property on the MID (see MID to Child Device).

### Discovering DER Topology

The wiring relationship between a DER child and the panel is no longer published on the DER child. Instead, it is published on the panel-side device that physically owns the connection point (a circuit or a lugs device) via the new `connection` capability. To find which circuit or lugs feeds a particular DER:

1. Subscribe to the panel's `$description` and walk the `children` array.
2. For each circuit and lugs child, read the `connection` capability. A downstream connection is described by `feeds-device-id` / `feeds-device-type` / `feeds-device-status`; an upstream connection (for example an upstream BESS feeding the panel through the main lugs) is described by `fed-by-device-id` / `fed-by-device-type` / `fed-by-device-status`.
3. A consumer scan returns 0, 1, or N matches for any given DER class. The eBus data model scales to N DERs without per-class panel-level properties, and the 0/1/N scan is the forward-compatible way to consume DER children. Note that SPAN firmware r202633 proxies at most **one** BESS, one PV, and one EVSE, so a scan today returns at most one child per class; consumers should still be written to handle N.

Absent properties mean "the publisher does not know" or "not applicable." Mixed-load circuits and unsurveyed circuits both look the same: no `connection/feeds-*` is published. Most residential branch circuits are in this state; only circuits dedicated to a specifically-commissioned DER carry connection records.

**Connection records are best-effort.** They are populated only when the panel resolves a commissioned DER to a concrete circuit or lugs. A DER can be commissioned and published as a child while no circuit or lugs record references it (an unresolved feed, or an upstream-of-panel arrangement). For such a DER, `relative-position` and the panel-side link-health signal are not derivable; treat the absence of any referencing `connection` record as "position unknown", not as a specific topology. Likewise, absence of `fed-by-device-id` on the upstream lugs is ambiguous between "the utility feeds this" and "the upstream device is unknown" (the utility is not modeled as an eBus device); do not read it as a positive "utility" assertion.

---

## Complete Property Migration Map

The eBus specification (see eBus and This Guide) defines each capability's generic contract; the tables below give SPAN's concrete v1.0 topics and note where a published name, datatype, or value differs from the flat schema.

### Panel Core to Panel Capabilities

The `core` node is split into `info`, `door`, `status`, `meter`, `breaker`, and `pcs` capability nodes on the panel device.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/core/vendor-name` | `<panel>/info/vendor-name` | |
| `<panel>/core/serial-number` | `<panel>/info/serial-number` | |
| `<panel>/core/hardware-version` | `<panel>/info/hardware-version` | |
| `<panel>/core/software-version` | `<panel>/info/firmware-version` | Renamed to `firmware-version` |
| *(none)* | `<panel>/info/model` | Panel model enum: `MAIN_16`, `MLO_24`, `MAIN_32`, `MAIN_40`, `MLO_48` |
| *(none)* | `<panel>/info/data-model-version` | eBus data-model version string (`1.0`); its presence is the schema discriminator (see Client Migration Strategy) |
| `<panel>/core/door` | `<panel>/door/state` | Moved to the `door` capability; renamed to `state`; enum `UNKNOWN`, `OPEN`, `CLOSED` |
| `<panel>/core/relay` | `<panel>/status/relay` | Enum `UNKNOWN`, `OPEN`, `CLOSED` |
| `<panel>/core/l1-voltage` | `<panel>/meter/voltage-a` | Renamed |
| `<panel>/core/l2-voltage` | `<panel>/meter/voltage-b` | Renamed |
| `<panel>/core/breaker-rating` | `<panel>/breaker/rating` | Moved to the new `breaker` capability; renamed to `rating` (integer A) |
| `<panel>/core/grid-islandable` | **retired** | Not published in v1.0. Off-grid capability is derivable from the MID `grid` capability and the panel's capability set; SPAN keeps the value internally, where it still drives backup commissioning. |
| `<panel>/core/dominant-power-source` | `<mid-id>/grid/grid-forming-entity` **and** `<panel>/shed/asserted-islanding-state` | **Split into two properties.** The identity half becomes `grid-forming-entity` (string, read-only) on the MID's `grid` capability; the settable-override half becomes `asserted-islanding-state` (enum, settable) on the panel's `shed` capability. See MID to Child Device and Shed Controls. |
| `<panel>/core/ethernet` | `<panel>/status/ethernet` | |
| `<panel>/core/wifi` | `<panel>/status/wifi` | |
| `<panel>/core/wifi-ssid` | `<panel>/status/wifi-ssid` | |
| `<panel>/core/vendor-cloud` | `<panel>/status/cloud-connection` | Renamed; enum `UNKNOWN`, `UNCONNECTED`, `CONNECTED` |
| `<panel>/core/postal-code` | `<panel>/status/postal-code` | |
| `<panel>/core/time-zone` | `<panel>/status/time-zone` | |

### Lugs to Child Devices

Lugs become child devices with `info`, `meter`, and `connection` capabilities.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/lugs-upstream/direction` | `<panel>-lugs-up/info/direction` | Enum `UPSTREAM`, `DOWNSTREAM` |
| `<panel>/lugs-upstream/feed` | `<panel>-lugs-up/connection/fed-by-device-id` (+ `-type`, `-status`) | **Relocated to the `connection` capability.** Populated when the publisher knows the upstream device (typical for an upstream BESS or an upstream sister panel); omitted when the upstream side is the utility, which is not modeled as an eBus device. |
| `<panel>/lugs-upstream/l1-current` | `<panel>-lugs-up/meter/current-a` | Renamed |
| `<panel>/lugs-upstream/l2-current` | `<panel>-lugs-up/meter/current-b` | Renamed |
| `<panel>/lugs-upstream/active-power` | `<panel>-lugs-up/meter/active-power` | |
| `<panel>/lugs-upstream/imported-energy` | `<panel>-lugs-up/meter/imported-energy` | |
| `<panel>/lugs-upstream/exported-energy` | `<panel>-lugs-up/meter/exported-energy` | |
| `<panel>/lugs-downstream/direction` | `<panel>-lugs-dn/info/direction` | |
| `<panel>/lugs-downstream/feed` | `<panel>-lugs-dn/connection/feeds-device-id` (+ `-type`, `-status`) | **Relocated to the `connection` capability.** Populated when the publisher knows what is fed through the lugs (for example a downstream DER on a feedthrough path). |
| `<panel>/lugs-downstream/l1-current` | `<panel>-lugs-dn/meter/current-a` | Renamed |
| `<panel>/lugs-downstream/l2-current` | `<panel>-lugs-dn/meter/current-b` | Renamed |
| `<panel>/lugs-downstream/active-power` | `<panel>-lugs-dn/meter/active-power` | |
| `<panel>/lugs-downstream/imported-energy` | `<panel>-lugs-dn/meter/imported-energy` | |
| `<panel>/lugs-downstream/exported-energy` | `<panel>-lugs-dn/meter/exported-energy` | |

### Circuits to Child Devices

Each circuit becomes its own device. Properties are split into `info`, `switch`, `breaker`, `meter`, `load-shed`, `pcs`, and `connection` capabilities. `<circuit>` below is the circuit UUID (for example `ac3dccda46a94b98878a227df6fed588`), which was a node ID under the panel in the flat schema and is now the child device ID.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/<circuit>/name` | `<circuit>/info/name` | Read-only. There is no circuit rename over eBus. |
| `<panel>/<circuit>/relay` | `<circuit>/switch/relay` | Settable only when `<circuit>/switch/relay-controllable = true`. When `relay-controllable = false`, the `relay` property's `$settable` attribute is also `false`. Enum `UNKNOWN`, `OPEN`, `CLOSED`. |
| `<panel>/<circuit>/relay-requester` | `<circuit>/switch/relay-requester` | Enum reframed as source attribution with a canonical set (`UNKNOWN`, `NONE`, `LOAD_SHED`, `USER`, `PCS`, `CONFIGURATION`, `FAULT`). Vendors MAY extend via Homie `$format`. Per-value mapping is in the Relay-Requester Enum Migration subsection below. |
| *(new)* | `<circuit>/switch/relay-controllable` | Boolean. `true` = the relay can be commanded. `false` = the relay is locked closed and no path can open it. Drives the `switch/relay` `$settable` attribute. Equals the panel's existing REST `isUserControllable` field (`!alwaysOn`). |
| `<panel>/<circuit>/breaker-rating` | `<circuit>/breaker/rating` | Moved to the new `breaker` capability; renamed to `rating` (integer A) |
| `<panel>/<circuit>/dipole` | `<circuit>/breaker/poles` | Moved to the `breaker` capability; datatype changes boolean to integer pole count (format `1:4:1`) |
| `<panel>/<circuit>/current` | `<circuit>/meter/current` | |
| `<panel>/<circuit>/active-power` | `<circuit>/meter/active-power` | Value and sign unchanged from flat. Panel-perspective: a load reads **negative**. See the direction note below. |
| `<panel>/<circuit>/imported-energy` | `<circuit>/meter/imported-energy` | Value unchanged from flat. Panel-perspective: accumulates circuit-to-panel backfeed. See the direction note below. |
| `<panel>/<circuit>/exported-energy` | `<circuit>/meter/exported-energy` | Value unchanged from flat. Panel-perspective: a load accumulates here (panel-to-circuit). See the direction note below. |

**Circuit energy direction (unchanged from flat, but read carefully).** SPAN publishes circuit `meter` power and energy from the **distribution enclosure's** reference direction: a consuming load reads **negative** `active-power` and accumulates **`exported-energy`** (energy delivered enclosure-to-circuit); a backfeeding circuit (PV on that breaker) reads positive `active-power` and accumulates `imported-energy`. This is the enclosure frame, the same frame as the feed lugs and the service entrance: every terminal reports power flowing *into* the enclosure, so the enclosure's power balance closes as a signed sum, and in a single-feed panel the hosted circuits' `active-power` sums to the negative of the service-feed reading, with no per-terminal sign flip. It can surprise a reader who expects a branch circuit's own consumption to read positive; on a SPAN enclosure the reference point is the enclosure busbar, not the branch load. The direction did not change between flat and v1.0 (the mapping is a value-preserving pass-through), so a consumer already reading flat circuit energy correctly needs no change. This is the eBus enclosure reference direction, defined in the eBus [`distribution-enclosure`](https://github.com/electrification-bus/specification/blob/main/devices/distribution-enclosure.md#enclosure-specific-meter-reference-direction) and [`meter`](https://github.com/electrification-bus/specification/blob/main/capabilities/meter.md#sign-convention-reference-direction) specs, which SPAN implements. See [Power and Energy Conventions](power-and-energy-conventions.md).
| `<panel>/<circuit>/space` | `<circuit>/info/spaces` | Moved to `info` and **renamed to `spaces`**; datatype changes integer to string, and it becomes multi-valued (comma-separated positions, for example `17,19`) so a multi-pole breaker names every slot it occupies. The flat `space` was a single integer; recover a multi-pole circuit's positions from `spaces` (with `breaker/poles`) rather than assuming a +2 split-phase step. |
| `<panel>/<circuit>/shed-priority` | `<circuit>/load-shed/priority` | Moved to the `load-shed` capability; renamed to `priority`. Enum `UNKNOWN`, `OFF_GRID`, `SOC_THRESHOLD`, `NEVER`, of which `OFF_GRID`, `SOC_THRESHOLD`, and `NEVER` are writable; a write of `UNKNOWN` is silently ignored. `$settable` is `false` on a circuit commissioned as never-backup. |
| `<panel>/<circuit>/pcs-managed` | `<circuit>/pcs/managed` | Moved to the circuit's own `pcs` capability; renamed to `managed` (boolean) |
| `<panel>/<circuit>/pcs-priority` | `<circuit>/pcs/priority` | Moved to the circuit's `pcs` capability; renamed to `priority` (integer) |
| `<panel>/<circuit>/sheddable` | **retired** | Redundant with `priority`. A consumer that wants the old `sheddable` semantic computes `load-shed/priority != NEVER && switch/relay-controllable`. |
| `<panel>/<circuit>/never-backup` | **retired** | Expressed via the Homie `$settable` attribute on `load-shed/priority`: the panel publishes `$settable = !never-backup` (locked when the circuit was commissioned as never-backup). |
| `<panel>/<circuit>/always-on` | **retired** | Expressed via `switch/relay-controllable`: the panel publishes `relay-controllable = !always-on`. |
| *(new)* | `<circuit>/connection/feeds-device-id` (+ `-type`, `-status`) | Published when the circuit is dedicated to a specifically-commissioned downstream DER. See Capability Type Semantics for the full `connection` catalog. Mixed-load and unsurveyed circuits omit these properties. The capability also declares `count`, which SPAN Panel does not publish in this release. |

### Worked Example: Per-Circuit Shed-Config Migration

The four flat mechanisms on each circuit (`shed-priority`, `sheddable`, `never-backup`, `always-on`) consolidate to two v1.0 mechanisms (`load-shed/priority` with its Homie `$settable` attribute, and `switch/relay-controllable`). The mapping is **per-property**, not per-combination: the three flat booleans are independent commissioning inputs stored as separate fields in each circuit's commissioning state, so the derivation is a simple per-input rule.

| Flat property | v1.0 mapping | Rule |
|---|---|---|
| `shed-priority` (enum) | `<circuit>/load-shed/priority` (value unchanged) | Enum values carry forward: `UNKNOWN`, `OFF_GRID`, `SOC_THRESHOLD`, `NEVER`. |
| `never-backup` (boolean) | `<circuit>/load-shed/priority`'s `$settable` attribute | Published with `$settable = !never-backup`. Locked-priority circuits (commissioned permanently OFF_GRID) appear as `priority = OFF_GRID, $settable = false`; user-configurable circuits appear as `$settable = true`. |
| `always-on` (boolean) | `<circuit>/switch/relay-controllable` (new) | `relay-controllable = !always-on`. When `relay-controllable = false`, the `<circuit>/switch/relay` property's `$settable` attribute is also `false`. |
| `sheddable` (boolean) | *(retired, no new property)* | Compute `load-shed/priority != NEVER && switch/relay-controllable`. |

**Consumer translation summary:**

- Where it read `<panel>/<circuit>/shed-priority`, it now reads `<circuit>/load-shed/priority` (same enum values).
- Where it read `<panel>/<circuit>/never-backup`, it now reads the Homie `$settable` attribute on `<circuit>/load-shed/priority` (inverted: `never-backup = true` corresponds to `$settable = false`).
- Where it read `<panel>/<circuit>/always-on`, it now reads `<circuit>/switch/relay-controllable` (inverted: `always-on = true` corresponds to `relay-controllable = false`).
- Where it read `<panel>/<circuit>/sheddable`, it now computes `<circuit>/load-shed/priority != NEVER && <circuit>/switch/relay-controllable`.

### Relay-Requester Enum Migration

The `relay-requester` enum (`<circuit>/switch/relay-requester`, the source-attribution property) uses a canonical, vendor-neutral set: `UNKNOWN`, `NONE`, `LOAD_SHED`, `USER`, `PCS`, `CONFIGURATION`, `FAULT`. Per-value migration of any previously-published value:

| Flat value | v1.0 value | Note |
|---|---|---|
| `USER` | `USER` | Unchanged. |
| `BACKUP` | `LOAD_SHED` | Renamed, matching the load-shed vocabulary. |
| `PCS` | `PCS` | Unchanged. |
| `PCS_FAIL_SAFE` | `PCS` | Consolidated. The fail-safe variant is a sub-mode of the PCS actor. Vendors MAY publish the finer distinction via Homie `$format`. |
| `INVERTER` | `PCS` | Consolidated. The flat `INVERTER` value identified off-grid CSL enforcement, a PCS-driven event. |
| `NEVER_BACKUP` | `CONFIGURATION` | The commissioning lock is now expressed structurally via `load-shed/priority = OFF_GRID` with `$settable = false`; `CONFIGURATION` captures the source attribution. |
| `ALWAYS_ON` | `CONFIGURATION` | The lock-closed semantic is now expressed structurally via `switch/relay-controllable = false`; `CONFIGURATION` captures the source attribution. |
| `FAULT` | `FAULT` | Unchanged. |
| `NONE` | `NONE` | Unchanged. |
| `UNKNOWN` | `UNKNOWN` | Unchanged. |

`relay-requester` is observed, not settable.

### MID to Child Device

Any home with a battery energy storage system (BESS) requires a Microgrid Interconnect Device (MID): the device that manages the electrical boundary between the grid and the home during islanding events. Today the MID is typically integrated into the BESS product (for example built into the Tesla Powerwall or the Enphase IQ System Controller). SPAN models the MID as a separate entity in the eBus data model, because it is a distinct physical function regardless of which product houses it.

The MID is the canonical home for grid-connection state, islanding state, and the grid-forming-entity identity (the property the flat schema called `dominant-power-source` on the panel core). Where the MID appears in the device hierarchy depends on who owns the hardware:

- **SPAN Panel with a built-in MID module:** the panel publishes the MID as a direct panel child device (`<panel-serial>-mid`). This model exists in the eBus data model but is not exercised by current SPAN hardware: SPAN Panel MAIN 32 has no built-in MID module.
- **BESS includes the MID and the panel proxies the BESS:** the panel proxies the MID as a child of the proxied BESS device.
- **BESS represents itself on eBus (with its own MID):** the BESS publishes the MID as its own child device; the panel does not publish a MID in this case.

A conformant BESS publisher includes a MID child device. When the underlying hardware does not present a separable MID, the publisher synthesizes one: the panel-side load-shedding integration is the foundation of the SPAN backup product, so the panel always has enough state to populate the synthetic MID's grid properties.

**Device type:** `energy.ebus.device.mid`
**Capabilities:** `info` (identity and metadata) and `grid` (grid connection state, islanding state, and grid-forming-entity).

**`grid` capability properties:**

| Property | Datatype | Description |
|---|---|---|
| `islanding-state` | enum | Operational state: `ON_GRID`, `OFF_GRID`, `UNKNOWN`. Reflects the MID's relay position (is the home electrically connected to the utility). |
| `grid-state` | enum | Sensed grid condition: `UP`, `DOWN`, `DEGRADED`, `UNKNOWN`. In the data model this reflects what the MID senses about the grid itself, independently of `islanding-state`: a system can be `OFF_GRID` with `grid-state = UP` (intentional island) or `OFF_GRID` with `grid-state = DOWN` (outage). On SPAN Panel this property is always `UNKNOWN`: the panel has no upstream-grid sensor on the MID it synthesizes, so it cannot observe the utility supply independently of the battery system's own connection state. Do not write logic that branches on `UP` or `DOWN` here; use `islanding-state` for the relay position. |
| `grid-forming-entity` | string | Identity of the device currently establishing the AC voltage and frequency reference. Value: `"GRID"` when grid-tied, or the Homie device ID of the grid-forming DER (typically the BESS) when islanded. Read-only. |

Flat-schema mapping:

- `<panel>/bess/grid-state` becomes `<mid-id>/grid/islanding-state`. This is a rename and a relocation: the property describes the MID's relay position, not the grid's condition. The MID's separate `grid-state` property reflects what the MID senses about the grid.
- `<panel>/core/dominant-power-source` becomes `<mid-id>/grid/grid-forming-entity`. The datatype changes from an enum (`GRID` / `BATTERY` / `PV` / `GENERATOR` / `NONE` / `UNKNOWN`) to a string (`"GRID"` or the Homie device ID of the grid-forming DER), and the property becomes read-only. Load-shedding logic that gated on `dominant-power-source != GRID` now reads the same signal from `grid-forming-entity != "GRID"`.

### Proxied DER Devices (BESS, PV, EVSE)

Today, BESS, PV, and EVSE devices do not represent themselves on eBus. The panel **proxies** them: it publishes child devices on their behalf, populated from internal data sources (backup_client, backup-manager, commissioning data). When a DER later represents itself on eBus (natively or via a dedicated SPAN adapter), the panel stops proxying that device and the eBus-native device takes over. Consumers identify all DER children by the same `$description.type` regardless of whether the panel is proxying or the device is self-representing; the distinction is transparent to consumers.

### BESS to Child Device

The BESS node becomes a child device with `info`, `soc`, `meter`, and `status` capabilities. It is currently proxied by the panel. Every BESS child publishes a MID child device (see MID to Child Device).

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/bess/vendor-name` | `<bess-id>/info/vendor-name` | The BESS is now a child device. The physical serial is in `<bess-id>/info/serial-number`. |
| `<panel>/bess/product-name` | **retired**, see `info/model` | Product identity is restandardized (eBus `info` 0.2): `info/model` carries the human-facing designation and the new `info/part-number` carries the vendor SKU. `product-name` is no longer published. |
| `<panel>/bess/model` | `<bess-id>/info/model` **and** `<bess-id>/info/part-number` | **Semantic remap.** The flat `bess/model` held the SKU code and flat `bess/product-name` held the designation; in v1.0 the designation goes in `info/model` (e.g. `Powerwall 2 AC`) and the SKU goes in the new `info/part-number` (e.g. `1232100-00-E`). A consumer reading flat `model` for a display name should switch to `info/model`. |
| `<panel>/bess/serial-number` | `<bess-id>/info/serial-number` | |
| `<panel>/bess/software-version` | `<bess-id>/info/firmware-version` | Renamed |
| `<panel>/bess/nameplate-capacity` | `<bess-id>/info/nameplate-capacity` | Float, kWh |
| `<panel>/bess/soc` | `<bess-id>/soc/soc` | Float, % |
| `<panel>/bess/soe` | `<bess-id>/soc/soe` | Float, kWh |
| *(none)* | `<bess-id>/meter/active-power` | Float, W. Per-BESS active power. |
| `<panel>/bess/connected` | `<connection-owner>/connection/fed-by-device-status` or `feeds-device-status` | **Semantic and datatype and location change.** Datatype boolean to enum (`OK`, `LOST`, `DEGRADED`). Location moves to the panel-side connection owner (the lugs or circuit wired to the BESS), on the side that matches the wiring direction: `fed-by-device-status` when the BESS is upstream (the common case, on `<panel>-lugs-up`), `feeds-device-status` when downstream. This is the panel's view of link health. The BESS's own `status/communication-state` is the publisher's self-report and is a distinct signal. |
| *(none)* | `<bess-id>/status/communication-state` | Enum `OK`, `DEGRADED`, `LOST`, `UNKNOWN`. The BESS publisher's self-reported communication state. |
| `<panel>/bess/grid-state` | `<bess-id>-mid/grid/islanding-state` | Renamed and relocated to the MID child. |
| `<panel>/bess/relative-position` | **retired, derivable from connection records (when present)** | Derived from which panel-side connection owner references this BESS and from which direction: a circuit or downstream lugs `feeds-device-id == <bess-id>` implies IN_PANEL; an upstream lugs `fed-by-device-id == <bess-id>` implies UPSTREAM. Connection records are best-effort (see Discovering DER Topology): if no owner references the BESS, position is not derivable. When a record is present, the same physical BESS reads consistently from any panel observing it. |
| `<panel>/bess/feed` | **retired, on the connection record** | Now `<connection-owner>/connection/feeds-device-id` (or `fed-by-device-id` for upstream) where the connection owner is the circuit or lugs that physically connects to the BESS. |

### PV to Child Device

The PV node becomes a child device with an `info` capability. It is currently proxied by the panel.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/pv/vendor-name` | `<pv-id>/info/vendor-name` | |
| `<panel>/pv/product-name` | `<pv-id>/info/model` | Product identity restandardized (eBus `info` 0.2): the designation moves to `info/model` (e.g. `IQ7PLUS-72-x-US`); `product-name` is retired. The PV has no `part-number` source, so none is published. |
| `<panel>/pv/serial-number` | `<pv-id>/info/serial-number` | |
| `<panel>/pv/software-version` | `<pv-id>/info/firmware-version` | Renamed |
| `<panel>/pv/nameplate-capacity` | `<pv-id>/info/nominal-power` | **Renamed** to `nominal-power` (float, W). Per eBus `info` 0.2, `nameplate-capacity` is rated *energy* (storage devices); a power-rated device such as PV publishes its rated power as `nominal-power`. Same value (rated DC array power), correct property. |
| `<panel>/pv/relative-position` | **retired, derivable from connection records (when present)** | Same logic, and the same best-effort caveat, as for the BESS. |
| `<panel>/pv/feed` | **retired, on the connection record** | Now `<connection-owner>/connection/feeds-device-id` on the circuit or lugs that physically feeds the PV. |

### EVSE to Child Device

The EVSE node becomes a child device with `info`, `switch`, `status`, `meter`, and `config` capabilities. It is currently proxied by the panel.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/evse/vendor-name` | `<evse-id>/info/vendor-name` | |
| `<panel>/evse/product-name` | `<evse-id>/info/model` | Product identity restandardized (eBus `info` 0.2): the designation moves to `info/model`; `product-name` is retired. The SKU stays in `info/part-number`. |
| `<panel>/evse/part-number` | `<evse-id>/info/part-number` | |
| `<panel>/evse/serial-number` | `<evse-id>/info/serial-number` | |
| `<panel>/evse/software-version` | `<evse-id>/info/firmware-version` | Renamed |
| `<panel>/evse/feed` | **retired, on the connection record of the feeding circuit** | The circuit that feeds the SPAN Drive publishes `connection/feeds-device-id = <evse-id>` and `connection/feeds-device-type = energy.ebus.device.evse`. |
| `<panel>/evse/lock-state` | `<evse-id>/switch/lock-state` | Moved to the `switch` capability; enum `UNLOCKED`, `LOCKED` |
| `<panel>/evse/status` | `<evse-id>/status/status` | Moved to the `status` capability; enum `AVAILABLE`, `PREPARING`, `CHARGING`, `UNAVAILABLE` |
| `<panel>/evse/advertised-current` | `<evse-id>/meter/advertised-current` | Float, A |
| `<panel>/evse/max-charge-current` | `<evse-id>/config/max-charge-current` | New `config` capability. Installer-configured maximum charge current (breaker rating and J1772 derating). Read-only. |
| `<panel>/evse/user-max-charge-current` | `<evse-id>/config/user-max-charge-current` | New `config` capability. User-configured maximum charge current ceiling, settable in the range 6 A up to `max-charge-current`; out-of-range values are clamped rather than rejected. |

### PCS (Power Control System) to Panel Capability

PCS stays on the panel device as the `pcs` capability. Most PCS topics are unchanged; the exceptions are noted.

| Flat Topic | v1.0 Topic | Notes |
|---|---|---|
| `<panel>/pcs/enabled` | `<panel>/pcs/enabled` | Unchanged |
| `<panel>/pcs/active` | `<panel>/pcs/active` | Unchanged |
| `<panel>/pcs/import-limit` | `<panel>/pcs/import-limit` | Unchanged (float A) |
| `<panel>/pcs/feed-import-limit` (+ `-enablement`, `-active`) | `<panel>/pcs/feed-import-limit` (+ `-enablement`, `-active`) | Unchanged |
| `<panel>/pcs/grid-import-limit` (+ `-enablement`, `-active`) | `<panel>/pcs/operator-import-limit` (+ `-enablement`, `-active`) | Renamed base name `grid-` to `operator-` |
| `<panel>/pcs/off-grid-import-limit` (+ `-enablement`, `-active`) | `<panel>/pcs/off-grid-import-limit` (+ `-enablement`, `-active`) | Unchanged |
| `<panel>/pcs/requested-import-limit` (+ `-enablement`, `-active`) | `<panel>/pcs/requested-import-limit` (+ `-enablement`, `-active`) | Unchanged |
| *(new)* | `<panel>/pcs/binding-constraint` | Enum `FSR`, `DOE`, `VOLTAGE`, `OFF_GRID`, `REQUESTED`, `OPERATOR`, `NONE`, `UNKNOWN`. Which constraint class currently sets the import limit. |

The `-enablement` properties are enums (`UNSPECIFIED`, `UNCONFIGURED`, `DISABLED`, `ENABLED`); the `-active` properties are booleans. The flat `core/grid-islandable` is retired (not republished under `pcs`; see Panel Core to Panel Capabilities). The flat `core/breaker-rating` does NOT move into `pcs`; it moves to the new `breaker` capability as `breaker/rating`.

### Shed Forecast to Panel Capability

The panel publishes a `shed-forecast` capability when at least one BESS is commissioned. It carries the four Battery Time Remaining (BTR) values and an algorithm-confidence indicator. All properties are read-only.

| Property | Type | Description |
|---|---|---|
| `<panel>/shed-forecast/total-time-remaining` | integer (min) | At current aggregate SOE, total time before backed-up circuits drop. |
| `<panel>/shed-forecast/time-to-priority-shed` | integer (min) | At current aggregate SOE, time until the next priority tier is shed. |
| `<panel>/shed-forecast/full-charge-total-time-remaining` | integer (min) | Total backup duration assuming the BESS starts at full charge. |
| `<panel>/shed-forecast/full-charge-time-to-priority-shed` | integer (min) | Time to the next priority shed assuming the BESS starts at full charge. |
| `<panel>/shed-forecast/confidence` | enum (`LOW`, `MEDIUM`, `HIGH`) | The algorithm's self-assessed confidence. |

The capability is published only when a BESS is commissioned; its absence means no BESS. The forecast is a single panel-level set of values that aggregates across all commissioned BESS children (not per-BESS); SPAN r202633 commissions at most one BESS, but the aggregate semantics hold if more are ever present.

### Shed Controls to Panel Capability

The panel publishes a `shed` capability when at least one BESS is commissioned. It carries the consumer-asserted islanding-state override and the SoC-based shed policy.

| Property | Type | Description |
|---|---|---|
| `<panel>/shed/asserted-islanding-state` | enum (`NONE`, `ON_GRID`, `OFF_GRID`) | **Settable, `ON_GRID` / `OFF_GRID` only.** A consumer-asserted islanding-state that overrides the sensed grid-state for load-shedding purposes, accepted only while the panel has lost or degraded communication with the MID or BESS. `ON_GRID` forces on-grid treatment (suppressing off-grid and SoC-triggered shedding). `OFF_GRID` forces off-grid treatment. `NONE` is the default and is panel-authored: the panel publishes it to clear an assertion once communication is stably restored, and a consumer write of `NONE` is ignored. |
| `<panel>/shed/policy` | json | The active shed policy: algorithm identifier plus parameters. On SPAN panels the value is a `soc-priority.v1` policy (see below). The property's `$format` is a JSONSchema for the policy object. |

**`shed/policy` value.** On SPAN panels the policy is the SoC-priority algorithm, carrying a shed threshold and a release threshold (hysteresis):

```json
{
  "algorithm": "soc-priority.v1",
  "parameters": {
    "soc-threshold-shed": 49,
    "soc-threshold-release": 51
  }
}
```

Circuits with `load-shed/priority = SOC_THRESHOLD` are shed when the BESS SoC falls below `soc-threshold-shed` and restored when it rises above `soc-threshold-release`. The property's `$format` carries a JSONSchema (`$id: "soc-priority.v1"`) that constrains this object, so a consumer can validate the policy and read the parameter bounds from the schema. The `$format` a panel publishes for `shed/policy`, pretty-printed for readability (the on-wire value is the same document minified, no whitespace):

```json
{
  "$id": "soc-priority.v1",
  "type": "object",
  "required": [
    "algorithm",
    "parameters"
  ],
  "additionalProperties": false,
  "properties": {
    "algorithm": {
      "const": "soc-priority.v1"
    },
    "parameters": {
      "type": "object",
      "required": [
        "soc-threshold-shed",
        "soc-threshold-release"
      ],
      "additionalProperties": false,
      "properties": {
        "soc-threshold-shed": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100,
          "description": "SoC percent below which SOC_THRESHOLD circuits shed"
        },
        "soc-threshold-release": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100,
          "description": "SoC percent above which shed SOC_THRESHOLD circuits restore"
        }
      }
    }
  }
}
```

Both `soc-threshold-shed` and `soc-threshold-release` are `required` for the `soc-priority.v1` algorithm, so a consumer keying on `algorithm` can rely on both thresholds being present. Keying on `algorithm` and preserving the raw object for any other value is the correct forward-compatible approach.

**Migrating `dominant-power-source` overrides.** In the flat schema, consumers wrote `<panel>/core/dominant-power-source` to force on-grid behavior when the panel's auto-shed was misbehaving on stale islanding state. That override role is now `<panel>/shed/asserted-islanding-state`: write `ON_GRID` to force on-grid treatment (the equivalent of the old "force on-grid" write), or `OFF_GRID` to force off-grid. A write is accepted only while the panel has lost or degraded communication with the MID or BESS. A write made while communication is healthy is silently ignored, and because a `/set` does not itself mutate a property, the published value simply does not change, which is how a consumer detects the rejection. Consumers never clear the assertion: `NONE` is panel-authored, a consumer write of `NONE` is ignored, and the panel returns the property to `NONE` itself once communication has been continuously restored. The panel auto-sheds when the effective islanding-state is not `ON_GRID`, where the effective state is `asserted-islanding-state` when it is `ON_GRID` or `OFF_GRID`, otherwise the MID's sensed `islanding-state`.

### Power Flows to Panel Capability

All `<panel>/power-flows/*` properties (`pv`, `battery`, `grid`, `site`; float, W) carry through with unchanged topics.

---

## Settable Properties Summary

The complete set of settable properties in v1.0:

| Device | Capability | Property | Topic | Notes |
|---|---|---|---|---|
| Circuit | `switch` | `relay` | `ebus/5/<circuit-uuid>/switch/relay/set` | `$settable = true` only when `switch/relay-controllable = true` |
| Circuit | `load-shed` | `priority` | `ebus/5/<circuit-uuid>/load-shed/priority/set` | Write `OFF_GRID`, `SOC_THRESHOLD`, or `NEVER`; a write of `UNKNOWN` is silently ignored. `$settable` is `false` on a circuit commissioned as never-backup |
| Panel | `shed` | `asserted-islanding-state` | `ebus/5/<panel>/shed/asserted-islanding-state/set` | Write `ON_GRID` or `OFF_GRID` only, and only during MID or BESS comm loss; `NONE` is panel-authored; see Shed Controls |
| EVSE | `config` | `user-max-charge-current` | `ebus/5/<evse-id>/config/user-max-charge-current/set` | Integer amps, from 6 (the J1772 minimum charge rate) up to `max-charge-current`. Out-of-range values are clamped to the nearest bound rather than rejected, and a non-integer payload is discarded |

Everything else is read-only, including `<circuit>/info/name` (there is no circuit rename over eBus) and `<mid-id>/grid/grid-forming-entity` (it reflects physical electrical reality, not a user preference).

---

## $description Changes

The panel's `$description` lists only the panel's own capability nodes plus a `children` array of child device IDs. Each child device has its own `$description`.

**To discover children by class:** parse `$description.children`, subscribe to each child's `$description`, and read the `type` field:

- Circuits: `energy.ebus.device.circuit`
- Lugs: `energy.ebus.device.lugs`
- MID: `energy.ebus.device.mid`
- BESS: `energy.ebus.device.bess`
- PV: `energy.ebus.device.pv`
- EVSE: `energy.ebus.device.evse`

Do not identify device classes by parsing device ID format. Device IDs are opaque; the `type` field is the authoritative device class.

**To discover DER wiring topology:** parse the panel's children, subscribe to each circuit and lugs child's `$description`, and read `connection/feeds-device-id`, `connection/feeds-device-type`, `connection/fed-by-device-id`, `connection/fed-by-device-type` where present. Each connection record is a panel-side fact about what is wired where. To find a particular DER:

- Scan the circuit and lugs children for any with `connection/feeds-device-id == <der-id>`: the matching device (a circuit or the downstream lugs) is what feeds the DER.
- Scan for any with `connection/fed-by-device-id == <der-id>`: the matching device (typically the upstream lugs when the DER is wired upstream) is fed by the DER.

The MID does not publish a `connection` record; connection lives on circuits and lugs only. Mixed-load and unsurveyed circuits have no `connection` records; the absence is the signal that no specific commissioned downstream device is known.

---

## Capability Type Semantics

Capability types (for example `energy.ebus.capability.meter`) define a **semantic namespace and intent**, not a fixed property contract. The same capability type may expose different property subsets on different device classes: `meter` on the panel exposes voltage; `meter` on a circuit exposes current, active power, and energy; `meter` on a lugs device exposes both currents, active power, and energy. The authoritative property set for any capability node is always declared in that device's `$description`.

The `connection` capability is published on **circuits and lugs only**. Its property vocabulary is shared, but the published subset depends on the connection point:

- A **circuit** publishes the downstream side only: `feeds-device-id`, `feeds-device-type`, and `feeds-device-status`.
- A **lugs** device declares both sides, but SPAN Panel populates only the upstream side: `fed-by-device-id`, `fed-by-device-type`, and `fed-by-device-status`. The downstream `feeds-*` triplet is declared and left unpublished.
- `count` is declared on both device classes and is not published by SPAN Panel in this release.

The full property vocabulary:

| Property | Datatype | Purpose |
|---|---|---|
| `feeds-device-id` | string | Homie device ID of the device wired downstream of this connection point. |
| `feeds-device-type` | string | `$description.type` of the downstream-connected device. |
| `feeds-device-status` | enum | Panel's view of communication-link health to the fed device: `OK`, `LOST`, `DEGRADED`. |
| `fed-by-device-id` | string | Homie device ID of the device wired upstream of this connection point. |
| `fed-by-device-type` | string | `$description.type` of the upstream-connected device. |
| `fed-by-device-status` | enum | Panel's view of communication-link health to the upstream device: `OK`, `LOST`, `DEGRADED`. |
| `count` | integer | When the connected node aggregates multiple physical units (for example 4 microinverters reported as one PV device, or several battery packs reported as one BESS), how many. Not settable. Declared in the schema but not published by SPAN Panel in this release, so no value ever appears on the topic. |

The publishing device's `$description.type` (`energy.ebus.device.circuit` versus `energy.ebus.device.lugs`) carries the connection-point class (feeder circuit versus feedthrough or main lugs), so no separate enum is needed on the connection record itself.

Worked example: a circuit feeds an Enphase microinverter array commissioned as a single PV device with ID `<panel>-iq7plus-72-x-us`. The circuit publishes `connection/feeds-device-id = "<panel>-iq7plus-72-x-us"` and `connection/feeds-device-type = "energy.ebus.device.pv"`. The four aggregated microinverters are what `count` is intended to report, but SPAN Panel does not publish `count` in this release, so a consumer cannot distinguish an aggregated PV child from a single one by that property. A circuit feeding a single Tesla Powerwall publishes the same two properties.

---

## Device Lifecycle and State Management

Device state semantics follow the [Homie 5 Specification](https://homieiot.github.io/specification/).

**State values:** `init`, `ready`, `disconnected`, `sleeping`, `lost`.

**State cascade:** if the panel (root) device's `$state` is `lost`, **every child device in its tree is also effectively `lost`**, regardless of what the child's own `$state` topic says. This is because the panel's MQTT Last Will and Testament sets only the root `$state` to `lost`; child `$state` topics are not updated by the broker.

**Effective state determination:**

| Child has `root` set? | Root `$state` | Effective child state |
|---|---|---|
| no | n/a | child's own `$state` |
| yes | not `lost` | child's own `$state` |
| yes | `lost` | `lost` (inherited from root) |

**Consumer implications:**

- Subscribe to both each device's `$state` and its root device's `$state` to determine effective state.
- Panel `ready` plus child `lost` means the child is independently unavailable (not a cascade).
- Panel `lost` means everything is unavailable.
- A child in the `children` array that is not yet publishing `$state` does not yet exist (per the Homie spec, a device exists once a valid value is set in `$state`).

**`$description` mutability:** a device's `$description` may only change when its `$state` is `init`, `disconnected`, or `lost`. Consumers can cache `$description` while a device is `ready`.

**Observing a commissioning change.** The retired `never-backup` and `always-on` flags are expressed structurally via the `$settable` attribute on `load-shed/priority` and `switch/relay-controllable`, both of which live in the circuit's `$description`. When an installer reconfigures an **already-published** circuit at runtime and this changes settability, only that circuit is affected: the circuit **child device** cycles its own `$state` (`init` to `ready`) and republishes its `$description` at the end of the transition, while the panel-root `$state` and `$description` are unchanged (the `children` array is identical). A consumer that caches `$description` while `ready` therefore re-reads that child's `$description` on its next `ready` transition and observes the new `$settable`, per the standard Homie mutability rule. No `$description` mutation occurs silently while `ready`, and no polling is required. (First-time commissioning of a **new** child device at runtime is the separate case where the root's `$description.children` grows and the root cycles `$state`; see Device Lifecycle and State Management.)

---

## Broker Semantics

**Retained messages:** all `$state`, `$description`, and property value topics are published as retained messages per the Homie 5 specification. On subscribe, the broker immediately delivers the last-known value for each topic, so a reconnecting client can rediscover the full topology and current state from retained messages alone.

**ACLs:** a single authorized panel-client session can subscribe across the panel and all of its children (the panel-derived IDs, circuit UUIDs, and proxied DER IDs of the form `<proxier-id>-<proxied-identifier>`). No per-child authorization is required.

**Discovery flow (two rounds):**

1. Subscribe to the panel's `$description` and receive the retained `$description` with its `children` array.
2. Issue a single batched SUBSCRIBE covering all child topic trees and receive retained `$description` and property messages for each child.

The startup cost is a burst of retained messages, not a per-child round trip.

---

## Device ID Stability

| Device Class | ID Pattern | Stable across reboot? | Stable across firmware upgrade? | Stable across factory reset / recommissioning? |
|---|---|---|---|---|
| Panel | `<panel-serial>` | Yes | Yes | Yes (hardware serial) |
| Lugs | `<panel-serial>-lugs-{up,dn}` | Yes | Yes | Yes (derived from panel serial) |
| MID (BESS-integrated) | `<bess-id>-mid` | Yes | Yes | Yes (derived from the BESS device ID; changes only if the BESS serial changes) |
| MID (panel-integrated) | `<panel-serial>-mid` | Yes | Yes | Yes (derived from panel serial) |
| Circuit | `<circuit-uuid>` | Yes | Yes | TBD |
| BESS (proxied) | `<proxier-id>-<bess-serial>` | Yes | Yes | Yes (both components stable) |
| PV (proxied) | `<proxier-id>-<pv-identifier>` | Yes | Yes | Yes (both components stable) |
| EVSE (proxied) | `<proxier-id>-<evse-identifier>` | Yes | Yes | Yes (both components stable) |

Proxied-device IDs take the form `<proxier-id>-<proxied-identifier>`, where the proxier is the panel and the identifier is derived from the DER (its serial for a BESS, a product or model identifier for a PV whose serial is unavailable). The identifier is normalized to lowercase in the published ID (for example a Tesla serial `TG121153003K7G` appears as `...-tg121153003k7g`). Because vendor serials can contain hyphens, do not split a device ID on `-` to recover its components; treat the whole ID as opaque and classify by `$description.type`.

---

## Client Migration Strategy

### Migration timeline

The flat schema is being retired in the same SPAN firmware release that introduces the parent/child schema. The current target is firmware **r202633**. Fleet rollout is projected (not committed) for the first two weeks of September 2026. A panel may be on either schema during the rollout window depending on when it receives the OTA update. After the rollout window completes, the flat schema is retired; consumer code is expected to drop flat-schema support shortly thereafter, so there is no long-term dual-schema support burden.

### Schema-generation detection

During the overlap window, consumers detect which schema a panel publishes by the presence of the MQTT `info/data-model-version` capability property: the flat schema never published a version property, so its absence is the signal; the parent/child schema publishes `<panel>/info/data-model-version` starting at `1.0`. So:

- `info/data-model-version` **absent** means the flat single-device model.
- `info/data-model-version` **present** (`1.0` or later) means the parent/child model.

For cloud-side consumers that do not see MQTT, the schema is also reachable over REST at `GET /api/v2/homie/schema` (public, unauthenticated), and the REST response is itself a reliable flat-versus-parent/child discriminator, so a consumer can select a parser before opening an MQTT connection:

- **Flat firmware (r202603 through r202627)** serves this endpoint but **omits `dataModelVersion`** entirely (the response carries `firmwareVersion`, `homieDomain`, `homieVersion`, and `types` keyed by the flat node types).
- **Parent/child firmware (r202633 and later)** returns `dataModelVersion` (`"1.0"`), `homieDomain` (`"ebus"`), `homieVersion` (`5`), and the device-class schema. `dataModelVersion` is a required field of the parent/child response and is computed statically from the panel's compiled schema, so it is always present.

So over REST, the **absence** of `dataModelVersion` means the flat model and its **presence** (`1.0` or later) means the parent/child model, exactly mirroring the MQTT `info/data-model-version` signal. Use whichever transport the consumer already has.

**`data-model-version` lifecycle within a session.** `data-model-version` is stable while the panel device's `$state` is `ready`. Any change to the data model is preceded by the panel cycling through `$state = init` (or `disconnected` / `lost`), at which point consumers re-read `$description` per the standard Homie 5 mutability rules. Consumers MAY cache `data-model-version` and the broader `$description` while the panel is `ready`, and MUST re-check on the next `$state = ready` transition after an `init` / `disconnected` / `lost` excursion.

### `data-model-version` increment policy

The data-model version follows [semver](https://semver.org/) semantics. Consumers can scope their parsers to a major-version range with the following guarantees:

| Change class | Bump |
|---|---|
| New optional capability node on an existing device | minor |
| New MAY-level property on an existing capability | minor |
| New MAY-level enum value added via Homie `$format` extension | minor |
| Editorial clarification with no on-the-wire impact | patch |
| Promoting a MAY property to SHOULD | minor |
| Promoting a SHOULD or MAY property to MUST | **major** |
| Retiring or renaming any property at MUST or SHOULD level | **major** |
| Retiring a MAY-level property | **major** |
| Changing the datatype of an existing property | **major** |
| Removing an enum value from a property's canonical `$format` | **major** |
| Redefining the semantics of an existing property | **major** |

In summary: **major** = breaking change for publishers or consumers; **minor** = backward-compatible additive change; **patch** = editorial only.

### Unknown enum-value handling for vendor-extended enums

Some enums (for example `relay-requester`) are defined with a canonical value set plus an explicit allowance for vendor-specific extensions via Homie `$format`. Consumer convention:

- Consumers SHOULD treat an unrecognised enum value as equivalent to `UNKNOWN` for canonical-set decisions (a consumer that branches on `relay-requester = LOAD_SHED` and otherwise falls through should treat a vendor-specific value as a fall-through case, the same as `UNKNOWN`).
- Consumers MAY preserve the raw string of the unrecognised value for logging or UI presentation.
- Consumers MUST NOT treat an unrecognised enum value as an error or refuse to process the property: `$format`-extended enums are a contract in which publishers may emit canonical or vendor-defined values and consumers handle both gracefully.

---

## Node Type Rename Summary

| Flat Node Type | v1.0 Type | Scope |
|---|---|---|
| `energy.ebus.device.distribution-enclosure` | `energy.ebus.device.distribution-enclosure` | Unchanged |
| `energy.ebus.device.distribution-enclosure.core` | `energy.ebus.capability.info` + `.door` + `.status` + `.meter` + `.breaker` + `.pcs` | Split into capabilities (the `breaker` capability is new) |
| `energy.ebus.device.lugs` | `energy.ebus.capability.info` + `.meter` + `.connection` (on a child device) | Lugs are now child devices |
| `energy.ebus.device.circuit` | `energy.ebus.capability.info` + `.switch` + `.breaker` + `.meter` + `.load-shed` + `.pcs` + `.connection` (on a child device) | Circuits are now child devices |
| `energy.ebus.device.bess` | `energy.ebus.device.bess` (child device; publishes a MID child) | BESS is now a child device |
| `energy.ebus.device.pv` | `energy.ebus.device.pv` (child device) | PV is now a child device |
| `energy.ebus.device.evse` | `energy.ebus.device.evse` (child device; includes the `config` capability) | EVSE is now a child device |
| `energy.ebus.device.pcs` | `energy.ebus.capability.pcs` | PCS stays on the panel as a capability |
| `energy.ebus.device.power-flows` | `energy.ebus.capability.power-flows` | Power flows stays on the panel as a capability |
| *(new)* | `energy.ebus.capability.breaker` | On the panel and on each circuit; carries `rating` (and `poles` on circuits) |
| *(new)* | `energy.ebus.capability.connection` | On circuits and lugs; see Capability Type Semantics |
| *(new)* | `energy.ebus.capability.shed-forecast` | On the panel when a BESS is commissioned |
| *(new)* | `energy.ebus.capability.shed` | On the panel when a BESS is commissioned |
| *(new)* | `energy.ebus.device.mid` | New child device class for the Microgrid Interconnect Device |

---

## Property Rename Summary

| Flat Property | v1.0 Property | Context |
|---|---|---|
| `software-version` | `firmware-version` | All devices, standardized naming |
| `door` | `door/state` | Panel, moved to a capability and renamed |
| `l1-voltage` / `l2-voltage` | `voltage-a` / `voltage-b` | Panel meter |
| `l1-current` / `l2-current` | `current-a` / `current-b` | Lugs meter |
| `breaker-rating` | `breaker/rating` | Panel and circuit, moved to the new `breaker` capability |
| `dipole` | `breaker/poles` | Circuit, moved to `breaker`; datatype boolean to integer pole count |
| `space` | `spaces` | Circuit `info`, renamed and datatype integer to multi-valued string (comma-separated occupied positions) |
| `vendor-cloud` | `status/cloud-connection` | Panel, clearer name |
| `grid-import-limit` (+ `-enablement`, `-active`) | `operator-import-limit` (+ `-enablement`, `-active`) | Panel PCS |
| `shed-priority` | `load-shed/priority` | Circuit, moved to the `load-shed` capability and renamed |
| `pcs-managed` / `pcs-priority` | `pcs/managed` / `pcs/priority` | Circuit, moved to the circuit's own `pcs` capability |
| `dominant-power-source` | `grid-forming-entity` (identity, MID `grid`, read-only) + `asserted-islanding-state` (override, panel `shed`, settable) | Split into two properties |
| `connected` (boolean) | `feeds-device-status` / `fed-by-device-status` (enum) | Rename, semantic, datatype, and location change. Moves from the BESS child to the panel-side connection owner, on the side matching the wiring direction. Datatype boolean to enum (`OK`, `LOST`, `DEGRADED`). Distinct from the BESS's own `status/communication-state`. |
| `grid-state` (BESS) | `islanding-state` (MID) | Rename and location change; moves to the MID child |
| `feed` (lugs, BESS, PV, EVSE) | `feeds-device-id` / `fed-by-device-id` on the `connection` capability of the panel-side connection owner | Rename, structure, and location change; a free-text string becomes structured connection properties |
| `relative-position` (BESS, PV) | **retired, derivable from connection records** | A property of the panel's relationship to the DER, not of the DER itself |
| `sheddable` | **retired, computed from `load-shed/priority` and `switch/relay-controllable`** | Circuit, consolidated |
| `never-backup` | **retired, expressed via Homie `$settable` on `load-shed/priority`** | Circuit, commissioning lock now uses Homie's existing attribute |
| `always-on` | **retired, expressed via `switch/relay-controllable = false`** | Circuit, consolidated |
| `product-name` | `model` (+ new `part-number`) | BESS / PV / EVSE / MID `info`. eBus `info` 0.2: designation in `model`, vendor SKU in `part-number`; `product-name` retired. On the BESS the flat `model`/`product-name` semantics swap (flat `model` was the SKU). PV and MID publish `model` only (no `part-number` source). |
| `nameplate-capacity` (PV) | `nominal-power` | PV `info`. eBus `info` 0.2: `nameplate-capacity` is rated energy (storage); a power-rated PV publishes rated power as `nominal-power` (float, W). The BESS keeps `nameplate-capacity` (kWh). |
| `grid-islandable` | **retired** | Panel. Not published in v1.0; off-grid capability is derivable from the MID `grid` capability and the capability set. |
| `relay-requester` values | `BACKUP` to `LOAD_SHED`; `PCS_FAIL_SAFE` and `INVERTER` to `PCS`; `NEVER_BACKUP` and `ALWAYS_ON` to `CONFIGURATION` | Circuit, canonical set `UNKNOWN` / `NONE` / `LOAD_SHED` / `USER` / `PCS` / `CONFIGURATION` / `FAULT` |
| *(new)* | `relay-controllable` (boolean) | Circuit `switch`, captures whether the relay can be controlled at all |
| *(new)* | `grid-forming-entity` (string) | MID `grid`, successor to the identity half of `dominant-power-source` |
| *(new)* | `asserted-islanding-state` (enum) | Panel `shed`, successor to the settable-override half of `dominant-power-source` |
| *(new)* | `policy` (json) | Panel `shed`, SoC-based shed policy (`soc-priority.v1`) |
| *(new)* | `binding-constraint` (enum) | Panel `pcs`, which constraint class currently sets the import limit |
| `max-charge-current` / `user-max-charge-current` | `config/max-charge-current` / `config/user-max-charge-current` | EVSE, moved into the new `config` capability (installer cap read-only, user ceiling settable) |
| *(new)* | `total-time-remaining` / `time-to-priority-shed` / `full-charge-total-time-remaining` / `full-charge-time-to-priority-shed` / `confidence` | Panel `shed-forecast`, BTR forecast values |
