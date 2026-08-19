# SPAN Home On-premise (HOP) Dashboard: Auto-Login via URL Query Parameter

The SPAN Home On-premise (HOP) Local Dashboard login page supports an optional `passphrase` query parameter that enables automatic authentication without manual user input. This allows external tooling (installer apps, integration scripts, deep-links) to open the dashboard already authenticated.

## URL Format

```
http://<panel-ip>/login?passphrase=<hopPassphrase>
```

| Component | Description |
|---|---|
| `<panel-ip>` | The IP address or hostname of the SPAN Panel on the local network. |
| `<hopPassphrase>` | The Home On-premise passphrase. Must be URL-encoded if it contains special characters or spaces (standard percent-encoding). |

## Example

```
http://192.168.1.100/login?passphrase=my-secret-passphrase
```

With a passphrase containing spaces:

```
http://192.168.1.100/login?passphrase=my%20secret%20passphrase
```

## Underlying API Call

When a `passphrase` query parameter is present, the dashboard automatically submits it to the existing registration endpoint:

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "dashboard",
  "hopPassphrase": "<value from query param>"
}
```

This is the same endpoint used by the manual login form; the query parameter simply automates the submission.

The client `name` is significant. `dashboard` is the one name the panel treats as re-registrable: registering it again replaces the existing client, which is what lets auto-login run repeatedly. Registering any other name a second time is rejected with `422 Unprocessable Entity` and the message `Name already exists`, so a client that used its own name here would authenticate once and fail on every later attempt.

## Behavior

| Scenario | Result |
|---|---|
| Valid passphrase | User is authenticated and redirected to `/home`. |
| Invalid passphrase (HTTP 422) | User is returned to the login form with the passphrase pre-filled and an "Incorrect passphrase" error displayed. |
| Other server error | User is returned to the login form with a "Failed to authenticate" toast notification. |
| Empty or whitespace-only value | Parameter is ignored; the standard login form is displayed. |
| Unknown extra query parameters | Extra parameters are stripped but do not prevent auto-login (e.g., `?passphrase=secret&foo=bar` still works). |

## Security Considerations

- The `passphrase` query parameter is **immediately removed** from the browser URL (via history replacement) after it is consumed. This prevents the passphrase from persisting in browser history or the address bar.
- Leading and trailing whitespace in the passphrase value is trimmed before submission.
