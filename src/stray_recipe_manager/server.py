import io
import logging
import qrcode
from qrcode.image.svg import SvgPathImage
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from stray_recipe_manager.storage import get_storage
from stray_recipe_manager.formatter import UnitPreferences, HTMLWriter
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
                Rule("/qr_recipe/<recipe_name>.svg", endpoint="recipe_qr"),
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

    def on_recipe_qr(self, request, recipe_name):
        img = qrcode.make(
            f"http://{self.host_base}/recipe/{recipe_name}.html",
            image_factory=SvgPathImage,
        )
        img_data = io.BytesIO()
        img.save(img_data)
        return Response(img_data.getvalue(), mimetype="image/svg+xml",)

    def on_view_index(self, request):
        return self.render_template(
            "recipe_index.html", recipes=self.storage.recipe_keys()
        )

    def on_view_recipe(self, request, recipe_name):
        try:
            prefs = UnitPreferences(self.unit_handler)
            formatter = HTMLWriter(prefs)
            recipe = self.storage.get_recipe(recipe_name)
            recipe_text = io.StringIO()
            formatter.write_recipe(recipe_text, recipe)
            return self.render_template(
                "recipe.html",
                recipe_qr=f"/qr_recipe/{recipe_name}.svg",
                recipe_name=recipe.name,
                recipe_text=recipe_text.getvalue(),
            )
        except KeyError as e:

            raise NotFound(str(e))

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
