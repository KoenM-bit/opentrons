"""Ultima High Viscosity Fluid Lifetest."""
import argparse
import asyncio

from typing import List, Optional
from opentrons.hardware_control.ot3api import OT3API
from opentrons.config.defaults_ot3 import (
    DEFAULT_RUN_CURRENT,
    DEFAULT_MAX_SPEEDS,
    DEFAULT_ACCELERATIONS,
)
from opentrons_shared_data.errors.exceptions import StallOrCollisionDetectedError

from hardware_testing.data.csv_report import (
    CSVReport,
    CSVResult,
    CSVSection,
    CSVLine,
)
from hardware_testing.opentrons_api.types import (
    OT3Mount,
    Axis,
    CriticalPoint,
    Point,
)
from hardware_testing.data import ui
from hardware_testing.opentrons_api import helpers_ot3

FLOW_TO_SPEED = 1.0/15.9 # mm/uL
DEFAULT_FLOW = 700
DEFAULT_TRIALS = 10

TIP_RACK_LABWARE = f"opentrons_flex_96_tiprack_1000ul"
TIP_RACK_SLOT = 6

RESERVOIR_LABWARE = "nest_1_reservoir_195ml"
RESERVOIR_SLOT = 5

OFFSET_FOR_1_WELL_LABWARE = Point(x=9 * -11 * 0.5, y=9 * 7 * 0.5)

def _get_test_tag(flow: float, trial: int) -> str:
    return f"flow-{flow}-trial-{trial}"


def _build_csv_report(flow: float, trials: List) -> CSVReport:
    """Build the CSVReport object to record data."""
    _report = CSVReport(
        test_name="ultima-lifetest",
        sections=[
            CSVSection(
                title=OT3Mount.LEFT.name,
                lines=[CSVLine(_get_test_tag(flow, trial), [int]) for trial in trials],
            ),
            CSVSection(
                title=OT3Mount.RIGHT.name,
                lines=[CSVLine(_get_test_tag(flow, trial), [int]) for trial in trials],
            ),
        ],
    )
    return _report



async def _get_next_pipette_mount(api: OT3API) -> OT3Mount:
    await api.cache_instruments()
    found = [
        OT3Mount.from_mount(m) for m, p in api.hardware_pipettes.items() if p
    ]
    if not found:
        return await _get_next_pipette_mount(api)
    return found[0]


def get_reservoir_nominal() -> Point:
    """Get nominal reservoir position."""
    reservoir_a1_nominal = helpers_ot3.get_theoretical_a1_position(
        RESERVOIR_SLOT, RESERVOIR_LABWARE
    )
    # center the 96ch of the 1-well labware
    reservoir_a1_nominal += OFFSET_FOR_1_WELL_LABWARE
    return reservoir_a1_nominal


def get_tiprack_nominal() -> Point:
    """Get nominal tiprack position for pick-up."""
    tip_rack_a1_nominal = helpers_ot3.get_theoretical_a1_position(
        TIP_RACK_SLOT, TIP_RACK_LABWARE
    )
    return tip_rack_a1_nominal


async def _reset_gantry(api: OT3API) -> None:
    await api.home(
        [
            Axis.Z_L,
            Axis.Z_R,
            Axis.X,
            Axis.Y,
        ]
    )
    home_pos = await api.gantry_position(
        OT3Mount.RIGHT, CriticalPoint.MOUNT
    )


async def move_twin_plunger_absolute_ot3(
    api: OT3API,
    position: List[float],
    motor_current: Optional[float] = None,
    speed: Optional[float] = None,
    expect_stalls: bool = False,
) -> None:
    """Move OT3 plunger position to an absolute position."""
    _move_coro = api._move(
        target_position={Axis.P_L: position[0],
                         Axis.P_R: position[1]},  # type: ignore[arg-type]
        speed=speed,
        expect_stalls=expect_stalls,
    )
    if motor_current is None:
        await _move_coro
    else:
        async with api._backend.motor_current(
            run_currents={Axis.P_L: motor_current,
                          Axis.P_R: motor_current}
        ):
            await _move_coro


async def test_cycle(
    api: OT3API,
    positions: List[List[float]],
    flow: float,
    starting_cycle: int,
    cycles: int
) -> None:

    speed = flow * FLOW_TO_SPEED

    for i in range(cycles):
        print(starting_cycle)
        await move_twin_plunger_absolute_ot3(api, positions[0], speed=speed)
        await move_twin_plunger_absolute_ot3(api, positions[1], speed=speed)
        starting_cycle += 1

