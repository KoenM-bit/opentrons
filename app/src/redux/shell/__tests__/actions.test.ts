import { describe, it, expect } from 'vitest'

<<<<<<< HEAD
import { uiInitialized, notifySubscribeAction } from '../actions'
=======
import {
  uiInitialized,
  notifySubscribeAction,
  notifyUnsubscribeAction,
} from '../actions'
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))

import type { NotifyTopic } from '../types'

const MOCK_HOSTNAME = 'hostTest'
const MOCK_TOPIC: NotifyTopic = 'robot-server/maintenance_runs/current_run'

describe('shell actions', () => {
  it('should be able to create a UI_INITIALIZED action', () => {
    expect(uiInitialized()).toEqual({
      type: 'shell:UI_INITIALIZED',
      meta: { shell: true },
    })
  })
  it('should be able to create a SUBSCRIBE action', () => {
    expect(notifySubscribeAction(MOCK_HOSTNAME, MOCK_TOPIC)).toEqual({
      type: 'shell:NOTIFY_SUBSCRIBE',
      payload: {
        hostname: MOCK_HOSTNAME,
        topic: MOCK_TOPIC,
      },
      meta: { shell: true },
    })
  })
})
