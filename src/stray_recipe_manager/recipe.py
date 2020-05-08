import pint
import attr
import typing

from stray_recipe_manager.units import UnitHandler, UnitPreferences


@attr.attrs(frozen=True, slots=True)
class Ingredient(object):
    item = attr.ib(type=str, kw_only=True)
    quantity = attr.ib(type=pint.Quantity, kw_only=True)
    identifier = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    category = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    notes = attr.ib(default=None, type=typing.Optional[str], kw_only=True)

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, str], UnitHandler) -> Ingredient
        data["quantity"] = unit_handler.parse_quantity(data["quantity"])
        return cls(**data)

    def to_dict(self):
        data = attr.asdict(self)
        data["quantity"] = str(data["quantity"])
        return data


@attr.attrs(frozen=True, slots=True)
class RecipeStep(object):
    description = attr.ib(type=str, kw_only=True)
    group = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    time = attr.ib(
        default=None, type=typing.Optional[pint.Quantity], kw_only=True
    )

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, str], UnitHandler) -> RecipeStep
        if "time" in data and data["time"] is not None:
            data["time"] = unit_handler.parse_quantity(data["time"], "[time]")
        return cls(**data)

    def to_dict(self):
        data = attr.asdict(self)
        if self.time is not None:
            data["time"] = str(data["time"])
        return data


@attr.attrs(frozen=True, slots=True)
class Recipe(object):
    name = attr.ib(type=str, kw_only=True)
    makes = attr.ib(type=Ingredient, kw_only=True)
    ingredients = attr.ib(type=typing.List[Ingredient], kw_only=True)
    steps = attr.ib(type=typing.List[RecipeStep], kw_only=True)
    tools = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )
    tags = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, typing.Any], UnitHandler) -> Recipe
        data["makes"] = Ingredient.from_dict(data["makes"], unit_handler)
        data["ingredients"] = [
            Ingredient.from_dict(i, unit_handler) for i in data["ingredients"]
        ]
        data["steps"] = [
            RecipeStep.from_dict(i, unit_handler) for i in data["steps"]
        ]
        return cls(**data)

    def to_dict(self):
        data = attr.asdict(self, recurse=False)
        data["makes"] = data["makes"].to_dict()
        data["ingredients"] = [i.to_dict() for i in data["ingredients"]]
        data["steps"] = [i.to_dict() for i in data["steps"]]
        return data


@attr.attrs(frozen=True, slots=True)
class CommentedRecipe(Recipe):
    comments = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    references = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, typing.Any], UnitHandler) -> Recipe
        data["makes"] = Ingredient.from_dict(data["makes"], unit_handler)
        data["ingredients"] = [
            Ingredient.from_dict(i, unit_handler) for i in data["ingredients"]
        ]
        data["steps"] = [
            RecipeStep.from_dict(i, unit_handler) for i in data["steps"]
        ]
        return cls(**data)


def present_recipe(recipe, prefs, scale=1.0):
    # type: (Recipe, UnitPreferences, float) -> Recipe
    def mutate_ingredient(ingredient):
        # type: (Ingredient) -> Ingredient
        if ingredient.category is None:
            n_unit = None
        else:
            n_unit = prefs.get_unit_preference(ingredient.category)
        n_quantity = (
            ingredient.quantity
            if n_unit is None
            else prefs.unit_handler.do_conversion(
                ingredient.quantity, n_unit, ingredient.identifier
            )
        )
        return Ingredient(
            item=ingredient.item,
            quantity=scale * n_quantity,
            identifier=ingredient.identifier,
            category=ingredient.category,
            notes=ingredient.notes,
        )

    data = attr.asdict(recipe, recurse=False)
    data["makes"] = mutate_ingredient(data["makes"])
    data["ingredients"] = [mutate_ingredient(i) for i in data["ingredients"]]
    return recipe.__class__(**data)
