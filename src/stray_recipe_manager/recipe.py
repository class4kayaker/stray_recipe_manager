import pint
import attr
import typing


@attr.s(frozen=True, slots=True)
class Ingredient(object):
    item = attr.ib(type=str, kw_only=True)
    quantity = attr.ib(type=pint.Quantity, kw_only=True)
    identifier = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    category = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    notes = attr.ib(default=None, type=typing.Optional[str], kw_only=True)


@attr.s(frozen=True, slots=True)
class RecipeStep(object):
    description = attr.ib(type=str, kw_only=True)
    time = attr.ib(
        default=None, type=typing.Optional[pint.Quantity], kw_only=True
    )


@attr.s(frozen=True, slots=True)
class Recipe(object):
    name = attr.ib(type=str, kw_only=True)
    tools = attr.ib(type=typing.List[str], kw_only=True)
    time = attr.ib(default=None, type=typing.Optional[str], kw_only=True)


@attr.s(frozen=True, slots=True)
class CommentedRecipe(Recipe):
    comments = attr.ib(default=None, type=typing.Optional[str], kw_only=True)
    references = attr.ib(
        default=attr.Factory(list), type=typing.List[str], kw_only=True
    )
