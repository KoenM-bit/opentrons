import { DndProvider } from 'react-dnd'
import { HashRouter } from 'react-router-dom'
import { HTML5Backend } from 'react-dnd-html5-backend'
import { DIRECTION_COLUMN, Flex, OVERFLOW_AUTO } from '@opentrons/components'

import { ProtocolRoutes } from './ProtocolRoutes'
import { useScreenSizeCheck } from './resources/useScreenSizeCheck'
import { PortalRoot, DisabledScreen } from './organisms'

function ProtocolEditorComponent(): JSX.Element {
  const isValidSize = useScreenSizeCheck()
  return (
    <div
      id="protocol-editor"
      style={{ width: '100%', height: '100vh', overflow: OVERFLOW_AUTO }}
    >
      <PortalRoot />
      <Flex flexDirection={DIRECTION_COLUMN}>
        {!isValidSize && <DisabledScreen />}
        <HashRouter>
          <ProtocolRoutes />
        </HashRouter>
      </Flex>
    </div>
  )
}

export const ProtocolEditor = (): JSX.Element => (
  <DndProvider backend={HTML5Backend}>
    <ProtocolEditorComponent />
  </DndProvider>
)
