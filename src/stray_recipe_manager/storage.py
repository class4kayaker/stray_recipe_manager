import toml
import typing
import pathlib

from stray_recipe_manager.recipe import Recipe, CommentedRecipe
from stray_recipe_manager.units import UnitHandler, default_unit_registry


class TOMLCoding:
    def __init__(self, unit_handler):
        # type: (UnitHandler) -> None
        self.unit_handler = unit_handler

    @staticmethod
    def load_unit_handler_toml(toml_file):
        # type: (typing.TextIO) -> UnitHandler
        data = toml.load(toml_file)
        unit_handler = UnitHandler(
            default_unit_registry, data.get("tolerance", 1e-3)
        )
        for k, v in data["densities"].items():
            unit_handler.add_density(
                k, unit_handler.parse_quantity(v, "[mass]/[length]**3")
            )
        return unit_handler

    def load_recipe_from_toml_file(self, toml_file):
        # type: (typing.TextIO) -> Recipe
        data = toml.load(toml_file)
        if "densities" in data:
            for k, v in data["densities"].items():
                self.unit_handler.add_density(
                    k,
                    self.unit_handler.parse_quantity(v, "[mass]/[length]**3"),
                )
            del data["densities"]
        if "comments" in data or "references" in data:
            return CommentedRecipe.from_dict(data, self.unit_handler)
        else:
            return Recipe.from_dict(data, self.unit_handler)

    def load_densities_from_toml_file(self, toml_file):
        # type: (typing.TextIO) -> None
        data = toml.load(toml_file)
        for k, v in data["densities"].items():
            self.unit_handler.add_density(
                k, self.unit_handler.parse_quantity(v, "[mass]/[length]**3")
            )

    @staticmethod
    def write_unit_handler_to_file(self, toml_file, unit_handler):
        # type: (typing.TextIO, UnitHandler) -> None
        data = {
            "tolerance": unit_handler.tolerance,
            "densities": unit_handler.densities,
        }
        toml.dump(data, toml_file)

    def write_recipe_to_toml_file(
        self, toml_file, recipe, include_densities=False
    ):
        # type: (typing.TextIO, Recipe, bool) -> None
        data = recipe.to_dict()
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
        data = {"densities": self.unit_handler.densities}
        toml.dump(data, toml_file)


class DirectoryStorage:
    def __init__(self, dirpath):
        # type: (pathlib.Path) -> None
        self.basepath = dirpath
        self.unit_handler_config = self.basepath / "config.toml"
        self.recipe_dir = self.basepath / "recipes"
        with self.unit_handler_config.open("r") as f:
            self.unit_handler = TOMLCoding.load_unit_handler_toml(f)
        self.toml_coding = TOMLCoding(self.unit_handler)

    @classmethod
    def from_path_str(cls, dirpath_str):
        return cls(pathlib.Path(dirpath_str))

    def recipes(self):
        # type: () -> typing.Iterator[typing.Tuple[str, Recipe]]
        for fpath in self.recipe_dir.glob("*.toml"):
            with fpath.open("r") as f:
                recipe = self.toml_coding.load_recipe_from_toml_file(f)
            yield (fpath.stem, recipe)

    def get_recipe(self, recipe_key):
        # type: (str) -> Recipe
        path = self.recipe_dir / (recipe_key + ".toml")
        if not path.exists() or path.is_dir():
            raise KeyError("No recipe for '{}'".format(recipe_key))
        with path.open("r") as f:
            return self.toml_coding.load_recipe_from_toml_file(f)
