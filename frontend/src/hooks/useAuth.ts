interface AuthUser {
  id: number;
  name: string;
  email: string;
  credits: number;
}

export function getToken(): string | null {
  return localStorage.getItem('token');
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}

export function getUser(): AuthUser | null {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setUser(user: AuthUser) {
  localStorage.setItem('user', JSON.stringify(user));
}

export function isAuthenticated(): boolean {
  return !!getToken();
}
