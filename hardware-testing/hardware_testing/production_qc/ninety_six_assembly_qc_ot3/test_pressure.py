"""Test Pressure."""
from asyncio import sleep
from hardware_testing.drivers.sealed_pressure_fixture import (
    SerialDriver as SealedPressureDriver,
)
from hardware_testing.opentrons_api import helpers_ot3
from typing import List, Union, Literal

from opentrons_hardware.firmware_bindings.constants import SensorId

from opentrons.hardware_control.ot3api import OT3API
from opentrons.hardware_control.backends.ot3utils import sensor_id_for_instrument
from opentrons.hardware_control.types import InstrumentProbeType

from opentrons.hardware_control.motion_utilities import target_position_from_relative

from hardware_testing.data import ui
from hardware_testing.opentrons_api import helpers_ot3
from hardware_testing.opentrons_api.types import OT3Mount, Point, Axis
from hardware_testing.data.csv_report import (
    CSVReport,
    CSVResult,
    CSVLine,
    CSVLineRepeating,
)

USE_SEALED_FIXTURE = False
USE_SEALED_BLOCK = True
PRIMARY_SEALED_PRESSURE_FIXTURE_POS = (
    Point(362.68, 148.83, 49.4) if USE_SEALED_BLOCK else Point(362.68, 148.83, 44.4)
)  # attached tip
SECOND_SEALED_PRESSURE_FIXTURE_POS = (
    Point(264.71, 212.81, 49.4) if USE_SEALED_BLOCK else Point(264.71, 212.81, 44.4)
)  # attached tip
SET_PRESSURE_TARGET = 100  # read air pressure when the force pressure value is over 100
REACHED_PRESSURE = 0

SECONDS_BETWEEN_READINGS = 0.25
NUM_PRESSURE_READINGS = 10
TIP_VOLUME = 50
ASPIRATE_VOLUME = 2
PRESSURE_READINGS = ["open-pa", "sealed-pa", "aspirate-pa", "dispense-pa"]

SLOT_FOR_PICK_UP_TIP = 5
TIP_RACK_FOR_PICK_UP_TIP = f"opentrons_flex_96_tiprack_{TIP_VOLUME}ul"
A1_OFFSET = Point(x=9 * 11, y=-9 * 7)
H12_OFFSET = Point(x=-9 * 11, y=9 * 7)
OFFSET_FOR_1_WELL_LABWARE = Point(x=9 * -11 * 0.5, y=9 * 7 * 0.5)

THRESHOLDS = {
    "open-pa": (
        -25,
        25,
    ),
    "sealed-pa": (
        -30,
        30,
    ),
    "aspirate-pa": (
        -750,
        -400,
    ),
    "dispense-pa": (
        2500,
        3500,
    ),
}


def _get_test_tag(probe: InstrumentProbeType, reading: str) -> str:
    assert reading in PRESSURE_READINGS, f"{reading} not in PRESSURE_READINGS"
    return f"{probe.name.lower()}-{reading}"


def build_csv_lines() -> List[Union[CSVLine, CSVLineRepeating]]:
    """Build CSV Lines."""
    lines: List[Union[CSVLine, CSVLineRepeating]] = list()
    for p in InstrumentProbeType:
        for r in PRESSURE_READINGS:
            tag = _get_test_tag(p, r)
            if r == "sealed-pa":
                lines.append(CSVLine(tag, [float, CSVResult, float]))
            else:
                lines.append(CSVLine(tag, [float, CSVResult]))
    return lines


async def _read_from_sensor(
    api: OT3API,
    sensor_id: SensorId,
    num_readings: int,
) -> float:
    readings: List[float] = []
    sequential_failures = 0
    while len(readings) != num_readings:
        try:
            r = await helpers_ot3.get_pressure_ot3(api, OT3Mount.LEFT, sensor_id)
            sequential_failures = 0
            readings.append(r)
            print(f"\t{r}")
            if not api.is_simulator:
                await sleep(SECONDS_BETWEEN_READINGS)
        except helpers_ot3.SensorResponseBad as e:
            sequential_failures += 1
            if sequential_failures == 3:
                raise e
            else:
                continue
    return sum(readings) / num_readings


def check_value(test_value: float, test_name: str) -> CSVResult:
    """Determine if value is within pass limits."""
    low_limit = THRESHOLDS[test_name][0]
    high_limit = THRESHOLDS[test_name][1]

    if low_limit < test_value and test_value < high_limit:
        return CSVResult.PASS
    else:
        return CSVResult.FAIL


