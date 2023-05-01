import {
  ALIGN_CENTER,
  DIRECTION_COLUMN,
  Flex,
  JUSTIFY_CENTER,
  JUSTIFY_SPACE_BETWEEN,
  SPACING,
} from '@opentrons/components'
import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { BackButton } from '../../atoms/buttons'
import { ContinueButton } from '../ProtocolSetupModules'
import { MediumButton } from '../../atoms/buttons/OnDeviceDisplay'
import { LabwarePositionCheck } from '../LabwarePositionCheck'

import type { SetupScreens } from '../../pages/OnDeviceDisplay/ProtocolSetup'

export interface ProtocolSetupLabwarePositionCheckProps {
  runId: string
  setSetupScreen: React.Dispatch<React.SetStateAction<SetupScreens>>
}

export function ProtocolSetupLabwarePositionCheck({
  runId,
  setSetupScreen,
}: ProtocolSetupLabwarePositionCheckProps): JSX.Element {
  const { t } = useTranslation('protocol_setup')

  const [
    showLabwarePositionCheck,
    setShowLabwarePositionCheck,
  ] = React.useState(false)
  const handleLaunchLPC = (): void => {
    setShowLabwarePositionCheck(true)
  }

  return showLabwarePositionCheck ? (
    <LabwarePositionCheck
      onCloseClick={() => setShowLabwarePositionCheck(false)}
      runId={runId}
    />
  ) : (
    <Flex
      flexDirection={DIRECTION_COLUMN}
      width="100%"
      gridGap={SPACING.spacing3}
    >
      <Flex justifyContent={JUSTIFY_SPACE_BETWEEN} alignItems={ALIGN_CENTER}>
        <BackButton onClick={() => setSetupScreen('labware')}>
          {t('labware_position_check')}
        </BackButton>
        <Flex gridGap={SPACING.spacingXXL}>
          <ContinueButton onClick={() => setSetupScreen('liquids')} />
        </Flex>
      </Flex>
      <Flex
        height="20rem"
        width="100%"
        alignItems={ALIGN_CENTER}
        justifyContent={JUSTIFY_CENTER}
      >
        <MediumButton
          onClick={handleLaunchLPC}
          buttonType="secondary"
          buttonText="Start Labware Position Check"
        />
      </Flex>
      {showLabwarePositionCheck && (
        <LabwarePositionCheck
          onCloseClick={() => setShowLabwarePositionCheck(false)}
          runId={runId}
        />
      )}
    </Flex>
  )
}
