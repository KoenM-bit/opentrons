import * as React from 'react'
import without from 'lodash/without'

import {
  getAllLabwareDefs,
  getLabwareDisplayName,
  getLoadedLabwareDefinitionsByUri,
} from '@opentrons/shared-data'

import type { WellGroup } from '@opentrons/components'
import type { CommandsData, Run } from '@opentrons/api-client'
import type {
  LabwareDefinition2,
  LoadedLabware,
  PickUpTipRunTimeCommand,
} from '@opentrons/shared-data'
import type { ErrorRecoveryFlowsProps } from '..'

interface UseFailedLabwareUtilsProps {
  failedCommand: ErrorRecoveryFlowsProps['failedCommand']
  protocolAnalysis: ErrorRecoveryFlowsProps['protocolAnalysis']
  runCommands?: CommandsData
  runRecord?: Run
}

export type UseFailedLabwareUtilsResult = UseTipSelectionUtilsResult & {
  pickUpTipLabwareName: string | null
  pickUpTipLabware: LoadedLabware | null
}

// Utils for labware relating to the failedCommand.
export function useFailedLabwareUtils({
  failedCommand,
  runCommands,
  runRecord,
  protocolAnalysis,
}: UseFailedLabwareUtilsProps): UseFailedLabwareUtilsResult {
  const recentRelevantPickUpTipCmd = React.useMemo(
    () => getRecentRelevantPickUpTipCommand(failedCommand, runCommands),
    [failedCommand, runCommands]
  )
  const tipSelectionUtils = useTipSelectionUtils(recentRelevantPickUpTipCmd)

  const pickUpTipLabwareName = React.useMemo(
    () =>
      getPickUpTipLabwareName(
        protocolAnalysis,
        recentRelevantPickUpTipCmd,
        runRecord
      ),
    [protocolAnalysis, recentRelevantPickUpTipCmd, runRecord]
  )

  const pickUpTipLabware = React.useMemo(
    () => getPickUpTipLabware(recentRelevantPickUpTipCmd, runRecord),
    [recentRelevantPickUpTipCmd, runRecord]
  )

  return {
    ...tipSelectionUtils,
    pickUpTipLabwareName,
    pickUpTipLabware,
  }
}

// Returns the most recent pickUpTip command for the pipette used in the failed command, if any.
function getRecentRelevantPickUpTipCommand(
  failedCommand: ErrorRecoveryFlowsProps['failedCommand'],
  runCommands?: CommandsData
): Omit<PickUpTipRunTimeCommand, 'result'> | undefined {
  if (
    failedCommand != null &&
    runCommands != null &&
    'wellName' in failedCommand.params &&
    'pipetteId' in failedCommand.params
  ) {
    const failedCmdPipetteId = failedCommand.params.pipetteId

    // Reverse iteration is faster as long as # recovery commands < # run commands.
    const failedCommandIdx = runCommands.data.findLastIndex(
      command => command.key === failedCommand.key
    )

    const recentPickUpTipCmd = runCommands.data
      .slice(0, failedCommandIdx)
      .findLast(
        command =>
          command.commandType === 'pickUpTip' &&
          command.params.pipetteId === failedCmdPipetteId
      )

    return recentPickUpTipCmd as Omit<PickUpTipRunTimeCommand, 'result'>
  }
}

interface UseTipSelectionUtilsResult {
  selectedTipLocations: WellGroup | null
  tipSelectorDef: LabwareDefinition2
  selectTips: (tipGroup: WellGroup) => void
  deselectTips: (locations: string[]) => void
}

// Utils for initializing and interacting with the Tip Selector component.
function useTipSelectionUtils(
  recentRelevantPickUpTipCmd?: Omit<PickUpTipRunTimeCommand, 'result'>
): UseTipSelectionUtilsResult {
  const [selectedLocs, setSelectedLocs] = React.useState<WellGroup | null>(null)

  const initialLocs = useInitialSelectedLocationsFrom(
    recentRelevantPickUpTipCmd
  )
  // Set the initial locs when they first become available.
  if (selectedLocs == null && initialLocs != null) {
    setSelectedLocs(initialLocs)
  }

  const deselectTips = (locations: string[]): void => {
    setSelectedLocs(prevLocs =>
      without(Object.keys(prevLocs as WellGroup), ...locations).reduce(
        (acc, well) => {
          return { ...acc, [well]: null }
        },
        {}
      )
    )
  }

  const selectTips = (tipGroup: WellGroup): void => {
    setSelectedLocs(() => ({ ...tipGroup }))
  }

  // Use this labware to represent all tip racks for manual tip selection.
  const tipSelectorDef = React.useMemo(
    () => getAllLabwareDefs().thermoscientificnunc96Wellplate1300UlV1,
    []
  )

  return {
    selectedTipLocations: selectedLocs,
    tipSelectorDef,
    selectTips,
    deselectTips,
  }
}

// Set the initial well selection to be the last pickup tip location for the pipette used in the failed command.
function useInitialSelectedLocationsFrom(
  recentRelevantPickUpTipCmd?: Omit<PickUpTipRunTimeCommand, 'result'>
): WellGroup | null {
  const [initialWells, setInitialWells] = React.useState<WellGroup | null>(null)

  if (recentRelevantPickUpTipCmd != null && initialWells == null) {
    setInitialWells({ [recentRelevantPickUpTipCmd.params.wellName]: null })
  }

  return initialWells
}

// TODO(jh 06-12-24): See EXEC-525.
// Get the name of the latest labware used by the failed command's pipette to pick up tips, if any.
function getPickUpTipLabwareName(
  protocolAnalysis: ErrorRecoveryFlowsProps['protocolAnalysis'],
  recentRelevantPickUpTipCmd?: Omit<PickUpTipRunTimeCommand, 'result'>,
  runRecord?: Run
): string | null {
  const lwDefsByURI = getLoadedLabwareDefinitionsByUri(
    protocolAnalysis?.commands ?? []
  )
  const pickUpTipLWURI = runRecord?.data.labware.find(
    labware => labware.id === recentRelevantPickUpTipCmd?.params.labwareId
  )?.definitionUri

  if (pickUpTipLWURI != null) {
    return getLabwareDisplayName(lwDefsByURI[pickUpTipLWURI])
  } else {
    return null
  }
}

// Get the latest labware used by the failed command's pipette to pick up tips, if any.
function getPickUpTipLabware(
  recentRelevantPickUpTipCmd?: Omit<PickUpTipRunTimeCommand, 'result'>,
  runRecord?: Run
): LoadedLabware | null {
  return (
    runRecord?.data.labware.find(
      lw => lw.id === recentRelevantPickUpTipCmd?.params.labwareId
    ) ?? null
  )
}
