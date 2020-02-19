import pytest

import stray_recipe_manager.units


@pytest.fixture(scope="module")
def unit_handler():
    registry = stray_recipe_manager.units.UnitHandler()
    return registry


def test_unit_handler_parse(unit_handler):
    ureg = unit_handler.unit_registry
    assert 1 * ureg.cup == unit_handler.parse_quantity("1 cup")
    with pytest.raises(stray_recipe_manager.units.InvalidData) as excinfo:
        unit_handler.parse_quantity("1 mile", "[length]**3")
    assert ureg.cup == unit_handler.parse_unit("cup")
    with pytest.raises(stray_recipe_manager.units.InvalidData) as excinfo:
        unit_handler.parse_unit("mile", "[length]**3")


def test_unit_handler_densities(unit_handler):
    ureg = unit_handler.unit_registry
    rice_density = 180 * ureg.g / ureg.cup
    unit_handler.add_density("rice", rice_density)
    assert unit_handler.get_density("rice") == rice_density
    with pytest.raises(stray_recipe_manager.units.InvalidData) as excinfo:
        unit_handler.add_density("rice", 2 * rice_density)
    assert "New density" in str(excinfo.value)


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

    in_quant = unit_handler.parse_quantity(in_quant_str)
    out_unit = unit_handler.parse_unit(out_unit_str)
    ans = unit_handler.parse_quantity(ans_str)
    assert unit_handler.do_conversion(in_quant, out_unit, identifier) == ans
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

    in_quant = unit_handler.parse_quantity(in_quant_str)
    out_unit = unit_handler.parse_unit(out_unit_str)
    with pytest.raises(
        stray_recipe_manager.units.InvalidConversion
    ) as excinfo:
        unit_handler.do_conversion(in_quant, out_unit, identifier)

    assert exc_str in str(excinfo.value)
    unit_handler.clear_densities()