async def _main(is_simulating: bool, trials: int, flow: float, continue_after_stall: bool) -> None:
    api = await helpers_ot3.build_async_ot3_hardware_api(
        is_simulating=is_simulating,
        pipette_left="p1000_multi_v3.4",
        pipette_right="p50_single_v3.4",
    )

    # home and move to a safe position
    await _reset_gantry(api)
    await api.home([Axis.P_L, Axis.P_R])

    # test each attached pipette
    mount = await _get_next_pipette_mount(api)
    print(mount)

    trial_list = []
    for i in range(trials):
        trial_list.append(i)

    report = _build_csv_report(flow=flow, trials=trial_list)
    dut = helpers_ot3.DeviceUnderTest.by_mount(mount)
    helpers_ot3.set_csv_report_meta_data_ot3(api, report, dut)


    # Pick up tips
    tip_len = helpers_ot3.get_default_tip_length(1000)
    left_tips = get_tiprack_nominal()
    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.LEFT, left_tips)
    input("Pick up tip? Press Enter" )
    await api.pick_up_tip(OT3Mount.LEFT, tip_length=tip_len)

    right_tips = left_tips + Point(x=9)
    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.RIGHT, right_tips)
    input("Pick up tip? Press Enter" )
    await api.pick_up_tip(OT3Mount.RIGHT, tip_length=tip_len)

    # Move to reservoir
    await api.home([Axis.Z_L, Axis.Z_R])
    z_home = await api.gantry_position(OT3Mount.LEFT)
    reservoir_a1_nominal = get_reservoir_nominal()
    reservoir_a1_home = reservoir_a1_nominal._replace(z=z_home.z)
    await helpers_ot3.move_to_arched_ot3(
        api, OT3Mount.LEFT, reservoir_a1_home
    )

    # Descend into reservoir
    input("Descend?")
    mounts = [OT3Mount.LEFT, OT3Mount.RIGHT]
    pip_top = [helpers_ot3.get_plunger_positions_ot3(api, mounts[0])[0],
               helpers_ot3.get_plunger_positions_ot3(api, mounts[1])[0]]
    pip_bot = [helpers_ot3.get_plunger_positions_ot3(api, mounts[0])[1],
               helpers_ot3.get_plunger_positions_ot3(api, mounts[1])[1]]
    pip_blow = [helpers_ot3.get_plunger_positions_ot3(api, mounts[0])[2],
               helpers_ot3.get_plunger_positions_ot3(api, mounts[1])[2]]
    pip_drop = [helpers_ot3.get_plunger_positions_ot3(api, mounts[0])[3],
               helpers_ot3.get_plunger_positions_ot3(api, mounts[1])[3]]

    await api.home([Axis.P_L, Axis.P_R])
    await move_twin_plunger_absolute_ot3(api, pip_bot)

    await helpers_ot3.move_to_arched_ot3(
        api, OT3Mount.LEFT, reservoir_a1_nominal
    )

    gantry_z = await api.gantry_position(OT3Mount.LEFT)
    await api._move({Axis.X:api._current_position[Axis.X],
                     Axis.Y:api._current_position[Axis.Y],
                     Axis.Z_R:api._current_position[Axis.Z_L]})


    total_cycles = 0
    cycles_per_trial = 10
    for t in range(trials):
        await test_cycle(api, [pip_top,pip_bot], flow,
                         total_cycles, cycles_per_trial)
        total_cycles += cycles_per_trial
        report(OT3Mount.LEFT.name, _get_test_tag(flow, t), [total_cycles])
        report(OT3Mount.RIGHT.name, _get_test_tag(flow, t), [total_cycles])

    report.save_to_disk()
    # report.print_results()

    # Drop Tips
    await api.home([Axis.Z_L, Axis.Z_R])
    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.LEFT,
                                         left_tips + Point(z=10))
    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.LEFT,
                                         left_tips - Point(z=tip_len/3))
    await api.drop_tip(OT3Mount.LEFT)

    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.RIGHT,
                                         right_tips - Point(z=tip_len/3))
    await api.drop_tip(OT3Mount.RIGHT)

    ui.print_title("DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--flow", type=float, default=DEFAULT_FLOW)
    parser.add_argument("--continue-after-stall", action="store_true")
    args = parser.parse_args()
    asyncio.run(_main(args.simulate, args.trials, args.flow, args.continue_after_stall))
