import * as React from 'react'
import { fireEvent, screen } from '@testing-library/react'
import { describe, it, vi, beforeEach, expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { renderWithProviders } from '../../../../__testing-utils__'
import { i18n } from '../../../../i18n'
import { PipetteOverflowMenu } from '../PipetteOverflowMenu'
import {
  mockLeftProtoPipette,
  mockPipetteSettingsFieldsMap,
} from '../../../../redux/pipettes/__fixtures__'
import { isFlexPipette } from '@opentrons/shared-data'

import type { Mount } from '../../../../redux/pipettes/types'
import type * as SharedData from '@opentrons/shared-data'

vi.mock('../../../../redux/config')
vi.mock('@opentrons/shared-data', async importOriginal => {
  const actualSharedData = await importOriginal<typeof SharedData>()
  return {
    ...actualSharedData,
    isFlexPipette: vi.fn(),
  }
})

const render = (props: React.ComponentProps<typeof PipetteOverflowMenu>) => {
  return renderWithProviders(<PipetteOverflowMenu {...props} />, {
    i18nInstance: i18n,
  })[0]
}

const LEFT = 'left' as Mount
describe('PipetteOverflowMenu', () => {
  let props: React.ComponentProps<typeof PipetteOverflowMenu>

  beforeEach(() => {
    props = {
      pipetteSpecs: mockLeftProtoPipette.modelSpecs,
      pipetteSettings: mockPipetteSettingsFieldsMap,
      mount: LEFT,
      handleDropTip: vi.fn(),
      handleChangePipette: vi.fn(),
<<<<<<< HEAD
      handleAboutSlideout: vi.fn(),
      handleSettingsSlideout: vi.fn(),
=======
      handleCalibrate: vi.fn(),
      handleAboutSlideout: vi.fn(),
      handleSettingsSlideout: vi.fn(),
      isPipetteCalibrated: false,
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
      isRunActive: false,
    }
  })

  it('renders information with a pipette attached', () => {
    render(props)
    const detach = screen.getByRole('button', { name: 'Detach pipette' })
    const settings = screen.getByRole('button', { name: 'Pipette Settings' })
    const about = screen.getByRole('button', { name: 'About pipette' })
    const dropTip = screen.getByRole('button', { name: 'Drop tips' })
    fireEvent.click(detach)
    expect(props.handleChangePipette).toHaveBeenCalled()
    fireEvent.click(settings)
    expect(props.handleSettingsSlideout).toHaveBeenCalled()
    fireEvent.click(about)
    expect(props.handleAboutSlideout).toHaveBeenCalled()
    fireEvent.click(dropTip)
    expect(props.handleDropTip).toHaveBeenCalled()
  })
  it('renders information with no pipette attached', () => {
    props = {
      ...props,
      pipetteSpecs: null,
    }
    render(props)
    const btn = screen.getByRole('button', { name: 'Attach pipette' })
    fireEvent.click(btn)
    expect(props.handleChangePipette).toHaveBeenCalled()
  })
<<<<<<< HEAD
=======
  it('renders recalibrate pipette text for Flex pipette', () => {
    vi.mocked(isFlexPipette).mockReturnValue(true)
    props = {
      ...props,
      isPipetteCalibrated: true,
    }
    render(props)
    const recalibrate = screen.getByRole('button', {
      name: 'Recalibrate pipette',
    })
    fireEvent.click(recalibrate)
    expect(props.handleCalibrate).toHaveBeenCalled()
  })

  it('should render recalibrate pipette text for Flex pipette', () => {
    vi.mocked(isFlexPipette).mockReturnValue(true)
    props = {
      ...props,
      isPipetteCalibrated: true,
    }
    render(props)
    screen.getByRole('button', {
      name: 'Recalibrate pipette',
    })
  })

  it('renders only the about pipette button if FLEX pipette is attached', () => {
    vi.mocked(isFlexPipette).mockReturnValue(true)

    render(props)

    const calibrate = screen.getByRole('button', {
      name: 'Calibrate pipette',
    })
    const detach = screen.getByRole('button', { name: 'Detach pipette' })
    const settings = screen.queryByRole('button', { name: 'Pipette Settings' })
    const about = screen.getByRole('button', { name: 'About pipette' })

    fireEvent.click(calibrate)
    expect(props.handleCalibrate).toHaveBeenCalled()
    fireEvent.click(detach)
    expect(props.handleChangePipette).toHaveBeenCalled()
    expect(settings).toBeNull()
    fireEvent.click(about)
    expect(props.handleAboutSlideout).toHaveBeenCalled()
  })
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))

  it('does not render the pipette settings button if the pipette has no settings', () => {
    vi.mocked(isFlexPipette).mockReturnValue(false)
    props = {
      ...props,
      pipetteSettings: null,
    }
    render(props)
    const settings = screen.queryByRole('button', { name: 'Pipette Settings' })

    expect(settings).not.toBeInTheDocument()
  })

<<<<<<< HEAD
=======
  it('should disable certain menu items if a run is active for Flex pipette', () => {
    vi.mocked(isFlexPipette).mockReturnValue(true)
    props = {
      ...props,
      isRunActive: true,
    }
    render(props)
    expect(
      screen.getByRole('button', {
        name: 'Calibrate pipette',
      })
    ).toBeDisabled()
    expect(
      screen.getByRole('button', {
        name: 'Detach pipette',
      })
    ).toBeDisabled()
    expect(
      screen.getByRole('button', {
        name: 'Drop tips',
      })
    ).toBeDisabled()
  })

>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
  it('should disable certain menu items if a run is active for OT-2 pipette', () => {
    vi.mocked(isFlexPipette).mockReturnValue(false)
    props = {
      ...props,
      isRunActive: true,
    }
    render(props)
    expect(
      screen.getByRole('button', {
        name: 'Detach pipette',
      })
    ).toBeDisabled()
    expect(
      screen.getByRole('button', {
        name: 'Drop tips',
      })
    ).toBeDisabled()
    expect(
      screen.getByRole('button', {
        name: 'Pipette Settings',
      })
    ).toBeDisabled()
  })
})
