# SPAN API Documentation: Flat Data Model (r202603-r202627)

**ARCHIVED / FROZEN.** This folder is a point-in-time snapshot of the SPAN API documentation as published for the **flat (single-device) data model**, the model shipped by SPAN API releases **r202603 through r202627**.

## Why this exists

SPAN API release **r202633** introduces a major, breaking change: the data model moves from a single flat device to a parent/child device plus capabilities model. This snapshot preserves the previous documentation so developers whose integrations still target a flat-model panel keep easy access to the docs they built against.

## What is here

- `README.md`: the SPAN API front-door README as of r202627.
- `mqtt-topic-reference.md`, `mqtt-api-overview.md`, `mqtt-broker-permissions.md`, `power-and-energy-conventions.md`: the flat-model MQTT reference set.

The prose is verbatim as published at r202627; only intra-repository links were adjusted so they resolve from this archived location.

## Which release am I on?

This snapshot reflects the **final** flat release (r202627), which carries every correction made across the flat series (for example the earlier `kW` to `W` unit fix). For the exact machine-readable surface of a specific flat release, see its per-release specs, each with `homie-schema.json`, `openapi.json`, and `mdns-services.json`: [`r202603`](../../r202603/), [`r202609`](../../r202609/), [`r202615`](../../r202615/), [`r202621`](../../r202621/), [`r202627`](../../r202627/). Release-to-release changes are recorded in the [CHANGELOG](../../../CHANGELOG.md).

## Moving to r202633

To migrate an existing flat-model integration to the parent/child model, follow the [eBus Schema Migration Guide](../../../docs/public/ebus-schema-migration-guide.md). The current API reference lives in [docs/public/](../../../docs/public/).

## Lifecycle

This archive is transitional. It will be removed once the fleet has migrated off the flat data model, together with the migration guide and the breaking-change banner in the current README.
