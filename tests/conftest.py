import pytest

pytest_plugins = ("jupyter_server.pytest_plugin",)


@pytest.fixture
def jp_server_config(jp_server_config):
    return {
        **jp_server_config,
        "ServerApp": {"jpserver_extensions": {"nbpipe": True}},
    }
