"""Measure Liquid Height."""
from typing import List, Tuple, Optional
from opentrons.protocol_api import (
    ProtocolContext,
    Labware,
    Well,
    InstrumentContext,
)
from opentrons.types import Point

###########################################
#  VARIABLES - START
###########################################
# TODO: use runtime-variables instead of constants
NUM_TRIALS = 10
TEST_VOLUME = 40
CSV_HEADER = "trial,volume,height,tip-z-error"

LIQUID_MOUNT = "right"
LIQUID_TIP_SIZE = 200
LIQUID_PIPETTE_SIZE = 1000

PROBING_MOUNT = "left"
PROBING_TIP_SIZE = 50
PROBING_PIPETTE_SIZE = 50

ASPIRATE_MM_FROM_BOTTOM = 5  # depth in source reservoir to aspirate
RESERVOIR = "nest_1_reservoir_195ml"
LABWARE = "armadillo_96_wellplate_200ul_pcr_full_skirt"

SLOT_LIQUID_TIPRACK = "C3"
SLOT_PROBING_TIPRACK = "D3"
SLOT_LABWARE = "D1"
SLOT_RESERVOIR = "C1"
SLOT_DIAL = "B3"

###########################################
#  VARIABLES - END
###########################################

metadata = {"protocolName": "lld-test-liquid-height"}
requirements = {"robotType": "Flex", "apiLevel": "2.20"}

_all_96_well_names = [f"{c}{r + 1}" for c in "ABCDEFG" for r in range(12)]
_first_row_well_names = [f"A{r + 1}" for r in range(12)]
TEST_WELLS = {
    1: {  # channel count
        "corning_96_wellplate_360ul_flat": _all_96_well_names,
        "armadillo_96_wellplate_200ul_pcr_full_skirt": _all_96_well_names,
    }
}

DIAL_POS_WITHOUT_TIP: List[Optional[float]] = [None, None]
DIAL_PORT_NAME = "/dev/ttyUSB0"
DIAL_PORT = None
RUN_ID = ""
FILE_NAME = ""


def _setup(
    ctx: ProtocolContext,
) -> Tuple[
    InstrumentContext,
    Labware,
    InstrumentContext,
    Labware,
    Labware,
    Labware,
    Labware,
]:
    global DIAL_PORT, RUN_ID, FILE_NAME
    # TODO: use runtime-variables instead of constants
    ctx.load_trash_bin("A3")

    liquid_rack_name = f"opentrons_flex_96_tiprack_{LIQUID_TIP_SIZE}uL"
    liquid_rack = ctx.load_labware(liquid_rack_name, SLOT_LIQUID_TIPRACK)
    probing_rack_name = f"opentrons_flex_96_tiprack_{PROBING_TIP_SIZE}uL"
    probing_rack = ctx.load_labware(probing_rack_name, SLOT_PROBING_TIPRACK)

    liquid_pip_name = f"flex_1channel_{LIQUID_PIPETTE_SIZE}"
    liquid_pipette = ctx.load_instrument(liquid_pip_name, LIQUID_MOUNT)
    probing_pip_name = f"flex_1channel_{PROBING_PIPETTE_SIZE}"
    probing_pipette = ctx.load_instrument(probing_pip_name, PROBING_MOUNT)

    reservoir = ctx.load_labware(RESERVOIR, SLOT_RESERVOIR)
    labware = ctx.load_labware(LABWARE, SLOT_LABWARE)
    dial = ctx.load_labware("dial_indicator", SLOT_DIAL)

    if not ctx.is_simulating() and DIAL_PORT is None:
        from hardware_testing.data import create_file_name, create_run_id
        from hardware_testing.drivers.mitutoyo_digimatic_indicator import (
            Mitutoyo_Digimatic_Indicator,
        )

        DIAL_PORT = Mitutoyo_Digimatic_Indicator(port=DIAL_PORT_NAME)
        DIAL_PORT.connect()
        RUN_ID = create_run_id()
        FILE_NAME = create_file_name(
            metadata["protocolName"], RUN_ID, f"{liquid_pip_name}-{liquid_rack_name}"
        )
        _write_line_to_csv(ctx, RUN_ID)
        _write_line_to_csv(ctx, liquid_pip_name)
        _write_line_to_csv(ctx, liquid_rack_name)
        _write_line_to_csv(ctx, LABWARE)
    return (
        liquid_pipette,
        liquid_rack,
        probing_pipette,
        probing_rack,
        labware,
        reservoir,
        dial,
    )


def _write_line_to_csv(ctx: ProtocolContext, line: str) -> None:
    if ctx.is_simulating():
        return
    from hardware_testing.data import append_data_to_file

    append_data_to_file(metadata["protocolName"], RUN_ID, FILE_NAME, f"{line}\n")


