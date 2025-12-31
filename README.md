---

# XRay Subscription Mixer

A lightweight and flexible **subscription mixer** built with **FastAPI + Uvicorn + requests**.
It combines multiple XRay/V2Ray subscription sources, modifies profile metadata, adjusts V2RayTun-specific fields, rewrites IPs based on SNI detection, **adds custom flag emojis to connection names**, and serves the final subscription over HTTP.

---

## Features

* Merge one or multiple subscription URLs (`sources`)
* Modify:

  * Profile title (`profile-title`)
  * Profile description (`announce`)
  * **V2RayTun-specific description** with color support (`v2raytun-announce`)
* Extract subscription userinfo by index (`subscription-userinfo-ord`)
* Supports color formatting for V2RayTun
  (Full header documentation:
  **[https://docs.v2raytun.com/overview/supported-headers](https://docs.v2raytun.com/overview/supported-headers)**)
* Replace IP addresses using SNI matching (`replace-ip`)
* **Add custom flag emojis to connection names** based on SNI rules (`flag`)
* Runs on **FastAPI + Uvicorn**
* Auto-update interval for fetching sources (`profile-update-interval`)
* Configurable HTTP endpoint prefix (`server-settings.accept-prefix`)

---
## Sequence diagram

![diagram](example.png)

---

## Example `config.json`

```json
{
    "type": "mixer",
    "sources": [
        "http://url/path/",
        "https://url1/path/"
    ],
    "profile-title": "NAME VPN",
    "announce": "ABOUT",
    "v2raytun-announce": "#d9c1c1ABOUT",
    "subscription-userinfo-ord": 0,
    "profile-update-interval": 1,

    "announce-url": "https://example.com/path",
    "support-url": "https://example.com/path",

    "replace-ip": {
        "0": {
            "sni": ["www.google.com", "google.com"],
            "ip": "1.2.3.4",
            "port": 8443,
            "flag": "🇺🇸 "
        },
        "1": {
            "sni": ["www.speedtest.net", "speedtest.net"],
            "ip": "2.3.4.5",
            "flag": "🇩🇪 "
        }
    },

    "server-settings": {
        "accept-prefix": "/cursed/sub",
        "bind": "0.0.0.0",
        "port": 8080
    }
}
```

---

## Configuration Fields

### **Main Fields**

| Field                       | Type        | Required | Description                                         |
| --------------------------- | ----------- | -------- | --------------------------------------------------- |
| `type`                      | `str`       | ✅ Yes   | Configuration type (e.g., `"mixer"`)                |
| `sources`                   | `list[str]` | ✅ Yes   | List of subscription URLs                           |
| `profile-title`             | `str`       | ✅ Yes   | Final profile name                                  |
| `announce`                  | `str`       | ❌ No     | Profile description                                 |
| `v2raytun-announce`         | `str`       | ❌ No     | Description for V2RayTun (**supports color codes**) |
| `subscription-userinfo-ord` | `int`       | ✅ Yes   | Index for extracting `subscription-userinfo`        |
| `profile-update-interval`   | `int`       | ✅ Yes   | Subscription refresh interval (minutes)             |
| `announce-url`              | `str`       | ❌ No     | URL for announcements                               |
| `support-url`               | `str`       | ❌ No     | Support contact URL                                 |

---

### **IP Replacement (`replace-ip`)**

| Field                | Type        | Required             | Description                                    |
| -------------------- | ----------- | -------------------- | ---------------------------------------------- |
| `replace-ip`         | object      | ❌ No                | IP rewrite rules keyed by index                |
| `replace-ip[n].sni`  | `list[str]` | ✅ Yes (when exists) | List of SNI values to match                    |
| `replace-ip[n].ip`   | `str`       | ✅ Yes               | New IP replacing matched SNI                   |
| `replace-ip[n].port` | `int`       | ❌ No                | Change port in vless url                       |
| `replace-ip[n].flag` | `str`       | ❌ No                | **Flag emoji prefix for connection name** 🆕   |

The `flag` field allows you to add custom emoji prefixes (like country flags 🇺🇸 🇩🇪 🇯🇵) to connection names that match the specified SNI. This makes it easier to identify connections at a glance.

Example:

```json
"replace-ip": {
    "0": {
        "sni": ["www.example.com", "example.com"],
        "ip": "1.1.1.1",
        "port": 8443,
        "flag": "🇺🇸 "
    },
    "1": {
        "sni": ["cdn.cloudflare.net"],
        "ip": "2.2.2.2",
        "flag": "🌐 "
    }
}
```

**Note:** Don't forget to add a space after the emoji if you want separation between the flag and the connection name!

---

### **Server Settings (`server-settings`)**

| Field             | Type   | Required | Description                             |
| ----------------- | ------ | -------- | --------------------------------------- |
| `server-settings` | object | ✅ Yes   | HTTP server configuration               |
| `accept-prefix`   | `str`  | ✅ Yes   | URL prefix where subscription is served |
| `bind`            | `str`  | ✅ Yes   | Listening address                       |
| `port`            | `int`  | ✅ Yes   | Listening port                          |

---

## Running the Server

### Install dependencies

```bash
pip install fastapi uvicorn requests
```

### Linux
```bash
python3 main.py
```

### Windows
```bash
python main.py
```

---

## Example Subscription URL

```
http://SERVER:PORT/cursed/sub/subscribe
```

---

## V2RayTun Header Documentation

To understand all extended headers supported by V2RayTun (including color formatting), refer to:

 **[https://docs.v2raytun.com/overview/supported-headers](https://docs.v2raytun.com/overview/supported-headers)**

---

## Flag Feature Examples

The flag feature is perfect for organizing connections by country, provider, or type:

```json
"replace-ip": {
    "0": {
        "sni": ["us-server.example.com"],
        "ip": "1.2.3.4",
        "flag": "🇺🇸 USA | "
    },
    "1": {
        "sni": ["de-server.example.com"],
        "ip": "5.6.7.8",
        "flag": "🇩🇪 Germany | "
    },
    "2": {
        "sni": ["cdn.example.com"],
        "ip": "9.10.11.12",
        "flag": "⚡ Fast | "
    }
}
```

This will transform connection names like `Server-01` into `🇺🇸 USA | Server-01` automatically!

---
