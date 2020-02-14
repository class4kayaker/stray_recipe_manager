import pytest

import pint
import jolly_recipe_manager.units


@pytest.fixture(scope="module")
def density_registry():
    registry = jolly_recipe_manager.units.DensityRegistry()
    ureg = registry.unit_registry
    registry.add_density("water", ureg.parse_expression("240 g/cp"))
    registry.add_density("rice", ureg.parse_expression("180 g/cp"))
    return registry


@pytest.mark.parametrize(
    "in_quant_str,out_unit_str,identifier,ans_str",
    [
        ("1cp", "tsp", None, "48 tsp"),
        ("1cp", "grams", "water", "240 grams"),
        ("1cp", "grams", "rice", "180 grams"),
        ("180g", "cp", "rice", "1cp"),
    ],
)
def test_conversion(
    density_registry, in_quant_str, out_unit_str, identifier, ans_str
):
    ureg = density_registry.unit_registry
    in_quant = ureg.parse_expression(in_quant_str)
    out_unit = ureg.parse_units(out_unit_str)
    ans = ureg.parse_expression(ans_str)
    assert (
        density_registry.do_conversion(in_quant, out_unit, identifier) == ans
    )


@pytest.mark.parametrize(
    "in_quant_str,out_unit_str,identifier,exc_str",
    [
        ("1cp", "grams", None, "No density known for 'None'"),
        ("1cp", "grams", "unknown", "No density known for 'unknown'"),
        ("1cp", "miles", "rice", "Unable to convert"),
    ],
)
def test_fail_conversion(
    density_registry, in_quant_str, out_unit_str, identifier, exc_str
):
    ureg = density_registry.unit_registry
    in_quant = ureg.parse_expression(in_quant_str)
    out_unit = ureg.parse_units(out_unit_str)
    with pytest.raises(
        jolly_recipe_manager.units.InvalidConversion
    ) as excinfo:
        density_registry.do_conversion(in_quant, out_unit, identifier)

    assert exc_str in str(excinfo.value)
