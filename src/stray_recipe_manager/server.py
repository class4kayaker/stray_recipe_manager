import logging
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from stray_recipe_manager.storage import get_storage
from stray_recipe_manager.units import UnitPreferences
from stray_recipe_manager.recipe import present_recipe
from jinja2 import BaseLoader, FileSystemLoader, PackageLoader, Environment


logger = logging.getLogger(__name__)


class RecipeViewer:
    def __init__(self, config):
        self.storage = get_storage(config["storage_path"])
        self.unit_handler = self.storage.get_unit_handler()
        self.host_base = config["host_base"]
        if config["template_dir"] is None:
            loader = PackageLoader(
                "stray_recipe_manager", "templates"
            )  # type: BaseLoader
        else:
            loader = FileSystemLoader(config["template_dir"])
        self.jinja_env = Environment(loader=loader, autoescape=True)
        self.url_map = Map(
            [
                Rule("/", endpoint="view_index"),
                Rule("/recipe/<recipe_name>.html", endpoint="view_recipe"),
            ]
        )

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, "on_" + endpoint)(request, **values)
        except HTTPException as e:
            return e

    def on_view_index(self, request):
        return self.render_template(
            "recipe_index.html", recipes=self.storage.recipe_keys()
        )

    def on_view_recipe(self, request, recipe_name):
        try:
            prefs = UnitPreferences(self.unit_handler)
        except KeyError as e:

            raise NotFound(str(e))
        recipe = self.storage.get_recipe(recipe_name)
        p_recipe = present_recipe(recipe, prefs, 1.0)
        return self.render_template("recipe.html", recipe=p_recipe)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(storage_path, host_base, template_dir=None, static_dir=None):
    app = RecipeViewer(
        {
            "storage_path": storage_path,
            "host_base": host_base,
            "template_dir": template_dir,
        }
    )
    if static_dir is None:
        static_dir = ("stray_recipe_manager", "static")
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {"/static": static_dir})
    return app
