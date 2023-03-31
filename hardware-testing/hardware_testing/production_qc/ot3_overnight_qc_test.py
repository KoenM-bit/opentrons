"""OT3 Overnight Test."""
import argparse
import asyncio
import os
import time

from dataclasses import dataclass
from typing import Optional, Callable, List, Any, Tuple,Dict
from pathlib import Path

from opentrons.hardware_control.ot3api import OT3API

from hardware_testing.opentrons_api import types
from hardware_testing.opentrons_api.types import OT3Axis
from hardware_testing.opentrons_api import helpers_ot3
from hardware_testing import data
from hardware_testing.data import ui


GANTRY_AXES = [types.OT3Axis.X, types.OT3Axis.Y, types.OT3Axis.Z_L, types.OT3Axis.Z_R]
MOUNT_AXES = [types.OT3Mount.LEFT, types.OT3Mount.RIGHT]
THRESHOLD_MM = 0.2


DEFAULT_AXIS_SETTINGS = {
    types.OT3Axis.X: helpers_ot3.GantryLoadSettings(
        max_speed=500,
        acceleration=1000,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.5,
        run_current=1.4,
    ),
    types.OT3Axis.Y: helpers_ot3.GantryLoadSettings(
        max_speed=500,
        acceleration=1000,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.5,
        run_current=1.4,
    ),
    types.OT3Axis.Z_L: helpers_ot3.GantryLoadSettings(
        max_speed=65,
        acceleration=100,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    ),
    types.OT3Axis.Z_R: helpers_ot3.GantryLoadSettings(
        max_speed=65,
        acceleration=100,
        max_start_stop_speed=10,
        max_change_dir_speed=5,
        hold_current=0.1,
        run_current=1.4,
    )
}

@dataclass
class CSVCallbacks:
    """CSV callback functions."""

    write: Callable


@dataclass
class CSVProperties:
    """CSV properties."""

    id: str
    name: str
    path: str


def _create_csv_and_get_callbacks(sn:str) -> Tuple[CSVProperties, CSVCallbacks]:
    run_id = data.create_run_id()
    test_name = data.create_test_name_from_file(__file__)
    folder_path = data.create_folder_for_test_data(test_name)
    file_name = data.create_file_name(test_name, run_id, sn)
    csv_display_name = os.path.join(folder_path, file_name)
    print(f"CSV: {csv_display_name}")
    start_time = time.time()

    def _append_csv_data(
        data_list: List[Any],
        line_number: Optional[int] = None,
        first_row_value: Optional[str] = None,
        first_row_value_included: bool = False,
    ) -> None:
        # every line in the CSV file begins with the elapsed seconds
        if not first_row_value_included:
            if first_row_value is None:
                first_row_value = str(round(time.time() - start_time, 2))
            data_list = [first_row_value] + data_list
        data_str = ",".join([str(d) for d in data_list])
        if line_number is None:
            data.append_data_to_file(test_name, file_name, data_str + "\n")
        else:
            data.insert_data_to_file(test_name, file_name, data_str + "\n", line_number)
    return (
        CSVProperties(id=run_id, name=test_name, path=csv_display_name),
        CSVCallbacks(
            write=_append_csv_data,
        ),
    )

def bool_to_string(result: bool) -> str:
    return 'PASS' if result else 'FAIL'

def _record_axis_data(type: str, write_cb: Callable,estimate: Dict[OT3Axis, float], encoder: Dict[OT3Axis, float], aligned: bool) -> None:
    write_cb([type] + [estimate[ax] for ax in estimate])
    write_cb([type] + [encoder[ax] for ax in estimate.keys()])
    write_cb([type,bool_to_string(aligned)])

def _record_motion_check_data(type: str, write_cb: Callable, speed:float, acceleration:float, cycles:int, pass_count:int, fail_count:int) -> None:
    write_cb([type] + ['Speed'] + [speed] + ['Acceleration'] + [acceleration] + ['Run Cycles'] + [cycles] + ['Pass Count'] + [pass_count] + ['Fail Count'] + [fail_count])

