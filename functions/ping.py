from firebase_functions import https_fn
from firebase_functions import https_fn
from firebase_admin import initialize_app

@https_fn.on_request()
def ping(req: https_fn.Request) -> https_fn.Response:
    if req.method != "GET":
        return https_fn.Response("Method not allowed", status=405)
    return https_fn.Response("Hello world!")
