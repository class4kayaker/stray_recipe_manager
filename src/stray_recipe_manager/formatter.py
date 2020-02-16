import pint
import typing
from stray_recipe_manager.units import UnitHandler
from stray_recipe_manager.recipe import (
    Ingredient,
    RecipeStep,
    Recipe,
    CommentedRecipe,
)


class UnitPreferences:
    def __init__(self, unit_handler):
        # type: (UnitHandler) -> None
        self.unit_handler = unit_handler
        self.preferences = {}  # type: typing.Dict[str, pint.Unit]

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


class MarkdownWriter:
    def __init__(self, unit_preferences):
        # type: (UnitPreferences) -> None
        self.unit_preferences = unit_preferences
        self.scale_factor = 1.0

    def set_scale_factor(self, scale_factor):
        self.scale_factor = scale_factor

    def format_ingredient(self, ingredient):
        # type: (Ingredient) -> str
        converted_quantity = (
            self.scale_factor
            * self.unit_preferences.handle_ingredient(ingredient)
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

    def write_recipe(self, io, recipe):
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
            io.write("-    {}\n".format(self.format_ingredient(ingredient)))
        io.write("\n#### Procedure\n\n")
        for step in recipe.steps:
            io.write("-    {}\n".format(self.format_step(step)))
        if isinstance(recipe, CommentedRecipe):
            if len(recipe.references) > 0:
                io.write("\n#### References\n\n")
                for reference in recipe.references:
                    io.write(f"-    {reference}\n")
