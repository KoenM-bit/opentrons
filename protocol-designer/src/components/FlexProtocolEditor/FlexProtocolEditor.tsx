import React, { useState, useEffect } from 'react'
import {
  Flex,
  DIRECTION_COLUMN,
  Box,
  COLORS,
  BORDERS,
  SPACING,
  NewPrimaryBtn,
  DIRECTION_ROW,
  JUSTIFY_SPACE_BETWEEN,
} from '@opentrons/components'
import {
  HEATERSHAKER_MODULE_V1,
  MAGNETIC_MODULE_TYPE,
  TEMPERATURE_MODULE_TYPE,
  THERMOCYCLER_MODULE_TYPE,
  THERMOCYCLER_MODULE_V1,
  HEATERSHAKER_MODULE_TYPE,
  ModuleModel,
  SPAN7_8_10_11_SLOT,
  MAGNETIC_MODULE_V1,
  TEMPERATURE_MODULE_V2,
  GRIPPER_V1,
  GRIPPER_MODULE_TYPE,
} from '@opentrons/shared-data'
import { Formik } from 'formik'
import * as Yup from 'yup'
import { i18n } from '../../localization'
import { StyledText } from './StyledText'
import styles from './FlexComponents.css'
import { mountSide, navPillTabListLength, pipetteSlot } from './constant'
import { FlexRoundTab } from './FlexRoundTab'
import { DeckSlot } from '../../types'
import { FlexProtocolName, SelectPipetteOption } from './FlexPillForm'
import { FlexModules } from './FlexModules'
import { connect, useDispatch } from 'react-redux'
import { actions as navActions } from '../../navigation'
import { reduce } from 'lodash'
import { PipetteOnDeck } from '../../step-forms'
import assert from 'assert'
import { ModuleCreationArgs } from '../modals/FilePipettesModal'
import { LabwareDefByDefURI } from '../../labware-defs'
import { NewProtocolFields } from '../../load-file'
import {
  mapDispatchToProps,
  mapStateToProps as newModalFileMapStateToProps,
} from '../modals/NewFileModal'
import { FlexFileDetails } from './FlexFileDetails'
type Props = React.ComponentProps<typeof FlexProtocolEditor>
export interface FormModule {
  onDeck: boolean
  model: ModuleModel | null
  slot: DeckSlot
}

export interface FormPipette {
  pipetteName: string | null | undefined
  mount: string | null | undefined
  tiprackDefURI: any[]
  isSelected: boolean
}
export interface FormPipettesByMount {
  left: FormPipette
  right: FormPipette
}
export interface InitialValues {
  fields: { name: string; author: string; description: string }
  mountSide: string
  pipettesByMount: FormPipettesByMount
  modulesByType: {
    magneticModuleType: FormModule
    temperatureModuleType: FormModule
    thermocyclerModuleType: FormModule
    heaterShakerModuleType: FormModule
    gripperModuleType: FormModule
  }
}

interface FlexProtocolEditorComponentProps {
  isEditValue: boolean
  tabIdValue: number
  formProps: any
  onSave: (args: {
    newProtocolFields: NewProtocolFields
    pipettes: PipetteFieldsData[]
    modules: ModuleCreationArgs[]
  }) => void
}

const validationSchema = Yup.object().shape({
  mountSide: Yup.string().required('Mount side is required'),
  pipettesByMount: Yup.object().shape({
    left: Yup.object().shape({
      pipetteName: Yup.string().required('First pipette is required'),
      // tiprackDefURI: Yup.array().min(
      //   1,
      //   'Select at least one tip rack for first pipette'
      // ),
    }),
    right: Yup.object().shape({
      pipetteName: Yup.string().required('Second pipette is required'),
      // tiprackDefURI: Yup.array().min(
      //   1,
      //   'Select at least one tip rack for second pipette'
      // ),
    }),
  }),
})

