import sys
try:
    from aiohttp import web
    import json
    import yaml
except ImportError as e:
    print(f"Failed import json or aiohttp or pyyaml: {type(e).__name__} -> {e}")
    input()
    sys.exit(1)

"""
Поднимает http сервер на указаном в конфиге host:port
Отвечает на любой get и post запрос JSON из указанного в конфиге файла
"""

ANSWER_JSON, HOST, PORT = "", "", 0


def read_config():
    global ANSWER_JSON, HOST, PORT
    try:
        with open("config.yml", "r") as f:
            config = yaml.load(f, yaml.Loader)
            ANSWER_JSON = config["from_json_file"]
            HOST = config["host"]
            PORT = config["port"]
    except Exception as err:
        print(f"Can't read config: {type(err).__name__} -> {err}")
        input()
        sys.exit(1)
    finally:
        f.close()


def read_json() -> dict:
    with open(ANSWER_JSON, "r") as f:
        js = f.read()

    try:
        answ = json.loads(js)
    except Exception as er:
        print(f"Can't parse json file: {type(er).__name__} -> {er}")
        input()
        sys.exit(1)

    return answ


async def http_response(request):
    return web.json_response(read_json())

read_config()
app = web.Application()
app.router.add_route("GET", "/{tail:.*}", http_response)
app.router.add_route("POST", "/{tail:.*}", http_response)
web.run_app(app, host=HOST, port=PORT)
