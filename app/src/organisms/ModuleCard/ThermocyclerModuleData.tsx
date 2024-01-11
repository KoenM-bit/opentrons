import * as React from 'react'
import { useTranslation } from 'react-i18next'
import { StatusLabel } from '../../atoms/StatusLabel'
import {
  Flex,
  TYPOGRAPHY,
  FONT_WEIGHT_REGULAR,
  DIRECTION_COLUMN,
  COLORS,
  SPACING,
  WRAP,
  Box,
  DIRECTION_ROW,
} from '@opentrons/components'
import { StyledText } from '../../atoms/text'

import type { ThermocyclerData } from '../../redux/modules/api-types'

interface ThermocyclerModuleProps {
  data: ThermocyclerData
}

export const ThermocyclerModuleData = (
  props: ThermocyclerModuleProps
): JSX.Element | null => {
  const { data } = props
  const { t } = useTranslation('device_details')

  const getStatusLabelProps = (
    status: string | null
  ): {
    backgroundColor: string
    iconColor: string
    textColor: string
  } => {
    const StatusLabelProps = {
      backgroundColor: COLORS.grey30,
      iconColor: COLORS.grey50,
      textColor: LEGACY_COLORS.bluePressed,
      pulse: false,
    }

    switch (status) {
      case 'idle': {
        StatusLabelProps.backgroundColor = COLORS.grey30
        StatusLabelProps.iconColor = COLORS.grey50
        StatusLabelProps.textColor = COLORS.black90
        break
      }
      case 'holding at target': {
        StatusLabelProps.backgroundColor = COLORS.medBlue
        StatusLabelProps.iconColor = COLORS.blueEnabled
        break
      }
      case 'cooling':
      case 'heating': {
        StatusLabelProps.backgroundColor = LEGACY_COLORS.medBlue
        StatusLabelProps.iconColor = COLORS.grey50
        StatusLabelProps.pulse = true
        break
      }
      case 'error': {
        StatusLabelProps.backgroundColor = COLORS.yellow20
        StatusLabelProps.iconColor = COLORS.yellow50
        StatusLabelProps.textColor = COLORS.yellow60
      }
    }
    return StatusLabelProps
  }

  return (
    <Flex flexWrap={WRAP} gridGap={`${SPACING.spacing2} ${SPACING.spacing32}`}>
      <Flex
        flexDirection={DIRECTION_COLUMN}
        data-testid="thermocycler_module_data_lid"
        gridColumn="1/4"
      >
        <StyledText
          textTransform={TYPOGRAPHY.textTransformUppercase}
          color={COLORS.grey50}
          fontSize={TYPOGRAPHY.fontSizeCaption}
          marginTop={SPACING.spacing8}
        >
          {t('tc_lid')}
        </StyledText>

        <Flex flexDirection={DIRECTION_ROW}>
          <Box marginRight={SPACING.spacing4}>
            <StatusLabel
              status={data.lidStatus === 'in_between' ? 'open' : data.lidStatus}
              backgroundColor={COLORS.grey30}
              textColor={COLORS.black90}
              showIcon={false}
              key="lidStatus"
              id="lidStatus"
            />
          </Box>
          <StatusLabel
            status={data.lidTemperatureStatus}
            {...getStatusLabelProps(data.lidTemperatureStatus)}
            key="lidTempStatus"
            id="lidTempStatus"
          />
        </Flex>
        <StyledText
          title="lid_target_temp"
          fontSize={TYPOGRAPHY.fontSizeCaption}
          marginBottom={SPACING.spacing2}
        >
          {t(data.lidTargetTemperature == null ? 'na_temp' : 'target_temp', {
            temp: data.lidTargetTemperature,
          })}
        </StyledText>
        <StyledText title="lid_temp" fontSize={TYPOGRAPHY.fontSizeCaption}>
          {t('current_temp', { temp: data.lidTemperature })}
        </StyledText>
      </Flex>
      <Flex
        flexDirection={DIRECTION_COLUMN}
        data-testid="thermocycler_module_data_block"
        gridColumn="5/8"
      >
        <StyledText
          textTransform={TYPOGRAPHY.textTransformUppercase}
          color={COLORS.grey50}
          fontWeight={FONT_WEIGHT_REGULAR}
          fontSize={TYPOGRAPHY.fontSizeCaption}
          marginTop={SPACING.spacing8}
        >
          {t('tc_block')}
        </StyledText>
        <StatusLabel
          status={data.status}
          {...getStatusLabelProps(data.status)}
          key="blockStatus"
          id="blockStatus"
        />
        <StyledText
          title="tc_target_temp"
          fontSize={TYPOGRAPHY.fontSizeCaption}
          marginBottom={SPACING.spacing2}
        >
          {t(data.targetTemperature == null ? 'na_temp' : 'target_temp', {
            temp: data.targetTemperature,
          })}
        </StyledText>
        <StyledText
          title="tc_current_temp"
          fontSize={TYPOGRAPHY.fontSizeCaption}
        >
          {t('current_temp', { temp: data.currentTemperature })}
        </StyledText>
      </Flex>
    </Flex>
  )
}