def _get_test_wells(labware: Labware, channels: int) -> List[Well]:
    return [labware[w] for w in TEST_WELLS[channels][labware.load_name]]


def _get_test_tips(rack: Labware, channels: int) -> List[Well]:
    if channels == 96:
        test_tips = [rack["A1"]]
    elif channels == 8:
        test_tips = rack.rows()[0][:NUM_TRIALS]
    else:
        test_tips = rack.wells()[:NUM_TRIALS]
    return test_tips


def _read_dial_indicator(
    ctx: ProtocolContext,
    pipette: InstrumentContext,
    dial: Labware,
    front_channel: bool = False,
) -> float:
    target = dial["A1"].top()
    if front_channel:
        target = target.move(Point(y=9 * 7))
        if pipette.channels == 96:
            target = target.move(Point(x=9 * -11))
    pipette.move_to(target.move(Point(z=10)))
    pipette.move_to(target)
    ctx.delay(seconds=2)
    if ctx.is_simulating():
        return 0.0
    dial_port = DIAL_PORT.read()  # type: ignore[union-attr]
    pipette.move_to(target.move(Point(z=10)))
    return dial_port


def _store_dial_baseline(
    ctx: ProtocolContext,
    pipette: InstrumentContext,
    dial: Labware,
    front_channel: bool = False,
) -> None:
    global DIAL_POS_WITHOUT_TIP
    idx = 0 if not front_channel else 1
    if DIAL_POS_WITHOUT_TIP[idx] is not None:
        return
    DIAL_POS_WITHOUT_TIP[idx] = _read_dial_indicator(ctx, pipette, dial, front_channel)
    tag = f"DIAL-BASELINE-{idx}"
    _write_line_to_csv(ctx, f"{tag},{DIAL_POS_WITHOUT_TIP[idx]}")


def _get_tip_z_error(
    ctx: ProtocolContext,
    pipette: InstrumentContext,
    dial: Labware,
    front_channel: bool = False,
) -> float:
    idx = 0 if not front_channel else 1
    dial_baseline_for_this_channel = DIAL_POS_WITHOUT_TIP[idx]
    assert dial_baseline_for_this_channel is not None
    new_val = _read_dial_indicator(ctx, pipette, dial, front_channel)
    z_error = new_val - dial_baseline_for_this_channel
    # NOTE: dial-indicators are upside-down, so we need to flip the values
    return z_error * -1.0


def _get_height_of_liquid_in_well(
    pipette: InstrumentContext,
    well: Well,
) -> float:
    # FIXME: calculate actual liquid height
    return pipette.measure_liquid_height(well)


def _test_for_finding_liquid_height(
    ctx: ProtocolContext,
    liquid_pipette: InstrumentContext,
    probing_pipette: InstrumentContext,
    dial: Labware,
    liquid_tips: List[Well],
    probing_tips: List[Well],
    src_well: Well,
    wells: List[Well],
) -> None:
    assert len(liquid_tips) == len(probing_tips), f"{len(liquid_tips)},{len(probing_tips)}"
    trial_counter = 0
    _store_dial_baseline(ctx, probing_pipette, dial)
    _write_line_to_csv(ctx, CSV_HEADER)

    for liq_tip, probe_tip, well in zip(liquid_tips, probing_tips, wells):
        trial_counter += 1
        # pickup probing tip, then measure Z-error
        probing_pipette.pick_up_tip(probe_tip)
        tip_z_error = _get_tip_z_error(ctx, probing_pipette, dial)
        # pickup liquid tip, then immediately transfer liquid
        liquid_pipette.pick_up_tip(liq_tip)
        liquid_pipette.aspirate(TEST_VOLUME, src_well.bottom(ASPIRATE_MM_FROM_BOTTOM))
        liquid_pipette.dispense(TEST_VOLUME, well)
        liquid_pipette.prepare_to_aspirate()
        # get height of liquid
        height = _get_height_of_liquid_in_well(probing_pipette, well)
        # drop all tips
        liquid_pipette.drop_tip()
        probing_pipette.drop_tip()
        # save data
        trial_data = [trial_counter, TEST_VOLUME, height, tip_z_error]
        _write_line_to_csv(ctx, ",".join([str(d) for d in trial_data]))


def run(ctx: ProtocolContext) -> None:
    """Run."""
    liq_pipette, liq_rack, probe_pipette, probe_rack, labware, reservoir, dial = _setup(
        ctx
    )
    test_wells = _get_test_wells(labware, channels=1)
    test_tips_liquid = _get_test_tips(liq_rack, channels=1)
    test_tips_probe = _get_test_tips(probe_rack, channels=1)
    _test_for_finding_liquid_height(
        ctx,
        liq_pipette,
        probe_pipette,
        dial,
        liquid_tips=test_tips_liquid,
        probing_tips=test_tips_probe,
        src_well=reservoir["A1"],
        wells=test_wells,
    )
