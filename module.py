from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import base64

def extract_from_vurl(vless_url):
    parsed = urlparse(vless_url)
    if '@' not in parsed.netloc:
        raise ValueError("Invalid VLESS URL: non '@'")
    uuid, host_port = parsed.netloc.split('@', 1)
    if ':' not in host_port:
        raise ValueError("Invalid VLESS URL: non ':' for port")
    ip, port_str = host_port.split(':', 1)
    port = int(port_str)
    raw_query = parse_qs(parsed.query)
    query = {k: v[0] for k, v in raw_query.items()}
    return uuid, ip, port, query

def add_to_vurl(vless_url, new_query: dict):
    uuid, ip, port, query = extract_from_vurl(vless_url)
    for k, v in new_query.items():
        if k not in query:
            query[k] = v
    query_str = urlencode(query)
    new_url = f"vless://{uuid}@{ip}:{port}?{query_str}"
    return new_url

def modify_vurl(vless_url, uuid=None, ip=None, port=None, query=None):
    old_uuid, old_ip, old_port, old_query = extract_from_vurl(vless_url)
    
    new_uuid = uuid or old_uuid
    new_ip = ip or old_ip
    new_port = port or old_port
    new_query = query if query is not None else old_query
    
    query_str = urlencode(new_query)
    new_url = f"vless://{new_uuid}@{new_ip}:{new_port}?{query_str}"
    return new_url

def to_base64(text):
    b64 = base64.b64encode(text.encode()).decode()
    return b64

def from_base64(b64):
    text = base64.b64decode(b64.encode()).decode()
    return text

def main(response_list, headers, sub_id, module_config):
    vless_list = []
    for vurl in response_list:
        vless_list.extend(vurl.get("vless-url"))
        
    if headers.get("user-agent") in "v2raytun":
        announce = "base64:" + to_base64(module_config.get("v2raytun-announce"))
    else:
        announce = "base64:" + to_base64(module_config.get("announce"))
    header = {
        "profile-title": "base64:" + to_base64(module_config.get("profile-title")),
        "subscription-userinfo":module_config.get("subscription-userinfo"),
        "profile-update-interval":module_config.get("profile-update-interval"),
        "announce": announce,
        "announce-url":module_config.get("announce-url")
    }
        
    return 200, vless_list, header, True