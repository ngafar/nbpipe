def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "nbpipe"}]


def _jupyter_server_extension_points():
    return [{"module": "nbpipe"}]


def _load_jupyter_server_extension(server_app):
    from .handlers import setup_handlers

    setup_handlers(server_app.web_app)
