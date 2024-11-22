"""Liquid Class helpers."""
from typing import List, Any

from opentrons_shared_data.liquid_classes import liquid_class_definition as lcd

# EXPORT requirements:
#   - display entire contents (figure out layout manually)
#   - display schema version
#   - columns will be of unpredictable and differing lengths

DELIMITER = "\t"
LINE_END = "\n"

META_DATA_KEYS_V1 = [
    "liquidClassName",
    "displayName",
    "schemaVersion",
    "namespace"
]


def _list_to_csv_line(*data: Any) -> str:
    return DELIMITER.join([str(d) for d in data]) + LINE_END


def _attribute_to_csv_line(subclass_instance: Any, name: str) -> str:
    return _list_to_csv_line(name, getattr(subclass_instance, name))


def _meta_to_csv(lc: lcd.LiquidClassSchemaV1) -> List[str]:
    return [
        _attribute_to_csv_line(lc, key)
        for key in lc.dict().keys()
        if key != "byPipette"
    ]


def _pipette_to_csv(pipette: lcd.ByPipetteSetting) -> List[str]:
    pip_model_line = [_attribute_to_csv_line(pipette, "pipetteModel")]
    for tip in pipette.byTipType:
        tiprack_line = _attribute_to_csv_line(tip, "tiprack")
        aspirate_lines = [
            "submerge"
        ]
    return pip_model_line + tip_lines


def generate_csv(lc: lcd.LiquidClassSchemaV1) -> List[str]:
    meta_lines = _meta_to_csv(lc)
    pipette_lines = [
        _pipette_to_csv(pipette)
        for pipette in lc.byPipette
    ]
    return meta_lines + pipette_lines

