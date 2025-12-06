from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import urllib.parse
import requests
import uvicorn
import base64
import json
import sys
import re

# Variables

app = FastAPI()

# READ CONFIG FILE

with open("config.json", "r", encoding="utf-8") as f:
    init_file = json.load(f)
_type = init_file.get("type")
sources = init_file.get("sources")
profile_title = init_file.get("profile-title") or "SUB SYSTEM"
announce = init_file.get("announce") or "SUB SYSTEM ANNOUNCE"
v2raytun_announce = init_file.get("v2raytun-announce") or announce
subscription_userinfo_ord = init_file.get("subscription-userinfo-ord") or 0
replace_ip = init_file.get("replace-ip") or None
profile_update_interval = init_file.get("profile-update-interval") or 1
announce_url = init_file.get("announce-url") or None
support_url = init_file.get("support-url") or None
server_settings = init_file.get("server-settings", {})
bind = server_settings.get("bind") or "127.0.0.1"
port = server_settings.get("port") or 8080
accept_prefix = server_settings.get("accept-prefix") or "/sub"

# CONFIG CHECK

if _type is None:
    sys.exit("The type is not found in config.json. Exit...")

if _type not in ("mixer", "onesource"):
    sys.exit("The type is not contains mixer or onesource. Exit...")

if not sources:
    sys.exit("The sources is not found. Exit...")

pr_profile_title = profile_title
pr_profile_title = base64.b64encode(profile_title.encode("utf-8")).decode("utf-8")
pr_profile_title = "base64:" + pr_profile_title

#Primary code

def def_replace_ip(text, new_ip):
    print(f"Changing {text} to {new_ip}")
    return re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', new_ip, text)
def request_sub(url):
    response = requests.get(url=url)
    if response.status_code != 200:
        return False
    else:
        return True
def sub_info(url):
    response = requests.get(url=url)
    return response.headers["subscription-userinfo"]
def req_subs(url):
    response = requests.get(url=url)
    return response
def decode_vless_lines(b64_text: str) -> list:
    try:
        decoded = base64.b64decode(b64_text).decode("utf-8")
    except Exception as e:
        print(f"Error while decoding b64: {e}")
        return []

    lines = [line.strip() for line in decoded.strip().splitlines() if line.strip()]

    return lines
def deprecated_decode_vless_lines(b64_text: str) -> list:
    print(b64_text)
    try:
        b64_text += "=" * (-len(b64_text) % 4)
        decoded = base64.b64decode(b64_text).decode("utf-8")
    except Exception as e:
        print(f"Error while decoding b64: {e}")
        return []

    lines = [line.strip() for line in decoded.strip().splitlines() if line.strip()]

    return lines
def find_ip_by_sni(sni_value: str, replace_ip_rules: dict) -> str | None:
    for rule in replace_ip_rules.values():
        for sni in rule["sni"]:
            if sni in sni_value:
                return rule["ip"]
    return None

@app.get(f"{accept_prefix}/{{sub_id}}")
async def subsys(sub_id: str, request: Request, response: Response):
    ss_rs_dri = ""

    if not sources or len(sources) == 0:
        raise HTTPException(status_code=500, detail="No sources configured")

    print(f"[INFO] LIST {sources[0] + sub_id}")

    # Проверяем доступность первого источника
    if not request_sub(sources[0] + sub_id):
        raise HTTPException(status_code=404, detail="Subscription not found")

    ss_def_subinfo = sub_info(sources[subscription_userinfo_ord] + sub_id)

    if "v2raytun" in request.headers.get("user-agent", "").lower():
        ss_announce = v2raytun_announce
    else:
        ss_announce = announce

    for source in sources:
        raw_text = req_subs(source + sub_id).text
        urls_list = decode_vless_lines(raw_text)

        for url in urls_list:
            query = url.split("?", 1)[1] if "?" in url else ""
            params = urllib.parse.parse_qs(query)
            sni_value = params.get("sni", [""])[0]

            new_ip = find_ip_by_sni(sni_value, replace_ip)
            if new_ip:
                url = def_replace_ip(url, new_ip)

            ss_rs_dri += url + "\n"

    ss_url = base64.b64encode(ss_rs_dri.encode("utf-8")).decode("utf-8")

    ss_announce = ss_announce
    ss_announce = base64.b64encode(ss_announce.encode("utf-8")).decode("utf-8")
    ss_announce = "base64:" + ss_announce
    headers = {
        "profile-title": pr_profile_title,
        "profile-update-interval": str(profile_update_interval),
        "announce": ss_announce,
        "subscription-userinfo": str(ss_def_subinfo),
        "announce-url": announce_url,
        "support-url": support_url
    }

    return Response(content=ss_url, media_type="text/plain; charset=utf-8", headers=headers)


if __name__ == "__main__": 
    uvicorn.run("main:app", host=bind, port=port, reload=True)