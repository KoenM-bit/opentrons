"""Chicken Test 96ch."""
from opentrons.protocol_api import protocol_context

metadata = {"protocolName": "chicken-test-96ch"}
requirements = {"robotType": "Flex", "apiLevel": "2.20"}

TIP_LOCATION = "A1"


def run(ctx: protocol_context.ProtocolContext) -> None:
    pipette = ctx.load_instrument(
        instrument_name="flex_96channel_1000",
        mount="left"
    )
    tip_rack = ctx.load_labware(
        load_name="opentrons_flex_96_tiprack_200ul",
        location="A1",
        adapter="opentrons_flex_96_tiprack_adapter"
    )

    # hover a safe distance above tip-rack
    tip = tip_rack[TIP_LOCATION]
    pipette.move_to(tip.top(100))

    ctx.pause("prepare the chicken...")
    pipette.pick_up_tip(tip)

    # if somehow we haven't stalled, retract back up to a safe distance
    pipette.move_to(tip.top(20))
