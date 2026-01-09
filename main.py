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

# Debug
def event_register(event):
    if advanced_print is True:
        print(event)
    return None
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
subscription_userinfo_ord = check_none(init_file.get("subscription-userinfo-ord"), "subscription-userinfo-ord")
replace_ip = check_none(init_file.get("replace-ip"), "replace-ip")
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
    event_register(f"[func:sub_info] HEAD {response.headers}")
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
def base_finder(sni_value: str, rules: list): # USED
    rew_sni = None
    new_port = None
    ip_list = None
    for rule in rules:
        for sni in rule.get("sni", []):
            if sni_value.strip().lower() == sni.strip().lower():
                for base in rule.get("base", []):
                    if base.get("type", "") == "rewriteip":
                        event_register("[func:base_finder] finded type rewriteip")
                        ip_list = base.get("ips", [])
                        if not ip_list:
                            ip_list = []
                        event_register(f"[func:base_finder] ips: {ip_list}")
                    elif base.get("type", "") == "rewriteport":
                        event_register("[func:base_finder] finded type rewriteport")
                        new_port = base.get("port")
                        event_register("[func:base_finder] New port: {new_port}")
                        if not new_port:
                            new_port = None
                        event_register(f"[func:base_finder] port: {new_port}")
                    elif base.get("type", "") == "rewritesni":
                        event_register("[func:base_finder] finded type rewritesni")
                        rew_sni = base.get("sni", [])
                        if not rew_sni:
                            rew_sni = []
                        event_register(f"[func:base_finder] sni's: {rew_sni}")
                        need_to_return = {
                            "ip": random.choice(ip_list), 
                            "port": new_port,
                            "sni": random.choice(rew_sni)
                        }
                        event_register(f"[func:base_finder] FIN Return: {need_to_return}")
                        return need_to_return
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
    if not comments:
        event_register("[func:comment_handler] no comments provided")
        return remark_first

    event_register("[func:comment_handler] start processing comments")

    text = remark_first

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
            text = text[:count]

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
def vlesses_creator(urls_list): # USED
    ss_rs_dri = ""
    formated_text = None
    for url in urls_list:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        sni_value = params.get("sni", [""])[0]
        fragment_value = parsed.fragment
        base_rule = base_finder(sni_value, rules=rules)
        com_rules = comment_finder(sni_value=sni_value, rules=rules)
        if com_rules:
            event_register("[func:vlesses_creator] com_rules not None")
            formated_text = comment_handler(remark_first=fragment_value, comments=com_rules)
        if base_rule:
            event_register("[func:vlesses_creator] base_rule not None")
            new_ip = base_rule.get("ip", "")
            new_port = base_rule.get("port")
            new_sni = base_rule.get("sni", "")
            url = replace_vless_params(vless_url=url, new_ip=new_ip, new_port=new_port, new_sni=new_sni)
            hash_index = url.rfind("#")
            if hash_index != -1:
                url_part = url[:hash_index]
                name_part = url[hash_index+1:]
                if formated_text is not None:
                    event_register("[func:vlesses_creator] formated_text not None")
                    url = f"{url_part}#{formated_text}"
                else:
                    url = f"{url_part}#{name_part}"
            event_register(f"[func:vlesses_creator] finally url: {url}")
            ss_rs_dri += url + "\n"
    return ss_rs_dri
@app.get(f"{accept_prefix}/{{sub_id}}")
async def subsys(sub_id: str, request: Request, response: Response):
    start = time.time()
    if not sources or len(sources) == 0:
        end = time.time()
        event_register(f"[func:subsys] Elapsed time {end - start}")
        raise HTTPException(status_code=500, detail="No sources configured")
    print(f"[INFO] LIST {sources[0] + sub_id}")
    if not request_sub(sources[0] + sub_id):
        end = time.time()
        event_register(f"[func:subsys] Elapsed time {end - start}")
        raise HTTPException(status_code=404, detail="Subscription not found")
    ss_def_subinfo = sub_info(sources[subscription_userinfo_ord] + sub_id)
    if "v2raytun" in request.headers.get("user-agent", "").lower():
        event_register("[func:subsys] v2raytun matched")
        ss_announce = v2raytun_announce
    else:
        ss_announce = announce
    for source in sources:
        raw_text = req_subs(source + sub_id).text
        urls_list = decode_vless_lines(raw_text)
    ss_rs_dri = vlesses_creator(urls_list)
    ss_url = base64.b64encode(
        ss_rs_dri.encode("utf-8")
    ).decode("utf-8")
    ss_announce = base64.b64encode(
        ss_announce.encode("utf-8")
    ).decode("utf-8")
    ss_announce = "base64:" + ss_announce
    headers = {
        "profile-title": pr_profile_title,
        "profile-update-interval": str(profile_update_interval),
        "announce": ss_announce,
        "subscription-userinfo": str(ss_def_subinfo),
        "announce-url": announce_url,
        "support-url": support_url
    }
    event_register(f"[func:subsys] Finally headers: {headers}")
    end = time.time()
    event_register(f"[func:subsys] Elapsed time {end - start}")
    return Response(
        content=ss_url,
        media_type="text/plain; charset=utf-8",
        headers=headers
    )

if __name__ == "__main__": 
    uvicorn.run("main:app", host=bind, port=port, reload=True)