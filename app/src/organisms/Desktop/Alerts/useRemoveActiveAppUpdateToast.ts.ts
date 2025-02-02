import { useContext } from 'react'
import { AlertsContext } from '.'
import type { AlertsContextProps } from '.'

export function useRemoveActiveAppUpdateToast(): AlertsContextProps {
  return useContext(AlertsContext)
}
