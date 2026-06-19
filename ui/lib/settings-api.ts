import { AppSettings } from '@/store/settings-store';

export function getApiBaseUrl(settings: Pick<AppSettings, 'apiHost' | 'apiPort'>) {
  return `http://${settings.apiHost}:${settings.apiPort}`;
}

export async function testApiConnection(settings: Pick<AppSettings, 'apiHost' | 'apiPort'>) {
  const base = getApiBaseUrl(settings);
  const start = performance.now();

  try {
    const res = await fetch(`${base}/`, { method: 'GET', signal: AbortSignal.timeout(8000) });
    const latency = Math.round(performance.now() - start);
    if (!res.ok) {
      return { ok: false, latency, message: `HTTP ${res.status}` };
    }
    const data = await res.json().catch(() => ({}));
    return {
      ok: true,
      latency,
      message: data?.message || 'Kết nối thành công',
    };
  } catch (err) {
    return {
      ok: false,
      latency: Math.round(performance.now() - start),
      message: err instanceof Error ? err.message : 'Không thể kết nối',
    };
  }
}
