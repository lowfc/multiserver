import sys
import os
try:
    from aiohttp import web
    import json
    import yaml
    import logging
except ImportError as e:
    print(f"Failed import json or aiohttp or pyyaml or logging: {type(e).__name__} -> {e}")
    input()
    sys.exit(1)


"""
Поднимает http сервер на указаном в конфиге host:port
Отвечает на любой get и post запрос JSON из указанного в конфиге файла
"""


try:
    with open("config.yml", "r") as f:
        config = yaml.load(f, yaml.Loader)
        ANSWER_JSON = config["from_json_file"]
        HOST = config["host"]
        PORT = config["port"]
        LOG_PATH = config["log_full_path"]
except Exception as err:
    print(f"Can't read config: {type(err).__name__} -> {err}")
    input()
    sys.exit(1)
finally:
    f.close()

LOGGER = logging.getLogger("multiserver")
LOGGER.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(LOG_PATH)
uni_formatter = logging.Formatter(f"%(asctime)s [%(levelname)s] in %(processName)s thread"
                                  "-> %(funcName)s(): %(message)s")
console_handler.setFormatter(uni_formatter)
file_handler.setFormatter(uni_formatter)
LOGGER.addHandler(console_handler)
LOGGER.addHandler(file_handler)

REQUESTS = 0


def read_json() -> dict:
    try:
        with open(ANSWER_JSON, "r") as f:
            js = f.read()
        answ = json.loads(js)
    except Exception as er:
        LOGGER.critical(f"Can't parse json file: {type(er).__name__} -> {er}")
        sys.exit(1)

    return answ


def get_formatted_parameters(params: dict):
    _formatted = ''
    for par in params:
        _formatted += par + "=" + params[par] + ", "
    return _formatted[:-2]


async def http_response(request):
    global REQUESTS
    REQUESTS += 1
    LOGGER.info(f"Receive {request.scheme}{request.version.major}.{request.version.minor} Request#{REQUESTS}")
    LOGGER.info(f"Request#{REQUESTS} method: {request.method}, url: {request.url}, original client ip {request.remote}")
    LOGGER.info(f"Request#{REQUESTS} query parameters: {get_formatted_parameters(request.query)}")
    LOGGER.info(f"Request#{REQUESTS} headers: {get_formatted_parameters(request.headers)}")
    if request.body_exists and request.can_read_body:
        body = await request.content.read()
        if request.content_type == "application/json":
            body = json.loads(body)
        LOGGER.info(f"Request#{REQUESTS} have body: {body}")
    return web.json_response(read_json())


LOGGER.info(f"{'-'*5} App started {'-'*5}")
app = web.Application()
app.router.add_route("GET", "/{tail:.*}", http_response)
app.router.add_route("POST", "/{tail:.*}", http_response)
web.run_app(app, host=HOST, port=PORT)
