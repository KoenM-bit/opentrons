"""Liquid Class helpers."""

from opentrons_shared_data.liquid_classes.liquid_class_definition import LiquidClassSchemaV1

# EXPORT requirements:
#   - display entire contents (figure out layout manually)
#   - display schema version
#   - columns will be of unpredictable and differing lengths


def to_csv_str(liqiud_class: LiquidClassSchemaV1) -> str:
    # CONVERT the contents of a liquid class into a CSV
    return ""


def from_csv_str(csv_str: str) -> LiquidClassSchemaV1:
    # PARSE the contents of a CSV liquid-class
    return LiquidClassSchemaV1()