async def calibrate_to_pressue_fixture(
    api: OT3API, sensor: SealedPressureDriver, fixture_pos: Point
):
    """move to suitable height for readding air pressure"""
    global REACHED_PRESSURE
    await api.move_to(OT3Mount.LEFT, fixture_pos)
    debug_target = input(f"Setting target pressure (default: {SET_PRESSURE_TARGET}g): ")
    if debug_target.strip() == "":
        debug_target = f"{SET_PRESSURE_TARGET}"
    while True:
        force_pressure = sensor.get_pressure()
        # step = -0.06 if abs(float(force_pressure)) > 0.1 else -0.1
        step = -0.06
        print("Force pressure is: ", force_pressure)
        if force_pressure < float(debug_target.strip()):
            await api.move_rel(OT3Mount.LEFT, Point(x=0, y=0, z=step))
            await sleep(3)
        else:
            REACHED_PRESSURE = sensor.get_pressure()
            ui.print_info(f"Reaching force is {REACHED_PRESSURE}, exit calibration.")
            break


async def _partial_pick_up_z_motion(
    api: OT3API, current: float, distance: float, speed: float
) -> None:
    async with api._backend.motor_current(run_currents={Axis.Z_L: current}):
        target_down = target_position_from_relative(
            OT3Mount.LEFT, Point(z=-distance), api._current_position
        )
        await api._move(target_down, speed=speed)
    target_up = target_position_from_relative(
        OT3Mount.LEFT, Point(z=distance), api._current_position
    )
    await api._move(target_up)
    await api._update_position_estimation([Axis.Z_L])


async def _partial_pick_up(api: OT3API, position: Point, current: float) -> None:
    await helpers_ot3.move_to_arched_ot3(
        api,
        OT3Mount.LEFT,
        position,
        safe_height=position.z + 10,
    )
    await _partial_pick_up_z_motion(
        api, current=current, distance=12, speed=3
    )  # change distance and speed, in case collision detected error
    await api.add_tip(OT3Mount.LEFT, helpers_ot3.get_default_tip_length(TIP_VOLUME))
    await api.prepare_for_aspirate(OT3Mount.LEFT)
    await api.home_z(OT3Mount.LEFT)


