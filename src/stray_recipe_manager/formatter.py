import logging
import typing
from stray_recipe_manager.recipe import (
    Ingredient,
    RecipeStep,
    Recipe,
    CommentedRecipe,
)


logger = logging.getLogger(__name__)


class BaseWriter:
    mimetype = None  # type: typing.Optional[str]

    def write_recipe(self, io, recipe):
        # type: (typing.TextIO, Recipe) -> None
        raise NotImplementedError()


class MarkdownWriter(BaseWriter):
    mimetype = "text/markdown"

    @classmethod
    def format_ingredient(cls, ingredient):
        # type: (Ingredient) -> str
        if ingredient.notes is None:
            return f"{ingredient.quantity!s} {ingredient.item}"
        else:
            return f"{ingredient.quantity!s} {ingredient.item}, {ingredient.notes}"

    @classmethod
    def format_step(cls, step):
        # type: (RecipeStep) -> str
        if step.time is None:
            return f"{step.description}"
        else:
            return f"{step.description} ({step.time!s})"

    @classmethod
    def write_recipe(cls, io, recipe):
        # type: (typing.TextIO, Recipe) -> None
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
            io.write("-    {}\n".format(clsl.format_ingredient(ingredient)))
        io.write("\n#### Procedure\n\n")
        for i, step in enumerate(recipe.steps):
            io.write("{:d})   {}\n".format(i + 1, cls.format_step(step)))
        if isinstance(recipe, CommentedRecipe):
            if len(recipe.references) > 0:
                io.write("\n#### References\n\n")
                for reference in recipe.references:
                    io.write(f"-    {reference}\n")


class HTMLWriter(BaseWriter):
    mimetype = "text/html"

    @classmethod
    def format_ingredient(cls, ingredient):
        # type: (Ingredient) -> str
        if ingredient.notes is None:
            return f"{ingredient.quantity!s} {ingredient.item}"
        else:
            return f"{ingredient.quantity!s} {ingredient.item}, {ingredient.notes}"

    @classmethod
    def format_step(cls, step):
        # type: (RecipeStep) -> str
        if step.time is None:
            return f"{step.description}"
        else:
            return f"{step.description} ({step.time!s})"

    @classmethod
    def write_recipe(cls, io, recipe):
        # type: (typing.TextIO, Recipe) -> None
        io.write("<html>")
        io.write(f"<head><title>{recipe.name}</title></head>")
        io.write("<body>")
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
            io.write("<li>{}</li>".format(cls.format_ingredient(ingredient)))
        io.write("</ul>")
        io.write("<h4>Instructions</h4><ol>")
        for step in recipe.steps:
            io.write("<li>{}</li>".format(cls.format_step(step)))
        io.write("</ol>")
        if isinstance(recipe, CommentedRecipe):
            if len(recipe.references) > 0:
                io.write("<h4>References</h4><ul>")
                for reference in recipe.references:
                    io.write(f"<li>{reference}</li>")
                io.write("</ul>")
        io.write("</body></html>")


def get_writer(mimetype):
    for cls in BaseWriter.__subclasses__():
        if mimetype == cls.mimetype:
            return cls
    raise NotImplementedError(f"No writer for mimetype {mimetype}")
