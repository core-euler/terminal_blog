/** Клиент публичного API. Сервер живёт на домашнем сервере и проксируется через `/api`. */

export interface CommentAuthor {
  kind: 'human' | 'agent';
  name: string;
}

export interface CommentItem {
  id: string;
  author: CommentAuthor;
  text: string;
  created_at: string;
}

export interface CommentReceipt {
  id: string;
  status: string;
  message: string;
}

/** Адрес API: в сборке задаётся PUBLIC_API_BASE, по умолчанию тот же домен. */
export const API_BASE = (import.meta.env.PUBLIC_API_BASE ?? '/api').replace(/\/+$/, '');

/** Ошибка с кодом ответа: интерфейс показывает текст, а не «что-то пошло не так». */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

function explain(status: number, payload: unknown): string {
  const body = payload as { message?: string; detail?: unknown };
  if (typeof body?.message === 'string' && body.message) return body.message;
  if (Array.isArray(body?.detail)) {
    const first = body.detail[0] as { msg?: string } | undefined;
    if (first?.msg) return 'проверьте поля формы';
  }
  if (status === 404) return 'не найдено';
  if (status === 429) return 'слишком много попыток, попробуйте позже';
  if (status >= 500) return 'сервер недоступен, попробуйте позже';
  return 'запрос отклонён';
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
  } catch {
    throw new ApiError(0, 'нет связи с сервером');
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, explain(response.status, payload));
  return payload as T;
}

export const fetchComments = (slug: string) =>
  request<{ items: CommentItem[] }>(`/news/${encodeURIComponent(slug)}/comments`);

export const postComment = (slug: string, text: string, name: string, clientId: string) =>
  request<CommentReceipt>(`/news/${encodeURIComponent(slug)}/comments`, {
    method: 'POST',
    headers: { 'X-Idempotency-Key': clientId },
    body: JSON.stringify({ text, name: name.trim() ? name.trim() : null, client_id: clientId }),
  });
