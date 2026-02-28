interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

const MAX_CACHE_SIZE = 80;
const cache = new Map<string, CacheEntry<any>>();

/**
 * Evict oldest entries when cache exceeds max size.
 */
function evictIfNeeded(): void {
  if (cache.size <= MAX_CACHE_SIZE) return;

  // Map preserves insertion order — delete oldest entries first
  const toDelete = cache.size - MAX_CACHE_SIZE;
  let deleted = 0;
  for (const key of cache.keys()) {
    if (deleted >= toDelete) break;
    cache.delete(key);
    deleted++;
  }
}

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
    // Move to end (most recently used) by re-inserting
    cache.delete(key);
    cache.set(key, entry);
    return entry.data as T;
  }

  const data = await fetcher();
  cache.set(key, { data, timestamp: Date.now(), ttl: ttlMs });
  evictIfNeeded();
  return data;
}

/**
 * Store data directly into cache (e.g., after polling completes).
 */
export function setCacheEntry<T>(key: string, data: T, ttlMs: number = 5 * 60 * 1000): void {
  cache.set(key, { data, timestamp: Date.now(), ttl: ttlMs });
  evictIfNeeded();
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
