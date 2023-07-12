import * as React from 'react'
import { useSelector } from 'react-redux'
import {
  ALIGN_CENTER,
  Flex,
  FormGroup,
  SPACING,
  Tooltip,
  TOOLTIP_BOTTOM,
  TOOLTIP_FIXED,
  useHoverTooltip,
} from '@opentrons/components'
import {
  LabwareField,
  LabwareLocationField,
  CheckboxRowField,
} from '../../fields'
import styles from '../../StepEditForm.css'
import { FLEX_ROBOT_TYPE } from '@opentrons/shared-data'
import { getRobotType } from '../../../../file-data/selectors'
import { getAdditionalEquipment } from '../../../../step-forms/selectors'
import type { StepFormProps } from '../../types'
import { useTranslation } from 'react-i18next'

export const MoveLabwareForm = (props: StepFormProps): JSX.Element => {
  const { propsForFields } = props
  const { t } = useTranslation(['form', 'tooltip', 'application'])
  const robotType = useSelector(getRobotType)
  const additionalEquipment = useSelector(getAdditionalEquipment)
  const isGripperAttached = Object.values(additionalEquipment).some(
    equipment => equipment?.name === 'gripper'
  )
  const [targetProps, tooltipProps] = useHoverTooltip({
    placement: TOOLTIP_BOTTOM,
    strategy: TOOLTIP_FIXED,
  })

  return (
    <div className={styles.form_wrapper}>
      <div className={styles.section_header}>
        <span className={styles.section_header_text}>
          {t('application:stepType.moveLabware')}
        </span>
      </div>
      <div className={styles.form_row}>
        <FormGroup
          label={t('step_edit_form.labwareLabel.movedLabware')}
          className={styles.large_field}
        >
          <LabwareField {...propsForFields.labware} />
        </FormGroup>
        {robotType === FLEX_ROBOT_TYPE ? (
          <Flex
            alignItems={ALIGN_CENTER}
            marginTop={SPACING.spacing4}
            marginLeft={SPACING.spacing16}
          >
            {!isGripperAttached ? (
              <Tooltip {...tooltipProps}>
                {t('tooltip:step_fields.moveLabware.disabled.gripper_not_used')}
              </Tooltip>
            ) : null}
            <div {...targetProps}>
              <FormGroup>
                <CheckboxRowField
                  {...propsForFields.useGripper}
                  disabled={!isGripperAttached}
                  label={t('step_edit_form.field.useGripper.label')}
                />
              </FormGroup>
            </div>
          </Flex>
        ) : null}
      </div>
      <div className={styles.form_row}>
        <FormGroup
          className={styles.small_field}
          label={t('step_edit_form.field.newLocation.label')}
        >
          <LabwareLocationField
            {...propsForFields.newLocation}
            useGripper={propsForFields.useGripper.value === true}
          />
        </FormGroup>
      </div>
    </div>
  )
}
