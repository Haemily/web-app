import type { Session } from './types';

let csrf = '';
export function setSession(session: Session | null) { csrf = session?.csrf_token ?? ''; }

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = options.method ?? 'GET';
  const response = await fetch(`/api${path}`, {
    ...options,
    credentials: 'same-origin',
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(method !== 'GET' && csrf ? { 'X-CSRF-Token': csrf } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const detail = payload.detail;
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map((x: { msg: string }) => x.msg).join('; ') : `Request failed (${response.status})`);
  }
  return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}

export function json(method: 'POST' | 'PUT' | 'PATCH' | 'DELETE', body?: unknown): RequestInit {
  return { method, ...(body === undefined ? {} : { body: JSON.stringify(body) }) };
}
