import json

from opentrons_shared_data import load_shared_data
from opentrons_shared_data.liquid_classes import load_definition
from opentrons_shared_data.liquid_classes.liquid_class_definition import (
    LiquidClassSchemaV1,
    PositionReference,
    Coordinate,
    Submerge,
    DelayParams,
    DelayProperties,
)


def test_load_liquid_class_schema_v1() -> None:
    fixture_data = load_shared_data("liquid-class/definitions/1/water.json")
    liquid_class_model = LiquidClassSchemaV1.parse_raw(fixture_data)
    liquid_class_def_from_model = json.loads(
        liquid_class_model.json(exclude_unset=True)
    )
    expected_liquid_class_def = json.loads(fixture_data)
    assert liquid_class_def_from_model == expected_liquid_class_def


def test_load_definition() -> None:
    water_definition = load_definition(name="water", version=1)
    assert type(water_definition) is LiquidClassSchemaV1
    assert water_definition.byPipette[0].pipetteModel == "p10_single"
    assert water_definition.byPipette[0].byTipType[0].aspirate.submerge == Submerge(
        positionReference=PositionReference.LIQUID_MENISCUS,
        offset=Coordinate(x=0, y=0, z=-5),
        speed=100,
        delay=DelayProperties(enable=True, params=DelayParams(duration=1.5)),
    )
