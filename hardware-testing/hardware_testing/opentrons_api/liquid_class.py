"""Liquid Class helpers."""
from typing import List, Any, Dict

from opentrons_shared_data.liquid_classes import liquid_class_definition as lcd, load_definition

# EXPORT requirements:
#   - display entire contents (figure out layout manually)
#   - display schema version
#   - columns will be of unpredictable and differing lengths

DELIMITER = "\t"
LINE_END = "\n"


def _list_to_csv_line(*data: Any) -> str:
    return DELIMITER.join([str(d) for d in data]) + LINE_END


def _sort_liquid_class_dict(obj: Dict[str, Any]) -> Dict[str, Any]:
    ret = {}
    # first get all simple values, add them first so their on top
    _attr_added = []
    try:
        for attr, val in obj.items():
            if isinstance(val, str) or isinstance(val, int) or isinstance(val, float):
                ret[attr] = val
        # then grab the "by-volume" values
        for attr, val in obj.items():
            if "ByVolume" in attr:
                ret[attr] = {}
                for vol, by_vol_val in val:
                    ret[attr][vol] = by_vol_val
        for attr, val in obj.items():
            if "byPipette" in attr:
                ret[attr] = {}
                for
        # finally, get all the DICT values and recursively part them too
        for attr, val in obj.items():
            if not ret.get(attr):
                ret[attr] = _sort_liquid_class_dict(val)
        return ret
    finally:
        print(obj)


def gcs(load_name: str) -> Dict[str, Any]:
    lc_as_dict = _sort_liquid_class_dict(load_definition(load_name).dict())
    from pprint import pprint
    pprint(lc_as_dict)
    return lc_as_dict
