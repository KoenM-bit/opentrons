import * as React from 'react'
import { MemoryRouter } from 'react-router-dom'
import { fireEvent, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { renderWithProviders } from '../../../__testing-utils__'
import { i18n } from '../../../i18n'
import { SetWifiCred } from '../SetWifiCred'

const mockSetPassword = vi.fn()
vi.mock('../../../redux/discovery')
vi.mock('../../../redux/robot-api')

const render = (props: React.ComponentProps<typeof SetWifiCred>) => {
  return renderWithProviders(
    <MemoryRouter>
      <SetWifiCred {...props} />
    </MemoryRouter>,
    {
      i18nInstance: i18n,
    }
  )
}

describe('SetWifiCred', () => {
  let props: React.ComponentProps<typeof SetWifiCred>
  beforeEach(() => {
    props = {
      password: 'mock-password',
      setPassword: mockSetPassword,
    }
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should render text, button and software keyboard', () => {
    render(props)
    screen.getByText('Enter password')
    expect(screen.getByLabelText('wifi_password')).toBeInTheDocument()
    screen.getByRole('button', { name: 'Show' })
    // software keyboard
    screen.getByRole('button', { name: 'del' })
    screen.getByRole('button', { name: 'a' })
<<<<<<< HEAD
    screen.getByRole('button', { name: 'ABC' })
=======
    screen.getByRole('button', { name: 'SHIFT' })
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
  })

  it('should display password', () => {
    render(props)
    const inputBox = screen.getByLabelText('wifi_password')
    expect(inputBox).toHaveValue('mock-password')
  })

  it('should switch the input type and button text when tapping the icon next to the input', () => {
    render(props)
    const button = screen.getByRole('button', { name: 'Show' })
<<<<<<< HEAD
=======
    // ToDo: 11/08/2022 kj switch to screen.getByRole once understand the issue on this input
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
    const inputBox = screen.getByLabelText('wifi_password')
    expect(inputBox).toHaveAttribute('type', 'password')
    fireEvent.click(button)
    screen.getByRole('button', { name: 'Hide' })
<<<<<<< HEAD
    screen.getByTestId('icon_eye-slash')
    expect(screen.getByLabelText('wifi_password')).toHaveAttribute(
      'type',
      'text'
    )
=======
    expect(inputBox).toHaveAttribute('type', 'text')
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
  })
})