def _create_bowtie_points(homed_position: types.Point) -> List[types.Point]:
    pos_max = homed_position - types.Point(x=1, y=1, z=1)
    pos_min = types.Point(x=0, y=25, z=pos_max.z)  # stay above deck to be safe
    bowtie_points = [
        pos_max,  # back-right
        pos_min,  # front-left
        pos_min._replace(y=pos_max.y),  # back-left
        pos_max._replace(y=pos_min.y),  # front-right
        pos_max,  # back-right
    ]
    return bowtie_points

def _create_hour_glass_points(homed_position: types.Point) -> List[types.Point]:
    pos_max = homed_position - types.Point(x=1, y=1, z=1)
    pos_min = types.Point(x=0, y=25, z=pos_max.z)  # stay above deck to be safe
    hour_glass_points = [
        pos_max,  # back-right
        pos_min._replace(y=pos_max.y),  # back-left
        pos_max._replace(y=pos_min.y),  # front-right
        pos_min,  # front-left
        pos_max,  # back-right
    ]
    return hour_glass_points

def _create_mounts_up_down_points(homed_position: types.Point) -> List[types.Point]:
    pos_max = homed_position - types.Point(x=1, y=1, z=1)
    pos_min = types.Point(x=0, y=25, z=pos_max.z)  # stay above deck to be safe
    mounts_up_down_points = [
        pos_max._replace(z=pos_max.z - 200),  # down
        pos_max,  # up
    ]
    return mounts_up_down_points

async def _move_and_check(api: OT3API, is_simulating: bool, mount: types.OT3Mount, position: types.Point) -> None:
    if not is_simulating:
        await api.move_to(mount,position)
        estimate = {ax: api._current_position[ax] for ax in GANTRY_AXES}
        encoder = {ax: api._encoder_position[ax] for ax in GANTRY_AXES}
    else:
        pass

    all_aligned_axes = [
        ax
        for ax in GANTRY_AXES
        if abs(estimate[ax] - encoder[ax]) <= THRESHOLD_MM
    ]
    for ax in GANTRY_AXES:
        if ax in all_aligned_axes:
            aligned = True
        else:
            aligned = False
    return estimate,encoder,aligned

async def _run_mount_up_down(api: OT3API, is_simulating: bool, mount: types.OT3Mount, write_cb: Callable, record_bool=True) -> bool:
    ui.print_header('Run mount up and down')
    mount_up_down_points = _create_mounts_up_down_points(await api.gantry_position(mount))
    pass_count = 0
    for pos in mount_up_down_points:
        es,en,al = await _move_and_check(api,is_simulating,mount,pos)
        if record_bool:
            _record_axis_data('Mount_up_down',write_cb,es,en,al)
        print(f'mounts results: {al}')
    if pass_count == len(mount_up_down_points):
        return True
    else:
        return False

async def _run_bowtie(api: OT3API, is_simulating: bool, mount: types.OT3Mount, write_cb: Callable, record_bool=True) -> bool:
    ui.print_header('Run bowtie')
    bowtie_points = _create_bowtie_points(await api.gantry_position(mount))
    pass_count = 0
    for p in bowtie_points:
        es,en,al = await _move_and_check(api,is_simulating,mount,p)
        if record_bool:
            _record_axis_data('Bowtie',write_cb,es,en,al)
        if al:
            pass_count += 1
        print(f'bowtie results: {al}')
    if pass_count == len(bowtie_points):
        return True
    else:
        return False


async def _run_hour_glass(api: OT3API, is_simulating: bool, mount: types.OT3Mount, write_cb: Callable) -> None:
    ui.print_header('Run hour glass')
    hour_glass_points = _create_hour_glass_points(await api.gantry_position(mount))
    for q in hour_glass_points:
        es,en,al = await _move_and_check(api,is_simulating,mount,q)
        _record_axis_data('Hour_glass',write_cb,es,en,al)
        print(f'hour glass results: {al}')

def _get_accelerations_from_user() -> List:
    condition = True
    accelerations = []
    while condition:
        accelerations_input = input(f"WAIT: please input the acceleration and split with ',' like: 100,200,300 then press ENTER when ready: ")
        try:
            accelerations = [float(acc) for acc in accelerations_input.strip().replace(' ','').split(',')]
            condition = False
        except Exception as e:
            ui.print_error(e)
    return accelerations

