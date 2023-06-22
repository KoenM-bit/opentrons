import {
  LABWARE_MOVE_DELAY_MS,
  LABWARE_MOVE_DURATION_MS,
  LABWARE_MOVE_TO_OFFDECK_DELAY_MS,
  LABWARE_MOVE_TO_OFFDECK_DURATION_MS,
  SPLASH_IN_DELAY_MS,
  SPLASH_IN_DURATION_MS,
  SPLASH_IN_OFFDECK_DELAY_MS,
  SPLASH_OUT_DELAY_MS,
  SPLASH_OUT_DURATION_MS,
} from './animationConstants'

import type {
  MoveLabwareAnimationParams,
  SplashAnimationParams,
} from '@opentrons/components'
import type {
  DeckDefinition,
  MoveLabwareRunTimeCommand,
} from '@opentrons/shared-data'
import type { RunLabwareInfo } from './getCurrentRunLabwareRenderInfo'
import type { RunModuleInfo } from './getCurrentRunModulesRenderInfo'

export interface LabwareAnimationParams {
  movementParams: MoveLabwareAnimationParams
  splashParams: SplashAnimationParams
}

export function getLabwareAnimationParams(
  runLabwareInfo: RunLabwareInfo[],
  runModuleInfo: RunModuleInfo[],
  command: Omit<MoveLabwareRunTimeCommand, 'result'>,
  deckDef: DeckDefinition
): {
  movementParams: MoveLabwareAnimationParams
  splashParams: SplashAnimationParams
} | null {
  const labwareId = command.params.labwareId
  let labwareFromRun:
    | RunLabwareInfo
    | RunModuleInfo
    | undefined = runLabwareInfo.find(l => l.labwareId === labwareId)
  if (labwareFromRun == null) {
    labwareFromRun = runModuleInfo.find(m => m.nestedLabwareId === labwareId)
    if (labwareFromRun == null) {
      return null
    }
  }
  const currentPos = [labwareFromRun.x, labwareFromRun.y]
  let newPos: [number, number] | null = null
  if (command.params?.newLocation === 'offDeck') {
    // we want the labware to slide straight down off the deck
    // so we maintain the x position and set the y to the cornerOffsetFromOrigin y axis value and subtract the labware yDimension to be safe
    const labwareYDimension =
      'labwareDef' in labwareFromRun
        ? labwareFromRun.labwareDef.dimensions.yDimension
        : labwareFromRun.nestedLabwareDef?.dimensions.yDimension ?? 0
    newPos = [
      labwareFromRun.x,
      deckDef.cornerOffsetFromOrigin[1] - labwareYDimension,
    ]
  } else if ('moduleId' in command.params?.newLocation) {
    const destModuleId = command.params.newLocation.moduleId
    const matchedModule = runModuleInfo.find(m => m.moduleId === destModuleId)
    newPos = matchedModule != null ? [matchedModule.x, matchedModule.y] : null
  } else {
    const destSlotName = command.params.newLocation.slotName
    const slotPosition = deckDef.locations.orderedSlots.find(
      slot => slot.id === destSlotName
    )?.position
    if (slotPosition == null) {
      return null
    }
    newPos = [slotPosition[0], slotPosition[1]]
  }

  return newPos != null
    ? {
        movementParams: {
          xMovement: newPos[0] - currentPos[0],
          yMovement: newPos[1] - currentPos[1],
          begin:
            command.params.newLocation === 'offDeck'
              ? `splash-out.end+${LABWARE_MOVE_TO_OFFDECK_DELAY_MS}ms`
              : `${LABWARE_MOVE_DELAY_MS}ms;deck-in.end+0ms`,
          duration:
            command.params.newLocation === 'offDeck'
              ? `${LABWARE_MOVE_TO_OFFDECK_DURATION_MS}ms`
              : `${LABWARE_MOVE_DURATION_MS}ms`,
        },
        splashParams: {
          inParams: {
            begin:
              command.params.newLocation === 'offDeck'
                ? `${SPLASH_IN_OFFDECK_DELAY_MS}ms;deck-in.end+${SPLASH_IN_OFFDECK_DELAY_MS}ms`
                : `labware-move.end+${SPLASH_IN_DELAY_MS}ms`,
            duration: `${SPLASH_IN_DURATION_MS}ms`,
          },
          outParams: {
            begin: `splash-in.end+${SPLASH_OUT_DELAY_MS}ms`,
            duration: `${SPLASH_OUT_DURATION_MS}ms`,
          },
        },
      }
    : null
}
