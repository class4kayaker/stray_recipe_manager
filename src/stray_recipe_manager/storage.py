import toml
import attr
import typing

from stray_recipe_manager.recipe import Recipe
from stray_recipe_manager.units import UnitHandler


class TOMLCoding:
    def __init__(self, unit_handler):
        # type: (UnitHandler) -> None
        self.unit_handler = unit_handler

    def load_recipe_from_toml_file(self, toml_file):
        # type: (typing.TextIO) -> Recipe
        data = toml.load(toml_file)
        for k, v in data["densities"].items():
            self.unit_handler.add_density(
                k, self.unit_handler.parse_quantity(v, "[mass]/[length]**3")
            )
        del data["densities"]
        return Recipe.from_dict(data, self.unit_handler)

    def load_densities_from_toml_file(self, toml_file):
        # type: (typing.TextIO) -> None
        data = toml.load(toml_file)
        for k, v in data["densities"].items():
            self.unit_handler.add_density(
                k, self.unit_handler.parse_quantity(v, "[mass]/[length]**3")
            )

    def write_recipe_to_toml_file(
        self, toml_file, recipe, include_densities=False
    ):
        # type: (typing.TextIO, Recipe, bool) -> None
        data = attr.asdict(recipe, recurse=True)
        if include_densities:
            data["densities"] = {}
            density_types = set(
                ingredient.identifier for ingredient in recipe.ingredients
            )
            for identifier in density_types:
                if identifier is not None:
                    density = self.unit_handler.get_density(identifier)
                    if density is not None:
                        data["densities"][identifier] = density
        toml.dump(data, toml_file)

    def write_densities_to_toml_file(self, toml_file):
        # type: (typing.TextIO) -> None
        toml.dump(self.unit_handler.densities, toml_file)
