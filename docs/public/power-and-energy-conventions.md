# Power and Energy Sign Conventions

This document describes how the SPAN Panel represents the **direction** of power and energy flow in its APIs: when a value is positive versus negative, and what the import / export labels mean in each context.

## The principle

All power and energy values on SPAN Panel APIs are reported **from the panel's perspective**:

- **Imported** = energy flowing *into* the panel across that boundary.
- **Exported** = energy flowing *out of* the panel across that boundary.

This is the same convention used by utility revenue meters at the service entrance: "imported" is what the utility delivers to the home; "exported" is what the home pushes back to the utility.

For instantaneous power (the `meter/active-power` property in Homie; `instantPowerW` in the deprecated v1 REST API), the **sign of the value matches the imported direction**:

- **Positive** = power flowing in the imported direction (into the panel)
- **Negative** = power flowing in the exported direction (out of the panel)
- **Zero** = no net flow at that instant

The same property and convention apply whether you are looking at a grid connection or an individual circuit. Only the *meaning* of "imported" changes per context, because each context measures across a different boundary.

Three surfaces on r202633 do not follow this rule, and each is called out where it appears below: the downstream (feedthrough) lugs `meter`, the BESS `meter`, and the panel's `power-flows` capability. The v1 REST `feedthroughPowerW` field shares the downstream-lugs sign, so it does not follow the rule either.

## Per-context meaning

The panel measures energy crossing several distinct boundaries. Each is exposed by the `meter` capability on a device. Here is what "imported" and "exported" mean at each:

| Context (device) | `meter/imported-energy` / positive `meter/active-power` | `meter/exported-energy` / negative `meter/active-power` |
|---|---|---|
| Upstream lugs (`<panel>-lugs-up`) | Grid → panel (utility delivering energy to the home) | Panel → grid (home exporting energy to the utility) |
| Downstream lugs (`<panel>-lugs-dn`) | Panel → sub-panel (feedthrough delivery to the sub-panel) | Sub-panel → panel (feedthrough backfeed into the main panel) |
| Circuit (per child device) | Circuit → panel (backfeed, e.g. a PV inverter on that breaker) | Panel → circuit (normal load consumption) |

The downstream lugs are the one `meter` context whose sign runs the other way: `<panel>-lugs-dn` reports positive `active-power` when the panel is *delivering* power out to the sub-panel, not when the sub-panel backfeeds into the panel.

On the BESS child device, `meter/active-power` is **positive while the battery is charging** and negative while it is discharging. It carries the same value and sign as the panel's `power-flows/battery` property.

> **Deviations from the eBus specification.** The eBus specification puts every enclosure terminal in one frame where positive `active-power` is power flowing *into* the enclosure, and requires a BESS to publish `active-power` positive when *discharging* (out of the device). SPAN Panel r202633 publishes the opposite sign in both places, as described above. Code against the behavior documented here; these signs may be corrected in a future release, which would be a breaking change announced in the changelog.

### The `power-flows` capability is an exception

The panel's `power-flows` capability does **not** use the panel-perspective rule above. Its four properties are a derived, source-centric summary in which each value describes what the named entity is doing, so their signs are inverted relative to the `meter` capabilities:

| `power-flows` property | Positive | Negative |
|---|---|---|
| `grid` | Panel exporting to the utility | Utility delivering into the panel |
| `pv` | (not produced in normal operation) | PV generating into the panel |
| `battery` | Battery charging (panel delivering to it) | Battery discharging into the panel |
| `site` | Site consuming | Site net-producing |

This is a longstanding SPAN convention that predates the eBus data model, and it is stable: it did not change in the parent/child migration. If you need one consistent frame across every device, prefer the `meter` capabilities, which all follow the panel-perspective rule.

## A worked example

A residential installation at midday, with a 6 kW PV system on a dedicated breaker, 2 kW of house load distributed across other circuits, and a Tesla Powerwall charging at 1 kW:

| Property | Value (W) | Interpretation |
|---|---|---|
| Upstream lugs `meter/active-power` | −3000 | Panel is exporting 3 kW to the grid |
| PV circuit `meter/active-power` | +6000 | PV inverter is backfeeding 6 kW into the panel |
| Sum of all non-PV circuits' `meter/active-power` | −2000 | House loads consuming 2 kW total |
| BESS `meter/active-power` | +1000 | Powerwall is charging at 1 kW (positive = charging, per the BESS note above) |

Balance check: PV backfeed (6000 W) minus house loads (2000 W) minus battery charging (1000 W) leaves a 3000 W surplus, so the panel exports 3 kW to the grid and the upstream lugs read −3000 W. Note that you cannot perform this check by summing the published values directly, because the BESS `meter` does not share the panel-perspective frame: its `+1000` denotes power leaving the panel, the same physical direction the circuit meters denote with a negative value.

## v1 REST API field-name correspondence

The deprecated v1 REST API uses different names for the same underlying quantities. The convention is the same (panel-perspective), but the field *names* on individual circuits are written from the *circuit's* perspective, which can confuse readers used to the Homie property names:

| v1 REST field (per circuit) | Same quantity in Homie | Direction |
|---|---|---|
| `producedEnergyWh` | `meter/imported-energy` | Circuit → panel |
| `consumedEnergyWh` | `meter/exported-energy` | Panel → circuit |
| `instantPowerW` | `meter/active-power` | Sign per the main rule above |

Reading these in v1: a PV-feeding circuit "produces" energy (positive accumulator, sending it back to the panel) and load circuits "consume" energy (positive accumulator, drawing it from the panel). In Homie, the corresponding accumulators are labeled from the panel's perspective: "imported" = energy received from the circuit, "exported" = energy delivered to the circuit.

The v1 `feedthroughPowerW` field corresponds to the downstream lugs `meter/active-power` property. The v1 `feedthroughEnergy` totals correspond to the downstream lugs `meter/imported-energy` and `meter/exported-energy` properties.

## Why this convention

Anchoring the convention at the panel's perspective is what lets the panel's power balance close: the upstream lugs and each branch circuit all report power flowing *into* the panel, with no per-terminal sign flip. It also aligns the grid connection's sign convention with how utility revenue meters and most energy-management platforms (the Home Assistant Energy dashboard, OpenEMS, third-party PV inverter integrations) treat the grid boundary. This is the eBus enclosure reference direction.

Two caveats apply when you use this to check your own arithmetic on r202633. The signed sum across terminals closes to zero only on a panel with no feedthrough load, because the downstream lugs report with the opposite sign (see the deviation note above); include the feedthrough term with its sign reversed to make the balance close. Likewise, the branch `meter/active-power` values sum to the negative of the upstream-lugs reading only when no power leaves through the feedthrough lugs. Both are consequences of the downstream-lugs sign, not of the underlying measurements.

## See also

- [MQTT Topic Reference](mqtt-topic-reference.md): full property list
- [MQTT API Overview](mqtt-api-overview.md): broader API introduction
- eBus [`distribution-enclosure`](https://github.com/electrification-bus/specification/blob/main/devices/distribution-enclosure.md#enclosure-specific-meter-reference-direction) and [`meter`](https://github.com/electrification-bus/specification/blob/main/capabilities/meter.md#sign-convention-reference-direction) specs: the enclosure reference direction defined at the standard level
