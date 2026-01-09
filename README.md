# V2Ray Subscription Mixer

A flexible V2Ray subscription mixer that combines multiple subscription sources with advanced rule-based configuration modification.

## Description

V2Ray Subscription Mixer is a tool for merging multiple V2Ray subscriptions into one, with flexible modification of connection parameters through a rule system. The mixer allows you to combine sources and modify comments, IP addresses, ports, and SNI on the fly.

## Features

- 🔄 Combine multiple subscription sources into one
- 🎯 Flexible rule system for configuration modification
- 🏷️ Advanced comment management for connections
- 🔧 Modify base parameters (IP, port, SNI)
- 📊 Support for subscription headers (compatible with [v2raytun headers](https://docs.v2raytun.com/overview/supported-headers))
- 🚀 Fast and lightweight FastAPI-based server

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/V2Ray_Subscription_Mixer.git
cd V2Ray_Subscription_Mixer
```

2. Install required dependencies:
```bash
pip install fastapi uvicorn requests
```

3. Copy one of the configuration files to the root directory:
```bash
# For minimal configuration
cp minimum_conf/config.json config.json

# OR for maximum configuration with examples
cp maximum_conf/config.json config.json
```

4. Edit `config.json` according to your needs

5. Run the server:
```bash
python3 main.py
# or
python main.py
```

## Configuration

### Minimal Configuration Example

```json
{
    "type": "mixer",
    "sources": ["http://url/path/", "https://url1/path/"],
    "profile-title": "NAME VPN",
    "announce": "ABOUT",
    "v2raytun-announce": "#d9c1c1ABOUT",
    "subscription-userinfo-ord": 0,
    "profile-update-interval": 1,
    "announce-url": "https://example.com/path",
    "support-url": "https://example.com/path",
    "rules": [],
    "server-settings": {
        "accept-prefix": "/cursed/sub",
        "bind": "0.0.0.0",
        "port": 8080
    }
}
```

### Configuration Parameters

| Parameter | Description |
|-----------|-------------|
| `type` | Configuration type (always "mixer") |
| `sources` | Array of subscription URLs to combine |
| `profile-title` | Name of the combined profile |
| `announce` | Announcement text |
| `v2raytun-announce` | V2RayTun-specific announcement |
| `subscription-userinfo-ord` | Subscription user info order |
| `profile-update-interval` | Update interval in hours |
| `announce-url` | URL for announcements |
| `support-url` | Support page URL |
| `rules` | Array of modification rules (see below) |
| `server-settings` | Server configuration |

### Server Settings

| Parameter | Description |
|-----------|-------------|
| `accept-prefix` | URL prefix for subscription endpoint |
| `bind` | IP address to bind to |
| `port` | Port number |
| `advanced-print` | Enable detailed logging (optional) |

## Rules System

Rules are matched by SNI (Server Name Indication) in vless or other protocol links. Each rule can contain `base` modifications and `comment` modifications.

### Base Modifications

Modify core connection parameters:

```json
"base": [
    {"type": "rewriteip", "ips": ["1.2.3.4", "5.6.7.8"]},
    {"type": "rewriteport", "port": 8080},
    {"type": "rewritesni", "sni": ["youtube.com", "www.youtube.com"]}
]
```

- **rewriteip** - Replace IP address (randomly selected from array)
- **rewriteport** - Replace port
- **rewritesni** - Replace SNI (randomly selected from array)

### Comment Modifications

Modify connection comments/names with various operations:

#### Add Operations
- **start-add** - Add text at the beginning
  ```json
  {"type": "start-add", "text": "PREFIX-"}
  ```

- **end-add** - Add text at the end
  ```json
  {"type": "end-add", "text": "-SUFFIX"}
  ```

- **start-exactly-add** - Add text at specific position from start
  ```json
  {"type": "start-exactly-add", "text": "INSERT", "count": 5}
  ```

- **end-exactly-add** - Add text at specific position from end
  ```json
  {"type": "end-exactly-add", "text": "INSERT", "count": 3}
  ```

- **add-after** - Add text after specified character/string
  ```json
  {"type": "add-after", "text": "NEW", "after": "-"}
  ```

- **add-before** - Add text before specified character/string
  ```json
  {"type": "add-before", "text": "NEW", "before": "-"}
  ```

#### Delete Operations
- **delete-all-after** - Delete everything after specified character/string
  ```json
  {"type": "delete-all-after", "after": "|"}
  ```

- **delete-all-before** - Delete everything before specified character/string
  ```json
  {"type": "delete-all-before", "before": "|"}
  ```

- **start-delete** - Delete N characters from start
  ```json
  {"type": "start-delete", "count": 6}
  ```
  Example: `NAMEtxtNEW` → `NAMEtx` (with count=6)

- **end-delete** - Delete N characters from end
  ```json
  {"type": "end-delete", "count": 3}
  ```

### Complete Rule Example

```json
{
    "sni": ["www.google.com", "google.com"],
    "base": [
        {"type": "rewriteip", "ips": ["1.2.3.4"]},
        {"type": "rewriteport", "port": 443},
        {"type": "rewritesni", "sni": ["cdn.example.com"]}
    ],
    "comment": [
        {"type": "start-add", "text": "🇺🇸 "},
        {"type": "end-add", "text": " | Premium"},
        {"type": "delete-all-after", "after": "|"}
    ]
}
```

## Usage

After starting the server, your combined subscription will be available at:

```
http://your-server:8080/cursed/sub
```

(Replace `/cursed/sub` with your `accept-prefix` value)

You can use this URL in your V2Ray client as a subscription link.

## Maximum Configuration Example

See `maximum_conf/config.json` for a complete example with all possible rule types:

```json
{
    "type": "mixer",
    "sources": ["http://url/path/", "https://url1/path/"],
    "profile-title": "NAME VPN",
    "announce": "ABOUT",
    "v2raytun-announce": "#d9c1c1ABOUT",
    "subscription-userinfo-ord": 0,
    "profile-update-interval": 1,
    "announce-url": "https://example.com/path",
    "support-url": "https://example.com/path",
    "rules": [
        {
            "sni": ["www.google.com", "google.com"],
            "base": [
                {"type": "rewriteip", "ips": ["1.2.3.4"]},
                {"type": "rewriteport", "port": 8080},
                {"type": "rewritesni", "sni": ["youtube.com", "www.youtube.com"]}
            ],
            "comment": [
                {"type": "start-add", "text": "TEXT"},
                {"type": "end-add", "text": "TEXT"},
                {"type": "start-exactly-add", "text": "TEXT", "count": 1},
                {"type": "end-exactly-add", "text": "TEXT", "count": 1},
                {"type": "add-after", "text": "TEXT", "after": "TEXT"},
                {"type": "add-before", "text": "TEXT", "before": "before"},
                {"type": "delete-all-after", "after": "TEXT"},
                {"type": "delete-all-before", "before": "TEXT"},
                {"type": "start-delete", "count": 1},
                {"type": "end-delete", "count": 1}
            ]
        }
    ],
    "server-settings": {
        "accept-prefix": "/cursed/sub",
        "bind": "0.0.0.0",
        "port": 8080,
        "advanced-print": true
    }
}
```

## Advanced Features

- **Unlimited Rules**: You can create as many rules as needed
- **Multiple SNI Matching**: Each rule can match multiple SNI values
- **Random Selection**: IP and SNI rewrite operations randomly select from provided arrays
- **Header Support**: Full compatibility with v2raytun subscription headers

## Requirements

- Python 3.x
- FastAPI
- Uvicorn
- Requests

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.