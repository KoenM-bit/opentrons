import { useTranslation } from 'react-i18next'
import type { RecoveryContentProps } from '../types'
import { RECOVERY_MAP } from '../constants'
import { TwoColTextAndFailedStepNextStep } from '../shared'
import { RetryStep } from './RetryStep'
import { ManageTips } from './ManageTips'
import { SelectRecoveryOption } from './SelectRecoveryOption'

const { HOME_AND_RETRY } = RECOVERY_MAP
export function HomeAndRetry(props: RecoveryContentProps): JSX.Element {
  const { recoveryMap } = props
  const { route, step } = recoveryMap
  switch (step) {
    case HOME_AND_RETRY.STEPS.PREPARE_DECK_FOR_HOME: {
      return <PrepareDeckForHome {...props} />
    }
    case HOME_AND_RETRY.STEPS.REMOVE_TIPS_FROM_PIPETTE: {
      return <ManageTips {...props} />
    }
    case HOME_AND_RETRY.STEPS.HOME_BEFORE_RETRY: {
      return <HomeGantryBeforeRetry {...props} />
    }
    case HOME_AND_RETRY.STEPS.CONFIRM_RETRY: {
      return <RetryStep {...props} />
    }
    default:
      console.warn(`${step} in ${route} not explicitly handled. Rerouting.}`)
      return <SelectRecoveryOption {...props} />
  }
}

export function PrepareDeckForHome(props: RecoveryContentProps): JSX.Element {
  const { t } = useTranslation('error_recovery')
  const { routeUpdateActions } = props
  const { proceedToRouteAndStep } = routeUpdateActions
  const primaryBtnOnClick = (): Promise<void> =>
    proceedToRouteAndStep(
      RECOVERY_MAP.HOME_AND_RETRY.ROUTE,
      RECOVERY_MAP.HOME_AND_RETRY.STEPS.REMOVE_TIPS_FROM_PIPETTE
    )
  return (
    <TwoColTextAndFailedStepNextStep
      {...props}
      leftColTitle={t('prepare_deck_for_homing')}
      leftColBodyText={t('carefully_move_labware')}
      primaryBtnCopy={t('continue')}
      primaryBtnOnClick={primaryBtnOnClick}
    />
  )
}

export function HomeGantryBeforeRetry(
  props: RecoveryContentProps
): JSX.Element {
  const { t } = useTranslation('error_recovery')
  const { recoveryCommands, routeUpdateActions } = props
  const { homeExceptPlungers } = recoveryCommands
  const { handleMotionRouting, proceedToRouteAndStep } = routeUpdateActions
  const { HOME_AND_RETRY } = RECOVERY_MAP
  const primaryBtnOnClick = (): Promise<void> =>
    handleMotionRouting(true)
      .then(() => homeExceptPlungers())
      .then(() =>
        proceedToRouteAndStep(
          HOME_AND_RETRY.ROUTE,
          HOME_AND_RETRY.STEPS.CONFIRM_RETRY
        )
      )
      .then(() => handleMotionRouting(false))
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