const initialFormValues: InitialValues = {
  fields: {
    name: '',
    author: '',
    description: '',
  },
  mountSide,
  pipettesByMount: {
    left: {
      pipetteName: '',
      mount: 'left',
      tiprackDefURI: [],
      isSelected: false,
    },
    right: {
      pipetteName: '',
      mount: 'right',
      tiprackDefURI: [],
      isSelected: false,
    },
  },
  modulesByType: {
    [HEATERSHAKER_MODULE_TYPE]: {
      onDeck: false,
      model: HEATERSHAKER_MODULE_V1,
      slot: '1',
    },
    [MAGNETIC_MODULE_TYPE]: {
      onDeck: false,
      model: MAGNETIC_MODULE_V1,
      slot: '4',
    },
    [TEMPERATURE_MODULE_TYPE]: {
      onDeck: false,
      model: TEMPERATURE_MODULE_V2,
      slot: '3',
    },
    [THERMOCYCLER_MODULE_TYPE]: {
      onDeck: false,
      model: THERMOCYCLER_MODULE_V1, // Default to GEN1 for TC only
      slot: SPAN7_8_10_11_SLOT,
    },
    [GRIPPER_MODULE_TYPE]: {
      onDeck: false,
      model: GRIPPER_V1,
      slot: '',
    },
  },
}

const getInitialValues = (values: any): InitialValues => {
  if (Boolean(values)) {
    // Matching the form values
    initialFormValues.fields.name = values.formValues.protocolName
    initialFormValues.fields.author = values.formValues.author
    initialFormValues.fields.description = values.formValues.description

    // Matching the pipette values
    initialFormValues.pipettesByMount.right.pipetteName =
      values.instruments.right?.pipetteSpecs.name
    initialFormValues.pipettesByMount.left.pipetteName =
      values.instruments.left?.pipetteSpecs.name

    // Matching the tip rack
    initialFormValues.pipettesByMount.right.tiprackDefURI = values.instruments
      .right?.tiprackModel
      ? [values.instruments.right.tiprackModel]
      : []
    initialFormValues.pipettesByMount.left.tiprackDefURI = values.instruments
      .left?.tiprackModel
      ? [values.instruments.left.tiprackModel]
      : []

    // Matching the module values
    if (values.modules.heaterShakerModuleType) {
      initialFormValues.modulesByType[HEATERSHAKER_MODULE_TYPE].onDeck = true
      initialFormValues.modulesByType[HEATERSHAKER_MODULE_TYPE].model =
        values.modules.heaterShakerModuleType.model
      initialFormValues.modulesByType[HEATERSHAKER_MODULE_TYPE].slot =
        values.modules.heaterShakerModuleType.slot
    }

    if (values.modules.magneticModuleType) {
      initialFormValues.modulesByType[MAGNETIC_MODULE_TYPE].onDeck = true
      initialFormValues.modulesByType[MAGNETIC_MODULE_TYPE].model =
        values.modules.magneticModuleType.model
      initialFormValues.modulesByType[MAGNETIC_MODULE_TYPE].slot =
        values.modules.magneticModuleType.slot
    }

    if (values.modules.temperatureModuleType) {
      initialFormValues.modulesByType[TEMPERATURE_MODULE_TYPE].onDeck = true
      initialFormValues.modulesByType[TEMPERATURE_MODULE_TYPE].model =
        values.modules.temperatureModuleType.model
      initialFormValues.modulesByType[TEMPERATURE_MODULE_TYPE].slot =
        values.modules.temperatureModuleType.slot
    }

    if (values.modules.thermocyclerModuleType) {
      initialFormValues.modulesByType[THERMOCYCLER_MODULE_TYPE].onDeck = true
      initialFormValues.modulesByType[THERMOCYCLER_MODULE_TYPE].model =
        values.modules.thermocyclerModuleType.model
      initialFormValues.modulesByType[THERMOCYCLER_MODULE_TYPE].slot =
        values.modules.thermocyclerModuleType.slot
    }

    if (!initialFormValues.modulesByType[GRIPPER_MODULE_TYPE].onDeck) {
      initialFormValues.modulesByType[GRIPPER_MODULE_TYPE].onDeck = false
    }

    return initialFormValues
  } else {
    return initialFormValues
  }
}

interface selectedTabProps {
  selectedTab: number
}

