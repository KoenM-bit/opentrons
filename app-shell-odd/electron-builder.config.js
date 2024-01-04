'use strict'

module.exports = {
  appId: 'com.opentrons.odd',
  electronVersion: '28.1.0',
  nodeVersion: '21.4.0',
  npmRebuild: false,
  files: [
    '**/*',
    '!Makefile',
    {
      from: '../app/dist',
      to: './ui',
      filter: ['**/*'],
    },
  ],
  /* eslint-disable no-template-curly-in-string */
  artifactName: '${productName}-v${version}-${os}-${env.BUILD_ID}.${ext}',
  /* eslint-enable no-template-curly-in-string */
  asar: true,
  linux: {
    target: ['dir'],
    executableName: 'opentrons',
    category: 'Science',
  },
}