def _get_speeds_from_user() -> List:
    condition = True
    speeds = []
    while condition:
        speeds_input = input(f"WAIT: please input the speeds and split with ',' like: 100,200,300 then press ENTER when ready: ")
        try:
            speeds = [float(spe) for spe in speeds_input.strip().replace(' ','').split(',')]
            condition = False
        except Exception as e:
            ui.print_error(e)
    return speeds

def _creat_z_axis_settings(arguments: argparse.Namespace) -> List:
    if arguments.z_speeds and arguments.z_accelerations:
        accelerations = [float(acc) for acc in arguments.z_accelerations.strip().replace(' ','').split(',')]
        speeds = [float(spe) for spe in arguments.z_speeds.strip().replace(' ','').split(',')]
    else:
        speeds = _get_speeds_from_user()
        accelerations = _get_accelerations_from_user()
    Z_AXIS_SETTINGS = []
    for speed in speeds:
        for acceleration in accelerations:
            Z_AXIS_SETTING = {
            types.OT3Axis.Z_L: helpers_ot3.GantryLoadSettings(
                max_speed=speed,
                acceleration=acceleration,
                max_start_stop_speed=10,
                max_change_dir_speed=5,
                hold_current=0.1,
                run_current=1.4,
            ),
            types.OT3Axis.Z_R: helpers_ot3.GantryLoadSettings(
                max_speed=speed,
                acceleration=acceleration,
                max_start_stop_speed=10,
                max_change_dir_speed=5,
                hold_current=0.1,
                run_current=1.4,
            )
            }
            Z_AXIS_SETTINGS.append(Z_AXIS_SETTING)

    return Z_AXIS_SETTINGS

def _creat_xy_axis_settings(arguments: argparse.Namespace) -> List:
    if arguments.xy_speeds and arguments.xy_accelerations:
        accelerations = [float(acc) for acc in arguments.xy_accelerations.strip().replace(' ','').split(',')]
        speeds = [float(spe) for spe in arguments.xy_speeds.strip().replace(' ','').split(',')]
    else:
        speeds = _get_speeds_from_user()
        accelerations = _get_accelerations_from_user()
    XY_AXIS_SETTINGS = []
    for speed in speeds:
        for acceleration in accelerations:
            XY_AXIS_SETTING = {
            types.OT3Axis.X: helpers_ot3.GantryLoadSettings(
                max_speed=speed,
                acceleration=acceleration,
                max_start_stop_speed=10,
                max_change_dir_speed=5,
                hold_current=0.5,
                run_current=1.4,
            ),
            types.OT3Axis.Y: helpers_ot3.GantryLoadSettings(
                max_speed=speed,
                acceleration=acceleration,
                max_start_stop_speed=10,
                max_change_dir_speed=5,
                hold_current=0.5,
                run_current=1.4,
            )
            }
            XY_AXIS_SETTINGS.append(XY_AXIS_SETTING)

    return XY_AXIS_SETTINGS

async def _run_z_motion(arguments: argparse.Namespace, api: OT3API, mount: types.OT3Mount, write_cb: Callable) -> None:
    ui.print_header('Run z motion check...')
    Z_AXIS_SETTINGS = _creat_z_axis_settings(arguments)
    for setting in Z_AXIS_SETTINGS:
        print(f'Run speed={setting[OT3Axis.Z_L].max_speed}, acceleration={setting[OT3Axis.Z_L].acceleration}')
        await helpers_ot3.set_gantry_load_per_axis_settings_ot3(api, setting)
        fail_count = 0
        pass_count = 0
        for i in range(arguments.cycles):
            for mount in MOUNT_AXES:
                res = await _run_mount_up_down(api,arguments.simulate,mount,write_cb,False)
                if res:
                    pass_count+=1
                else:
                    fail_count+=1
                print(f'Run mount up and down cycle: {i}, results: {res}, pass count: {pass_count}, fail count: {fail_count}')
    _record_motion_check_data('z_motion',write_cb,setting[OT3Axis.Z_L].max_speed,setting[OT3Axis.Z_L].acceleration,arguments.cycles,pass_count,fail_count)

