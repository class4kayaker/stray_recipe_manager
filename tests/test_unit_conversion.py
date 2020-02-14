import pytest

import stray_recipe_manager.units


@pytest.fixture(scope="module")
def unit_handler():
    registry = stray_recipe_manager.units.UnitHandler()
    return registry


def test_unit_handler():
    registry = stray_recipe_manager.units.UnitHandler()


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
    unit_handler, in_quant_str, out_unit_str, identifier, ans_str
):
    unit_handler.add_density("water", unit_handler.parse_quantity("240 g/cp"))
    unit_handler.add_density("rice", unit_handler.parse_quantity("180 g/cp"))
    ureg = unit_handler.unit_registry
    in_quant = unit_handler.parse_quantity(in_quant_str)
    out_unit = ureg.parse_units(out_unit_str)
    ans = unit_handler.parse_quantity(ans_str)
    assert (
        unit_handler.do_conversion(in_quant, out_unit, identifier) == ans
    )
    unit_handler.clear_densities()


@pytest.mark.parametrize(
    "in_quant_str,out_unit_str,identifier,exc_str",
    [
        ("1cp", "grams", None, "No density known for 'None'"),
        ("1cp", "grams", "unknown", "No density known for 'unknown'"),
        ("1cp", "miles", "rice", "Unable to convert"),
    ],
)
def test_fail_conversion(
    unit_handler, in_quant_str, out_unit_str, identifier, exc_str
):
    unit_handler.add_density("water", unit_handler.parse_quantity("240 g/cp"))
    unit_handler.add_density("rice", unit_handler.parse_quantity("180 g/cp"))

    ureg = unit_handler.unit_registry
    in_quant = unit_handler.parse_quantity(in_quant_str)
    out_unit = ureg.parse_units(out_unit_str)
    with pytest.raises(
        stray_recipe_manager.units.InvalidConversion
    ) as excinfo:
        unit_handler.do_conversion(in_quant, out_unit, identifier)

    assert exc_str in str(excinfo.value)
    unit_handler.clear_densities()
