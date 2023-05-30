import * as React from 'react'
import cx from 'classnames'
import { DragDropContext } from 'react-dnd'
import MouseBackEnd from 'react-dnd-mouse-backend'
import { ComputingSpinner } from '../components/ComputingSpinner'
import { ConnectedNav } from '../containers/ConnectedNav'
import { ConnectedSidebar } from '../containers/ConnectedSidebar'
import { ConnectedTitleBar } from '../containers/ConnectedTitleBar'
import { ConnectedMainPanel } from '../containers/ConnectedMainPanel'
import { PortalRoot as MainPageModalPortalRoot } from '../components/portals/MainPageModalPortal'
import { MAIN_CONTENT_FORCED_SCROLL_CLASSNAME } from '../ui/steps/utils'
import { PrereleaseModeIndicator } from './PrereleaseModeIndicator'
import { PortalRoot as TopPortalRoot } from './portals/TopPortal'
import { NewFileModal } from './modals/NewFileModal'
import { FileUploadMessageModal } from './modals/FileUploadMessageModal'
import { LabwareUploadMessageModal } from './modals/LabwareUploadMessageModal'
import { GateModal } from './modals/GateModal'
import { AnnouncementModal } from './modals/AnnouncementModal'
import styles from './ProtocolEditor.css'
import { connect } from 'react-redux'
import { selectors } from '../navigation'
import { BaseState } from '../types'
import { RobotDataFields, selectors as fileSelectors } from '../file-data'
import {
  OT2_STANDARD_DECKID,
  OT3_STANDARD_DECKID,
} from '@opentrons/shared-data'

const showGateModal =
  process.env.NODE_ENV === 'production' || process.env.OT_PD_SHOW_GATE
export interface Props {
  children?: React.ReactNode
  page: string
  robot: RobotDataFields
}

function ProtocolEditorComponent(props: Props): JSX.Element {
  const {
    page,
    robot: { deckId },
  } = props
  const conditionalStyle =
    deckId === OT2_STANDARD_DECKID && page === 'file-detail'
      ? cx(styles.main_page_content, MAIN_CONTENT_FORCED_SCROLL_CLASSNAME)
      : cx(styles.flex_main_page_content, MAIN_CONTENT_FORCED_SCROLL_CLASSNAME)
  const notLandingPage = page !== 'landing-page'
  return (
    <div>
      <ComputingSpinner />
      <TopPortalRoot />
      {showGateModal ? <GateModal /> : null}
      <PrereleaseModeIndicator />
      <div className={styles.wrapper}>
        {notLandingPage && (
          <>
            <ConnectedNav />
            {deckId === OT3_STANDARD_DECKID && page !== 'file-detail' && (
              <ConnectedSidebar />
            )}
            {deckId === OT2_STANDARD_DECKID && <ConnectedSidebar />}
          </>
        )}

        <div className={styles.main_page_wrapper}>
          {notLandingPage && <ConnectedTitleBar />}

          <div id="main-page" className={conditionalStyle}>
            <AnnouncementModal />
            <NewFileModal showProtocolFields />
            <FileUploadMessageModal />
            <MainPageModalPortalRoot />
            <LabwareUploadMessageModal />
            <ConnectedMainPanel />
          </div>
        </div>
      </div>
    </div>
  )
}

function mapStateToProps(state: BaseState): Props {
  return {
    page: selectors.getCurrentPage(state),
    robot: fileSelectors.protocolRobotModelName(state),
  }
}

export const ProtocolEditorOne = DragDropContext(MouseBackEnd)(
  ProtocolEditorComponent
)

export const ProtocolEditor = connect(mapStateToProps)(ProtocolEditorOne)
