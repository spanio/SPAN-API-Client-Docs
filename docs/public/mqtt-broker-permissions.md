# MQTT Broker Permissions

The SPAN Panel eBus MQTT broker enforces access controls on what clients can publish. This document describes what SPAN API clients are permitted to do.

SPAN API publishes multiple Homie devices: the panel (parent) and its child devices (lugs, circuits, and commissioned DERs). Throughout this document, **SPAN's own devices** means the panel plus every child device listed in the panel's `$description.children`.

## Subscribe (Read)

SPAN API clients **MAY** subscribe to all topics under `ebus/#`. This includes:

- `ebus/5/<device-id>/$state`: device lifecycle state
- `ebus/5/<device-id>/$description`: device schema (JSON)
- `ebus/5/<device-id>/<capability>/<property>`: property values
- `ebus/5/<other-device>/#`: other eBus devices on the broker

There are no restrictions on what clients can read.

## Publish (Write)

### Controlling SPAN Devices

Clients **MAY** publish to `/set` topics on any SPAN device (the panel or a child device) to issue Homie commands:

```
ebus/5/<device-id>/<capability>/<property>/set
```

For example:

- `ebus/5/<circuit-uuid>/switch/relay/set`: open or close a circuit relay
- `ebus/5/<circuit-uuid>/load-shed/priority/set`: set a circuit's load-shed priority
- `ebus/5/<panel-serial>/shed/asserted-islanding-state/set`: assert the islanding-state override
- `ebus/5/<evse-id>/config/user-max-charge-current/set`: set the SPAN Drive charge-current ceiling

These are the only topics through which clients can control device behavior. The device processes the `/set` command and publishes the resulting state change on the corresponding property topic. (Only settable properties respond; the settable set is listed in the [MQTT Topic Reference](mqtt-topic-reference.md).)

### SPAN Device State Topics (Protected)

Clients **MUST NOT** publish to a SPAN device's own state topics. The broker enforces this for the panel **and every child device**; publishes to the following are silently rejected:

- `ebus/5/<device-id>/$state`
- `ebus/5/<device-id>/$description`
- `ebus/5/<device-id>/<capability>/<property>` (bare property topics without the `/set` suffix)

This protection also applies to MQTT Last Will and Testament (LWT) messages. A client **SHOULD NOT** set an LWT on any SPAN device topic; the broker will discard it.

> **Why?** Without this protection, a client that set an LWT on a device's `$state` with payload `lost` could permanently corrupt that device's Homie state on ungraceful disconnect, rendering it invisible to all other Homie-compliant clients.

### Other Device Topics (Open)

Clients **MAY** publish to topic trees under `ebus/5/` that do not belong to a SPAN device:

```
ebus/5/<your-device-id>/<capability>/<property>
```

This enables other eBus-compatible devices on the home network to publish their own Homie device representations through the panel's broker, without needing to host their own broker.

> **Note on multi-device publishing:** SPAN's own devices are protected as described above, but the broker does not enforce per-device ownership among other (non-SPAN) device trees. Any authenticated client can publish to any non-SPAN device-id, so one integrator's client could overwrite another's device state. SPAN has intentionally prioritized ease of adoption for early eBus integrators over strict topic isolation among third-party devices. Broader per-device access controls may be introduced in a future firmware release as the eBus ecosystem matures.

## Summary

| Action | Topic Pattern | Permitted |
|--------|--------------|-----------|
| Subscribe | `ebus/#` | Yes |
| Publish | `ebus/5/<span-device-id>/<capability>/<property>/set` | Yes |
| Publish | `ebus/5/<span-device-id>/$state` | No |
| Publish | `ebus/5/<span-device-id>/$description` | No |
| Publish | `ebus/5/<span-device-id>/<capability>/<property>` | No |
| Publish | `ebus/5/<non-span-device-id>/#` | Yes |
| LWT | `ebus/5/<span-device-id>/*` | No |

## Availability

Publish protection for the panel's own state topics is available in firmware release `r202615` and later. Under the v1.0 parent/child data model (`r202633` and later), the same protection is extended to every child device the panel publishes.
