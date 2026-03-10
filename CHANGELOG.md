# SPAN API Changelog

All notable changes to the SPAN API will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

SPAN API versions are tied to SPAN Panel firmware releases using the format `rYYYYWW`.

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
