"""Pipette Capacitance Test."""
import asyncio
import argparse
import string
import time

from opentrons_shared_data.deck import load
from opentrons.hardware_control.ot3api import OT3API
from opentrons.hardware_control.ot3_calibration import (
    calibrate_pipette,
    find_calibration_structure_height,
    _probe_deck_at,
)
from opentrons_shared_data.deck import (
    get_calibration_square_position_in_slot,
)
from hardware_testing import data
from hardware_testing.opentrons_api.types import OT3Mount, OT3Axis, Point, GripperProbe
from hardware_testing.opentrons_api.helpers_ot3 import (
    home_ot3,
    build_async_ot3_hardware_api,
    get_capacitance_ot3,
)
from opentrons.config.types import (
    CapacitivePassSettings,
)
from opentrons_hardware.firmware_bindings.constants import SensorId
from hardware_testing.drivers import mitutoyo_digimatic_indicator

def build_arg_parser():
    arg_parser = argparse.ArgumentParser(description='OT-3 Pipette Capacitance Test')
    arg_parser.add_argument('-m', '--mount', choices=['l','r'], required=False, help='The pipette mount to be tested', default='l')
    arg_parser.add_argument('-c', '--cycles', type=int, required=False, help='Number of testing cycles', default=1)
    arg_parser.add_argument('-o', '--slot', type=int, required=False, help='Deck slot number', default=5)
    arg_parser.add_argument('-x', '--x_increment', type=float, required=False, help='Probe increment size for X-Axis', default=0.5)
    arg_parser.add_argument('-z', '--z_increment', type=float, required=False, help='Probe increment size for Z-Axis', default=0.01)
    arg_parser.add_argument('-d', '--x_steps', type=int, required=False, help='Number of steps for X-Axis', default=10)
    arg_parser.add_argument('-t', '--z_steps', type=int, required=False, help='Number of steps for Z-Axis', default=200)
    arg_parser.add_argument('-s', '--simulate', action="store_true", required=False, help='Simulate this test script')
    return arg_parser