const SelectComponent = (selectedTab: number): JSX.Element | null => {
  const [is96ChannelSelected, setIs96ChangeSelected] = useState(false)
  const { left, right } = pipetteSlot
  switch (selectedTab) {
    case 0:
      return <FlexProtocolName />
    case 1:
      return (
        <Flex
          flexDirection={DIRECTION_ROW}
          justifyContent={JUSTIFY_SPACE_BETWEEN}
        >
          <SelectPipetteOption
            pipetteName={left}
            changeIs96Selected={setIs96ChangeSelected}
            isLeft96ChannelSelected={is96ChannelSelected}
          />
          <SelectPipetteOption
            pipetteName={right}
            changeIs96Selected={setIs96ChangeSelected}
            isLeft96ChannelSelected={is96ChannelSelected}
          />
        </Flex>
      )
    case 2:
      return <FlexModules />
    default:
      return null
  }
}

type PipetteFieldsData = Omit<
  PipetteOnDeck,
  'id' | 'spec' | 'tiprackLabwareDef'
>

function FlexProtocolEditor({
  isEditValue,
  tabIdValue,
  formProps,
  onSave,
}: FlexProtocolEditorComponentProps): JSX.Element {
  const [selectedTab, setTab] = useState<number>(0)
  const [redirectToDetails, setRedirectToDetails] = useState(false)
  const dispatch = useDispatch()
  const [isEdit, setEdit] = useState(false)
  // On Redirction if page tab edit set to true
  useEffect(() => {
    if (isEditValue) {
      setEdit(isEditValue)
      setTab(tabIdValue)
    }
  }, [isEditValue, tabIdValue])

  // Next button click
  const handleNext = ({ selectedTab }: selectedTabProps): any => {
    if (isEdit) {
      // Redirect back to file details page
      setRedirectToDetails(true)
      return <FlexFileDetails />
    } else {
      const setTabNumber =
        selectedTab >= 0 && selectedTab <= navPillTabListLength
          ? selectedTab + 1
          : selectedTab
      setTab(setTabNumber)
    }
  }

  // Previous button click
  const handlePrevious = ({ selectedTab }: selectedTabProps): void => {
    const setTabNumber =
      selectedTab > 0 && selectedTab <= navPillTabListLength
        ? selectedTab - 1
        : selectedTab
    setTab(setTabNumber)
  }

  const nextButton =
    selectedTab === navPillTabListLength
      ? isEdit
        ? i18n.t('flex.round_tabs.update')
        : i18n.t('flex.round_tabs.go_to_liquids_page')
      : isEdit
      ? i18n.t('flex.round_tabs.update')
      : i18n.t('flex.round_tabs.next')

  interface FormikErrors {
    pipette?: string
    tiprack?: string
  }

  const validateFields = (values: InitialValues): FormikErrors => {
    const { pipettesByMount } = values
    const errors: FormikErrors = {}
    if (!pipettesByMount.left.pipetteName) {
      errors.pipette = `${i18n.t('flex.errors.first_pipette_not_selected')}`
    }

    if (!pipettesByMount.left.tiprackDefURI.length) {
      errors.tiprack = `${i18n.t('flex.errors.tiprack_not_selected')}`
    }

    return errors
  }

  const handleSubmit = ({ values }: any): void => {
    console.log('***Final OT3 JSON Data ***', values)
    const newProtocolFields = values.fields

    const pipettes = reduce<FormPipettesByMount, PipetteFieldsData[]>(
      values.pipettesByMount,
      (acc, formPipette: FormPipette, mount): PipetteFieldsData[] => {
        assert(mount === 'left' || mount === 'right', `invalid mount: ${mount}`) // this is mostly for flow
        // @ts-expect-error(sa, 2021-6-21): TODO validate that pipette names coming from the modal are actually valid pipette names on PipetteName type
        return formPipette &&
          formPipette.pipetteName &&
          formPipette.tiprackDefURI &&
          (mount === 'left' || mount === 'right')
          ? [
              ...acc,
              {
                mount,
                name: formPipette.pipetteName,
                tiprackDefURI: formPipette.tiprackDefURI,
              },
            ]
          : acc
      },
      []
    )

    // NOTE: this is extra-explicit for flow. Reduce fns won't cooperate
    // with enum-typed key like `{[ModuleType]: ___}`
    // @ts-expect-error(sa, 2021-6-21): TS not smart enough to take real type from Object.keys
    const moduleTypes: ModuleType[] = Object.keys(values.modulesByType)
    const modules: ModuleCreationArgs[] = moduleTypes.reduce<
      ModuleCreationArgs[]
    >((acc, moduleType) => {
      const formModule = values.modulesByType[moduleType]
      return formModule?.onDeck
        ? [
            ...acc,
            {
              type: moduleType,
              model: formModule.model || ('' as ModuleModel), // TODO: we need to validate that module models are of type ModuleModel
              slot: formModule.slot,
            },
          ]
        : acc
    }, [])

    onSave({ modules, newProtocolFields, pipettes })
    dispatch(navActions.navigateToPage('liquids'))
  }

  return redirectToDetails ? (
    <FlexFileDetails />
  ) : (
    <Flex flexDirection={DIRECTION_COLUMN}>
      <Flex>
        <FlexRoundTab
          setCurrentTab={setTab}
          currentTab={selectedTab}
          isEdit={isEditValue}
        />
      </Flex>
      <Box
        backgroundColor={COLORS.white}
        border={BORDERS.lineBorder}
        // remove left upper corner border radius when first tab is active
        borderRadius={selectedTab === 1 ? '0' : BORDERS.radiusSoftCorners}
        padding={SPACING.spacing4}
      >
        {
          <Formik
            enableReinitialize
            initialValues={getInitialValues(formProps)}
            validateOnChange={true}
            validate={validateFields}
            validationSchema={validationSchema}
            onSubmit={(values, actions) => {
              selectedTab === 3 && handleSubmit({ values })
            }}
          >
            {(props: {
              errors: any
              isValid: any
              handleSubmit: () => void
            }) => (
              <form onSubmit={props.handleSubmit}>
                <section className={styles.editor_form}>
                  {SelectComponent(selectedTab)}
                </section>
                <div className={styles.flex_round_tabs_button_wrapper}>
                  {selectedTab !== 0 && !isEdit && (
                    <NewPrimaryBtn
                      tabIndex={5}
                      onClick={() => handlePrevious({ selectedTab })}
                      className={styles.flex_round_tabs_button_50p}
                    >
                      <StyledText as="h3">
                        {i18n.t('flex.round_tabs.previous')}
                      </StyledText>
                    </NewPrimaryBtn>
                  )}
                  <NewPrimaryBtn
                    tabIndex={4}
                    type="submit"
                    onClick={() => handleNext({ selectedTab })}
                    className={
                      selectedTab !== 0
                        ? styles.flex_round_tabs_button_50p
                        : styles.flex_round_tabs_button_100p
                    }
                  >
                    <StyledText as="h3">{nextButton}</StyledText>
                  </NewPrimaryBtn>
                </div>
              </form>
            )}
          </Formik>
        }
      </Box>
    </Flex>
  )
}

interface CreateNewProtocolArgs {
  customLabware: LabwareDefByDefURI
  newProtocolFields: NewProtocolFields
  pipettes: PipetteFieldsData[]
  modules: ModuleCreationArgs[]
}
interface DP {
  onCancel: () => unknown
  _createNewProtocol: (arg0: CreateNewProtocolArgs) => void
}
function mergeProps(stateProps: SP, dispatchProps: DP, ownProps: any): Props {
  const { isEditValue, tabIdValue, formProps } = ownProps.FlexFileDetails
  return {
    isEditValue,
    tabIdValue,
    formProps,
    onSave: fields => {
      if (
        !stateProps._hasUnsavedChanges ||
        window.confirm(i18n.t('alert.window.confirm_create_new'))
      ) {
        dispatchProps._createNewProtocol({
          ...fields,
          customLabware: stateProps._customLabware,
        })
      }
    },
  }
}

export const FlexProtocolEditorComponent = connect(
  newModalFileMapStateToProps,
  mapDispatchToProps,
  mergeProps
)(FlexProtocolEditor)
