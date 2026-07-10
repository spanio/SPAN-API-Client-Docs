# SPAN API Changelog

All notable changes to the SPAN API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

SPAN API versions are tied to SPAN Panel firmware releases using the format `rYYYYWW`.

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
