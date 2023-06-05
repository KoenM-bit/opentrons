import * as React from 'react'
import { connect } from 'react-redux'
import { Splash } from '@opentrons/components'
import { START_TERMINAL_ITEM_ID, TerminalItemId } from '../steplist'
import { Portal as MainPageModalPortal } from '../components/portals/MainPageModalPortal'
import { DeckSetupManager } from '../components/DeckSetupManager'
import { ConnectedFilePage } from '../containers/ConnectedFilePage'
import { SettingsPage } from '../components/SettingsPage'
import { LiquidsPage } from '../components/LiquidsPage'
import { Hints } from '../components/Hints'
import { LiquidPlacementModal } from '../components/LiquidPlacementModal'
import { LabwareSelectionModal } from '../components/LabwareSelectionModal'
import { FormManager } from '../components/FormManager'
import { TimelineAlerts } from '../components/alerts/TimelineAlerts'
import { getSelectedTerminalItemId } from '../ui/steps'
import { selectors as labwareIngredSelectors } from '../labware-ingred/selectors'
import { selectors, Page } from '../navigation'
import { BaseState } from '../types'
import { FlexFileDetails } from '../components/FlexProtocolEditor/FlexFileDetails'
import { LandingPageComponent } from '../components/LandingPage'
import { CreateFlexFileForm } from '../components/FlexProtocolEditor'
import { OT3_STANDARD_DECKID } from '@opentrons/shared-data'
import { selectors as fileSelectors, RobotDataFields } from '../file-data'

interface Props {
  page: Page
  selectedTerminalItemId: TerminalItemId | null | undefined
  ingredSelectionMode: boolean
  robot: RobotDataFields
}

function MainPanelComponent(props: Props): JSX.Element {
  const { page, selectedTerminalItemId, ingredSelectionMode, robot } = props
  const fileComponent = robot.deckId ? (
    robot.deckId === OT3_STANDARD_DECKID ? (
      <FlexFileDetails />
    ) : (
      <ConnectedFilePage />
    )
  ) : (
    <></>
  )
  switch (page) {
    case 'file-splash':
      return <Splash />
    case 'file-detail':
      return fileComponent
    case 'liquids':
      return <LiquidsPage />
    case 'landing-page':
      return <LandingPageComponent />
    case 'settings-app':
      return <SettingsPage />
    case 'new-flex-file-form':
      return <CreateFlexFileForm />
    default: {
      const startTerminalItemSelected =
        selectedTerminalItemId === START_TERMINAL_ITEM_ID
      return (
        <>
          <MainPageModalPortal>
            <TimelineAlerts />
            <Hints />
            {startTerminalItemSelected && <LabwareSelectionModal />}
            <FormManager />
            {startTerminalItemSelected && ingredSelectionMode && (
              <LiquidPlacementModal />
            )}
          </MainPageModalPortal>
          <DeckSetupManager />
        </>
      )
    }
  }
}

function mapStateToProps(state: BaseState): Props {
  return {
    page: selectors.getCurrentPage(state),
    selectedTerminalItemId: getSelectedTerminalItemId(state),
    ingredSelectionMode:
      labwareIngredSelectors.getSelectedLabwareId(state) != null,
    robot: fileSelectors.protocolRobotModelName(state),
  }
}

export const ConnectedMainPanel = connect(mapStateToProps)(MainPanelComponent)
