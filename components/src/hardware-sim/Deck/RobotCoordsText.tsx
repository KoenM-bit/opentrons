import type * as React from 'react'
import { css } from 'styled-components'

export interface RobotCoordsTextProps extends React.ComponentProps<'text'> {
  x: number
  y: number
  children?: React.ReactNode
  canHighlight?: boolean
}

/** SVG text reflected to use take robot coordinates as props */
// TODO: Ian 2019-05-07 reconcile this with Brian's version
export function RobotCoordsText(props: RobotCoordsTextProps): JSX.Element {
  const { x, y, children, canHighlight = true, ...additionalProps } = props
  return (
    <text
      {...additionalProps}
      x={x}
      y={-1 * y}
      transform="scale(1, -1)"
      css={
        !canHighlight
          ? css`
              user-select: none;
            `
          : undefined
      }
    >
      {children}
    </text>
  )
}
