> **ARCHIVED: SPAN API flat data model (r202603-r202627), frozen.** This is the previous single-device SPAN API documentation, retained for integrations not yet migrated to the r202633 parent/child data model. It will be removed once fleet migration completes. See [`INDEX.md`](INDEX.md) for scope and migration pointers; for the current API, see [docs/public/](../../../docs/public/).

# MQTT Broker Permissions

The SPAN Panel eBus MQTT broker enforces access controls on what clients can publish. This document describes what SPAN API clients are permitted to do.

## Subscribe (Read)

SPAN API clients **MAY** subscribe to all topics under `ebus/#`. This includes:

- `ebus/5/<serial>/$state` — device lifecycle state
- `ebus/5/<serial>/$description` — device schema (JSON)
- `ebus/5/<serial>/<node>/<property>` — property values
- `ebus/5/<other-device>/#` — other eBus devices on the broker

There are no restrictions on what clients can read.

## Publish (Write)

### Controlling the Panel

Clients **MAY** publish to `/set` topics on the panel to issue Homie commands:

```
ebus/5/<serial>/<node>/<property>/set
```

For example:
- `ebus/5/<serial>/core/relay/set` — control a relay
- `ebus/5/<serial>/<circuit-id>/shed-priority/set` — set circuit priority

These are the only topics through which clients can control panel behavior. The panel processes the `/set` command and publishes the resulting state change on the corresponding property topic.

### Panel State Topics (Protected)

Clients **MUST NOT** publish to the panel's own state topics. The broker enforces this — publishes to the following are silently rejected:

- `ebus/5/<serial>/$state`
- `ebus/5/<serial>/$description`
- `ebus/5/<serial>/<node>/<property>` (bare property topics without `/set` suffix)

This protection also applies to MQTT Last Will and Testament (LWT) messages. A client **SHOULD NOT** set an LWT on any `ebus/5/<serial>/` topic — the broker will discard it.

> **Why?** Prior to this enforcement, a client that set an LWT on `$state` with payload `lost` could permanently corrupt the panel's Homie state on ungraceful disconnect, rendering the panel invisible to all other Homie-compliant clients.

### Other Device Topics (Open)

Clients **MAY** publish to topic trees under `ebus/5/` that do not belong to the panel's serial number:

```
ebus/5/<your-device-id>/<node>/<property>
```

This enables other eBus-compatible devices on the home network to publish their own Homie device representations through the panel's broker, without needing to host their own broker.

> **Note on multi-device publishing:** The broker does not currently enforce per-device topic ownership. Any authenticated client can publish to any non-panel device topic tree. This means one client could overwrite another client's device state. SPAN has intentionally prioritized ease of adoption for early eBus integrators over strict topic isolation. Per-device access controls will be introduced in a future firmware release as the eBus ecosystem matures.

## Summary

| Action | Topic Pattern | Permitted |
|--------|--------------|-----------|
| Subscribe | `ebus/#` | Yes |
| Publish | `ebus/5/<serial>/<node>/<property>/set` | Yes |
| Publish | `ebus/5/<serial>/$state` | No |
| Publish | `ebus/5/<serial>/$description` | No |
| Publish | `ebus/5/<serial>/<node>/<property>` | No |
| Publish | `ebus/5/<other-device>/#` | Yes |
| LWT | `ebus/5/<serial>/*` | No |

## Availability

This access control model is available in firmware release `r202615` and later.
