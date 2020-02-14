import pint
import typing

default_unit_registry = pint.UnitRegistry()


class InvalidConversion(Exception):
    pass


class DensityRegistry:
    __slots__ = ["densities", "unit_registry"]

    def __init__(self, unit_registry=default_unit_registry):
        # type: (pint.UnitRegistry) -> None
        self.densities = {}  # type: typing.Dict["str", pint.Quantity]
        self.unit_registry = unit_registry

    def add_density(self, item, density):
        # type: (str, pint.Quantity) -> None
        if item not in self.densities:
            self.densities[item] = density

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
                    "No density known for '{}' in dimensional conversion".format(
                        identifier
                    )
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