async def _run_xy_motion(arguments: argparse.Namespace, api: OT3API, mount: types.OT3Mount, write_cb: Callable) -> None:
    ui.print_header('Run xy motion check...')
    XY_AXIS_SETTINGS = _creat_xy_axis_settings(arguments)
    for setting in XY_AXIS_SETTINGS:
        print(f'Run speed={setting[OT3Axis.X].max_speed}, acceleration={setting[OT3Axis.X].acceleration}')
        await helpers_ot3.set_gantry_load_per_axis_settings_ot3(api, setting)
        fail_count = 0
        pass_count = 0
        for i in range(arguments.cycles):
            res = await _run_bowtie(api,arguments.simulate,mount,write_cb,False)
            if res:
                pass_count+=1
            else:
                fail_count+=1
            print(f'Run bowtie cycle: {i}, results: {res}, pass count: {pass_count}, fail count: {fail_count}')
    _record_motion_check_data('xy_motion',write_cb,setting[OT3Axis.X].max_speed,setting[OT3Axis.X].acceleration,arguments.cycles,pass_count,fail_count)


async def _main(arguments: argparse.Namespace) -> None:
    # callback function for writing new data to CSV file
    csv_props, csv_cb = _create_csv_and_get_callbacks(arguments.sn)
    # cache the pressure-data header
    # add metadata to CSV
    # FIXME: create a set of CSV helpers, such that you can define a test-report
    #        schema/format/line-length/etc., before having to fill its contents.
    #        This would be very helpful, because changes to CVS length/contents
    #        will break the analysis done in our Sheets
    csv_cb.write(["--------"])
    csv_cb.write(["METADATA"])
    csv_cb.write(["test-name", csv_props.name])
    csv_cb.write(["serial-number",arguments.sn])
    csv_cb.write(["operator-name", arguments.operator])
    csv_cb.write(["date", csv_props.id])  # run-id includes a date/time string
    test_name = Path(__file__).name
    ui.print_title(test_name.replace("_", " ").upper())
    api = await helpers_ot3.build_async_ot3_hardware_api(is_simulating=arguments.simulate)
    await helpers_ot3.home_ot3(api)
    ui.get_user_ready("Is the deck totally empty?")
    mount = types.OT3Mount.LEFT
    if arguments.xy_motion:
        await _run_xy_motion(arguments,api,mount,csv_cb.write)
    if arguments.z_motion:
        await _run_z_motion(arguments,api,mount,csv_cb.write)
    for i in range(arguments.cycles):
            csv_cb.write(["--------"])
            csv_cb.write(["run-cycle", i])
            print(f"Cycle {i + 1}/{arguments.cycles}")
            if not arguments.skip_bowtie:
                await _run_bowtie(api,arguments.simulate,mount,csv_cb.write)
                if not arguments.skip_mount:
                    for mount in MOUNT_AXES:
                        await _run_mount_up_down(api,arguments.simulate,mount,csv_cb.write,True)
            if not arguments.skip_hourglass:
                await _run_hour_glass(api,arguments.simulate,mount,csv_cb.write)
                if not arguments.skip_mount:
                    for mount in MOUNT_AXES:
                        await _run_mount_up_down(api,arguments.simulate,mount,csv_cb.write,True)
        
    await api.disengage_axes([types.OT3Axis.X, types.OT3Axis.Y])
    ui.print_title('Test Done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--operator", type=str, required=True)
    parser.add_argument("--sn", type=str, required=True)
    parser.add_argument("--skip_bowtie", action="store_true")
    parser.add_argument("--skip_hourglass", action="store_true")
    parser.add_argument("--skip_mount", action="store_true")
    parser.add_argument("--xy_motion", action="store_true")
    parser.add_argument("--xy_speeds", type=str)
    parser.add_argument("--xy_accelerations", type=str)
    parser.add_argument("--z_motion", action="store_true")
    parser.add_argument("--z_speeds", type=str)
    parser.add_argument("--z_accelerations", type=str)

    args = parser.parse_args()
    asyncio.run(_main(args))
