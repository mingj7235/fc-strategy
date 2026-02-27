interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

const cache = new Map<string, CacheEntry<any>>();

/**
 * Fetch with in-memory caching. Returns cached data if fresh, otherwise calls fetcher.
 */
export async function cachedFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  ttlMs: number = 5 * 60 * 1000
): Promise<T> {
  const entry = cache.get(key);
  if (entry && Date.now() - entry.timestamp < entry.ttl) {
    return entry.data as T;
  }

  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now(), ttl: ttlMs });
  return data;
}

/**
 * Store data directly into cache (e.g., after polling completes).
 */
export function setCacheEntry<T>(key: string, data: T, ttlMs: number = 5 * 60 * 1000): void {
  cache.set(key, { data, timestamp: Date.now(), ttl: ttlMs });
}

/**
 * Invalidate cache entries matching a key prefix.
 */
export function invalidateCache(keyPrefix: string): void {
  for (const key of cache.keys()) {
    if (key.startsWith(keyPrefix)) {
      cache.delete(key);
    }
  }
}
