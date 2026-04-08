# SPAN API Changelog

All notable changes to the SPAN API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

SPAN API versions are tied to SPAN Panel firmware releases using the format `rYYYYWW`.

## Release 202615

### Fixed

- Homie/MQTT: Fixed EVSE `lock-state` enum format from `UNKNOWN,LOCKED,UNLOCKED`
  to `UNLOCKED,LOCKED` — removed invalid `UNKNOWN` value to match actual OCPP-derived states
  ([#9](https://github.com/spanio/SPAN-API-Client-Docs/issues/9))
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
