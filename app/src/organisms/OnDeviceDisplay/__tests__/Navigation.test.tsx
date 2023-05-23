import * as React from 'react'
import { MemoryRouter } from 'react-router-dom'

import { renderWithProviders } from '@opentrons/components'

import { getLocalRobot } from '../../../redux/discovery'
import { mockConnectedRobot } from '../../../redux/discovery/__fixtures__'
import { NavigationMenu } from '../Navigation/NavigationMenu'
import { Navigation } from '../Navigation'

jest.mock('../../../redux/discovery')
jest.mock('../Navigation/NavigationMenu')

const mockGetLocalRobot = getLocalRobot as jest.MockedFunction<
  typeof getLocalRobot
>
const mockNavigationMenu = NavigationMenu as jest.MockedFunction<
  typeof NavigationMenu
>
const mockComponent = () => null

const mockRoutes = [
  {
    Component: mockComponent,
    exact: true,
    name: 'Get started',
    path: '/get-started',
  },
  {
    Component: mockComponent,
    exact: true,
    name: 'All Protocols',
    navLinkTo: '/protocols',
    path: '/protocols',
  },
  {
    Component: mockComponent,
    exact: true,
    name: 'Instruments',
    navLinkTo: '/instruments',
    path: '/instruments',
  },
  {
    Component: mockComponent,
    exact: true,
    name: 'Settings',
    navLinkTo: '/robot-settings',
    path: '/robot-settings',
  },
]

// Change the name to follow the future name length rule
mockConnectedRobot.name = 'opentrons-dev'

const render = (props: React.ComponentProps<typeof Navigation>) => {
  return renderWithProviders(
    <MemoryRouter>
      <Navigation {...props} />
    </MemoryRouter>
  )
}

describe('Navigation', () => {
  let props: React.ComponentProps<typeof Navigation>
  beforeEach(() => {
    props = {
      routes: mockRoutes,
    }
    mockGetLocalRobot.mockReturnValue(mockConnectedRobot)
    mockNavigationMenu.mockReturnValue(<div>mock NavigationMenu</div>)
  })
  it('should render text and they have attribute', () => {
    const [{ getByRole, queryByText }] = render(props)
    getByRole('link', { name: 'opentrons-dev' }) // because of the truncate function
    const allProtocols = getByRole('link', { name: 'All Protocols' })
    expect(allProtocols).toHaveAttribute('href', '/protocols')

    const instruments = getByRole('link', { name: 'Instruments' })
    expect(instruments).toHaveAttribute('href', '/instruments')

    const settings = getByRole('link', { name: 'Settings' })
    expect(settings).toHaveAttribute('href', '/robot-settings')

    expect(queryByText('Get started')).not.toBeInTheDocument()
  })
  it('should render the overflow btn and clicking on it renders the menu', () => {
    const [{ getByRole, getByText }] = render(props)
    getByRole('button', { name: 'overflow menu button' }).click()
    getByText('mock NavigationMenu')
  })
  it('should call the setNavMenuIsOpened prop when you click on the overflow menu button', () => {
    props = {
      ...props,
      setNavMenuIsOpened: jest.fn(),
    }
    const [{ getByRole, getByText }] = render(props)
    getByRole('button', { name: 'overflow menu button' }).click()
    getByText('mock NavigationMenu')
    expect(props.setNavMenuIsOpened).toHaveBeenCalled()
  })
  it('should change z index of nav bar when longPressModalIsOpened is defined and true', () => {
    props = {
      ...props,
      longPressModalIsOpened: true,
    }
    const [{ getByLabelText }] = render(props)
    expect(getByLabelText('Navigation_container')).toHaveStyle({ zIndex: 0 })
  })
})
