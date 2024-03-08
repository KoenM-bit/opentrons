import path from 'path'
import { app } from 'electron'
import type { UpdateManifestUrls } from './types'
import type { RobotUpdateTarget } from '@opentrons/app/src/redux/robot-update/types'
import { CURRENT_VERSION } from '../update'

const OPENTRONS_PROJECT: string = _OPENTRONS_PROJECT_

const UPDATE_MANIFEST_URLS_RELEASE = {
  ot2: 'https://builds.opentrons.com/ot2-br/releases.json',
  flex: 'https://builds.opentrons.com/ot3-oe/releases.json',
}

const UPDATE_MANIFEST_URLS_INTERNAL_RELEASE = {
  ot2: 'https://ot3-development.builds.opentrons.com/ot2-br/releases.json',
  flex: 'https://ot3-development.builds.opentrons.com/ot3-oe/releases.json',
}

export const getUpdateManifestUrls = (): UpdateManifestUrls =>
<<<<<<< HEAD
  OPENTRONS_PROJECT.includes('robot-stack')
=======
  // @ts-expect-error can't get TS to recognize global.d.ts
  global._OPENTRONS_PROJECT_.includes('robot-stack')
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
    ? UPDATE_MANIFEST_URLS_RELEASE
    : UPDATE_MANIFEST_URLS_INTERNAL_RELEASE

const DIRECTORY = path.join(app.getPath('userData'), 'robot-update-cache')
export const cacheDirForMachine = (machine: RobotUpdateTarget): string =>
  path.join(DIRECTORY, machine)
export const cacheDirForMachineFiles = (machine: RobotUpdateTarget): string =>
  path.join(cacheDirForMachine(machine), CURRENT_VERSION)
