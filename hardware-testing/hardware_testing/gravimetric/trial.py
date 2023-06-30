"""Dataclass that describes the arguments for trials."""
from dataclasses import dataclass
from typing import List, Optional, Union, Dict
from . import config
from opentrons.protocol_api import ProtocolContext, InstrumentContext, Well, Labware
from .measurement.record import GravimetricRecorder
from .measurement import DELAY_FOR_MEASUREMENT
from .liquid_height.height import LiquidTracker
from hardware_testing.data.csv_report import CSVReport
from hardware_testing.opentrons_api.types import Point
from .helpers import _get_channel_offset
from . import report

QC_VOLUMES_G = {
    1: {
        50: {  # P50
            50: [1, 50],  # T50
        },
        1000: {  # P1000
            50: [5],  # T50
            200: [],  # T200
            1000: [1000],  # T1000
        },
    },
    8: {
        50: {  # P50
            50: [1, 50],  # T50
        },
        1000: {  # P1000
            50: [5],  # T50
            200: [],  # T200
            1000: [1000],  # T1000
        },
    },
    96: {
        1000: {  # P1000
            50: [5],  # T50
            200: [200],  # T200
            1000: [1000],  # T1000
        },
    },
}


QC_VOLUMES_EXTRA_G = {
    1: {
        50: {  # P50
            50: [1, 10, 50],  # T50
        },
        1000: {  # P1000
            50: [5],  # T50
            200: [50, 200],  # T200
            1000: [1000],  # T1000
        },
    },
    8: {
        50: {  # P50
            50: [1, 10, 50],  # T50
        },
        1000: {  # P1000
            50: [5],  # T50
            200: [50, 200],  # T200
            1000: [1000],  # T1000
        },
    },
    96: {
        1000: {  # P1000
            50: [5],  # T50
            200: [200],  # T200
            1000: [1000],  # T1000
        },
    },
}

QC_VOLUMES_P = {
    96: {
        1000: {  # P1000
            50: [5],  # T50
            200: [],  # T200
            1000: [200],  # T1000
        },
    },
}


@dataclass
class GravimetricTrial:
    """All the arguments for a single gravimetric trial."""

    ctx: ProtocolContext
    pipette: InstrumentContext
    well: Well
    channel_offset: Point
    tip_volume: int
    volume: float
    channel: int
    channel_count: int
    trial: int
    recorder: GravimetricRecorder
    test_report: CSVReport
    liquid_tracker: LiquidTracker
    blank: bool
    inspect: bool
    mix: bool = False
    stable: bool = True
    scale_delay: int = DELAY_FOR_MEASUREMENT
    measure_height: float = 50
    acceptable_cv: Optional[float] = None


@dataclass
class PhotometricTrial:
    """All the arguments for a single photometric trial."""

    ctx: ProtocolContext
    test_report: CSVReport
    pipette: InstrumentContext
    source: Well
    dest: Labware
    channel_offset: Point
    tip_volume: int
    volume: float
    trial: int
    liquid_tracker: LiquidTracker
    blank: bool
    inspect: bool
    do_jog: bool
    cfg: config.PhotometricConfig
    mix: bool = False
    stable: bool = True
    acceptable_cv: Optional[float] = None


@dataclass
class TrialOrder:
    """A list of all of the trials that a particular QC run needs to run."""

    trials: List[Union[GravimetricTrial, PhotometricTrial]]


def build_gravimetric_trials(
    ctx: ProtocolContext,
    instr: InstrumentContext,
    cfg: config.GravimetricConfig,
    well: Well,
    test_volumes: List[float],
    channels_to_test: List[int],
    recorder: GravimetricRecorder,
    test_report: report.CSVReport,
    liquid_tracker: LiquidTracker,
    blank: bool,
) -> Dict[float, Dict[int, List[GravimetricTrial]]]:
    """Build a list of all the trials that will be run."""
    trial_list: Dict[float, Dict[int, List[GravimetricTrial]]] = {}
    if len(channels_to_test) > 1:
        num_channels_per_transfer = 1
    else:
        num_channels_per_transfer = cfg.pipette_channels
    if blank:
        trial_list[test_volumes[-1]] = {0: []}
        for trial in range(config.NUM_BLANK_TRIALS):
            trial_list[test_volumes[-1]][0].append(
                GravimetricTrial(
                    ctx=ctx,
                    pipette=instr,
                    well=well,
                    channel_offset=Point(),
                    tip_volume=cfg.tip_volume,
                    volume=test_volumes[-1],
                    channel=0,
                    channel_count=num_channels_per_transfer,
                    trial=trial,
                    recorder=recorder,
                    test_report=test_report,
                    liquid_tracker=liquid_tracker,
                    blank=blank,
                    inspect=cfg.inspect,
                    mix=cfg.mix,
                    stable=False,
                    scale_delay=cfg.scale_delay,
                )
            )
    else:
        for volume in test_volumes:
            for channel in channels_to_test:
                if cfg.isolate_channels and (channel + 1) not in cfg.isolate_channels:
                    print(f"skipping channel {channel + 1}")
                    continue
                trial_list[volume] = {channel: []}
                channel_offset = _get_channel_offset(cfg, channel)
                for trial in range(cfg.trials):
                    trial_list[volume][channel].append(
                        GravimetricTrial(
                            ctx=ctx,
                            pipette=instr,
                            well=well,
                            channel_offset=channel_offset,
                            tip_volume=cfg.tip_volume,
                            volume=volume,
                            channel=channel,
                            channel_count=num_channels_per_transfer,
                            trial=trial,
                            recorder=recorder,
                            test_report=test_report,
                            liquid_tracker=liquid_tracker,
                            blank=blank,
                            inspect=cfg.inspect,
                            mix=cfg.mix,
                            stable=True,
                            scale_delay=cfg.scale_delay,
                        )
                    )
    return trial_list
