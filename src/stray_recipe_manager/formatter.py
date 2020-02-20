import pint
import toml
import logging
import typing
from stray_recipe_manager.units import UnitHandler
from stray_recipe_manager.recipe import (
    Ingredient,
    RecipeStep,
    Recipe,
    CommentedRecipe,
)


logger = logging.getLogger(__name__)


class UnitPreferences:
    def __init__(self, unit_handler):
        # type: (UnitHandler) -> None
        self.unit_handler = unit_handler
        self.preferences = {}  # type: typing.Dict[str, pint.Unit]

    def set_unit_preference(self, category, unit):
        # type: (str, typing.Optional[pint.Unit]) -> None
        if unit is not None:
            self.preferences[category] = unit
        else:
            if category in self.preferences:
                del self.preferences[category]

    def get_unit_preference(self, category):
        # type: (str) -> typing.Optional[pint.Unit]
        return self.preferences.get(category, None)

    def clear_unit_preferences(self):
        # type: () -> None
        self.preferences = {}

    def load_from_toml_file(self, io):
        # type: (typing.TextIO) -> None
        data = toml.load(io)
        for k, v in data["units"].items():
            self.set_unit_preference(k, self.unit_handler.parse_unit(v))

    def handle_ingredient(self, ingredient):
        # type: (Ingredient) -> pint.Quantity
        if (
            ingredient.category is None
            or ingredient.category not in self.preferences
        ):
            return ingredient.quantity
        else:
            return self.unit_handler.do_conversion(
                ingredient.quantity,
                self.preferences[ingredient.category],
                ingredient.identifier,
            )


class BaseWriter:
    mimetype = None  # type: typing.Optional[str]

    def write_recipe(self, io, recipe, scale_factor):
        # type: (typing.TextIO, Recipe, float) -> None
        raise NotImplementedError()

    def write_standalone(self, io, recipe, scale_factor=1.0):
        # type: (typing.TextIO, Recipe, float) -> None
        self.write_recipe(io, recipe, scale_factor)


class MarkdownWriter(BaseWriter):
    mimetype = "text/markdown"

    def __init__(self, unit_preferences):
        # type: (UnitPreferences) -> None
        self.unit_preferences = unit_preferences
        self.scale_factor = 1.0

    def format_ingredient(self, ingredient, scale_factor=1.0):
        # type: (Ingredient, float) -> str
        converted_quantity = (
            scale_factor * self.unit_preferences.handle_ingredient(ingredient)
        )
        if ingredient.notes is None:
            return f"{converted_quantity!s} {ingredient.item}"
        else:
            return (
                f"{converted_quantity!s} {ingredient.item}, {ingredient.notes}"
            )

    def format_step(self, step):
        # type: (RecipeStep) -> str
        if step.time is None:
            return f"{step.description}"
        else:
            return f"{step.description} ({step.time!s})"

    def write_recipe(self, io, recipe, scale_factor=1.0):
        # type: (typing.TextIO, Recipe, float) -> None
        io.write(f"### {recipe.name}\n")
        if isinstance(recipe, CommentedRecipe):
            if recipe.comments is not None:
                io.write("\n#### Comments\n")
                io.write(f"\n{recipe.comments}\n")
        if len(recipe.tools) > 0:
            io.write("\n#### Tools\n\n")
            for tool in recipe.tools:
                io.write(f"-    {tool}\n")
        io.write("\n#### Ingredients\n\n")
        for ingredient in recipe.ingredients:
            io.write("-    {}\n".format(self.format_ingredient(ingredient)))
        io.write("\n#### Procedure\n\n")
        for i, step in enumerate(recipe.steps):
            io.write("{:d})   {}\n".format(i + 1, self.format_step(step)))
        if isinstance(recipe, CommentedRecipe):
            if len(recipe.references) > 0:
                io.write("\n#### References\n\n")
                for reference in recipe.references:
                    io.write(f"-    {reference}\n")


class HTMLWriter(BaseWriter):
    mimetype = "text/html"

    def __init__(self, unit_preferences):
        # type: (UnitPreferences) -> None
        self.unit_preferences = unit_preferences
        self.scale_factor = 1.0

    def format_ingredient(self, ingredient, scale_factor=1.0):
        # type: (Ingredient, float) -> str
        converted_quantity = (
            scale_factor * self.unit_preferences.handle_ingredient(ingredient)
        )
        if ingredient.notes is None:
            return f"{converted_quantity!s} {ingredient.item}"
        else:
            return (
                f"{converted_quantity!s} {ingredient.item}, {ingredient.notes}"
            )

    def format_step(self, step):
        # type: (RecipeStep) -> str
        if step.time is None:
            return f"{step.description}"
        else:
            return f"{step.description} ({step.time!s})"

    def write_recipe(self, io, recipe, scale_factor=1.0):
        # type: (typing.TextIO, Recipe, float) -> None
        io.write(f"<h3>{recipe.name}</h3>")
        if isinstance(recipe, CommentedRecipe):
            if recipe.comments is not None:
                io.write("<h4>Comments</h4>")
                io.write(f"<p>{recipe.comments}</p>")
        if len(recipe.tools) > 0:
            io.write("<h4>Tools</h4><ul>")
            for tool in recipe.tools:
                io.write(f"<li>{tool}</li>")
            io.write("</ul>")
        io.write("<h4>Ingredients</h4><ul>")
        for ingredient in recipe.ingredients:
            io.write("<li>{}</li>".format(self.format_ingredient(ingredient)))
        io.write("</ul>")
        io.write("<h4>Instructions</h4><ol>")
        for step in recipe.steps:
            io.write("<li>{}</li>".format(self.format_step(step)))
        io.write("</ol>")
        if isinstance(recipe, CommentedRecipe):
            if len(recipe.references) > 0:
                io.write("<h4>References</h4><ul>")
                for reference in recipe.references:
                    io.write(f"<li>{reference}</li>")
                io.write("</ul>")

    def write_standalone(self, io, recipe, scale_factor=1.0):
        # type: (typing.TextIO, Recipe, float) -> None
        io.write("<html>")
        io.write(f"<head><title>{recipe.name}</title></head>")
        io.write("<body>")
        self.write_recipe(io, recipe, scale_factor)
        io.write("</body></html>")


def get_writer(mimetype):
    for cls in BaseWriter.__subclasses__():
        if mimetype == cls.mimetype:
            return cls
    raise NotImplementedError(f"No writer for mimetype {mimetype}")
