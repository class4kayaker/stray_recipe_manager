import toml

import stray_recipe_manager.recipe
import stray_recipe_manager.units


class LoaderTOML:
    def __init__(
        self, unit_handler=stray_recipe_manager.units.default_unit_registry
    ):
        self.unit_handler = unit_handler

    def load_toml(self):
        pass

    def load_recipe_from_toml(fileobj):
        pass

    def load_densities_from_toml(fileobj):
        pass
