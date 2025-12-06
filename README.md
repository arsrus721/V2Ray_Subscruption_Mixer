# xray-sub-mixer

## <span style="color: grey;">I don't have many time to debug if you find any bug, please create issue</span>

---

# XRay Subscription Mixer

A lightweight and flexible **subscription mixer** built with **FastAPI + Uvicorn**.
It combines multiple XRay/V2Ray subscription sources, modifies profile metadata, adjusts V2RayTun-specific fields, rewrites IPs based on SNI detection, and serves the final subscription over HTTP.

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
* Runs on **FastAPI + Uvicorn**
* Auto-update interval for fetching sources (`profile-update-interval`)
* Configurable HTTP endpoint prefix (`server-settings.accept-prefix`)

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
            "ip": "1.2.3.4"
        },
        "1": {
            "sni": ["www.speedtest.net", "speedtest.net"],
            "ip": "2.3.4.5"
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
| `type`                      | `str`       | ✔️ Yes   | Configuration type (e.g., `"mixer"`)                |
| `sources`                   | `list[str]` | ✔️ Yes   | List of subscription URLs                           |
| `profile-title`             | `str`       | ✔️ Yes   | Final profile name                                  |
| `announce`                  | `str`       | ❌ No     | Profile description                                 |
| `v2raytun-announce`         | `str`       | ❌ No     | Description for V2RayTun (**supports color codes**) |
| `subscription-userinfo-ord` | `int`       | ✔️ Yes   | Index for extracting `subscription-userinfo`        |
| `profile-update-interval`   | `int`       | ✔️ Yes   | Subscription refresh interval (minutes)             |
| `announce-url`              | `str`       | ❌ No     | URL for announcements                               |
| `support-url`               | `str`       | ❌ No     | Support contact URL                                 |

---

### **IP Replacement (`replace-ip`)**

| Field               | Type        | Required             | Description                     |
| ------------------- | ----------- | -------------------- | ------------------------------- |
| `replace-ip`        | object      | ❌ No                 | IP rewrite rules keyed by index |
| `replace-ip[n].sni` | `list[str]` | ✔️ Yes (when exists) | List of SNI values to match     |
| `replace-ip[n].ip`  | `str`       | ✔️ Yes               | New IP replacing matched SNI    |

Example:

```json
"replace-ip": {
    "0": {
        "sni": ["example.com"],
        "ip": "1.1.1.1"
    }
}
```

---

### **Server Settings (`server-settings`)**

| Field             | Type   | Required | Description                             |
| ----------------- | ------ | -------- | --------------------------------------- |
| `server-settings` | object | ✔️ Yes   | HTTP server configuration               |
| `accept-prefix`   | `str`  | ✔️ Yes   | URL prefix where subscription is served |
| `bind`            | `str`  | ✔️ Yes   | Listening address                       |
| `port`            | `int`  | ✔️ Yes   | Listening port                          |

---

## Running the Server
Linux
```bash
python3 main.py
```

Windows
```bash
python main.py
```

### Install dependencies

```bash
pip install fastapi uvicorn 
```

## Example Subscription URL

```
http://SERVER:PORT/cursed/sub/subscribe
```

or

```
http://SERVER:PORT/cursed/sub/subscribe
```

---

## V2RayTun Header Documentation

To understand all extended headers supported by V2RayTun (including color formatting), refer to:

 **[https://docs.v2raytun.com/overview/supported-headers](https://docs.v2raytun.com/overview/supported-headers)**

---
