from fastapi import FastAPI, Request, HTTPException, Response
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, ParseResult
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import requests
import uvicorn
import random
import urllib
import base64
import json
import time
import sys
import os
import re

# Checks

def check_none(value, name):
    if value is None:
        print(f"[INIT] {name} is None")
        sys.exit()
    return value
def check(value, name, ntr=None):
    if value is None:
        print(f"[INIT] {name} is None")
        return ntr
    return value

# READ CONFIG FILE

if not os.path.exists("config.json"):
    print("[INIT] config.json not found")
    sys.exit()

with open("config.json", "r", encoding="utf-8") as f:
    init_file = json.load(f)
    print("[INIT] Started")

_type = check_none(init_file.get("type"), "type")
sources = check_none(init_file.get("sources"), "sources")
profile_title = check_none(init_file.get("profile-title"), "profile-title")
announce = check_none(init_file.get("announce"), "announce")
v2raytun_announce = check_none(init_file.get("v2raytun-announce"), "v2raytun-announce")
subscription_userinfo = check_none(init_file.get("subscription-userinfo"), "subscription-userinfo")
expire_source = check_none(subscription_userinfo.get("expire-source"), "subscription-userinfo.expire-source")
replace_ip = check(init_file.get("replace-ip"), "replace-ip")
rules = check(init_file.get("rules"), "rules")
profile_update_interval = check_none(init_file.get("profile-update-interval"), "profile-update-interval")
announce_url = check_none(init_file.get("announce-url"), "announce-url")
support_url = check_none(init_file.get("support-url"), "support-url")
server_settings = check_none(init_file.get("server-settings"), "server-settings")
bind = check_none(server_settings.get("bind"), "server-settings.bind")
port = check_none(server_settings.get("port"), "server-settings.port")
accept_prefix = check_none(server_settings.get("accept-prefix"), "server-settings.accept-prefix")
advanced_print = check(server_settings.get("advanced-print"), "server-settings.advanced-print", False)

# Debug

def event_register(event):
    if advanced_print is True:
        print(event)
    return None

# Variables

app = FastAPI()

# READ CONFIG FILE

if not os.path.exists("config.json"):
    print("[INIT] config.json not found")
    sys.exit()

with open("config.json", "r", encoding="utf-8") as f:
    init_file = json.load(f)
    event_register("[INIT] Started")

_type = check_none(init_file.get("type"), "type")
sources = check_none(init_file.get("sources"), "sources")
profile_title = check_none(init_file.get("profile-title"), "profile-title")
announce = check_none(init_file.get("announce"), "announce")
v2raytun_announce = check_none(init_file.get("v2raytun-announce"), "v2raytun-announce")
subscription_userinfo = check_none(init_file.get("subscription-userinfo"), "subscription-userinfo-ord")
replace_ip = check(init_file.get("replace-ip"), "replace-ip")
rules = check(init_file.get("rules"), "rules")
profile_update_interval = check_none(init_file.get("profile-update-interval"), "profile-update-interval")
announce_url = check_none(init_file.get("announce-url"), "announce-url")
support_url = check_none(init_file.get("support-url"), "support-url")
server_settings = check_none(init_file.get("server-settings"), "server-settings")
bind = check_none(server_settings.get("bind"), "server-settings.bind")
port = check_none(server_settings.get("port"), "server-settings.port")
accept_prefix = check_none(server_settings.get("accept-prefix"), "server-settings.accept-prefix")
advanced_print = check(server_settings.get("advanced-print"), "server-settings.advanced-print", False)

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

def request_sub(url): # USED
    response = requests.get(url=url)
    event_register("[func:request_sub] requested")
    if response.status_code != 200:
        event_register("[func:request_sub] False 200")
        return False
    else:
        event_register("[func:request_sub] True 200")
        return True
def sub_info(url):    # USED
    response = requests.get(url=url)
    event_register("[func:sub_info] requested")
    if response.status_code != 200:
        return None
    return response.headers["subscription-userinfo"]
def req_subs(url):    # USED
    response = requests.get(url=url)
    event_register("[func:req_subs] requested")
    return response
def decode_vless_lines(b64_text: str) -> list: # USED
    try:
        event_register("[func:decode_vless_lines] trying to decode")
        decoded = base64.b64decode(b64_text).decode("utf-8")
    except Exception as e:
        print(f"Error while decoding b64: {e}")
        return []
    lines = [line.strip() for line in decoded.strip().splitlines() if line.strip()]
    event_register("[func:decode_vless_lines] decoded")
    return lines
