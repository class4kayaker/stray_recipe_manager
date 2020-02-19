import pint
import typing

default_unit_registry = pint.UnitRegistry()


class InvalidData(Exception):
    pass


class InvalidConversion(Exception):
    pass


class UnitHandler:
    __slots__ = ["densities", "unit_registry", "tolerance"]

    def __init__(self, unit_registry=default_unit_registry, tolerance=1e-3):
        # type: (pint.UnitRegistry, float) -> None
        self.densities = {}  # type: typing.Dict["str", pint.Quantity]
        self.unit_registry = unit_registry
        self.tolerance = tolerance

    def parse_quantity(self, quantity, dimensionality=None):
        # type: (str, typing.Optional[str]) -> pint.Quantity
        q = self.unit_registry.parse_expression(quantity)
        if dimensionality is not None and not q.check(dimensionality):
            raise InvalidData(
                f"Quantity {quantity} does not match required "
                f"dimensionality {dimensionality} "
                f"(actually {q.dimensionality})"
            )
        return q

    def parse_unit(self, unit, dimensionality=None):
        # type: (str, typing.Optional[str]) -> pint.Quantity
        u = self.unit_registry.parse_units(unit)
        if (dimensionality is not None) and (
            not u.dimensionality
            == self.unit_registry.get_dimensionality(dimensionality)
        ):
            raise InvalidData(
                f"Unit {unit} does not match required "
                f"dimensionality {dimensionality} "
                f"(actually {u.dimensionality})"
            )
        return u

    def add_density(self, item, density):
        # type: (str, pint.Quantity) -> None
        if item not in self.densities:
            self.densities[item] = density
        else:
            curr_density = self.densities[item]
            if abs(curr_density - density) > self.tolerance * curr_density:
                raise InvalidData(
                    f"New density for {item} ({density}) does not match "
                    f"earlier density ({curr_density})"
                )

    def get_density(self, item):
        # type: (str) -> typing.Optional[pint.Quantity]
        return self.densities.get(item, None)

    def clear_densities(self):
        # type: () -> None
        self.densities = {}

    def do_conversion(
        self,
        in_quantity,  # type: pint.Quantity
        out_unit,  # type: pint.Unit
        identifier,  # type: typing.Optional[str]
    ):
        # type: (...) -> pint.Quantity
        if in_quantity.dimensionality == out_unit.dimensionality:
            return in_quantity.to(out_unit)
        else:
            if identifier is None or identifier not in self.densities:
                raise InvalidConversion(
                    f"No density known for '{identifier}' "
                    "in dimensional conversion"
                )
            density = self.densities[identifier]
            if (
                in_quantity.dimensionality / out_unit.dimensionality
                == density.dimensionality
            ):
                return (in_quantity / density).to(out_unit)
            if (
                out_unit.dimensionality / in_quantity.dimensionality
                == density.dimensionality
            ):
                return (in_quantity * density).to(out_unit)
            raise InvalidConversion("Unable to convert")
