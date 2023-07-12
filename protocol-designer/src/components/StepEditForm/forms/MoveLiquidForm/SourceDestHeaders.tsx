import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { FormGroup } from '@opentrons/components'
import { LabwareField, WellSelectionField } from '../../fields'
import { AspDispSection } from '../AspDispSection'
import { StepFieldName } from '../../../../steplist/fieldLevel'
import { FormData } from '../../../../form-types'
import { FieldPropsByName } from '../../types'

import styles from '../../StepEditForm.css'

interface Props {
  className?: string | null
  collapsed?: boolean | null
  formData: FormData
  prefix: 'aspirate' | 'dispense'
  propsForFields: FieldPropsByName
  toggleCollapsed: () => void
}

const makeAddFieldNamePrefix = (prefix: string) => (
  fieldName: string
): StepFieldName => `${prefix}_${fieldName}`

export const SourceDestHeaders = (props: Props): JSX.Element => {
  const {
    className,
    collapsed,
    toggleCollapsed,
    prefix,
    propsForFields,
    formData,
  } = props
  const { t } = useTranslation('form')
  const addFieldNamePrefix = makeAddFieldNamePrefix(prefix)
  const labwareLabel = t(`step_edit_form.labwareLabel.${prefix}`)

  return (
    <AspDispSection {...{ className, collapsed, toggleCollapsed, prefix }}>
      <div className={styles.form_row}>
        <FormGroup label={labwareLabel}>
          <LabwareField {...propsForFields[addFieldNamePrefix('labware')]} />
        </FormGroup>
        <WellSelectionField
          {...propsForFields[addFieldNamePrefix('wells')]}
          labwareId={formData[addFieldNamePrefix('labware')]}
          pipetteId={formData.pipette}
        />
      </div>
    </AspDispSection>
  )
}
