# SPAN API

[SPAN](https://www.span.io/) provides SPAN API to enable software integrations between [SPAN Panel](https://www.span.io/panel) and other devices within the home for the personal, non-commercial use of the SPAN Panel owner or authorized user.

SPAN API is initially available for [SPAN Panel MAIN 32](https://www.span.io/products/main-32) as a public beta release.

> **Notice:** SPAN API is an optional, advanced integration interface for elective use by SPAN Panel owners, residential power users and developers, subject to the restrictions set forth in this GitHub repository, and is not required for normal SPAN Panel operation.
>
> Support of SPAN API is provided on an "as time and resources permit" basis via this GitHub repository **only**.
>
> **Do not contact SPAN customer support for SPAN API related questions.**


Potential uses of SPAN API include:

- Integrations with home automation systems, e.g. [Home Assistant](https://www.home-assistant.io/)
- Collection and storage of SPAN Panel power/energy data into a local database for long-term analysis and comparison
- Displaying and charting SPAN Panel power and energy data using applications like [Grafana](https://grafana.com/oss/grafana/)

SPAN API is provided for use exclusively over the home's Local Area Network (LAN).

## Terms of Use

SPAN API is provided exclusively for personal, non-commercial use by homeowners and developers to whom access is granted by homeowners.

Use of SPAN API is governed by the provisions of this repository and the [SPAN Terms of Service](https://www.span.io/terms-of-service). By accessing or using SPAN API, you agree to be bound by both.

Key restrictions:

- SPAN API is solely for personal use (i) within a SPAN Panel owner's home or (ii) with access to the home network
- Commercial use, fleet management, and multi-site data aggregation are prohibited uses of SPAN API
- Commercial and organizational use of SPAN data and controls requires the use of SPAN Fleet Manager under a separate commercial license
- The MIT-0 license applies to the documentation and example code in this repository only — it does not grant any license to the SPAN API service, SPAN Panel firmware, or any other SPAN intellectual property

> **Note:** The **bolded** key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

## SPAN API Scope & Responsibility Model

SPAN is aware of requests from advanced users and developers for a broader scope of local integrations with SPAN Panel. SPAN API enables those integrations while preserving the core SPAN Panel experience.

SPAN API is an optional, advanced local interface that runs directly on SPAN Panel and is intended for developers and power users. It is not a hosted or cloud service operated by SPAN.

The documentation and example code in this repository are provided under the [MIT No Attribution (MIT-0) license](LICENSE) to support development of integrations and tools that interact with SPAN Panel.

Homeowners **SHOULD** only grant SPAN API access to software and developers they trust. Because access is credential-based and locally controlled, SPAN is not responsible for the operation, security, or outcomes of any application, integration, or automation enabled by any homeowner. Use within the home or with access to the home network of SPAN API in combination with software developed by the homeowner, or third-party software integrations (the foregoing sometimes being referred to as "SPAN API clients"), is at the homeowner's sole discretion and risk, and SPAN expressly disclaims any and all liability with respect thereto.

Examples of SPAN API clients may include:

- Software developed by the homeowner
- Third-party applications running on, or with access to, the home network
- SPAN-provided local applications such as SPAN Home On-Premise

SPAN API is licensed for personal, non-commercial use only. Use of SPAN API to provide commercial services, fleet management, multi-site data aggregation, or any other commercial purpose is a violation of the [SPAN Terms of Service](https://www.span.io/terms-of-service) and may result in termination of SPAN API access. Organizations and businesses requiring programmatic access to SPAN Panel data should contact SPAN to discuss commercial licensing, including licensing of SPAN Fleet Manager.

SPAN Panel is fully functional without SPAN API.
All advertised product features of SPAN Panel operate independently of SPAN API availability or usage.

## SPAN API Support Model

SPAN API is provided for advanced and custom integrations beyond the core product experience.

Because these integrations are created by developers or homeowners and may involve third-party software, SPAN does not provide support, guarantees, or compatibility commitments for custom SPAN API clients or automations.

**SPAN API functionality and third-party integrations are not subject to any form of product warranty.**

### SPAN Support of SPAN API

SPAN API IS PROVIDED “AS IS” AND SPAN EXPRESSLY DISCLAIMS ANY AND ALL REPRESENTATIONS, WARRANTIES, AND CONDITIONS, WHETHER EXPRESS, IMPLIED, ORAL OR WRITTEN, STATUTORY OR OTHERWISE, INCLUDING WITHOUT LIMITATION ANY IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS OR SUFFICIENCY FOR A PARTICULAR USE OR PURPOSE, AVAILABILITY, SECURITY, TITLE, NON-INFRINGEMENT. AND ANY WARRANTY ARISING FROM A COURSE OF DEALING OR USAGE OF TRADE. SPAN DOES NOT WARRANT, GUARANTEE, OR MAKE ANY REPRESENTATION THAT SPAN API IS FREE OF INACCURACIES, ERRORS OR INTERRUPTIONS, IS RELIABLE, ACCURATE OR COMPLETE, OR THAT ALL ERRORS CAN BE CORRECTED. THE HOMEOWNER’S USE, OR USE BY A DEVELOPER AUTHORIZED OR FACILITATED BY THE HOMEOWNER, OF SPAN API IS AT THE HOMEOWNER’S OWN DISCRETION AND RISK AND THE HOMEOWNER WILL BE SOLELY RESPONSIBLE FOR ANY DAMAGE THAT RESULTS FROM SUCH USE OF SPAN API, INCLUDING WITHOUT LIMITATION ANY DAMAGES FOR LOSS OF USE OF FACILITIES OR EQUIPMENT, LOSS OF DATA, OR INTERRUPTION OF ELECTRIC POWER TO ALL OR ANY PORTION OF THE HOME.

SPAN API updates and maintenance, including responses to issues filed on GitHub, will take place on an "as time and resources permit" basis.

#### GitHub Issues

Use [Issues](https://github.com/spanio/SPAN-API-Client-Docs/issues) to report:

- Bugs in the SPAN API itself (unexpected behavior, errors, crashes)
- Errors or omissions in the documentation in this repository

GitHub Issues is not the place for questions, feature requests, or general discussion.

#### GitHub Discussions

Use [Discussions](https://github.com/spanio/SPAN-API-Client-Docs/discussions) for:

- Questions about SPAN API usage
- Feature requests and suggestions
- Sharing integration ideas and projects
- Asking other SPAN API users for advice

Discussions are more free-form and open and a good place to connect with the developer community.

#### What SPAN Does Not Provide

Beyond SPAN API itself and the documentation in this repository, SPAN is not able to provide assistance to developers integrating SPAN API into their applications. This includes debugging application code, architectural guidance, and implementation support.

**SPAN customer support does not provide assistance for API usage, troubleshooting, or integrations.**

### Stability & Compatibility

SPAN API may evolve as the product firmware evolves. While SPAN aims to minimize unnecessary disruption, **backward compatibility is not guaranteed**, and SPAN API behavior may change across firmware releases.

As a public beta:

- Not all features are finalized
- Documentation is evolving

### Intended Audience

SPAN API is intended for:

- Homeowners building custom or experimental integrations for personal use
- Homeowners and developers operating local automation platforms within a single home
- Developers creating open-source home automation integrations for personal, non-commercial use

SPAN API is **not intended for**:

- Commercial products or services
- Fleet management, multi-site monitoring, or commercial energy services (see SPAN Fleet Manager)
- Organizational or enterprise deployments
- Use cases requiring guaranteed stability or support SLAs

## [SPAN API Interaction Models](#span-api-interaction-models)

SPAN API is focused primarily on the publish/subscribe interaction model, using the [MQTT protocol](https://mqtt.org/), with some operations provided via request/response interactions using [REST](https://en.wikipedia.org/wiki/REST)

### [Publish/Subscribe](#publishsubscribe)

SPAN API has adopted the [Electrification Bus](https://ebus.energy/) integration framework (hereinafter “eBus”) which specifies use of the [Homie Convention](https://homieiot.github.io/) for MQTT topics and messages.  SPAN API developers are strongly encouraged to study and digest the Homie documentation:

- [Homie README](https://github.com/homieiot/convention/blob/develop/readme.md)
- [Homie Overview](https://homieiot.github.io)
- [Homie Specification](https://homieiot.github.io/specification/)

SPAN API publishes data regarding SPAN Panel state and status on MQTT topics; SPAN API clients subscribe to these topics, and receive (updated) messages as they are published by SPAN API.

SPAN API clients can also control certain SPAN Panel state by publishing messages to specified topics—for example, to operate the relay that disconnects power to a circuit.

#### [MQTT Broker](#mqtt-broker)

MQTT clients (both subscribers and publishers) connect to, and through, a broker.
To support SPAN API publish/subscribe interactions, SPAN Panel hosts a MQTT broker.

The SPAN API eBus MQTT broker offers client access via:

- Secure MQTT (MQTTS: MQTT over [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security))
- Websockets (WS)
- Secure Websockets (WSS: WS over TLS)

The WS protocol is provided (primarily) to enable browser-based JavaScript applications, e.g. the SPAN Home On-premise application, and the WSS protocol is available for use by SPAN API clients that prefer to use Websockets instead of native MQTT.

##### [MQTT Broker Authentication](#mqtt-broker-authentication)

To access and connect to the SPAN API eBus MQTT broker, a MQTT client will need the following:

- Host: `ebusBrokerHost`
  The network address of SPAN Panel: `.local` [mDNS](https://en.wikipedia.org/wiki/Multicast_DNS) hostname or IP address
- Port: `ebusBrokerMqttsPort`
  The port number of the SPAN API MQTT broker: `8883`
- Username: `ebusBrokerUsername`
  The SPAN Panel `serialNumber`
- Password: `ebusBrokerPassword`

The host, port, and username are obtainable via the SPAN Panel [mDNS advertisements](#mdns-service-advertisements), or via the response to the [REST API authentication request](#authentication-endpoint)

[SPAN Panel Network Interfaces](#appendix-a-span-panel-network-interfaces) provides details regarding network addresses of SPAN Panel (and the eBus MQTT broker)

The password is obtained via the response to the [REST API authentication request](#authentication-endpoint)

See [Obtaining SPAN API Authentication Credentials](#obtaining-span-api-authentication-credentials) for passphrase acquisition details.

#### [MQTT Topic and Message Structure](#mqtt-topic-and-message-structure)

SPAN API implements and provides the [Homie “device role”](https://homieiot.github.io/specification/#roles), to represent SPAN Panel on MQTT.
The Homie/eBus topic structure follows the pattern:

`ebus/5/[device ID]/[node ID]/[property ID]`

SPAN API publishes:

- A single device, the device ID being the serial number of SPAN Panel
- A number of nodes, some nodes are always provided, other nodes are dependent on the commissioned state of SPAN Panel; the individual circuits, and associated integrations, including SPAN Drive, energy storage (backup) systems, etc.
- Each node publishes a number of property IDs.

> **Note on Serial Number Naming:** The serial number of SPAN Panel appears in different naming conventions depending on context: `serialNumber` (camelCase) in JSON/REST responses, `serial-number` (kebab-case) in Homie property names, and `serial_number` (snake_case) in mDNS TXT records. These all refer to the same value (e.g., `ab-1234-c5d67`). This document uses `<serial>` as shorthand in topic patterns.

The Homie Convention requires a device to publish a schema specifying the device itself, its nodes, and each property of each node, as the value of the `$description` attribute, [this value is a well-defined JSON object](https://homieiot.github.io/specification/#device-attributes).

Devices and nodes specify a type in the `$description` schema which **SHOULD** be used for identification and discovery of a device and its nodes, NOT the device ID and node ID opaque strings which may change over time.

An important consideration for SPAN API clients (and developers) is to incorporate and respond to the value of the device's `$state` attribute, which provides crucial and required information about the lifecycle status of the device, including the validity of the device's `$description` attribute. The [lifecycle section of the Homie Convention](https://homieiot.github.io/specification/#device-lifecycle) defines and specifies this behavior.

##### [Electrification Bus, SPAN API, and Naming](#electrification-bus-span-api-and-naming)

Electrification Bus (eBus) is an open, multi-vendor integration and interoperability framework for home energy infrastructure devices.  SPAN has adopted eBus for SPAN API.  In support of its goal of multi-vendor integration, eBus aspires to use non-proprietary and generic naming wherever possible.  The SPAN API device and node types, and property IDs, attempt to use vendor-independent naming and seek to avoid the use of SPAN registered trademarks.

Homie types **SHOULD** be namespaced to prevent naming collisions. To that end, Electrification Bus (eBus) uses [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) for type values, using the domain name `ebus.energy`.

The SPAN Panel device type is:

```shell
energy.ebus.device.distribution-enclosure
```

Node types use the `energy.ebus.device.` prefix, with type-specific suffixes (e.g., `energy.ebus.device.circuit`, `energy.ebus.device.bess`). The `core` node retains the full device type prefix: `energy.ebus.device.distribution-enclosure.core`.

##### [SPAN Panel Component Mapping to Homie/eBus](#span-panel-component-mapping-to-homieebus)

SPAN Panel components are represented as Homie/eBus nodes, each having a type. Most node types use the `energy.ebus.device.` prefix with a type-specific suffix.

The following nodes/types are published for all SPAN Panels:

| Type Suffix | Description |
| :---- | :---- |
| `core` | SPAN Panel-wide properties |
| `lugs.upstream` | Input lugs |
| `lugs.downstream` | Output lugs |
| `power-flows` | Known power flows for the home |
| `circuit` | Per-circuit data (one node per commissioned circuit) |

The following nodes/types may be published depending on SPAN Panel commissioning:

| Type Suffix | Description |
| :---- | :---- |
| `pcs` | UL 3141 Power Control Systems (SPAN PowerUp®) |
| `bess` | Battery energy storage system |
| `pv` | Photovoltaic/solar system |
| `evse` | EV charger (SPAN Drive®) |

##### [SPAN Panel Properties](#span-panel-properties)

Homie/eBus device IDs and node IDs provide a hierarchical structure for organizing and namespacing properties.

Each property provided by a node is defined by a schema, published as the value of the device's `$description` attribute. SPAN API developers **SHOULD** reference both the [Property Attributes section](https://homieiot.github.io/specification/#property-attributes) in the [Homie Specification](https://homieiot.github.io/specification/), and the value of the `$description` attribute in order to obtain the formal description of each property.

SPAN API aspires to be self-documenting and discoverable, and were key motivating factors in the adoption of the Homie Convention.

See [Accessing & Exploring SPAN API](#accessing--exploring-span-api) for an example of obtaining the `$description` attribute's value/schema.

### [Request/Response](#requestresponse)

Some administrative operations are best implemented using REST-style request/response; examples include client authentication and file downloads, SPAN API provides a small number of REST endpoints.

#### [HTTP Server](#http-server)

SPAN API REST endpoints are served via HTTP on port 80, and HTTPS/TLS on port 443\.  See [Transport Security](#transport-security) for TLS details.

#### [SPAN API REST Endpoint Documentation](#span-api-rest-endpoint-documentation)

OpenAPI documentation for the REST endpoints can be viewed in a browser at the URL:

```shell
http://span-{serial-number}.local/api/docs
```

With the `{serial-number}` portion of the URL host component replaced by the serial-number of the SPAN Panel.

The SPAN Panel OpenAPI specification in JSON can be downloaded by the URL:

```shell
http://span-{serial-number}.local/api/openapi.json
```

Deprecated URLs `/api/v1/docs` and `/api/v1/openapi.json` redirect (301) to the version-neutral URLs above.

#### [Download CA Certificate Endpoint](#download-ca-certificate-endpoint)

The self-signed CA-certificate used to create/sign the server-certificate used for SPAN API over TLS is returned as the response to the (unauthenticated) endpoint:
`GET /api/v2/certificate/ca`
e.g. for the `serialNumber` `ab-1234-c5d67`

```shell
$ curl http://span-ab-1234-c5d67.local/api/v2/certificate/ca -–output my-span-ca.crt
```

See [Transport Security](#transport-security) for more about TLS.

#### [Authentication Endpoint](#authentication-endpoint)

All client connections to the SPAN Panel's MQTT broker require authentication, as do most SPAN API REST requests.

The response to the `POST /api/v2/auth/register` endpoint contains a JSON object, for example:

```json
{
    "accessToken": "REDACTED-TOKEN",
    "tokenType": "bearer",
    "iatMs": 1760728511000,
    "hostname": "span-ab-1234-c5d67.local",
    "serialNumber": "ab-1234-c5d67",
    "hopPassphrase": "REDACTED-PASSPHRASE",
    "ebusBrokerUsername": "ab-1234-c5d67",
    "ebusBrokerPassword": "REDACTED-PASSPHRASE",
    "ebusBrokerHost": "span-ab-1234-c5d67.local",
    "ebusBrokerMqttsPort": 8883,
    "ebusBrokerWsPort": 9001,
    "ebusBrokerWssPort": 9002
}
```

The `accessToken` value is used by the client for subsequent SPAN API HTTP REST endpoint requests.
All the `ebusBroker*` values (with the exception of `ebusBrokerPassword`) are also discoverable via mDNS, and are provided here primarily for the benefit of browser-based JavaScript applications that may not have access to mDNS.

In the initial beta version of SPAN API, the values of `hopPassphrase` and `ebusBrokerPassword` are identical, but that will likely change in the future. SPAN API clients must use the value of `ebusBrokerPassword` when connecting and authenticating to the SPAN Panel MQTT broker.

#### [Passphrase/Password Regeneration Endpoint](#passphrasepassword-regeneration-endpoint)

Initially a single `hopPassphrase` and `ebusBrokerPassword` is supported; any client possessing this credential has full access to SPAN API, including both control and data access functionality.

The (authenticated) request `PUT /api/v2/auth/passphrase` will remove the existing credential, regenerate, and return the new credentials, the JSON response:

```json
{
  "ebusBrokerPassword": "string",
  "hopPassphrase": "string"
}
```

#### [Endpoints Enabling FQDN Inclusion in Server-Certificate SAN](#endpoints-enabling-fqdn-inclusion-in-server-certificate-san)

As described in [Transport Security](#transport-security), the SPAN Panel TLS server-certificate includes the SPAN Panel mDNS `.local` hostname, and all SPAN Panel IP addresses in its list of SANs.
For homeowners that administer/provide a local [DNS](https://en.wikipedia.org/wiki/Name_server) server for the home LAN, and configure a [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) for SPAN Panel, the `POST /api/v2/dns/fqdn` endpoint will add the provided FQDN to the SPAN Panel TLS server-certificate SAN list. The request body is of the form:

```json
{
  "ebusTlsFqdn": "string"
}
```

The configured FQDN can be removed via the endpoint:
`DELETE /api/v2/dns/fqdn`

The currently configured FQDN value can be obtained via the endpoint:
`GET /api/v2/dns/fqdn`

#### [Homie Schema Endpoint](#homie-schema-endpoint)

The `GET /api/v2/homie/schema` endpoint returns a JSON object containing the Homie property schema organized by node type, along with versioning metadata. This provides client developers with a complete reference of all properties published by SPAN API, independent of the commissioning/configuration state of SPAN Panel, and without requiring an MQTT connection.

```shell
$ curl http://span-ab-1234-c5d67.local/api/v2/homie/schema | jq
{
  "firmwareVersion": "spanos2/r202546/03",
  "homieDomain": "ebus",
  "homieVersion": 5,
  "types": {
    "energy.ebus.device.distribution-enclosure.core": {
      "serial-number": { "name": "Serial number", "datatype": "string" },
      "door": { "name": "Door state", "datatype": "enum", "format": "UNKNOWN,OPEN,CLOSED" },
      ...
    },
    "energy.ebus.device.circuit": {
      "relay": { "name": "Circuit relay state", "datatype": "enum", "format": "UNKNOWN,OPEN,CLOSED", "settable": true },
      ...
    },
    ...
  },
  "typesSchemaHash": "sha256:a1b2c3d4e5f67890"
}
```

| Field | Type | Description |
| --- | --- | --- |
| `firmwareVersion` | string | SPAN Panel firmware version |
| `homieDomain` | string | MQTT topic domain prefix (`ebus`) |
| `homieVersion` | integer | Homie convention version (`5`) |
| `types` | object | Schema organized by node type |
| `typesSchemaHash` | string | SHA-256 hash of canonicalized `types` object (first 16 hex chars) |

The `typesSchemaHash` enables clients to detect schema changes across firmware versions without comparing the full `types` object. The schema may remain unchanged across multiple firmware releases.

This schema complements the `$description` attribute published on MQTT, providing the same property metadata in a format organized by node type rather than by device instance.

#### [SPAN API v2 REST Endpoints Summary](#span-api-v2-rest-endpoints-summary)

All endpoints below are relative to `/api/v2`

| Method | Endpoint | Description | Auth |
| --- | --- | --- | --- |
| GET | `/status` | Get SPAN Panel serial number and firmware version | None |
| GET | `/certificate/ca` | Download CA-certificate | None |
| POST | `/auth/register` | Register client and obtain access token | `hopPassphrase`* |
| GET | `/auth/clients` | List registered clients | `accessToken` |
| GET | `/auth/clients/{name}` | Get client details | `accessToken` |
| DELETE | `/auth/clients/{name}` | Delete a client | `accessToken` |
| PUT | `/auth/passphrase` | Regenerate passphrase | `accessToken` |
| GET | `/dns/fqdn` | Get FQDN configuration | `accessToken` |
| POST | `/dns/fqdn` | Set FQDN configuration | `accessToken` |
| DELETE | `/dns/fqdn` | Delete FQDN configuration | `accessToken` |
| GET | `/homie/schema` | Get Homie property schema with versioning metadata | None |

\* Requires `hopPassphrase` in request body, or proof-of-proximity (door switch pressed 3 times)

The [span-curl](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/span-curl) script simplifies authenticated REST API calls:

```shell
# After running 'span-auth setup', authentication is automatic

$ span-curl /api/v2/auth/clients
$ span-curl /api/v2/dns/fqdn
$ span-curl -X POST -d '{"ebusTlsFqdn":"panel.home"}' /api/v2/dns/fqdn
```

#### [Migrating from v1 REST Endpoints](#migrating-from-v1-rest-endpoints)

The v1 REST endpoints originated from an internal API developed several years ago that was never officially announced, documented, or supported. External developers discovered this API and used it to build valuable integrations, most notably the [Home Assistant integration](https://github.com/SpanPanel/span). SPAN API acknowledges this community effort by formally documenting v1 endpoints (as deprecated) while introducing MQTT/Homie as the path forward for real-time data, along with v2 REST endpoints for administrative operations.

The MQTT/Homie interface is a significant improvement for obtaining and maintaining the dynamic state of SPAN Panel (which is by far the most prevalent use-case), obviating the need for clients to repeatedly poll REST endpoints for this data. **For panel state and measurements, use MQTT subscriptions instead of REST API polling.**

##### [v1-Only Endpoints (Deprecated)](#v1-only-endpoints-deprecated)

The following v1 endpoints provided SPAN Panel state and control via REST. **This functionality is now available through the MQTT/Homie interface.** These endpoints will be removed on the [sunset date](#sunset-date) (December 31, 2026).

All Homie/eBus topics below are relative to `ebus/5/<serial>/`

| Method | Endpoint | Operation | Homie/eBus Topic |
| --- | --- | --- | --- |
| GET | `/api/v1/status` | Subscribe | `$state` (see note) |
| GET | `/api/v1/panel` | Subscribe | `core/#` |
| GET | `/api/v1/panel/grid` | Subscribe | `core/relay` |
| POST | `/api/v1/panel/grid` | — | *(no MQTT equivalent)* |
| GET | `/api/v1/panel/power` | Subscribe | `core/*` power properties |
| GET | `/api/v1/panel/meter` | Subscribe | `lugs-*/#` |
| GET | `/api/v1/circuits` | Subscribe | `<circuit-id>/#` |
| GET | `/api/v1/circuits/{id}` | Subscribe | `<circuit-id>/#` |
| POST | `/api/v1/circuits/{id}` | Publish | `<circuit-id>/*/set` |
| GET | `/api/v1/storage/soe` | Subscribe | `bess/soe` |
| POST | `/api/v1/storage/soe` | — | *(no MQTT equivalent)* |
| GET | `/api/v1/storage/nice-to-have-thresh` | — | *(no MQTT equivalent)* |
| POST | `/api/v1/storage/nice-to-have-thresh` | — | *(no MQTT equivalent)* |
| GET | `/api/v1/islanding-state` | Subscribe | `bess/grid-state` |
| POST | `/api/v1/panel/emergency-reconnect` | — | *(no MQTT equivalent)* |
| GET | `/api/v1/wifi/status` | Subscribe | `core/wifi`, `wifi-ssid` |
| GET | `/api/v1/wifi/scan` | — | *(no MQTT equivalent)* |
| POST | `/api/v1/wifi/connect` | — | *(no MQTT equivalent)* |

**Note on `/api/v1/status`:** The v1 status endpoint returns a large object with many fields. The v2 status endpoint (`GET /api/v2/status`) is not a direct replacement—it returns only `serialNumber` and `firmwareVersion` for basic identification. For real-time SPAN Panel state, subscribe to MQTT topics.

##### [Deprecation HTTP Headers](#deprecation-http-headers)

All `/api/v1/*` endpoints return HTTP headers indicating their deprecation status:

| Header | Value | Description |
| --- | --- | --- |
| `Deprecation` | `true` | Endpoint is deprecated |
| `Sunset` | `2026-12-31` | Date when v1 endpoints will be removed |
| `Link` | `</api/v2/...>; rel="successor-version"` | v2 replacement (for dual-version endpoints) |

Example response from a v1-only endpoint:

```http
GET /api/v1/status HTTP/1.1

HTTP/1.1 200 OK
Deprecation: true
Sunset: 2026-12-31
```

Example response from a dual-version endpoint (v1 path):

```http
GET /api/v1/auth/clients HTTP/1.1

HTTP/1.1 200 OK
Deprecation: true
Sunset: 2026-12-31
Link: </api/v2/auth/clients>; rel="successor-version"
```

##### [Sunset Date](#sunset-date)

**All v1 endpoints will be removed on: December 31, 2026**

After this date, all `/api/v1/*` paths will return `404 Not Found`.

##### [Migration Summary](#migration-summary)

| v1 / Polling Approach | SPAN API v2 Replacement |
| --- | --- |
| Poll `/api/v1/panel` for state | Subscribe to MQTT topics |
| Poll `/api/v1/circuits` for circuit data | Subscribe to circuit node topics |
| POST to `/api/v1/circuits/{id}` for control | Publish to `/set` topics via MQTT |
| `/api/v1/auth/register` for tokens | `/api/v2/auth/register` |

##### [Migration Recommendations](#migration-recommendations)

1. **Use MQTT/Homie** for all SPAN Panel state and real-time data
2. **Use REST API v2** for authentication, certificates, and configuration
3. **Check deprecation headers** and log warnings for monitoring
4. **Complete migration before sunset date** (2026-12-31)

SPAN anticipates offering SPAN API for additional SPAN Panel models in the second half of 2026.

Note that v1 REST endpoints are provided only on MAIN 32 during the deprecation period and will not be available on other SPAN Panel models.

## [Obtaining SPAN API Authentication Credentials](#obtaining-span-api-authentication-credentials)

To recap:

- SPAN API clients accessing authenticated REST endpoints **MUST** include an `accessToken` within the request; the `accessToken` is obtained via the [auth/register endpoint](#authentication-endpoint) which requires the `hopPassphrase` in the request body.
- SPAN API clients connecting to the SPAN Panel eBus MQTT broker **MUST** authenticate with `ebusBrokerPassword`, which is obtained via the [auth/register endpoint](#authentication-endpoint), which itself requires the `hopPassphrase`.

Therefore a SPAN API client must possess the `hopPassphrase` in order to authenticate; two methods of obtaining this credential are provided:

1. Proof-of-proximity: When the SPAN Panel door switch is depressed three times in rapid succession, authentication of the `auth/register` endpoint is disabled for approximately 15 minutes. During this interval, requests to [auth/register](#authentication-endpoint) will bypass the check of the `hopPassphrase` in the request body, and the response received will contain the `hopPassphrase`, `ebusBrokerPassword`, and the `accessToken`.
2. [SPAN Home mobile app](https://www.span.io/app) users can navigate to a page that provides the `hopPassphrase`of SPAN Panel.

The [`span-auth`](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/span-auth) script manages authentication credentials:

```shell
# SPAN Panel door switch is pressed 3 times in rapid succession,
#   within 15 minutes execute the following command:

$ span-auth setup

Discovering SPAN panels on the network...
Found 1 panel(s)

Setting up ab-1234-c5d67 (span-ab-1234-c5d67.local)...
  Trying door bypass...
  ✓ Credentials saved for ab-1234-c5d67

Successfully configured 1 panel(s).
Credentials saved to: /Users/you/.span-auth.json
```

Alternatively, if you know the `hopPassphrase` of your SPAN Panel:

```shell
$ span-auth setup -p YOUR_PASSPHRASE
```

Credentials are stored in `~/.span-auth.json` and used automatically by the other scripts (`span-mqtt-sub`, `span-curl`). See [`scripts/README.md`](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/README.md) for complete usage documentation.

## [Accessing & Exploring SPAN API](#accessing--exploring-span-api)

The [span-mqtt-sub](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/span-mqtt-sub) script provides the easiest way to explore SPAN API. It wraps `mosquitto_sub` with automatic credential loading and provides the topic macro `@s` to simplify topic paths.

After running `span-auth setup`, credentials are loaded automatically:

```shell
# Subscribe to SPAN Panel state (uses default SPAN Panel from ~/.span-auth.json)
$ span-mqtt-sub -t '@s/$state' -v

# Override SPAN Panel if you have multiple
$ span-mqtt-sub -u ab-1234-c5d6 -t '@s/$state' -v
```

The `@s` macro expands to `ebus/5/<serial-number>`.

To subscribe and obtain the value of the `$state` attribute:

```shell
$ span-mqtt-sub -C 1 -t '@s/$state' -v

ebus/5/ab-1234-c5d67/$state ready
```

To obtain the `$description` attribute (which provides the schema description for this SPAN Panel) and format it for easier reading using the [`jq`](https://jqlang.org) utility:

```shell
$ span-mqtt-sub -C 1 -t '@s/$description' | jq

{
  "homie": "5.0",
  "version": 1766683742148,
  "type": "energy.ebus.device.distribution-enclosure",
  "name": "SPAN Panel eBus Adapter",
  "nodes": {
    "core": {
      "name": "Distribution Enclosure Core",
      "type": "energy.ebus.device.distribution-enclosure.core",
      "properties": {
        "vendor-name": {
          "name": "Vendor name",
          "datatype": "string"
        },
        "serial-number": {
          "name": "Serial number",
          "datatype": "string"
        },
        "hardware-version": {
          "name": "Hardware version",
          "datatype": "string"
        },
        "software-version": {
          "name": "Software version",
          "datatype": "string"
        },
TRUNCATED FOR BREVITY
```

To subscribe and receive all topics published by SPAN API, the result will be a continuous stream of `topic: value` pairs.

```shell
$ span-mqtt-sub -t '@s/#' -v
```

For those who prefer a GUI, [MQTT Explorer](https://mqtt-explorer.com/) is a free multi-platform app for browsing MQTT brokers. You will need to configure it with the SPAN Panel hostname, port (8883), credentials, and CA-certificate.

## [Service Discovery of SPAN Panel & SPAN API](#service-discovery-of-span-panel--span-api)

SPAN Panel claims a `.local` hostname, and advertises the network services it provides, via [multicast DNS (mDNS)](https://en.wikipedia.org/wiki/Multicast_DNS).

The [span-discover](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/span-discover) script provides an easy way to find all SPAN panels on your network:

```shell
$ span-discover

Found 1 SPAN panel(s):

  Serial: ab-1234-c5d67
  Hostname: span-ab-1234-c5d67.local
  Addresses: 192.0.2.100
  Model: SPAN32
  Firmware: spanos2/r202546/03
```

For browsing mDNS service advertisements interactively, the Discovery app is available for [macOS](https://apps.apple.com/us/app/discovery-dns-sd-browser/id1381004916) and [Android](https://play.google.com/store/apps/details?id=com.mdns_discovery.app).

### [mDNS .local Hostname](#mdns-local-hostname)

SPAN Panel claims (and resolves) a mDNS `.local` hostname in the format

`span-{serialNumber}.local`

This hostname can be used to discover and connect to SPAN Panel, by hosts and clients capable of using and resolving mDNS hostnames.  Of course IP addresses can be used instead of the `.local` hostname, if preferred.

### [mDNS Service Advertisements](#mdns-service-advertisements)

SPAN Panel advertises each network service it provides, as illustrated by the following examples, using the [span-mdns-query](https://github.com/spanio/SPAN-API-Client-Docs/blob/main/scripts/span-mdns-query) script.

#### [HTTP REST API Advertisement](#http-rest-api-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _http

Instance:   span-ab-1234-c5d67-HTTP-API
Type:       _http._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       80
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  path = /api
  schema = /api/openapi.json
  docs = /api/docs
  versions = v1,v2
  version_default = v2
  v1_path = /api/v1
  v1_deprecated = true
  v2_path = /api/v2
  txtvers = 1
```

#### [HTTPS REST API Advertisement](#https-rest-api-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _https

Instance:   span-ab-1234-c5d67-HTTPS-API
Type:       _https._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       443
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  path = /api
  schema = /api/openapi.json
  docs = /api/docs
  versions = v1,v2
  version_default = v2
  v1_path = /api/v1
  v1_deprecated = true
  v2_path = /api/v2
  txtvers = 1
```

#### [MQTTS Broker Advertisement](#mqtts-broker-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _secure-mqtt

Instance:   span-ab-1234-c5d67-MQTTS
Type:       _secure-mqtt._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       8883
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  protocol = mqtt
  versions = 3.1,3.1.1,5.0
  txtvers = 1
```

#### [Websocket MQTT Broker Advertisement](#websocket-mqtt-broker-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _mqtt-ws

Instance:   span-ab-1234-c5d67-MQTT-WS
Type:       _mqtt-ws._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       9001
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  protocol = mqtt
  versions = 3.1,3.1.1,5.0
  subprotocol = mqtt
  txtvers = 1
```

#### [Secure Websocket MQTT Broker Advertisement](#secure-websocket-mqtt-broker-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _mqtt-wss

Instance:   span-ab-1234-c5d67-MQTT-WSS
Type:       _mqtt-wss._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       9002
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  protocol = mqtt
  versions = 3.1,3.1.1,5.0
  subprotocol = mqtt
  txtvers = 1
```

#### [Metadata Advertisements](#metadata-advertisements)

Generally speaking mDNS advertisements are provided only for network services offered by a host, but there is value in advertising host metadata, SPAN Panel supports both the `device-info` convention and an eBus advertisement:

##### [Device-Info Metadata Advertisement](#device-info-metadata-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _device-info

Instance:   span-ab-1234-c5d67
Type:       _device-info._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       0
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  manufacturer = SPAN.io
  model = SPAN32
  hardware_version = 1.2
  serial_number = ab-1234-c5d67
  firmware_version = spanos2/r202546/03
  eth0_mac = 00:19:b8:09:f6:48
  wlan0_mac = 08:3a:88:1f:9c:6e
  wlan0_ap_mac = 08:3a:88:a2:9c:6e
  eth1_mac = unknown
  txtvers = 1
```

##### [eBus Metadata Advertisement](#ebus-metadata-advertisement)

```shell
$ span-mdns-query ab-1234-c5d67 _ebus

Instance:   span-ab-1234-c5d67-EBUS
Type:       _ebus._tcp.local.
Hostname:   span-ab-1234-c5d67.local.
Port:       0
Addresses:  192.0.2.1, 2001:db8::1, 2001:db8::2
TXT Records:
  homie_domain = ebus
  homie_version = 5
  homie_roles = device
  mqtt_broker = span-ab-1234-c5d67
  txtvers = 1
```

## [Transport Security](#transport-security)

SPAN API clients **SHOULD** use [TLS](https://en.wikipedia.org/wiki/Transport_Layer_Security) (MQTTS, WSS, and HTTPS) whenever possible, so SPAN API interactions are encrypted.

TLS certificate verification requires that the client:

- Checks the server-certificate expiration date
- Compares the domain name within the server-certificate to the domain name the client used to connect to the server
- Compares the digital certificate used to sign the certificate against a trusted root Certificate Authority (CA) in a certificate chain

Given that SPAN Panel is network-connected to the home’s LAN (which SPAN Panel does not manage or control), it is somewhere between technically difficult and infeasible to provide a certificate that contains, and is accessible by, a domain name and that is signed by a public well-known CA (chain).

In order to support TLS, SPAN Panel generates (and maintains) a self-signed CA-certificate, which is used to sign a server-certificate that is used by both the MQTT broker and REST/HTTP server.

SPAN API provides an [unauthenticated endpoint](#download-ca-certificate-endpoint) for client requests for the SPAN Panel CA-certificate, which the client **MAY** use (subsequently) to verify TLS connections to the MQTT broker and/or HTTP server.

The SPAN Panel server-certificate contains Subject Alternative Names (SANs) as follows:

- The mDNS `.local` hostname of SPAN Panel, in the form `span-{serialNumber}.local` e.g. `span-ab-1234-c5d6.local`
- The IP addresses assigned to each of the SPAN Panel network interfaces

For homeowners that provide and support a DNS server on the home LAN, and have configured a FQDN for a SPAN Panel, [SPAN API REST endpoints are provided to configure the assigned FQDN](#endpoints-enabling-fqdn-inclusion-in-server-certificate-san), for the sole purpose of adding the FQDN to the SAN list of the SPAN Panel server-certificate.

A client **MAY** download the SPAN Panel CA-certificate, and thereafter connect to the SPAN Panel MQTT broker and/or HTTP server via TLS, and use the CA-certificate for TLS verification.

SPAN Panel maintains its server-certificate, renewing it prior to expiration, and regenerating the certificate whenever any of its network interfaces is assigned a new/different IP address.  Homeowners are encouraged to configure the [DHCP](https://en.wikipedia.org/wiki/Dynamic_Host_Configuration_Protocol) server with static IP address assignments for the panel’s network interface MAC addresses, in order to minimize server-certificate regeneration.

JavaScript applications (especially when browser-based) typically lack the ability to use the MQTT protocol natively, and access MQTT brokers via Websockets, so the SPAN Panel MQTT broker provides both the MQTT and Websocket protocols (as do many other MQTT brokers).

SPAN Home On-premise is a (JavaScript) application provided by SPAN Panel, providing local control and management of SPAN Panel via a web browser, and is itself a SPAN API client.  In order to provide the simplest and easiest user experience for a Homeowner, SPAN Home On-premise and SPAN API provide a non-TLS workflow (via HTTP and WS).  This is a deliberate and conscious tradeoff to provide the Homeowner the simplest tool for panel management at times when transport security may not be the highest priority (for example, during a power outage).

### [Security Considerations for Self-Signed Certificates](#security-considerations-for-self-signed-certificates)

SPAN Panel uses self-signed certificates because it operates on a local network where public Certificate Authority validation is not feasible. While this enables TLS encryption, users should be aware of the following:

- **Trust scope:** Only add the SPAN Panel CA-certificate to trust stores of applications dedicated to SPAN API access. Never add it to general-purpose web browsers used for Internet browsing.
- **Initial trust:** The first download of the CA-certificate (via `GET /api/v2/certificate/ca`) occurs over HTTP. Ensure you are on your home network and connected to the correct SPAN Panel.
- **Certificate changes:** If the SPAN Panel CA-certificate changes unexpectedly, investigate before trusting the new certificate.

For more information about self-signed certificates, see [DigiCert's guide on self-signed certificates](https://www.digicert.com/resources/self-signed-certificate).

## [Frequently Asked Questions with Answers](#frequently-asked-questions-with-answers)

### [Why is SPAN API offered initially on SPAN Panel MAIN 32?](#why-is-span-api-offered-initially-on-span-panel-main-32)

SPAN Panel MAIN 32 included an internal API that, while never officially released, was discovered and adopted by the developer community. SPAN API development began by formally documenting that API (now designated as v1, deprecated), then designing and implementing the new MQTT/Homie interface along with v2 REST endpoints. This foundational work on MAIN 32 positions SPAN to offer SPAN API on newer Panel models in the second half of 2026.

### [When will the v1 REST endpoints be discontinued?](#when-will-the-v1-rest-endpoints-be-discontinued)

The v1 REST endpoints are deprecated and will be removed on **December 31, 2026**. All v1 endpoints return HTTP headers indicating their deprecation status (see [Deprecation HTTP Headers](#deprecation-http-headers)). Developers **SHOULD** migrate to the MQTT/Homie interface for real-time SPAN Panel state and measurements, and use v2 REST endpoints for authentication and configuration. See [Migrating from v1 REST Endpoints](#migrating-from-v1-rest-endpoints) for details.

### [Will SPAN API become available for SPAN Panel models other than MAIN 32?](#will-span-api-become-available-for-other-span-panel-models)

SPAN plans to provide SPAN API on newer SPAN Panel models (MAIN 40, MLO 48, MAIN 16, and MLO 24) in the second half of 2026. This timing is an estimate only and is not binding on SPAN.

### [Will the existing Home Assistant integration for SPAN be compatible with this new SPAN API?](#will-the-existing-home-assistant-integration-for-span-be-compatible-with-this-new-span-api)

The [existing Home Assistant integration for SPAN](https://github.com/SpanPanel/span) uses the v1 REST endpoints, which remain available during the deprecation period (until December 31, 2026). To continue working after the sunset date, the integration will need to be updated to use the MQTT/Homie interface for real-time panel state and measurements, and v2 REST endpoints for authentication. The migration path is documented in [Migrating from v1 REST Endpoints](#migrating-from-v1-rest-endpoints).

### [Does SPAN API work with SPAN Drive?](#does-span-api-work-with-span-drive)

Yes. SPAN Drive connects directly to SPAN Panel through a SPAN-specific connection (using a non-Internet Protocol transport) and is not independently network-accessible. When a SPAN Drive is paired with SPAN Panel, SPAN API publishes SPAN Drive status, state, and metadata through the Homie node with type `energy.ebus.device.evse`. This enables integrations to monitor charging state, energy usage, and other SPAN Drive properties through SPAN API.

### [Why is this a beta? When will it be final?](#why-is-this-a-beta-when-will-it-be-final)

A primary goal for any API is to meet the needs of application developers. During the design of SPAN API, decisions and tradeoffs were made without the benefit of real-world developer feedback. The beta period allows SPAN to understand the issues developers encounter while using SPAN API.

Most developers have little or no experience with the Homie Convention—including SPAN. SPAN wants to learn: Is the SPAN Panel data model as represented via Homie the best and most general approach? MQTT works well for publishing status and state, but are there concerns with SPAN Panel control functions provided via MQTT rather than REST?

SPAN welcomes constructive feedback from developers as they begin to use SPAN API. That said, incorporation of any feedback is at SPAN's sole discretion.

A timeline for exiting beta has not been established.

## Contributing

This repository does not accept pull requests. All changes are managed through SPAN's internal development process.

### How to Contribute

- **Bug Reports:** Use [Issues](https://github.com/spanio/SPAN-API-Client-Docs/issues) for documentation errors, script bugs, or SPAN API issues
- **Feature Requests:** Use [GitHub Discussions](https://github.com/spanio/SPAN-API-Client-Docs/discussions) for suggestions and ideas
- **Questions:** Use [GitHub Discussions](https://github.com/spanio/SPAN-API-Client-Docs/discussions) to connect with other developers

Suggestions and corrections will be reviewed and, if accepted, implemented by SPAN and included in a future release. Any and all recommendations of changes to SPAN API, including without limitation new features or functionality relating thereto, or any comments, questions, suggestions, or the like relating to SPAN API (collectively, "Feedback") is and will be treated as non-confidential. By using SPAN API, each Homeowner assigns to SPAN on its behalf all right, title, and interest in and to, and SPAN is free to use, without any attribution or compensation to any Homeowner, developer, or any other third party, any ideas, know-how, concepts, techniques, or other intellectual property rights contained in the Feedback, for any purpose whatsoever, although SPAN is not required to use any Feedback.

## [Appendix A: SPAN Panel Network Interfaces](#appendix-a-span-panel-network-interfaces)

SPAN Panel provides both client and hosted network interfaces, both hardwired Ethernet and Wi-Fi

### [SPAN Panel Client Network Interfaces](#span-panel-client-network-interfaces)

These interfaces connect to the home's LAN, and typically the home's LAN routes (provides access) to the public Internet. One of these client interfaces **SHOULD** be enabled and connected to the home's LAN:

- `eth0` \- Connection to home's LAN via hardwired Ethernet
- `wlan0` \- Connection to the home's LAN via home's Wi-Fi access point

### [SPAN Panel Hosted Network Interfaces](#span-panel-hosted-network-interfaces)

These interfaces are provided by SPAN Panel to facilitate network connections to energy-related devices in the home, in order to facilitate integrations between those devices and the Panel when it is not feasible to provide those connections via the home's LAN:

- `eth1` \- Direct hardwired Ethernet connection to SPAN Panel
- `wlan0_ap` \- A Wi-Fi AP provided by SPAN Panel

These SPAN Panel hosted networks provide access to SPAN Panel itself, and outbound-only access to the home's LAN (and the Internet), via Network Address Translation (NAT).
> *Note that a host connected to SPAN Panel via a hosted network interface will not be reachable/accessible by (other) hosts on the home LAN.*

For example, a Battery Energy Storage System (BESS) connected to SPAN Panel via a hosted network interface will not be accessible to other hosts on the home LAN, for example, a [Home Assistant BESS integration](https://www.home-assistant.io/integrations/powerwall/).

While SPAN API is served on all four network interfaces, most users will find access via the SPAN Panel client interfaces more accessible and easier to use, and SPAN API access via a client interface is **RECOMMENDED**

It is a well-established fact that network connections via hardwired Ethernet are faster, and more reliable, than Wi-Fi, SPAN API access via the `eth0` (Ethernet client interface) is **RECOMMENDED**.

The hosted Wi-Fi AP is powered by SPAN Panel directly, consequently might be the only network interface available in a grid/power outage.  [This document describes how to use the SPAN Home app in conjunction with SPAN Panel to connect to the hosted AP](https://support.span.io/hc/en-us/articles/4411570234519-Emergency-Reconnect), and provides clues how to connect and authenticate with this AP by other clients.

### [SPAN Panel & SPAN API Networking Recommended Best Practices](#span-panel--span-api-networking-recommended-best-practices)

- The SPAN Panel connection to the home's LAN **SHOULD** be via hardwired Ethernet, using the `eth0` interface.
- The home’s LAN infrastructure (e.g. Ethernet switch) **SHOULD** maintain (backup) power during grid-outages, or other power interruptions.
- Home energy infrastructure hosts (e.g. BESS, PV systems) **SHOULD** connect to the home LAN via hardwired Ethernet.
- The home LAN’s DHCP server **SHOULD** be configured with an IP address reservation for SPAN Panel, and for other home energy infrastructure hosts.
- A home LAN providing a DNS server **MAY** configure a FQDN for SPAN Panel (and any other home energy infrastructure hosts).  Having done so, homeowner **SHOULD** [use SPAN API to set the FQDN assigned to SPAN Panel](#endpoints-enabling-fqdn-inclusion-in-server-certificate-san) for inclusion in the TLS server-certificate SAN list of SPAN Panel.
- Dedicated IoT hosts on the home LAN **MAY** choose to download the SPAN Panel CA-certificate, and use TLS for SPAN API interactions,
- The home LAN’s connection to the Internet **MUST** include and support [secure firewall](https://en.wikipedia.org/wiki/Firewall_\(computing\)) functionality.  SPAN Panel network interfaces **MUST NOT** be directly accessible over the public Internet.
- The SPAN Panel CA-certificate **SHOULD NOT** be added to the trust-store of a web browser used to access secure websites.