async def run(
    api: OT3API, report: CSVReport, section: str, pipette: Literal[200, 1000]
) -> None:
    """Run."""
    await api.home_z(OT3Mount.LEFT)
    slot_5 = helpers_ot3.get_slot_calibration_square_position_ot3(5)
    home_pos = await api.gantry_position(OT3Mount.LEFT)
    await api.move_to(OT3Mount.LEFT, slot_5._replace(z=home_pos.z))
    if USE_SEALED_FIXTURE:
        # init driver
        pressure_sensor = SealedPressureDriver()
        pressure_sensor.init(9600)

    # move to slot
    if not api.is_simulator:
        ui.get_user_ready(f"Place tip tack 50ul at slot - {SLOT_FOR_PICK_UP_TIP}")
    # await api.add_tip(OT3Mount.LEFT, helpers_ot3.get_default_tip_length(TIP_VOLUME))

    tip_rack_pos = helpers_ot3.get_theoretical_a1_position(
        SLOT_FOR_PICK_UP_TIP, TIP_RACK_FOR_PICK_UP_TIP
    )
    await helpers_ot3.move_to_arched_ot3(api, OT3Mount.LEFT, tip_rack_pos + Point(z=30))
    await helpers_ot3.jog_mount_ot3(api, OT3Mount.LEFT)
    tip_rack_actual_pos = await api.gantry_position(OT3Mount.LEFT)

    for probe in InstrumentProbeType:
        await helpers_ot3.move_to_arched_ot3(
            api, OT3Mount.LEFT, tip_rack_pos + Point(z=50)
        )
        sensor_id = sensor_id_for_instrument(probe)
        ui.print_header(f"Sensor: {probe}")

        # OPEN-Pa
        open_pa = 0.0
        if not api.is_simulator:
            try:
                open_pa = await _read_from_sensor(api, sensor_id, NUM_PRESSURE_READINGS)
            except helpers_ot3.SensorResponseBad:
                ui.print_error(f"{probe} pressure sensor not working, skipping")
                continue
        print(f"open-pa: {open_pa}")
        open_result = check_value(open_pa, "open-pa")
        report(section, _get_test_tag(probe, "open-pa"), [open_pa, open_result])

        # SEALED-Pa
        sealed_pa = 0.0
        if probe == InstrumentProbeType.PRIMARY:
            offset_pos = A1_OFFSET
            fixture_pos = PRIMARY_SEALED_PRESSURE_FIXTURE_POS
        elif probe == InstrumentProbeType.SECONDARY:
            offset_pos = H12_OFFSET
            fixture_pos = SECOND_SEALED_PRESSURE_FIXTURE_POS
        else:
            raise NameError("offset position miss")

        if not api.is_simulator:
            # ui.get_user_ready(f"attach {TIP_VOLUME} uL TIP to {probe.name} sensor")

            tip_pos = tip_rack_actual_pos + offset_pos
            print(f"Tip pos: {tip_pos}")
            ui.get_user_ready("Pick up tip")
            await _partial_pick_up(api, tip_pos, current=0.1)
            await api.prepare_for_aspirate(OT3Mount.LEFT)
            if not (USE_SEALED_FIXTURE or USE_SEALED_BLOCK):
                ui.get_user_ready("SEAL tip using your FINGER")
            else:
                await helpers_ot3.move_to_arched_ot3(
                    api, OT3Mount.LEFT, fixture_pos._replace(z=fixture_pos.z + 50)
                )
                ui.get_user_ready("Ready for moving to sealed fixture")
                if USE_SEALED_FIXTURE:
                    await calibrate_to_pressue_fixture(
                        api, pressure_sensor, fixture_pos
                    )
                else:
                    await helpers_ot3.move_to_arched_ot3(
                        api, OT3Mount.LEFT, fixture_pos
                    )

            try:
                sealed_pa = await _read_from_sensor(
                    api, sensor_id, NUM_PRESSURE_READINGS
                )
            except helpers_ot3.SensorResponseBad:
                ui.print_error(f"{probe} pressure sensor not working, skipping")
                break
        else:
            await api.add_tip(
                OT3Mount.LEFT, helpers_ot3.get_default_tip_length(TIP_VOLUME)
            )
            await api.prepare_for_aspirate(OT3Mount.LEFT)
        print(f"sealed-pa: {sealed_pa}")
        sealed_result = check_value(sealed_pa, "sealed-pa")
        report(
            section,
            _get_test_tag(probe, "sealed-pa"),
            [sealed_pa, sealed_result, REACHED_PRESSURE],
        )

        # ASPIRATE-Pa
        aspirate_pa = 0.0
        await api.aspirate(OT3Mount.LEFT, ASPIRATE_VOLUME)
        if not api.is_simulator:
            try:
                aspirate_pa = await _read_from_sensor(
                    api, sensor_id, NUM_PRESSURE_READINGS
                )
            except helpers_ot3.SensorResponseBad:
                ui.print_error(f"{probe} pressure sensor not working, skipping")
                break
        print(f"aspirate-pa: {aspirate_pa}")
        aspirate_result = check_value(aspirate_pa, "aspirate-pa")
        report(
            section, _get_test_tag(probe, "aspirate-pa"), [aspirate_pa, aspirate_result]
        )

        # DISPENSE-Pa
        dispense_pa = 0.0
        await api.dispense(OT3Mount.LEFT, ASPIRATE_VOLUME)
        if not api.is_simulator:
            try:
                dispense_pa = await _read_from_sensor(
                    api, sensor_id, NUM_PRESSURE_READINGS
                )
            except helpers_ot3.SensorResponseBad:
                ui.print_error(f"{probe} pressure sensor not working, skipping")
                break
        print(f"dispense-pa: {dispense_pa}")
        dispense_result = check_value(dispense_pa, "dispense-pa")
        report(
            section, _get_test_tag(probe, "dispense-pa"), [dispense_pa, dispense_result]
        )
        if USE_SEALED_FIXTURE or USE_SEALED_BLOCK:
            await helpers_ot3.move_to_arched_ot3(
                api, OT3Mount.LEFT, fixture_pos._replace(z=fixture_pos.z + 50)
            )
        if not api.is_simulator:
            ui.get_user_ready("REMOVE tip")

        trash_nominal = helpers_ot3.get_slot_calibration_square_position_ot3(
            12
        ) + Point(z=40)
        # center the 96ch of the 1-well labware
        trash_nominal += OFFSET_FOR_1_WELL_LABWARE
        await helpers_ot3.move_to_arched_ot3(
            api, OT3Mount.LEFT, trash_nominal + Point(z=20)
        )
        await api.move_to(OT3Mount.LEFT, trash_nominal)
        await api.drop_tip(OT3Mount.LEFT)
        await api.remove_tip(OT3Mount.LEFT)
        await api.home()
