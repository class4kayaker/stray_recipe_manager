import toml
import typing
import pathlib
import logging

from stray_recipe_manager.recipe import Recipe, CommentedRecipe
from stray_recipe_manager.units import UnitHandler, default_unit_registry


logger = logging.getLogger(__name__)


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
        if "densities" in data:
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


class InvalidPathType(Exception):
    pass


class BaseStorage:
    @classmethod
    def from_path_str(cls, dirpath_str):
        raise NotImplementedError(
            f"No implementation for getting storage "
            f"{cls.__module__}.{cls.__name__} from path string"
        )

    def get_unit_handler(self):
        # type: () -> UnitHandler
        raise NotImplementedError()

    def recipe_keys(self):
        # type: () -> typing.Iterator[str]
        raise NotImplementedError()

    def recipes(self):
        # type: () -> typing.Iterator[typing.Tuple[str, Recipe]]
        for key in self.recipe_keys():
            yield (key, self.get_recipe(key))

    def get_recipe(self, recipe_key):
        # type: (str) -> Recipe
        raise NotImplementedError()

    def write_recipe(self, recipe_key, recipe, overwrite=False):
        # type: (str, Recipe, bool) -> None
        raise NotImplementedError()


class DirectoryStorage(BaseStorage):
    def __init__(self, config_file, recipe_dir):
        # type: (pathlib.Path, pathlib.Path) -> None
        self.unit_handler_config = config_file
        self.recipe_dir = recipe_dir
        with self.unit_handler_config.open("r") as f:
            self.unit_handler = TOMLCoding.load_unit_handler_toml(f)
        self.toml_coding = TOMLCoding(self.unit_handler)

    @classmethod
    def from_path_str(cls, dirpath_str):
        # type: (str) -> DirectoryStorage
        path = pathlib.Path(dirpath_str)
        if path.is_dir():
            config_file = path / "config.toml"
            if not config_file.exists():
                raise InvalidPathType(f"Missing configfile at {config_file}")
            recipe_dir = path / "recipes"
            if not recipe_dir.is_dir():
                raise InvalidPathType(
                    f"Missing recipe directory at {recipe_dir}"
                )
            return cls(config_file, recipe_dir)
        else:
            raise InvalidPathType(f"Path {dirpath_str} is not a directory")

    def get_unit_handler(self):
        # type: () -> UnitHandler
        return self.unit_handler

    def recipe_keys(self):
        # type: () -> typing.Iterator[str]
        for fpath in self.recipe_dir.glob("*.toml"):
            yield fpath.stem

    def get_recipe(self, recipe_key):
        # type: (str) -> Recipe
        path = self.recipe_dir / (recipe_key + ".toml")
        if not path.exists() or path.is_dir():
            raise KeyError("No recipe for '{}'".format(recipe_key))
        with path.open("r") as f:
            return self.toml_coding.load_recipe_from_toml_file(f)

    def write_recipe(self, recipe_key, recipe, overwrite=False):
        # type: (str, Recipe, bool) -> None
        path = self.recipe_dir / (recipe_key + ".toml")
        if path.exists() and not overwrite:
            raise KeyError("Recipe already exists, not overwriting")
        with path.open("w") as f:
            self.toml_coding.write_recipe_to_toml_file(f, recipe)


def get_storage(init_path):
    # type: (str) -> BaseStorage
    for cls in BaseStorage.__subclasses__():
        try:
            return cls.from_path_str(init_path)
        except InvalidPathType as e:
            logger.info(
                "Class %s.%s invalid: %s",
                cls.__module__,
                cls.__name__,
                repr(e),
            )
    raise InvalidPathType(f"No valid storage type found for {init_path}")
