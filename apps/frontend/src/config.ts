const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000';
const maxFileSizeMb = Number(import.meta.env.VITE_MAX_FILE_SIZE_MB || '100');

export const config = {
  apiBaseUrl,
  maxFileSizeMb,
  maxFileSizeBytes: maxFileSizeMb * 1024 * 1024,
};

const USER_ID_STORAGE_KEY = 'morphix.userId';

export function getUserId(): string {
  const existing = window.localStorage.getItem(USER_ID_STORAGE_KEY);
  if (existing) {
    return existing;
  }

  const generated = `user_${crypto.randomUUID()}`;
  window.localStorage.setItem(USER_ID_STORAGE_KEY, generated);
  return generated;
}

