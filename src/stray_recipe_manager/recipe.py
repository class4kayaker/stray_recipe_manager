import pint
import attr
import typing

from stray_recipe_manager.units import UnitHandler


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


@attr.attrs(frozen=True, slots=True)
class Recipe(object):
    name = attr.ib(type=str, kw_only=True)
    ingredients = attr.ib(
        type=typing.List[Ingredient], kw_only=True
    )
    steps = attr.ib(
        type=typing.List[RecipeStep], kw_only=True
    )
    tools = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )
    tags = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, typing.Any], UnitHandler) -> Recipe
        data["ingredients"] = [
            Ingredient.from_dict(i, unit_handler) for i in data["ingredients"]
        ]
        data["steps"] = [
            RecipeStep.from_dict(i, unit_handler) for i in data["steps"]
        ]
        return cls(**data)


@attr.attrs(frozen=True, slots=True)
class CommentedRecipe(Recipe):
    comments = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    references = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )

    @classmethod
    def from_dict(cls, data, unit_handler):
        # type: (typing.MutableMapping[str, typing.Any], UnitHandler) -> Recipe
        data["ingredients"] = [
            Ingredient.from_dict(i, unit_handler) for i in data["ingredients"]
        ]
        data["steps"] = [
            RecipeStep.from_dict(i, unit_handler) for i in data["steps"]
        ]
        return cls(**data)