class Pipette_Capacitance_Test:
    def __init__(
        self, simulate: bool, cycles: int, slot: int, x_increment: float, z_increment: float, x_steps: int, z_steps: int, probe_type: int, edge_mode: int, zero_mode: int
    ) -> None:
        self.simulate = simulate
        self.cycles = cycles
        self.slot = slot
        self.x_increment = x_increment
        self.z_increment = z_increment
        self.x_steps = x_steps
        self.z_steps = z_steps
        self.probe_type = probe_type
        self.edge_mode = edge_mode
        self.zero_mode = zero_mode
        self.api = None
        self.mount = None
        self.home = None
        self.pipette_id = None
        self.deck_definition = None
        self.deck_height = None
        self.edge = None
        self.sensor_id = SensorId.S0
        self.jog_step_forward = 0.1
        self.jog_step_backward = -0.01
        self.jog_speed = 10 # mm/s
        self.START_HEIGHT = 3 # mm
        self.PROBE_DIA = 4 # mm
        self.CUTOUT_SIZE = 20 # mm
        self.CUTOUT_HALF = self.CUTOUT_SIZE / 2
        self.axes = [OT3Axis.X, OT3Axis.Y, OT3Axis.Z_L, OT3Axis.Z_R]
        self.PROBE_SETTINGS_Z_AXIS = CapacitivePassSettings(
            prep_distance_mm=5,
            max_overrun_distance_mm=5,
            speed_mm_per_s=1,
            sensor_threshold_pf=1.0,
        )
        self.PROBE_SETTINGS_XY_AXIS = CapacitivePassSettings(
            prep_distance_mm=self.CUTOUT_HALF,
            max_overrun_distance_mm=5,
            speed_mm_per_s=1,
            sensor_threshold_pf=1.0,
        )
        self.test_data ={
            "Time":"None",
            "Cycle":"None",
            "X Step":"None",
            "Z Step":"None",
            "Slot":"None",
            "Pipette":"None",
            "X Gauge":"None",
            "X Zero":"None",
            "Deck Height":"None",
            "Edge Position":"None",
            "Capacitance":"None",
            "Current Position":"None",
        }
        self.gauges = {}
        self.gauge_ports = {
            "X":"/dev/ttyUSB0",
            # "Y":"/dev/ttyUSB1",
            # "Z":"/dev/ttyUSB2",
        }
        self.gauge_offsets = {
            "X":Point(x=5, y=-5, z=9),
            "Y":Point(x=-5, y=-5, z=9),
            "Z":Point(x=0, y=0, z=9),
            # "X":Point(x=5, y=-6, z=7),
            # "Y":Point(x=-6, y=-5, z=7),
            # "Z":Point(x=0, y=0, z=7),
        }
        self.probe_tag = {
            "1":"solid",
            "2":"hole",
        }
        self.edge_tag = {
            "1":"cali",
            "2":"dial",
        }

    async def test_setup(self):
        self.file_setup()
        if self.edge_mode == 2:
            self.gauge_setup()
        self.api = await build_async_ot3_hardware_api(is_simulating=self.simulate, use_defaults=True)
        self.mount = OT3Mount.LEFT if args.mount == "l" else OT3Mount.RIGHT
        self.nominal_center = Point(*get_calibration_square_position_in_slot(self.slot))
        if self.simulate:
            self.pipette_id = "SIMULATION"
        else:
            self.pipette_id = self.api._pipette_handler.get_pipette(self.mount)._pipette_id
        self.test_data["Pipette"] = str(self.pipette_id)
        self.test_data["Slot"] = str(self.slot)
        self.deck_definition = load("ot3_standard", version=3)
        self.start_time = time.time()
        print(f"\nStarting Test on Deck Slot #{self.slot}:\n")

    def file_setup(self):
        class_name = self.__class__.__name__
        probe_tag = self.probe_tag[str(self.probe_type)]
        edge_tag = self.edge_tag[str(self.edge_mode)]
        self.test_name = class_name.lower()
        self.test_tag = f"slot{self.slot}_{probe_tag}_{edge_tag}"
        self.test_header = self.dict_keys_to_line(self.test_data)
        self.test_id = data.create_run_id()
        self.test_path = data.create_folder_for_test_data(self.test_name)
        self.test_file = data.create_file_name(self.test_name, self.test_id, self.test_tag)
        data.append_data_to_file(self.test_name, self.test_file, self.test_header)
        print("FILE PATH = ", self.test_path)
        print("FILE NAME = ", self.test_file)

    def gauge_setup(self):
        for key, value in self.gauge_ports.items():
            self.gauges[key] = mitutoyo_digimatic_indicator.Mitutoyo_Digimatic_Indicator(port=value)
            self.gauges[key].connect()

    def dict_keys_to_line(self, dict):
        return str.join(",", list(dict.keys()))+"\n"

    def dict_values_to_line(self, dict):
        return str.join(",", list(dict.values()))+"\n"

    def _zero_gauges(self):
        if self.zero_mode == 1:
            print(f"\nPlace Gauge Block on Deck Slot #{self.slot}")
            for axis in self.gauges:
                gauge_zero = "{} Zero".format(axis)
                input(f"\nPush block against {axis}-axis Gauge and Press ENTER\n")
                _reading = True
                while _reading:
                    zeros = []
                    for i in range(5):
                        gauge = self.gauges[axis].read_stable(timeout=20)
                        zeros.append(gauge)
                    _variance = abs(max(zeros) - min(zeros))
                    print(f"Variance = {_variance}")
                    if _variance < 0.1:
                        _reading = False
                zero = sum(zeros) / len(zeros)
                self.test_data[gauge_zero] = str(zero)
                print(f"{axis} Gauge Zero = {zero}mm")
            input(f"\nRemove Gauge Block from Deck Slot #{self.slot} and Press ENTER\n")
        elif self.zero_mode == 2:
            for axis in self.gauges:
                zero = input(f"\nType value for {axis}-axis Gauge and Press ENTER\n")
                gauge_zero = "{} Zero".format(axis)
                self.test_data[gauge_zero] = str(zero)
                print(f"{axis} Gauge Zero = {zero}mm")

    async def _read_gauge(self, axis, step):
        current_position = await self.api.gantry_position(self.mount)
        if axis == "X":
            jog_position = current_position._replace(x=current_position.x + step)
        elif axis == "Y":
            jog_position = current_position._replace(y=current_position.y - step)
        elif axis == "Z":
            jog_position = self.nominal_center
        # Move to jog position
        await self.api.move_to(self.mount, jog_position, speed=self.jog_speed)
        # Read gauge
        gauge = self.gauges[axis].read_stable(timeout=20)
        return gauge

    async def _probe_axis(
        self, axis: OT3Axis, target: float
    ) -> float:
        if axis == OT3Axis.by_mount(self.mount):
            settings = self.PROBE_SETTINGS_Z_AXIS
        else:
            settings = self.PROBE_SETTINGS_XY_AXIS
        point = await self.api.capacitive_probe(
            self.mount, axis, target, settings
        )
        return point

    async def _record_data(self, cycle):
        elapsed_time = (time.time() - self.start_time)/60
        self.test_data["Time"] = str(round(elapsed_time, 3))
        self.test_data["Cycle"] = str(cycle)
        test_data = self.dict_values_to_line(self.test_data)
        data.append_data_to_file(self.test_name, self.test_file, test_data)

    async def _get_stable_capacitance(self, sensor_id) -> float:
        _reading = True
        _try = 1
        while _reading:
            capacitance = []
            for i in range(10):
                if self.simulate:
                    data = 0.0
                else:
                    data = await get_capacitance_ot3(self.api, self.mount, sensor_id)
                capacitance.append(data)
            _variance = round(abs(max(capacitance) - min(capacitance)), 5)
            print(f"Try #{_try} Variance = {_variance}")
            _try += 1
            if _variance < 0.1:
                _reading = False
        return sum(capacitance) / len(capacitance)

    async def _update_position(
        self, api: OT3API, mount: OT3Mount, x_step: int
    ) -> None:
        # Move to next position
        current_position = await api.gantry_position(mount)
        if x_step > 1:
            x_position = current_position.x + self.x_increment
        else:
            x_position = current_position.x
        next_position = current_position._replace(x=x_position, z=self.START_HEIGHT)
        await api.move_to(mount, next_position, speed=1)

    async def _record_capacitance(
        self, api: OT3API, mount: OT3Mount, sensor_id: SensorId, x_step: int, z_step: int, deck_height: float
    ) -> None:
        # Move to next height
        current_position = await api.gantry_position(mount)
        next_height = current_position._replace(z=deck_height + self.z_increment*(z_step - 1))
        await api.move_to(mount, next_height, speed=1)

        # Get current position
        current_position = await api.gantry_position(mount)
        self.test_data["Current Position"] = str(current_position).replace(", ",";")
        print(f"Current Position = {current_position}")

        # Read capacitance
        capacitance = await self._get_stable_capacitance(sensor_id)
        print(f"Capacitance = {capacitance}")
        self.test_data["Capacitance"] = str(capacitance)

    async def _measure_capacitance(
        self, api: OT3API, mount: OT3Mount, slot: int, cycle: int
    ) -> None:
        await api.add_tip(mount, api.config.calibration.probe_length)
        edge_position = self.edge._replace(z=self.deck_height)
        await api.move_to(mount, edge_position)
        for i in range(self.x_steps):
            x_step = i + 1
            self.test_data["X Step"] = str(x_step)
            print(f"\n-->> Measuring X Step {x_step}/{self.x_steps}")
            await self._update_position(self.api, self.mount, x_step)
            for j in range(self.z_steps):
                z_step = j + 1
                self.test_data["Z Step"] = str(z_step)
                print(f"\n--->>> Measuring Z Step {z_step}/{self.z_steps} (X Step {x_step}/{self.x_steps})")
                await self._record_capacitance(self.api, self.mount, self.sensor_id, x_step, z_step, self.deck_height)
                await self._record_data(cycle)
        current_position = await api.gantry_position(mount)
        home_z = current_position._replace(z=self.home.z)
        await api.move_to(mount, home_z)
        await api.remove_tip(mount)

    async def _calibrate_edge(
        self, api: OT3API, mount: OT3Mount, nominal_center: Point, deck_height: float
    ) -> None:
        # Move inside the cutout
        nominal_center = nominal_center._replace(y=nominal_center.y - 5)
        below_z = deck_height - 2
        current_position = await api.gantry_position(mount)
        slot_center_above = nominal_center._replace(z=current_position.z)
        slot_center_below = nominal_center._replace(z=below_z)
        await api.move_to(mount, slot_center_above, speed=20)
        await api.move_to(mount, slot_center_below, speed=20)

        # Probe slot X-Axis right edge
        x_right = await self._probe_axis(OT3Axis.X, nominal_center.x + self.CUTOUT_HALF)

        # Return edge position
        current_position = await api.gantry_position(mount)
        edge_position = current_position._replace(x=x_right,y=current_position.y + 5)
        return edge_position

    async def _measure_edge(
        self, api: OT3API, mount: OT3Mount, nominal_center: Point, axis: str
    ) -> None:
        # Move up
        current_pos = await api.gantry_position(mount)
        z_offset = current_pos + self.gauge_offsets["Z"]
        await api.move_to(mount, z_offset, speed=10)
        # Move above slot center
        above_slot_center = nominal_center + self.gauge_offsets["Z"]
        await api.move_to(mount, above_slot_center, speed=10)
        # Move to gauge position
        gauge_position = self.nominal_center + self.gauge_offsets[axis]
        await self.api.move_to(self.mount, gauge_position, speed=10)
        print("Measuring X Gauge...")
        # Read gauge
        gauge_value = 0
        while gauge_value < float(self.test_data[f"{axis} Zero"]):
            gauge_value = await self._read_gauge(axis, self.jog_step_forward)
        while gauge_value > float(self.test_data[f"{axis} Zero"]):
            gauge_value = await self._read_gauge(axis, self.jog_step_backward)
        self.test_data[f"{axis} Gauge"] = str(gauge_value)
        print(f"{axis} Gauge = ", self.test_data[f"{axis} Gauge"])
        # Get edge position
        current_position = await api.gantry_position(mount)
        edge_position = current_position._replace(y=current_position.y + 9, z=self.deck_height)
        # Move above slot center
        await self.api.move_to(self.mount, above_slot_center, speed=10)
        # Move to edge position
        await self.api.move_to(self.mount, edge_position, speed=10)
        input("\nRight Edge found! Press ENTER to start probing:")
        return edge_position

    async def _calibrate_probe(
        self, api: OT3API, mount: OT3Mount, slot: int, nominal_center: Point
    ) -> None:
        # Calibrate pipette
        await api.add_tip(mount, api.config.calibration.probe_length)
        home = await api.gantry_position(mount)
        self.deck_height = await find_calibration_structure_height(api, mount, nominal_center)
        self.test_data["Deck Height"] = str(self.deck_height)
        print(f"Deck Height: {self.deck_height}")
        if self.edge_mode == 1:
            self.edge = await self._calibrate_edge(api, mount, nominal_center, self.deck_height)
        elif self.edge_mode == 2:
            self.edge = await self._measure_edge(api, mount, nominal_center, "X")
        self.test_data[f"Edge Position"] = str(self.edge).replace(", ",";")
        print(f"Edge Position: {self.edge}")
        current_position = await api.gantry_position(mount)
        home_z = current_position._replace(z=home.z)
        await api.move_to(mount, home_z)
        await api.remove_tip(mount)

    async def _home(
        self, api: OT3API, mount: OT3Mount
    ) -> None:
        # Home grantry
        await api.home(self.axes)
        self.home = await api.gantry_position(mount)

    async def _reset(
        self, api: OT3API, mount: OT3Mount
    ) -> None:
        # Home Z-Axis
        current_position = await api.gantry_position(mount)
        home_z = current_position._replace(z=self.home.z)
        await api.move_to(mount, home_z)
        # Move next to XY home
        await api.move_to(mount, self.home + Point(x=-5, y=-5, z=0))

    async def exit(self):
        if self.api:
            await self.api.disengage_axes(self.axes)

    async def run(self) -> None:
        try:
            await self.test_setup()
            if self.api and self.mount:
                if self.edge_mode == 2:
                    if len(self.gauges) > 0:
                        self._zero_gauges()
                input(f"\nAdd Calibration Tip to pipette, then press ENTER:")
                for i in range(self.cycles):
                    cycle = i + 1
                    print(f"\n-> Starting Test Cycle {cycle}/{self.cycles}")
                    await self._home(self.api, self.mount)
                    await self._calibrate_probe(self.api, self.mount, self.slot, self.nominal_center)
                    await self._measure_capacitance(self.api, self.mount, self.slot, cycle)
                    await self._reset(self.api, self.mount)
        except Exception as e:
            await self.exit()
            raise e
        except KeyboardInterrupt:
            await self.exit()
            print("Test Cancelled!")
        finally:
            await self.exit()
            print("Test Completed!")

if __name__ == '__main__':
    print("\nOT-3 Pipette Capacitance Test\n")
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args()
    probe_type = int(input("Choose Probe Type: [Default = 1]\n 1. Solid\n 2. Hole\n") or "1")
    edge_mode = int(input("Choose Find Edge Mode: [Default = 1]\n 1. Calibration\n 2. Dial Indicator\n") or "1")
    zero_mode = int(input("Dial Zero Mode: [Default = 1]\n 1. Auto\n 2. Manual\n") or "1")

    if probe_type == 1:
        print("Probe Type = Solid")
    elif probe_type == 2:
        print("Probe Type = Hole")
    if edge_mode == 1:
        print("Find Edge = Calibration")
    elif edge_mode == 2:
        print("Find Edge = Dial Indicator")
    if zero_mode == 1:
        print("Dial Zero = Auto")
    elif zero_mode == 2:
        print("Dial Zero = Manual")

    test = Pipette_Capacitance_Test(args.simulate, args.cycles, args.slot, args.x_increment, args.z_increment, args.x_steps, args.z_steps, probe_type, edge_mode, zero_mode)
    asyncio.run(test.run())
