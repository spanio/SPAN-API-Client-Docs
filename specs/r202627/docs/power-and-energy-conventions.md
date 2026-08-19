> **ARCHIVED: SPAN API flat data model (r202603-r202627), frozen.** This is the previous single-device SPAN API documentation, retained for integrations not yet migrated to the r202633 parent/child data model. It will be removed once fleet migration completes. See [`INDEX.md`](INDEX.md) for scope and migration pointers; for the current API, see [docs/public/](../../../docs/public/).

# Power and Energy Sign Conventions

This document describes how the SPAN Panel represents the **direction** of power and energy flow in its APIs — when a value is positive vs. negative, and what the import / export labels mean in each context.

## The principle

All power and energy values on SPAN Panel APIs are reported **from the panel's perspective**:

- **Imported** = energy flowing *into* the panel across that boundary.
- **Exported** = energy flowing *out of* the panel across that boundary.

This is the same convention used by utility revenue meters at the service entrance: "imported" is what the utility delivers to the home; "exported" is what the home pushes back to the utility.

For instantaneous power (`active-power` in v2 Homie; `instantPowerW` and `feedthroughPowerW` in v1 REST), the **sign of the value matches the imported direction**:

- **Positive** = power flowing in the imported direction (into the panel)
- **Negative** = power flowing in the exported direction (out of the panel)
- **Zero** = no net flow at that instant

The same property and same convention apply whether you are looking at a grid connection, a downstream sub-panel feed, or an individual circuit — only the *meaning* of "imported" changes per context, because each context has a different boundary the panel is measuring across.

## Per-context meaning

The panel measures energy crossing several distinct boundaries. Here is what "imported" and "exported" mean at each:

| Context (Homie node)                | `imported-energy` / positive `active-power`                      | `exported-energy` / negative `active-power`                        |
|-------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------------|
| Upstream lugs (`lugs-upstream`)     | Grid → panel (utility delivering energy to the home)             | Panel → grid (home exporting energy to the utility)                |
| Downstream lugs (`lugs-downstream`) | Sub-panel → panel (feedthrough backfeed into main panel)         | Panel → sub-panel (feedthrough delivery to the sub-panel)          |
| Circuit (per breaker)               | Circuit → panel (backfeed, e.g. a PV inverter on that breaker)   | Panel → circuit (normal load consumption)                          |

The convention extends to other instrumented nodes (BESS, PV, EVSE, `power-flows`) following the same panel-perspective rule, but the exact "imported direction" for each of those is documented on the node itself rather than restated here.

## A worked example

A residential installation at midday, with a 6 kW PV system on a dedicated breaker, 2 kW of house load distributed across other circuits, and a Tesla Powerwall charging at 1 kW:

| Property                                       | Value (W) | Interpretation                                       |
|------------------------------------------------|-----------|------------------------------------------------------|
| `lugs-upstream/active-power`                   |   −3000   | Panel is exporting 3 kW to the grid                  |
| PV-circuit `active-power`                      |   +6000   | PV inverter is backfeeding 6 kW into the panel       |
| Sum of all non-PV circuits' `active-power`     |   −2000   | House loads consuming 2 kW total                     |
| Battery (`bess/active-power`, if exposed)      |   −1000   | Panel is sending 1 kW out to charge the Powerwall    |

Balance check: PV backfeed (+6000) − house loads (2000) − battery charging (1000) = +3000 W net surplus → panel exports 3 kW to grid → upstream lugs read −3000 W. The signs are self-consistent.

## v1 REST API field-name correspondence

The v1 REST API uses different names for the same underlying quantities. The convention is the same (panel-perspective), but the field *names* on individual circuits are written from the *circuit's* perspective, which can confuse readers used to v2:

| v1 REST field (per circuit) | Same quantity in v2 Homie | Direction        |
|-----------------------------|---------------------------|------------------|
| `producedEnergyWh`          | `imported-energy`         | Circuit → panel  |
| `consumedEnergyWh`          | `exported-energy`         | Panel → circuit  |
| `instantPowerW`             | `active-power`            | Sign per main rule above |

Reading these in v1: a PV-feeding circuit "produces" energy (positive accumulator, sending it back to the panel) and load circuits "consume" energy (positive accumulator, drawing it from the panel). In v2 Homie, the corresponding accumulators are labeled from the panel's perspective: "imported" = energy received from the circuit, "exported" = energy delivered to the circuit.

The v1 `feedthroughPowerW` field corresponds to the v2 `lugs-downstream/active-power` property. The v1 `feedthroughEnergy` totals correspond to the `lugs-downstream` node's `imported-energy` and `exported-energy` properties.

## Why this convention

Anchoring the convention at "panel's perspective" makes the panel's own arithmetic close cleanly: the upstream-lugs `active-power` is the net of all branch (circuit) `active-power` values, with sign preserved. It also aligns the grid connection's sign convention with how utility revenue meters and most energy-management platforms (Home Assistant Energy dashboard, OpenEMS, third-party PV inverter integrations) treat the grid boundary.

## See also

- [MQTT Topic Reference](mqtt-topic-reference.md) — full property list
- [MQTT API Overview](mqtt-api-overview.md) — broader API introduction
