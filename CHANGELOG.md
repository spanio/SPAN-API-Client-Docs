# SPAN API Changelog

All notable changes to the SPAN API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

SPAN API versions are tied to SPAN Panel firmware releases using the format `rYYYYWW`.

## Release 202633

### Changed

- **Homie/MQTT (BREAKING): SPAN Panel now publishes a parent/child device model (data model version `1.0`), replacing the flat single-device model.** Every integration built against the flat model published by `r202603` through `r202627` must be updated.
  - **What is published.** SPAN Panel no longer publishes one Homie device carrying many nodes. It publishes the panel as a parent device plus a set of child devices: the lugs assemblies (upstream, and downstream on panels that have them), every circuit, and every commissioned integration (energy storage, solar / PV, SPAN Drive EV charger).
  - **Where the MID sits.** A commissioned battery system additionally publishes a MID (Microgrid Interconnect Device). On current SPAN hardware the panel proxies the MID as a child of the proxied battery system, making it a grandchild of the panel. Because placement depends on which product houses it, walk each device's `children` rather than assuming a fixed depth.
  - **Topic shape.** Topics keep the `ebus/5/<device-id>/<node-id>/<property-id>` shape, but both middle segments change meaning. `<device-id>` now identifies an individual device (a bare circuit UUID, `<panel-serial>-lugs-up` / `<panel-serial>-lugs-dn`, `<panel-serial>-<bess-serial>`, and so on) instead of always being the panel serial. `<node-id>` is now a capability name (`info`, `meter`, `switch`, `breaker`, and so on) instead of a legacy node name.
  - **Treat a device ID as opaque.** Classify a device by the `type` in its `$description` rather than by parsing the ID, since vendor serials can themselves contain hyphens.
  - **Type namespaces.** Capability nodes carry a new type namespace, `energy.ebus.capability.<capability>`, while device types stay in `energy.ebus.device.<class>`.
  - **Three flat node types are retired outright:** `energy.ebus.device.distribution-enclosure.core` (split across the panel's capability nodes), `energy.ebus.device.pcs` (now `energy.ebus.capability.pcs`), and `energy.ebus.device.power-flows` (now `energy.ebus.capability.power-flows`).
  - **Five keep their exact strings but change role:** `energy.ebus.device.lugs`, `energy.ebus.device.circuit`, `energy.ebus.device.bess`, `energy.ebus.device.pv`, and `energy.ebus.device.evse` were node types on the single panel device and are now the `$type` of a child device. Code that matches these strings against a node keeps compiling and silently stops matching.
  - **Where to start.** See the [SPAN Panel eBus Schema Migration Guide](docs/public/ebus-schema-migration-guide.md) for the complete topic and property migration map, [MQTT Topic Reference](docs/public/mqtt-topic-reference.md) for the new surface, and [MQTT API Capabilities](docs/public/mqtt-api-overview.md) for a per-device capability summary. The flat-model documentation is archived, frozen, at [`specs/r202627/docs/`](specs/r202627/docs/).
- **REST (BREAKING): `GET /api/v2/homie/schema` returns the new device-class schema.**
  - The required response fields `types` and `typesSchemaHash` are replaced by `deviceClasses` and `deviceClassesSchemaHash`, and a new required field `dataModelVersion` (`"1.0"`) is added.
  - `deviceClasses` is nested one level deeper than `types` was: device class, then capability, then property ID, where `types` was node type, then property ID.
  - Its keys are short device-class names (`distribution-enclosure`, `lugs`, `circuit`, `bess`, `pv`, `evse`, `mid`) rather than fully qualified Homie node types.
  - `deviceClassesSchemaHash` keeps the same `sha256:<first 16 hex characters>` form as `typesSchemaHash` but is computed over the new structure, so the value differs even where property content is unchanged. Do not compare a cached `typesSchemaHash` against it.
  - `firmwareVersion`, `homieDomain`, and `homieVersion` are unchanged. See [Homie Schema Endpoint](README.md#homie-schema-endpoint).
- Homie/MQTT: The panel's `core` node is split across the panel's `info`, `door`, `status`, `meter`, and `breaker` capabilities, and property names are standardized as part of the new model. Datatypes, units, and values are otherwise unchanged by these renames. See [Property Rename Summary](docs/public/ebus-schema-migration-guide.md#property-rename-summary).
  - `software-version` → `info/firmware-version`, on the panel, BESS, PV, and EVSE.
  - Panel `l1-voltage` / `l2-voltage` → `meter/voltage-a` / `meter/voltage-b`.
  - Lugs `l1-current` / `l2-current` → `meter/current-a` / `meter/current-b`.
  - Panel `door` → `door/state`, and `vendor-cloud` → `status/cloud-connection`.
  - `breaker-rating` → `breaker/rating`, on both the panel and circuits.
  - Circuit `dipole` (boolean) → `breaker/poles`, an integer pole count with a declared `$format` of `1:4:1`.
  - Circuit `space` (integer) → `info/spaces`, a comma-separated string, so a two-pole circuit reports both panel positions (for example `7,9`).
  - PV `nameplate-capacity` → `info/nominal-power`. `nameplate-capacity` is now reserved for rated energy and survives only on the BESS (kWh).
- Homie/MQTT: The circuit `relay-requester` enum value set is reduced from ten values to seven, so consumers branching on the retired strings stop matching and the two collapsed pairs are no longer distinguishable. The published `$format` is now `UNKNOWN,NONE,LOAD_SHED,USER,PCS,CONFIGURATION,FAULT`. See [Relay-Requester Enum Migration](docs/public/ebus-schema-migration-guide.md#relay-requester-enum-migration).
  - `BACKUP` → `LOAD_SHED`.
  - `PCS_FAIL_SAFE` and `INVERTER` → `PCS`.
  - `ALWAYS_ON` and `NEVER_BACKUP` → `CONFIGURATION`.
  - `UNKNOWN`, `NONE`, `USER`, and `FAULT` are unchanged.
- Homie/MQTT: `$settable` on the two settable circuit properties is now decided per circuit rather than declared for every circuit. Read each circuit's own `$description` rather than assuming the class-level schema applies to every instance.
  - `switch/relay` advertises `$settable` only where the new `switch/relay-controllable` property is `true`.
  - `load-shed/priority` advertises `$settable` only where that circuit's shed priority is configurable.
  - The gates are recomputed and republished at runtime when an installer re-commissions a circuit, with no panel restart required: the affected circuit child device cycles its own `$state` and republishes its `$description`.
- Homie/MQTT: The SPAN Drive charge-current properties added in `r202627` move into the EVSE child device's new `config` capability.
  - `config/max-charge-current` is read-only and reports the commissioned ceiling; `config/user-max-charge-current` is settable.
  - `user-max-charge-current` must be less than or equal to `max-charge-current`, and the panel now publishes that bound as a `$format` range on `user-max-charge-current` of the form `6:<commissioned maximum>`, republished whenever the installer-configured maximum changes.
  - That range is a runtime attribute of the published `$description`; it does not appear in the generated schema document.
- Homie/MQTT: The circuit `pcs/priority` value is now published only on circuits where `pcs/managed` is true. Previously the panel published a priority value on every circuit, including circuits the power control system does not act on, which made unmanaged circuits appear to carry a meaningful ranking.
- Homie/MQTT: The panel PCS `grid-import-limit` family is renamed `operator-import-limit` (`operator-import-limit`, `operator-import-limit-active`, `operator-import-limit-enablement`). The values, datatypes, unit (A), and enablement enum are unchanged. The rename distinguishes an externally imposed operator / aggregator cap from the dynamic operating envelope now modeled on the separate `doe` capability.
- Homie/MQTT: Broker publish permissions extend to every child device.
  - The protection that prevented clients from publishing to the panel's own `$state`, `$description`, and bare property topics (added in `r202615`) now applies to each child device the panel publishes. On SPAN Panel, only `/set` topics accept client publishes.
  - Permissions are emitted per device at runtime as devices appear, and are withdrawn when a device is decommissioned.
  - The full set is re-emitted whenever the panel reconnects to the broker, so consumer `/set` writes keep working across a broker restart. See [MQTT Broker Permissions](docs/public/mqtt-broker-permissions.md) ([#7](https://github.com/spanio/SPAN-API-Client-Docs/issues/7)).
- Homie/MQTT: On a clean shutdown the panel root device now publishes a final retained `$state` of `disconnected`, which under the Homie 5 effective-state rule covers every child device. Previously it published `lost`. `lost` now indicates only an ungraceful disconnect, delivered by the MQTT Last Will and Testament. Retained property values are still not cleared on shutdown.

### Added

- Homie/MQTT: `<panel>/info/data-model-version` (string, `1.0`) is published as the runtime discriminator between the flat model and the parent/child model.
  - The flat model published no version property, so its absence means the flat model and its presence means the parent/child model.
  - The same signal is available over REST as the `dataModelVersion` field of `GET /api/v2/homie/schema`, so a cloud consumer can select a parser before opening an MQTT connection. See [Client Migration Strategy](docs/public/ebus-schema-migration-guide.md#client-migration-strategy).
- Homie/MQTT: Device `$description` documents now carry tree links, so a consumer can walk the device tree from the panel root instead of enumerating nodes on a single device.
  - The panel root lists its child device IDs in a `children` array.
  - Each child carries `parent` and `root` back-references to the panel.
  - A child that is itself a parent (a proxied battery system, which publishes the MID as its own child) carries all three.
- Homie/MQTT: A MID (Microgrid Interconnect Device) child device is published for every commissioned battery system, with `info` (`vendor-name`, `serial-number`, `model`, `firmware-version`, `hardware-version`) and `grid` capabilities.
  - `grid/islanding-state` (`ON_GRID`, `OFF_GRID`, `UNKNOWN`) carries the value the flat model published as `bess/grid-state`, and reflects the MID's relay position.
  - `grid/grid-forming-entity` (string) names the device establishing the AC voltage and frequency reference: `"GRID"` when grid-tied, or the battery's Homie device ID when islanded.
  - `grid/grid-state` (`UP`, `DOWN`, `DEGRADED`, `UNKNOWN`) reports the sensed utility-grid condition, a distinct observation from the islanding state. A system can be `OFF_GRID` with `grid-state = UP` (an intentional island) or `OFF_GRID` with `grid-state = DOWN` (an outage).
  - When the battery hardware does not present a separable MID, the publisher synthesizes one from panel-side state. SPAN Panel has no upstream-grid sensor on that synthesized MID, so it publishes `grid/grid-state` as `UNKNOWN` and never changes it. Use `grid/islanding-state` for the relay position; do not branch on `UP` or `DOWN`.
- Homie/MQTT: A new panel `shed` capability, published only when a battery system is commissioned.
  - `shed/policy` (json, read-only) is a self-describing document naming the shed algorithm and its parameters. On SPAN panels it is a `soc-priority.v1` policy carrying `soc-threshold-shed` (the state of charge below which `SOC_THRESHOLD` circuits shed) and `soc-threshold-release` (the state of charge above which they restore), and the property's `$format` is the JSON Schema for that document.
  - `shed/asserted-islanding-state` (enum `NONE`, `ON_GRID`, `OFF_GRID`, settable) lets a consumer override the panel's islanding-state belief for load-shedding purposes while the panel has lost or degraded communication with the MID or battery system. Write `ON_GRID` to force on-grid treatment (suppressing off-grid and state-of-charge shedding), or `OFF_GRID` to force off-grid treatment.
  - A write is accepted only while that communication is lost or degraded. A write made at any other time is silently ignored, and because a `/set` does not itself mutate a property, the published value simply does not change, which is how a consumer detects the rejection.
  - `NONE` is the default and is panel-authored: a consumer write of `NONE` is ignored, and the panel itself clears the assertion back to `NONE` once communication has been continuously restored.
- Homie/MQTT: A new panel `shed-forecast` capability, published only when a battery system is commissioned, exposes Battery Time Remaining forecasts for the first time: `total-time-remaining`, `time-to-priority-shed`, `full-charge-total-time-remaining`, and `full-charge-time-to-priority-shed` (all integer, minutes), plus `confidence` (enum `LOW`, `MEDIUM`, `HIGH`).
- Homie/MQTT: A new `connection` capability on circuit and lugs devices publishes the wiring graph explicitly.
  - Circuits publish the downstream side (`feeds-device-id`, `feeds-device-type`, `feeds-device-status`).
  - Lugs declare both the upstream (`fed-by-*`) and downstream (`feeds-*`) sides, and SPAN populates the upstream side only, leaving the downstream feedthrough side unpublished in this release.
  - The `*-device-type` properties carry the connected device's Homie `$type`, and the `*-device-status` properties are the panel's view of link health (`OK`, `LOST`, `DEGRADED`).
  - On a multi-panel cascade, a downstream panel's `lugs-up` reports the sister panel immediately upstream of it rather than the battery system, and reports `OK` only, because link-health detection in that direction is not yet implemented. Do not read the upstream-panel status as a liveness signal.
  - Both device classes also declare `connection/count` (integer), the number of physical units aggregated behind one connected device (four microinverters published as a single PV child, several packs published as a single battery system). SPAN Panel does not publish it in this release, so no value ever appears on the topic.
  - Circuits with mixed or unsurveyed loads publish no `connection` records. That absence is the signal that no specific commissioned downstream device is known.
- Homie/MQTT: `circuit/switch/relay-controllable` (boolean) reports whether a circuit's relay can be commanded at all, and drives that circuit's `switch/relay` `$settable` attribute.
- Homie/MQTT: `<panel>/pcs/binding-constraint` (enum `FSR`, `DOE`, `VOLTAGE`, `OFF_GRID`, `REQUESTED`, `OPERATOR`, `NONE`, `UNKNOWN`) reports which constraint class currently sets the effective import limit. The per-source `*-active` booleans could not express this when several limits were active at once.
  - `FSR` names `feed-import-limit`, `OFF_GRID` names `off-grid-import-limit`, `REQUESTED` names `requested-import-limit`, and `OPERATOR` names `operator-import-limit`.
  - `DOE` and `VOLTAGE` are reserved for dynamic-envelope and voltage-response sources that SPAN Panel does not have in this release, so neither value is published.
- Homie/MQTT: The BESS child device gains `meter/active-power` (float, W) and `status/communication-state` (enum `OK`, `DEGRADED`, `LOST`, `UNKNOWN`). `meter/active-power` is positive while the battery is charging and negative while it is discharging, carrying the same value and sign as the panel's `power-flows/battery` property. Note that this is the opposite of both the eBus specification (which defines positive as power flowing out of the battery) and the panel-perspective convention used by the circuit and upstream-lugs meters; the sign may be corrected in a future release. See [Power and Energy Sign Conventions](docs/public/power-and-energy-conventions.md).
- Homie/MQTT: A panel `doe` capability declaring `import-limit` and `export-limit` (both json) for dynamic operating envelopes appears in the published schema document. SPAN Panel has no envelope source in this release, so the `doe` node is not published on MQTT at all: no `doe` topics are created and no value reaches the wire. The capability is declared so that consumers can plan against a stable shape.

### Deprecated

- REST: All 21 `/api/v1/*` operations in the published OpenAPI document are now marked `deprecated: true`, and the document's `info.description` states the removal date.
  - This is a spec correction, not a change in runtime behavior. SPAN Panel already returned `Deprecation: true` and `Sunset: 2026-12-31` response headers on `/api/v1/*` in `r202627`, and the v1 endpoints continue to work exactly as before.
  - No v1 endpoint was removed, no v1 request or response schema changed, and no v2 operation is deprecated.
  - Generated clients and API documentation viewers will now render the v1 operations as deprecated.
  - All v1 endpoints will be removed on 2026-12-31. Four v1 operations (`POST /api/v1/auth/register` and the three `/api/v1/auth/clients` operations) have drop-in v2 equivalents; most of the rest are replaced by the MQTT/Homie interface, and several are marked as having no MQTT equivalent. See [Migrating from v1 REST Endpoints](README.md#migrating-from-v1-rest-endpoints) for the endpoint-by-endpoint mapping.

### Removed

- **Homie/MQTT (BREAKING): `always-on` is removed and replaced by `switch/relay-controllable`, which has inverted polarity.** A circuit that reported `always-on = true` now reports `relay-controllable = false`. The inversion is silent: a consumer that only renames the field keeps parsing successfully, keeps validating against `$format`, and reads every always-on circuit backward. Invert the value at the same time as the rename.
- Homie/MQTT: The other two per-circuit booleans are retired with it.
  - `never-backup` is removed. Its effect is now expressed by the `$settable` attribute on `load-shed/priority`, which is `false` on a circuit commissioned as never-backup.
  - `sheddable` is removed and is consumer-derivable: a circuit is sheddable when `switch/relay-controllable` is true and `load-shed/priority` is not `NEVER`. The published `$format` for `load-shed/priority` is `UNKNOWN,OFF_GRID,SOC_THRESHOLD,NEVER`, so treat `UNKNOWN` as "not yet known" rather than as sheddable.
- Homie/MQTT: The `feed` and `relative-position` properties are removed. Wiring relationships and device position are now expressed structurally through the `connection` capability on the panel-side device that owns the connection (the feeding circuit, or the upstream / downstream lugs).
  - `feed` is removed from the lugs, where it was a free-text string naming the connected device.
  - `feed` is removed from the BESS, PV, and EVSE, where it was an enum naming the circuit the system landed on.
  - `relative-position` is removed from the BESS and PV.
- Homie/MQTT: The BESS `connected` boolean is removed. Reachability is now reported by the `bess/status/communication-state` enum, and by `connection/feeds-device-status` / `connection/fed-by-device-status` on the panel-side connection owner.
- Homie/MQTT: `product-name` is removed from the BESS, PV, and EVSE. The human-facing product designation is now `info/model`, which is new on the PV and the EVSE. On the BESS, `model` previously carried the vendor part number; it now carries the designation (for example `Powerwall 2 AC`), and the vendor orderable code moves to a new BESS `info/part-number` (the EVSE already published `part-number`).
- Homie/MQTT: The panel `grid-islandable` boolean is removed. Islanding is now modeled on the MID's `grid` capability, and a panel's backup capability is derivable from the set of capabilities it publishes.
- Homie/MQTT: The panel `dominant-power-source` property (and its `/set` topic) is removed. Its two roles are published separately: the grid-forming identity as the read-only `grid/grid-forming-entity` on the MID, and the settable override as `shed/asserted-islanding-state` on the panel.

### Fixed

- Homie/MQTT: The lugs `direction` value is now published in upper case (`UPSTREAM` / `DOWNSTREAM`), matching its declared enum `$format`. Previously the property declared `UPSTREAM,DOWNSTREAM` but published the lower-case strings, so a strict Homie client that validates values against the declared format rejected every lugs direction publication.
- Homie/MQTT: A battery system that loses communication now surfaces as unreachable. Previously the panel could continue to report a healthy battery indefinitely after communication was lost, because it only re-evaluated battery health when the battery sent a message, so a silent battery was never re-evaluated. The panel now checks for staleness on a timer, and reachability is reported by `bess/status/communication-state` and by `connection/feeds-device-status` or `connection/fed-by-device-status` on the panel-side device that owns the connection.
- Homie/MQTT: Decommissioning a battery system, EV charger, or solar / PV system in the SPAN app now removes the corresponding child device from the published tree (its retained `$description` and `$state` are removed) and clears the now-dangling `connection` pointers on the feeding circuit and on the upstream lugs. Previously the device's values simply stopped updating, and stale identity data persisted until the panel restarted.
- Homie/MQTT: The local MQTT/Homie API now survives a broker start failure after an over-the-air update. Previously such a failure could leave the panel publishing nothing at all, taking the local MQTT/Homie API (and with it SPAN Home On-premise) down until the panel was restarted. The panel now starts and reconnects its eBus publishing independently of the broker.
- Homie/MQTT: On installations using an Enphase system, the panel's discovery of the Envoy is more robust.
  - A stale cached address no longer breaks reconnection, which previously left the system reported as unreachable until the panel was rebooted.
  - The commissioned Envoy is now selected by its advertised serial number, so other Envoys on the network are ignored.
  - An Envoy reachable only over an IPv6 link-local address now works.

## Release 202627

### Added

- Homie/MQTT: The EVSE node (`energy.ebus.device.evse`) gains two charge-current properties for the SPAN Drive EVSE. `max-charge-current` (integer, amps) reports the commissioned maximum charge current set at installation and is read-only. `user-max-charge-current` (integer, amps, settable) is the user-configured charge-current ceiling.

## Release 202621

### Added

- **SPAN Home On-premise (HOP) dashboard: auto-login via URL query parameter.** The Local Dashboard login page now accepts an optional `passphrase` query parameter that triggers automatic authentication, enabling deep-linking directly into an authenticated session without manual passphrase entry. URL format: `http://<panel-ip>/login?passphrase=<hopPassphrase>`. The `passphrase` parameter is immediately stripped from the URL after consumption to prevent exposure in browser history. See [HOP Dashboard Auto-Login](docs/public/hop-dashboard-auto-login.md) for the full feature documentation.

### Fixed

- Homie/MQTT: The `<panel>/lugs-downstream/active-power`, `imported-energy`, and `exported-energy` properties (feedthrough lug metering) previously reported `0` regardless of actual load on the downstream lugs. They now report the correct measured values.
- Homie/MQTT: The panel's `pcs/*` properties (`enabled`, `active`, `import-limit`, and the CSL family — `feed-import-limit` / `grid-import-limit` / `off-grid-import-limit` / `requested-import-limit`, each with its `-enablement` and `-active` companions) previously published default / empty values. On panels where PowerUp is configured, these properties now reflect the panel's live PowerUp state.
- The per-release `specs/<release>/openapi.json` artifacts published in earlier releases (`r202603`, `r202609`, `r202615`) were incomplete and have been republished with correct content. The spec-capture tooling now generates the OpenAPI document from the actual firmware source for each release.

## Release 202615

### Fixed

- Homie/MQTT: Fixed EVSE `lock-state` enum format from `UNKNOWN,LOCKED,UNLOCKED`
  to `UNLOCKED,LOCKED` — removed invalid `UNKNOWN` value, lock state is mechanical
  (LOCKED/UNLOCKED) and has no UNKNOWN representation in firmware
- REST: `POST /api/v2/dns/fqdn` now permitted for authenticated clients — previously
  returned 403 for all client types
  ([#10](https://github.com/spanio/SPAN-API-Client-Docs/issues/10))

### Added

- Homie/MQTT: eBus MQTT broker now enforces publish ACLs — consumer clients can only
  publish to `/set` topics. Publishes to panel state topics (`$state`, `$description`,
  bare property values) and LWT messages on panel topics are silently rejected.
  See [MQTT Broker Permissions](docs/public/mqtt-broker-permissions.md)
  ([#7](https://github.com/spanio/SPAN-API-Client-Docs/issues/7))
- mDNS: Automatic suppression of `wlan0` mDNS advertisements when `eth0` and `wlan0`
  share the same subnet, preventing hostname collisions and service discovery failures.
  See [eth0 and wlan0 on the Same Subnet](docs/public/span-panel-network-architecture.md#eth0-and-wlan0-on-the-same-subnet)
- Per-release API spec artifacts now published in `specs/` directory: OpenAPI 3.x
  (`openapi.json`), Homie property schema (`homie-schema.json`), and mDNS service
  definitions (`mdns-services.json`)

## Release 202609

### Changed

- Homie/MQTT: Narrowed the `evse/status` enum format from the full OCPP-1.6
  `ChargePointStatus` set (`UNKNOWN,AVAILABLE,PREPARING,CHARGING,SUSPENDED_EV,SUSPENDED_EVSE,FINISHING,RESERVED,FAULTED,UNAVAILABLE`)
  down to the four values firmware actually emits: `AVAILABLE,PREPARING,CHARGING,UNAVAILABLE`.
  The four-value set reflects the current best-effort mapping from the underlying
  J1772 pilot state; the broader OCPP states are not reachable on this generation
  of firmware. The schema's `format` field and the runtime publisher are generated
  from the same enum, so they are kept in sync by construction.

### Fixed

- Homie/MQTT: Corrected `unit` declaration for circuit `active-power` and PV
  `nameplate-capacity` from `kW` to `W` — actual published values are in watts
- mDNS: Fixed `_device-info._tcp` model TXT record from `SPAN32` to
  `MAIN_32`
- Homie/MQTT: Fixed `dominant-power-source` `/set` command having no effect — the
  settable callback was not registered for conditionally-settable properties
- Homie/MQTT: Fixed `backup/connected` not transitioning to `false` when inverter
  communication becomes stale (>5 minutes without update)
- Homie/MQTT: Fixed `core/door` property reporting persistent `UNKNOWN` value —
  door state is now polled periodically from hardware
- REST: Fixed retained MQTT messages being cleared on service restart, causing
  brief `(null)` property values

### Added

- Homie/MQTT: Added `model` property to Homie core node as an ENUM
  (`MAIN_16,MLO_24,MAIN_32,MAIN_40,MLO_48`)
- REST: Added `proximityProven` field to `/api/v2/status` endpoint

## Release 202603

Initial SPAN API documentation release.
