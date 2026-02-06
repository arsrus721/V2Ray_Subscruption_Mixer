import os
import json
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import sys
import base64
import logging
import requests
import importlib

def config_init():
    if not os.path.exists("config.json"):
        logging.critical("File config.json not found")
        return None
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)

def module_config_init(config):
    config = config.get("module").get("config_file")
    if not os.path.exists(config):
        logging.critical(f"File {config} not found")
        return None
    with open(config, "r", encoding="utf-8") as file:
        return json.load(file)

def config_logging(log_level, log_file):
    if log_level == "DEBUG":
        log_level = logging.DEBUG
    elif log_level == "INFO":
        log_level = logging.INFO
    elif log_level == "WARNING":
        log_level = logging.WARNING
    elif log_level == "ERROR":
        log_level = logging.ERROR
    elif log_level == "CRITICAL":
        log_level = logging.CRITICAL
    else:
        log_level = logging.INFO
    if not log_file:
        log_file = "sub.log"

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(funcName)s- %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def to_base64(text):
    b64 = base64.b64encode(text.encode()).decode()
    logging.debug(f"From text to b64: {b64}")
    return b64

def from_base64(b64):
    text = base64.b64decode(b64.encode()).decode()
    logging.debug(f"From b64 to text: {text}")
    return text

def main(config, module_config):
    app = FastAPI()
    @app.get(f"{config.get('server').get('prefix')}/{{sub_id}}")
    def subsys3(sub_id: str, request: Request):
        response_list = []
        for source in config.get("sources"):
            url = source.get("source") + sub_id
            logging.debug(f"Done url: {url}")
            response = requests.get(url)

            if response.status_code != 200 and source.get("exists-check") is True:
                logging.info("One of exists-check:true servers returned non-200")
                raise HTTPException(status_code=404, detail="Not found")
            
            response_decoded = from_base64(response.text)
            response_decoded = response_decoded.split("\n")
            response_list.append({"response": response, "vless-url": response_decoded, "url": url})

        logging.debug(f"Done for module: {response_list}")

        module = importlib.import_module(config.get("module").get("file"))
        func = getattr(module, config.get("module").get("func"))

        status_code, content, headers, b64encode = func(
            response_list,
            request.headers,
            sub_id,
            module_config
        )
        if b64encode is True:
            fin_text = ""
            for cont in content:
                fin_text += cont + "\n"
            fin_content = to_base64(fin_text)
        else:
            fin_content = content
            

        logging.debug(f"Module returned: status_code: {status_code}, content: {content}, headers: {headers}")
        return Response(status_code=status_code, content=fin_content, headers=headers)
    return app

def run_server(config, module_config):
    app = main(config, module_config)
    uvicorn.run(app, host=config.get("server").get("host"), port=config.get("server").get("port"))

if __name__ == "__main__":
    config = config_init()
    if not config:
        sys.exit()

    config_logging(config.get("logging").get("log_level"), config.get("logging").get("log_file"))
    module_config = module_config_init(config)
    logging.info("Start")

    try:
        run_server(config, module_config)
    except KeyboardInterrupt:
        logging.info("Goodbye!")