def base_finder(sni_value: str, rules: list):
    ip_list = None
    new_port = None
    rew_sni = None

    for rule in rules:
        for sni in rule.get("sni", []):
            if sni_value.strip().lower() != sni.strip().lower():
                continue
            for base in rule.get("base", []):
                btype = base.get("type")
                if btype == "rewriteip":
                    ip_list = base.get("ips") or None

                elif btype == "rewriteport":
                    new_port = base.get("port")

                elif btype == "rewritesni":
                    rew_sni = base.get("sni") or None
            if ip_list or new_port or rew_sni:
                result = {
                    "ip": random.choice(ip_list) if ip_list else None,
                    "port": new_port,
                    "sni": random.choice(rew_sni) if rew_sni else None
                }
                event_register(f"[func:base_finder] FIN Return: {result}")
                return result
    event_register("[func:base_finder] None returned")
    return None
def comment_finder(sni_value: str, rules: list): # USED
    for rule in rules:
        if any(sni in sni_value for sni in rule.get("sni", [])):
            event_register("[func:comment_finder] SNI matched")
            return rule.get("comment", [])
    event_register("[func:comment_finder] Return: None")
    return None
def comment_handler(remark_first, comments):  # USED
    event_register(f"[func:comment_handler] Gotted remark: {remark_first}")
    if not comments:
        event_register("[func:comment_handler] no comments provided")
        return remark_first

    event_register("[func:comment_handler] start processing comments")

    text = urllib.parse.unquote(remark_first)

    for comment in comments:
        ctype = comment.get("type", "")

        if ctype == "start-add":
            event_register("[func:comment_handler] type start-add matched")
            text = comment.get("text", "") + text

        elif ctype == "end-add":
            event_register("[func:comment_handler] type end-add matched")
            text = text + comment.get("text", "")

        elif ctype == "start-exactly-add":
            event_register("[func:comment_handler] type start-exactly-add matched")
            pos = comment.get("count", 0)
            text = text[:pos] + comment.get("text", "") + text[pos:]

        elif ctype == "end-exactly-add":
            event_register("[func:comment_handler] type end-exactly-add matched")
            count = comment.get("count", 0)
            pos = len(text) - count
            text = text[:pos] + comment.get("text", "") + text[pos:]

        elif ctype == "add-after":
            event_register("[func:comment_handler] type add-after matched")
            after = comment.get("after", "")
            idx = text.find(after)
            if idx != -1:
                text = (
                    text[:idx + len(after)]
                    + comment.get("text", "")
                    + text[idx + len(after):]
                )

        elif ctype == "add-before":
            event_register("[func:comment_handler] type add-before matched")
            before = comment.get("before", "")
            idx = text.find(before)
            if idx != -1:
                text = text[:idx] + comment.get("text", "") + text[idx:]

        elif ctype == "delete-all-after":
            event_register("[func:comment_handler] type delete-all-after matched")
            after = comment.get("after", "")
            idx = text.find(after)
            if idx != -1:
                text = text[:idx]

        elif ctype == "delete-all-before":
            event_register("[func:comment_handler] type delete-all-before matched")
            before = comment.get("before", "")
            idx = text.find(before)
            if idx != -1:
                text = text[idx + len(before):]

        elif ctype == "start-delete":
            event_register("[func:comment_handler] type start-delete matched")
            count = comment.get("count", 0)
            text = text[count:]
            event_register(f"[func:comment_handler] start-delete FIN: {text}")
        elif ctype == "end-delete":
            event_register("[func:comment_handler] type end-delete matched")
            count = comment.get("count", 0)
            text = text[:-count] if count <= len(text) else ""

        else:
            event_register(f"[func:comment_handler] unknown type '{ctype}' skipped")

    event_register(f"[func:comment_handler] finished, result='{text}'")
    return text
def replace_vless_params(vless_url: str,new_ip: str | None = None,new_port: int | None = None,new_sni: str | None = None) -> str: # USED
    parsed = urlparse(vless_url.replace("vless://", "http://"))
    event_register("[func:replace_vless_params] Start")
    userinfo, hostinfo = parsed.netloc.split("@")
    current_ip, current_port = hostinfo.split(":")

    ip = new_ip if new_ip is not None else current_ip
    port = new_port if new_port is not None else current_port
    event_register("[func:replace_vless_params] new_netloc created")
    new_netloc = f"{userinfo}@{ip}:{port}"
    event_register(f"[func:replace_vless_params] new_netloc: {new_netloc}")
    query_params = parse_qs(parsed.query)

    if new_sni is not None:
        event_register("[func:replace_vless_params] SNI is not None")
        query_params["sni"] = [new_sni]

    new_query = urlencode(query_params, doseq=True)

    new_parsed = parsed._replace(netloc=new_netloc,query=new_query)
    event_register("[func:replace_vless_params] returned")
    return urlunparse(new_parsed).replace("http://", "vless://")
