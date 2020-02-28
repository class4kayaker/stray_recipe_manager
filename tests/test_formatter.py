import io
import pytest
import stray_recipe_manager.units
from stray_recipe_manager.recipe import (
    CommentedRecipe,
    Recipe,
    Ingredient,
    RecipeStep,
)
import stray_recipe_manager.formatter


ureg = stray_recipe_manager.units.default_unit_registry


@pytest.mark.parametrize(
    "recipe,formatted_str",
    [
        (
            Recipe(
                name="Boiling Water",
                tools=["Saucepan"],
                ingredients=[Ingredient(item="Water", quantity=1. * ureg.cup,)],
                steps=[
                    RecipeStep(
                        description="Place water on stove until boiling"
                    )
                ],
            ),
            (
                "### Boiling Water\n"
                "\n"
                "#### Tools\n"
                "\n"
                "-    Saucepan\n"
                "\n"
                "#### Ingredients\n"
                "\n"
                "-    1.0 cup Water\n"
                "\n"
                "#### Procedure\n"
                "\n"
                "1)   Place water on stove until boiling\n"
            ),
        ),
        (
            CommentedRecipe(
                name="Boiling Water",
                comments="Utterly basic",
                tools=["Saucepan"],
                ingredients=[Ingredient(item="Water", quantity=1. * ureg.cup,)],
                steps=[
                    RecipeStep(
                        description="Place water on stove until boiling"
                    )
                ],
            ),
            (
                "### Boiling Water\n"
                "\n"
                "#### Comments\n"
                "\n"
                "Utterly basic\n"
                "\n"
                "#### Tools\n"
                "\n"
                "-    Saucepan\n"
                "\n"
                "#### Ingredients\n"
                "\n"
                "-    1.0 cup Water\n"
                "\n"
                "#### Procedure\n"
                "\n"
                "1)   Place water on stove until boiling\n"
            ),
        ),
    ],
)
def test_recipe_format_md(recipe, formatted_str):
    # type: (Recipe, str) -> None
    fstream = io.StringIO()
    stray_recipe_manager.formatter.MarkdownWriter.write_recipe(fstream, recipe)
    assert fstream.getvalue() == formatted_str
