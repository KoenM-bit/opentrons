import styled from 'styled-components'
import {
  COLORS,
  DIRECTION_COLUMN,
  DIRECTION_ROW,
  DropdownField,
  Flex,
  InputField,
  JUSTIFY_CENTER,
  JUSTIFY_END,
  LargeButton,
  StyledText,
  Link as LinkComponent,
} from '@opentrons/components'
import { UploadInput } from '../../molecules/UploadInput'
import { HeaderWithMeter } from '../../molecules/HeaderWithMeter'
import { useEffect, useState } from 'react'
import type { ChangeEvent } from 'react'
import { Trans, useTranslation } from 'react-i18next'

const updateOptions = [
  {
    name: 'Adapt Python protocol from OT-2 to Flex',
    value: 'adapt_python_protocol',
  },
  { name: 'Change labware', value: 'change_labware' },
  { name: 'Change pipettes', value: 'change_pipettes' },
  { name: 'Other', value: 'other' },
]

const Container = styled(Flex)`
  width: 100%;
  flex-direction: ${DIRECTION_COLUMN};
  align-items: ${JUSTIFY_CENTER};
`

const Spacer = styled(Flex)`
  height: 16px;
`

const ContentBox = styled(Flex)`
  background-color: white;
  border-radius: 16px;
  flex-direction: ${DIRECTION_COLUMN};
  justify-content: ${JUSTIFY_CENTER};
  padding: 32px 24px;
  width: 60%;
`

const ContentFlex = styled(Flex)`
  flex-direction: ${DIRECTION_COLUMN};
  justify-content: ${JUSTIFY_CENTER};
`

const HeadingText = styled(StyledText).attrs({
  desktopStyle: 'headingSmallBold',
})``

const BodyText = styled(StyledText).attrs({
  desktopStyle: 'bodyDefaultRegular',
  paddingBottom: '8px',
  paddingTop: '16px',
})``

const isValidProtocolFileName = (protocolFileName: string): boolean => {
  return protocolFileName.endsWith('.py')
}

export function UpdateProtocol(): JSX.Element {
  const { t } = useTranslation('protocol_generator')
  const [progressPercentage, setProgressPercentage] = useState<number>(0.0)
  const [updateType, setUpdateType] = useState<string>('')
  const [detailsValue, setDetailsValue] = useState<string>('')
  const [pythonText, setPythonTextValue] = useState<string>('')

  useEffect(() => {
    let progress = 0.0
    if (updateType !== '') {
      progress += 0.33
    }

    if (detailsValue !== '') {
      progress += 0.33
    }

    if (pythonText !== '') {
      progress += 0.34
    }

    setProgressPercentage(progress)
  }, [updateType, detailsValue, pythonText])

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>): void => {
    setDetailsValue(event.target.value)
  }

  const handleUpload = async (
    file: File2 & { name: string }
  ): Promise<void> => {
    if (file.path === null) {
      // logger.warn('Failed to upload file, path not found')
    }
    if (isValidProtocolFileName(file.name)) {
      // todo convert to text

      console.log('compatible_file_type')
      console.log(file.name)
      // const text = await new Response(new Blob([await file.text()])).text()
      const text = await file.text().catch(error => {
        console.error('Error reading file:', error)
      })

      console.log(text)
      if (text) {
        setPythonTextValue(text)
      }
    } else {
      console.log('incompatible_file_type')
    }
    // props.onUpload?.()
    // trackEvent({
    //   name: ANALYTICS_IMPORT_PROTOCOL_TO_APP,
    //   properties: { protocolFileName: file.name },
    // })
  }

  return (
    <Container>
      <HeaderWithMeter
        progressPercentage={progressPercentage}
      ></HeaderWithMeter>
      <Spacer />
      <ContentBox>
        <ContentFlex>
          <HeadingText>{t('update_existing_protocol')}</HeadingText>
          <BodyText>{t('protocol_file')}</BodyText>
          <Flex
            paddingTop="40px"
            width="auto"
            flexDirection={DIRECTION_ROW}
            justifyContent={JUSTIFY_CENTER}
          >
            <UploadInput
              uploadButtonText="Choose file"
              dragAndDropText={
                <StyledText as="p">
                  <Trans
                    t={t}
                    i18nKey={t('drag_and_drop')}
                    components={{
                      a: (
                        <LinkComponent
                          color={COLORS.blue55}
                          role="button"
                          to={''}
                        />
                      ),
                    }}
                  />
                </StyledText>
              }
              onUpload={async function (file: File) {
                try {
                  await handleUpload(file)
                } catch (error) {
                  console.error('Error uploading file:', error)
                }
              }}
            ></UploadInput>
          </Flex>

          <BodyText>{t('type_of_update')}</BodyText>
          <DropdownField
            value={updateType}
            options={updateOptions}
            onChange={function (event: ChangeEvent<HTMLSelectElement>): void {
              setUpdateType(event.target.value)
            }}
          />
          <BodyText>{t('provide_details_of_changes')}</BodyText>
          <InputField
            value={detailsValue}
            onChange={handleInputChange}
            size="medium"
          />
          <Flex
            paddingTop="40px"
            width="auto"
            flexDirection={DIRECTION_ROW}
            justifyContent={JUSTIFY_END}
          >
            <LargeButton
              disabled={progressPercentage !== 1.0}
              buttonText={t('submit_prompt')}
            />
          </Flex>
        </ContentFlex>
      </ContentBox>
    </Container>
  )
}

interface File2 {
  /**
   * The real path to the file on the users filesystem
   */
  path?: string
  /**
   * The name of the file
   */
  name: string

  /**
   * The contents of the file
   */
  // contents: string
  text: () => Promise<string>
}
