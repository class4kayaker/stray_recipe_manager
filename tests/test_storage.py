import io
import pytest
import stray_recipe_manager.units
import stray_recipe_manager.storage
from stray_recipe_manager.recipe import (
    CommentedRecipe,
    Recipe,
    Ingredient,
    RecipeStep,
)


ureg = stray_recipe_manager.units.default_unit_registry


@pytest.fixture(scope="module")
def toml_coding():
    registry = stray_recipe_manager.units.UnitHandler(ureg)
    toml_load = stray_recipe_manager.storage.TOMLCoding(registry)
    return toml_load


@pytest.mark.parametrize(
    "recipe",
    [
        Recipe(
            name="Boiling Water",
            makes=Ingredient(item="Boiling water", quantity=1.0 * ureg.cup),
            tools=["Saucepan"],
            ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
            steps=[
                RecipeStep(description="Place water on stove until boiling")
            ],
        ),
        CommentedRecipe(
            name="Boiling Water",
            comments="Utterly basic",
            makes=Ingredient(item="Boiling water", quantity=1.0 * ureg.cup),
            tools=["Saucepan"],
            ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
            steps=[
                RecipeStep(description="Place water on stove until boiling")
            ],
        ),
        Recipe(
            name="Boiling Water",
            makes=Ingredient(item="Boiling water", quantity=1.0 * ureg.cup),
            tools=["Saucepan"],
            ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
            steps=[
                RecipeStep(
                    description="Place water on stove until boiling",
                    time=10 * ureg.min,
                )
            ],
        ),
        CommentedRecipe(
            name="Boiling Water",
            makes=Ingredient(item="Boiling water", quantity=1.0 * ureg.cup),
            comments="Utterly basic",
            tools=["Saucepan"],
            ingredients=[Ingredient(item="Water", quantity=1 * ureg.cup,)],
            steps=[
                RecipeStep(
                    description="Place water on stove until boiling",
                    time=10 * ureg.min,
                )
            ],
        ),
    ],
)
def test_recipe_round_trip(recipe, toml_coding):
    # type: (Recipe, stray_recipe_manager.storage.TOMLCoding) -> None
    fstream = io.StringIO()
    toml_coding.write_recipe_to_toml_file(fstream, recipe)
    fstream.seek(0)
    print(fstream.getvalue())
    n_recipe = toml_coding.load_recipe_from_toml_file(fstream)
    assert recipe == n_recipe
