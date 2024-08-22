import { useAllRunsQuery } from '@opentrons/react-api-client'

import { useNotifyDataReady } from '../useNotifyDataReady'

import type { UseQueryResult } from 'react-query'
import type { AxiosError } from 'axios'
import type { HostConfig, GetRunsParams, Runs } from '@opentrons/api-client'
import type { UseAllRunsQueryOptions } from '@opentrons/react-api-client/src/runs/useAllRunsQuery'
import type { QueryOptionsWithPolling } from '../useNotifyDataReady'

// TODO(jh, 08-21-24): Abstract harder.
export function useNotifyAllRunsQuery(
  params: GetRunsParams = {},
  options: QueryOptionsWithPolling<UseAllRunsQueryOptions, AxiosError> = {},
  hostOverride?: HostConfig | null
): UseQueryResult<Runs, AxiosError> {
  const {
    notifyOnSettled,
    shouldRefetch,
    isNotifyEnabled,
  } = useNotifyDataReady({
    topic: 'robot-server/runs',
    options,
    hostOverride,
  })

  const queryOptions = {
    ...options,
    onSettled: isNotifyEnabled ? notifyOnSettled : options.onSettled,
    refetchInterval: isNotifyEnabled ? false : options.refetchInterval,
  }
  const httpResponse = useAllRunsQuery(
    params,
    queryOptions as UseAllRunsQueryOptions,
    hostOverride
  )

  if (isNotifyEnabled && shouldRefetch) {
    httpResponse.refetch()
  }

  return httpResponse
}
