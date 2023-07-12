import i18n from 'i18next'
import capitalize from 'lodash/capitalize'
import startCase from 'lodash/startCase'
import { initReactI18next } from 'react-i18next'
import { titleCase } from '@opentrons/shared-data'
import { en } from './en'

i18n.use(initReactI18next).init(
  {
    lng: 'en',
    resources: {
      en,
    },
    fallbackLng: 'en',
    debug: process.env.NOVE_ENV === 'development',
    defaultNS: 'shared',
    ns: [
      'alert',
      'application',
      'button',
      'card',
      'context_menu',
      'deck',
      'feature_flags',
      'form',
      'modal',
      'modules',
      'nav',
      'shared',
      'tooltip',
      'well_selection',
    ],
    interpolation: {
      escapeValue: false, // not needed for react as it escapes by default
      format: function (value, format, lng) {
        if (format === 'upperCase') return value.toUpperCase()
        if (format === 'capitalize') return capitalize(value)
        if (format === 'sentenceCase') return startCase(value)
        if (format === 'titleCase') return titleCase(value)
        return value
      },
    },
    saveMissing: true,
    missingKeyHandler: (lng, ns, key) => {
      process.env.NODE_ENV === 'test'
        ? console.error(`Missing ${lng} Translation: key={${key}} ns={${ns}}`)
        : console.warn(`Missing ${lng} Translation: key={${key}} ns={${ns}}`)
    },
  },
  err => {
    if (err) {
      console.error(
        'Internationalization was not initialized properly. error: ',
        err
      )
    }
  }
)

export { i18n }
