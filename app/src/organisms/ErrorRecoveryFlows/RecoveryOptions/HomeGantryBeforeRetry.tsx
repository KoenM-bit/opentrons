import { useTranslation } from 'react-i18next'
import type { RecoveryContentProps } from '../types'

import { TwoColTextAndFailedStepNextStep } from '../shared'

export function HomeGantryBeforeRetry(
  props: RecoveryContentProps
): JSX.Element {
  const { t } = useTranslation('error_recovery')
  const primaryBtnOnClick = (): Promise<void> => {}
  return (
    <TwoColTextAndFailedStepNextStep
      {...props}
      leftColTitle={t('home_gantry')}
      leftColBodyText={t('take_necessary_actions_home')}
      primaryBtnCopy={t('home_now')}
      primaryBtnOnClick={primaryBtnOnClick}
    />
  )
}
