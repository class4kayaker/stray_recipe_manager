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


def test_unit_prefs():
    unit_handler = stray_recipe_manager.units.UnitHandler(ureg)
    unit_preferences = stray_recipe_manager.formatter.UnitPreferences(
        unit_handler
    )
    assert unit_preferences.get_unit_preference("bulk_solid") is None
    unit_preferences.set_unit_preference("bulk_solid", ureg.liter)
    assert unit_preferences.get_unit_preference("bulk_solid") == ureg.liter
    unit_preferences.set_unit_preference("bulk_solid", ureg.cup)
    assert unit_preferences.get_unit_preference("bulk_solid") == ureg.cup
    unit_preferences.set_unit_preference("bulk_solid", None)
    assert unit_preferences.get_unit_preference("bulk_solid") is None
    unit_preferences.set_unit_preference("bulk_solid", ureg.gram)
    assert unit_preferences.get_unit_preference("bulk_solid") == ureg.gram
    unit_preferences.clear_unit_preferences()
    assert unit_preferences.get_unit_preference("bulk_solid") is None


@pytest.mark.parametrize(
    "recipe,formatted_str",
    [
        (
            Recipe(
                name="Boiling Water",
                tools=["Saucepan"],
                ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
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
                ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
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
    unit_handler = stray_recipe_manager.units.UnitHandler(ureg)
    unit_preferences = stray_recipe_manager.formatter.UnitPreferences(
        unit_handler
    )
    fmt_obj = stray_recipe_manager.formatter.MarkdownWriter(unit_preferences)
    fstream = io.StringIO()
    fmt_obj.write_recipe(fstream, recipe)
    assert fstream.getvalue() == formatted_str
