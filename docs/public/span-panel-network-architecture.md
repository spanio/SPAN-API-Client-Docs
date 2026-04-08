# SPAN Panel Network Architecture: Hosted Interfaces, NAT, and Home LAN Connectivity

## Overview

SPAN Panel has four network interfaces, divided into two categories: **client interfaces** that connect to your home LAN, and **hosted interfaces** that provide network connectivity to devices managed by or connected to the panel (such as a battery energy storage system).

## Network Interfaces

### Client Interfaces (Home LAN)

These interfaces connect SPAN Panel to your home network:

| Interface | Type | Purpose | IP Assignment |
|-----------|------|---------|---------------|
| `eth0` | Wired Ethernet | Primary connection to home LAN | DHCP from home router |
| `wlan0` | Wi-Fi client | Alternate connection to home LAN | DHCP from home router |

One of these client interfaces **SHOULD** be enabled and connected to the home LAN. The `eth0` (hardwired Ethernet) connection is recommended for reliability.

### Hosted Interfaces

These interfaces are provided by SPAN Panel itself, serving as small isolated networks for connected devices:

| Interface | Type | Subnet | Panel IP | Purpose |
|-----------|------|--------|----------|---------|
| `eth1` | Wired Ethernet | `10.42.1.0/24` | `10.42.1.1` | Direct connection to energy devices (e.g., Powerwall) |
| `wlan0_ap` | Wi-Fi AP | `10.42.0.0/24` | `10.42.0.1` | Panel hotspot for initial setup and emergency access |

## How Hosted Interfaces Work

### Shared Networking

Both hosted interfaces are configured as shared networks. This means SPAN Panel provides the following services to devices connected to these interfaces:

1. **DHCP** -- SPAN Panel automatically assigns IP addresses to connected devices
2. **DNS** -- SPAN Panel provides DNS resolution to connected devices
3. **Internet access via NAT** -- SPAN Panel forwards outbound traffic from hosted subnets through its active client interface (`eth0` or `wlan0`) to your home router, using Network Address Translation (NAT). This allows devices on the hosted subnets to reach the Internet without being directly visible on your home LAN.

## Network Topology

```
                        Internet
                           |
                      Home Router
                       (DHCP, DNS)
                           |
                       Home LAN
                  +--------+--------+
                  |                 |
              eth0 (DHCP)    wlan0 (DHCP)
                  |                 |
             +----+-----------------+----+
             |       SPAN Panel          |
             |   IP forwarding + NAT     |
             +----+-----------------+----+
                  |                 |
           eth1 (10.42.1.1)  wlan0_ap (10.42.0.1)
                  |                 |
            +-----+-----+    +-----+-----+
            | 10.42.1.x |    | 10.42.0.x |
            |  Hosted   |    |  Hosted   |
            |  Subnet   |    |  Subnet   |
            | (e.g. PW3)|    | (AP WiFi) |
            +-----------+    +-----------+
```

## Connectivity from Hosted Subnets

### What devices on hosted subnets CAN do

- **Reach the Internet** -- a Powerwall connected to `eth1` can reach cloud services (e.g., the Tesla app) because SPAN Panel forwards its traffic through `eth0` (or `wlan0`) to the home router, which routes to the Internet.
- **Reach SPAN Panel itself** -- the panel is the gateway (`10.42.1.1` or `10.42.0.1`) and is directly accessible from the hosted subnet.
- **Reach other devices on the home LAN** -- outbound connections initiated from a hosted subnet can reach hosts on the home LAN. The home LAN host sees the traffic as coming from SPAN Panel's client IP address.

### What devices on hosted subnets CANNOT do

- **Be reached from the home LAN** -- NAT is one-directional. A device on your home LAN cannot initiate a connection to a device on `10.42.1.x` or `10.42.0.x`. Your home router has no route to those subnets, and SPAN Panel does not advertise them. This is by design -- the hosted subnets are isolated from your home LAN.

### The `wlan0_ap` Hosted Wi-Fi AP

The `wlan0_ap` interface is powered by SPAN Panel directly. During a grid or power outage (when the panel is running on battery backup), this may be the only network interface available. The [SPAN Home app can connect to this AP for emergency panel access](https://support.span.io/hc/en-us/articles/4411570234519-Emergency-Reconnect).

## eth0 and wlan0 on the Same Subnet

SPAN recommends connecting only **one** client interface to the home LAN. If both `eth0` and `wlan0` are connected to the same subnet (i.e., the same broadcast domain), the panel's mDNS service discovery can be affected.

### Background

SPAN Panel advertises its `.local` hostname and network services (REST API, MQTT broker, etc.) using [mDNS (multicast DNS)](https://en.wikipedia.org/wiki/Multicast_DNS). The panel's mDNS responder advertises on all active network interfaces. When two interfaces share the same broadcast domain, the mDNS responder sees its own advertisement arriving on the other interface and cannot distinguish it from another device claiming the same name. This triggers the [RFC 6762](https://www.rfc-editor.org/rfc/rfc6762) conflict resolution mechanism.

On firmware versions **prior to r202615**, this caused:

- **Hostname flapping** -- the panel's `.local` hostname (e.g., `span-ab-1234-c5d67.local`) gets renamed to `span-ab-1234-c5d67-2.local`, then `-3`, etc., as the conflict is detected repeatedly
- **Unreliable service discovery** -- tools and integrations that rely on mDNS (such as Home Assistant's ZeroConf integration, or the `span-discover` script) return inconsistent or changing results
- **TLS certificate mismatches** -- the panel's TLS server-certificate contains the original `.local` hostname in its Subject Alternative Names (SANs); when the hostname is renamed by mDNS conflict resolution, the certificate no longer matches, causing TLS verification failures for clients that validate the hostname

### Firmware Mitigation (r202615+)

Starting with firmware release r202615, SPAN Panel automatically detects when `eth0` and `wlan0` share a subnet and suppresses mDNS advertising on `wlan0` to prevent the collision. Services continue to be advertised on `eth0` and other interfaces. The suppression is automatic and self-healing -- if the overlap clears (e.g., Wi-Fi disconnects or moves to a different subnet), full mDNS advertising resumes on all interfaces.

### Recommendation

Connect SPAN Panel to your home LAN via only **one** client interface -- preferably `eth0` (hardwired Ethernet) for reliability. If both interfaces must be active, they should be on different subnets. While the r202615 mitigation prevents mDNS collisions, using a single client interface remains the simplest and most reliable configuration.

If your panel is on firmware prior to r202615 and has both `eth0` and `wlan0` connected to the same subnet, contact SPAN Support to request that the Wi-Fi `wlan0` interface be unconfigured, or update to the latest firmware.
