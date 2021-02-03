from os.path import dirname, join, realpath

import jinja2
from starlette import templating

from app.utils.templating import Jinja2Templates

templates_directory = join(dirname(dirname(dirname(realpath(__file__)))), "templates")
templates = Jinja2Templates(loader=jinja2.FileSystemLoader(templates_directory))


def test_inheritance():
    assert issubclass(Jinja2Templates, templating.Jinja2Templates)


def test_templates_loaded():
    assert "home.html" in templates.env.list_templates()
    assert "base.html" in templates.env.list_templates()


def test_env():
    assert isinstance(templates.env, jinja2.Environment)
    assert "is_multipart" in templates.env.globals
    assert "url_params_update" in templates.env.globals
    assert "url_for" in templates.env.globals
