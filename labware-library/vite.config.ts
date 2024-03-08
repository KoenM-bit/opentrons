import path from 'path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import postCssImport from 'postcss-import'
import postCssApply from 'postcss-apply'
import postColorModFunction from 'postcss-color-mod-function'
import postCssPresetEnv from 'postcss-preset-env'
import lostCss from 'lost'

const testAliases: {} | { 'file-saver': string } =
  process.env.CYPRESS === '1'
    ? {
        'file-saver':
          path.resolve(__dirname, 'cypress/mocks/file-saver.js') ?? '',
      }
    : {}

export default defineConfig({
<<<<<<< HEAD
  // this makes imports relative rather than absolute
  base: '',
=======
>>>>>>> 9359adf484 (chore(monorepo): migrate frontend bundling from webpack to vite (#14405))
  build: {
    // Relative to the root
    outDir: 'dist',
  },
  plugins: [
    react({
      include: '**/*.tsx',
      babel: {
        // Use babel.config.js files
        configFile: true,
      },
    }),
  ],
  optimizeDeps: {
    esbuildOptions: {
      target: 'es2020',
    },
  },
  css: {
    postcss: {
      plugins: [
        postCssImport({ root: 'src/' }),
        postCssApply(),
        postColorModFunction(),
        postCssPresetEnv({ stage: 0 }),
        lostCss(),
      ],
    },
  },
  define: {
    'process.env': process.env,
    global: 'globalThis',
  },
  resolve: {
    alias: {
      '@opentrons/components/styles': path.resolve(
        '../components/src/index.module.css'
      ),
      '@opentrons/components': path.resolve('../components/src/index.ts'),
      '@opentrons/shared-data': path.resolve('../shared-data/js/index.ts'),
      '@opentrons/step-generation': path.resolve(
        '../step-generation/src/index.ts'
      ),
      ...testAliases,
    },
  },
})