def vlesses_creator(urls_list):
    ss_rs_dri = ""

    for url in urls_list:
        event_register(f"[func:vlesses_creator] Currently working on url: {url}")

        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        sni_value = params.get("sni", [""])[0]
        fragment_value = parsed.fragment

        base_rule = base_finder(sni_value, rules=rules)
        com_rules = comment_finder(sni_value=sni_value, rules=rules)

        formated_text = None

        # 1. comments
        if com_rules:
            event_register("[func:vlesses_creator] com_rules not None")
            formated_text = comment_handler(
                remark_first=fragment_value,
                comments=com_rules
            )

        # 2. base rule
        if base_rule:
            event_register("[func:vlesses_creator] base_rule not None")
            url = replace_vless_params(
                vless_url=url,
                new_ip=base_rule.get("ip", ""),
                new_port=base_rule.get("port"),
                new_sni=base_rule.get("sni", "")
            )

        # 3. fragment
        hash_index = url.rfind("#")
        if hash_index != -1:
            url_part = url[:hash_index]
            name_part = url[hash_index + 1:]

            if formated_text is not None:
                url = f"{url_part}#{formated_text}"
            else:
                url = f"{url_part}#{name_part}"

        event_register(f"[func:vlesses_creator] finally url: {url}")

        # 4. ALWAYS append
        ss_rs_dri += url + "\n"

    event_register(f"[func:vlesses_creator] ss_rs_dri returned: {ss_rs_dri}")
    return ss_rs_dri
def subscription_userinfo_simple(header_value: str):
    for item in header_value.split(";"):
        key, value = item.strip().split("=")
        event_register(f"[func:subscription_userinfo_simple] Subscription-userinfo key: {key} value: {value}")
        if key == "upload":
            fin_u = value
        elif key == "download":
            fin_d = value
        elif key == "total":
            fin_t = value
        elif key == "expire":
            fin_e = value
        else:
            event_register(f"[func:subscription_userinfo_simple] {key} not matched")
    return fin_u, fin_d, fin_t, fin_e
def combine_stats(**kwargs):
    return '; '.join(f"{key}={value}" for key, value in kwargs.items()) + ';'

@app.get(f"{accept_prefix}/{{sub_id}}")
async def subsys(sub_id: str, request: Request, response: Response):
    responses = {}
    start = time.time()
    fin_upload = 0
    fin_download = 0
    fin_total = 0
    fin_expire = 0
    urls_list = []

    if not sources:
        end = time.time()
        event_register(f"[func:subsys] Elapsed time {end - start}")
        raise HTTPException(status_code=500, detail="No sources configured")

    print(f"[INFO] LIST {sub_id}")

    for src in sources:
        event_register(f"[func:subsys] Currently requesting: {src['source']}")
        rurl = src["source"] + sub_id
        resp = requests.get(rurl)
        if src.get("exists-check") is True and resp.status_code != 200:
            end = time.time()
            event_register(f"[func:subsys] Elapsed time {end - start}")
            raise HTTPException(status_code=404, detail="Subscription not found")
        responses[rurl] = resp

    for index, src in enumerate(sources):
        rurl = src["source"] + sub_id
        resp = responses[rurl]
        if resp.status_code != 200:
            continue

        userinfo = resp.headers.get("subscription-userinfo")
        if not userinfo:
            continue

        upload_key, download_key, total_key, expire_key = subscription_userinfo_simple(userinfo)

        fin_upload += int(upload_key)
        fin_download += int(download_key)
        fin_total += int(total_key)

        if index == expire_source:
            fin_expire = expire_key

    fin_subscription_userinfo = combine_stats(
        upload=fin_upload,
        download=fin_download,
        total=fin_total,
        expire=fin_expire
    )

    if "v2raytun" in request.headers.get("user-agent", "").lower():
        event_register("[func:subsys] v2raytun matched")
        fin_announce = v2raytun_announce
    else:
        fin_announce = announce

    for src in sources:
        rurl = src["source"] + sub_id
        raw_text = responses[rurl].text
        urls_list.extend(decode_vless_lines(raw_text))

    event_register(f"[func:subsys] Finnaly urls_list: {urls_list}")

    fin_url = vlesses_creator(urls_list)
    fin_url = base64.b64encode(fin_url.encode("utf-8")).decode("utf-8")

    fin_announce = "base64:" + base64.b64encode(
        fin_announce.encode("utf-8")
    ).decode("utf-8")

    headers = {
        "profile-title": str(pr_profile_title),
        "profile-update-interval": str(profile_update_interval),
        "announce": str(fin_announce),
        "subscription-userinfo": str(fin_subscription_userinfo),
        "announce-url": str(announce_url),
        "support-url": str(support_url)
    }

    event_register(f"[func:subsys] Finally headers: {headers}")
    end = time.time()
    event_register(f"[func:subsys] Elapsed time {end - start}")
    event_register(f"[func:subsys] Url Config {fin_url}")

    return Response(
        content=fin_url,
        media_type="text/plain; charset=utf-8",
        headers=headers
    )

if __name__ == "__main__": 
    uvicorn.run("main:app", host=bind, port=port, reload=True)
