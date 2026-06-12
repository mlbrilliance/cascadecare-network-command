import { useEffect, useRef, useCallback, useState } from 'react';

interface UsePollingOptions<T> {
  fetchFn: () => Promise<T>;
  interval?: number;       // ms, default 5000
  enabled?: boolean;       // toggle on/off
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
  immediate?: boolean;     // fetch on mount, default true
  deps?: unknown[];        // Reset and refetch immediately when any dep changes (e.g., [instanceId])
}

interface UsePollingResult<T> {
  data: T | null;
  isLoading: boolean;      // True only during initial fetch (before first data arrives)
  error: Error | null;
  refetch: () => Promise<void>;
  start: () => void;
  stop: () => void;
  isActive: boolean;       // Whether the polling interval is running (use for "Live" indicator)
  lastUpdated: Date | null;
}

export function usePolling<T>({
  fetchFn, interval = 5000, enabled = true,
  onSuccess, onError, immediate = true, deps = [],
}: UsePollingOptions<T>): UsePollingResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isActive, setIsActive] = useState(enabled);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  useEffect(() => { setIsActive(enabled); }, [enabled]);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const fetchFnRef = useRef(fetchFn);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);
  const hasLoadedRef = useRef(false);

  useEffect(() => { fetchFnRef.current = fetchFn; }, [fetchFn]);
  useEffect(() => { onSuccessRef.current = onSuccess; }, [onSuccess]);
  useEffect(() => { onErrorRef.current = onError; }, [onError]);

  const prevJsonRef = useRef<string>('');

  const executeFetch = useCallback(async () => {
    try {
      const result = await fetchFnRef.current();
      // Only update state if data actually changed — prevents unnecessary re-renders
      const json = JSON.stringify(result);
      if (json !== prevJsonRef.current) {
        prevJsonRef.current = json;
        setData(result);
        setLastUpdated(new Date());
      }
      // Clear any previous error only if it was set (avoid no-op setState)
      setError(prev => prev === null ? prev : null);
      onSuccessRef.current?.(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      onErrorRef.current?.(error);
    } finally {
      // Only transition from loading → loaded once (on first successful or failed fetch)
      if (!hasLoadedRef.current) {
        hasLoadedRef.current = true;
        setIsLoading(false);
      }
    }
  }, []);

  const start = useCallback(() => setIsActive(true), []);
  const stop = useCallback(() => {
    setIsActive(false);
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; }
  }, []);
  const refetch = useCallback(async () => { await executeFetch(); }, [executeFetch]);

  // Serialize deps for comparison — when deps change, reset everything and refetch
  const depsKey = JSON.stringify(deps);
  const prevDepsKeyRef = useRef(depsKey);

  useEffect(() => {
    // Detect if deps changed (e.g., user selected a different instance)
    const depsChanged = depsKey !== prevDepsKeyRef.current;
    if (depsChanged) {
      prevDepsKeyRef.current = depsKey;
      // Full reset: clear old data, show loading, refetch immediately
      hasLoadedRef.current = false;
      prevJsonRef.current = '';
      setData(null);
      setIsLoading(true);
      setError(null);
    }

    if (!isActive || !enabled) {
      if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; }
      return;
    }
    if (intervalRef.current) { clearInterval(intervalRef.current); }
    if (immediate || depsChanged) executeFetch();
    intervalRef.current = setInterval(executeFetch, interval);
    return () => { if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; } };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, enabled, interval, immediate, executeFetch, depsKey]);

  return { data, isLoading, error, refetch, start, stop, isActive, lastUpdated };
}
