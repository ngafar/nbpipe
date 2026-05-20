def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": "nbpipe"}]


def _jupyter_server_extension_points():
    return [{"module": "nbpipe"}]


def _link_jupyter_server_extension(server_app):
    """Enable reading .nbpipe/ before the contents manager is created.

    jupyter_server_config.d/*.json only applies ServerApp.jpserver_extensions;
    other keys (e.g. ContentsManager) are ignored.
    """
    from traitlets.config import Config

    cfg = Config()
    cfg.ContentsManager = Config(allow_hidden=True)
    cfg.FileContentsManager = Config(allow_hidden=True)
    cfg.AsyncLargeFileManager = Config(allow_hidden=True)
    server_app.update_config(cfg)


def _load_jupyter_server_extension(server_app):
    from .handlers import setup_handlers

    # Belt-and-suspenders: link runs before init_configurables, but set again
    # in case another extension or config overrides the trait later.
    server_app.contents_manager.allow_hidden = True
    setup_handlers(server_app.web_app)
