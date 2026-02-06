# V2Ray Subscription Server (Modular)

A modular **V2Ray / VLESS subscription server** built with **FastAPI**.
It aggregates multiple subscription sources, processes them using pluggable modules, and serves the result to clients in the required format (base64 / plain).

The project is designed for flexible subscription logic **without modifying the core server**.

---
## Since version 3.0.0, the code has been modularized. If you want to use rules and don't want to write your own module, download version 2.3.0.

## Features

* 🚀 FastAPI + Uvicorn
* 🔌 Modular subscription processing
* 📡 Aggregation of multiple sources
* 🔐 Base64 encode / decode support
* 🧩 Custom processing modules
* 📱 Client-aware behavior (v2rayTun, etc.)
* 📝 Flexible logging system

---

## Project Structure

```text
.
├── main.py                # Main server
├── module.py              # Example processing module
├── config.json            # Main server config
├── module_config.json     # Module config
├── sub.log                # Logs (default)
└── README.md
```

---

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install fastapi uvicorn requests
```

---

## Run

```bash
python main.py
```

The server will start on:

```
http://0.0.0.0:8991
```

---

## API

### Get subscription

```http
GET /cursed/sub/{sub_id}
```

**Example:**

```
GET /cursed/sub/abcdef123
```

Where `sub_id` is the subscription ID appended to every source URL.

---

## Main Config (`config.json`)

```json
{
  "sources": [],
  "module": {
    "file": "module",
    "func": "main",
    "config_file": "module_config.json"
  },
  "logging": {
    "log_level": "DEBUG",
    "log_file": "sub.log"
  },
  "server": {
    "prefix": "/cursed/sub",
    "port": 8991,
    "host": "0.0.0.0"
  }
}
```

### Fields description

#### `sources`

List of subscription sources:

```json
{
  "source": "https://example.com/sub/",
  "exists-check": true
}
```

* `source` — source URL (without `sub_id`)
* `exists-check` — if `true`, server returns 404 if the source is unavailable

---

## Modules

A module is a regular Python file that contains a subscription processing function.

### Module function signature

```python
def main(response_list, headers, sub_id, module_config):
    return status_code, content, headers, b64encode
```

### Parameters

* `response_list` — list of responses from sources
* `headers` — client HTTP headers
* `sub_id` — subscription ID
* `module_config` — module configuration

### Return values

| Parameter     | Description                        |
| ------------- | ---------------------------------- |
| `status_code` | HTTP status code                   |
| `content`     | List of strings (VLESS URLs)       |
| `headers`     | Response headers                   |
| `b64encode`   | Whether to encode output as base64 |

---

## Example Module (`module.py`)

Module functionality:

* Parses VLESS URLs
* Merges them into a single list
* Changes `announce` depending on `User-Agent`
* Returns a base64-encoded subscription

Supported clients:

* `v2rayTun`
* Standard V2Ray clients

---

## Module Config (`module_config.json`)

```json
{
  "profile-title": "A VPN",
  "subscription-userinfo": "",
  "profile-update-interval": "1",
  "announce": "HELLO",
  "v2raytun-announce": "HELLO2",
  "announce-url": "https://t.me/moau12"
}
```

---

## Logging

Supported log levels:

* `DEBUG`
* `INFO`
* `WARNING`
* `ERROR`
* `CRITICAL`

Logs are written to:

* file (`sub.log`)
* stdout

---

## Ideas for Extensions

* 🔐 Token-based authentication
* 🗂 Subscription caching
* 📊 Metrics
* 🔁 Auto-refresh sources
* 🌍 Geo-based node filtering

---

## License

MIT