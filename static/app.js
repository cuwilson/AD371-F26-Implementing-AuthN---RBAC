'use strict';
let csrf = null;
const $ = id => document.getElementById(id);
async function api(path, method = 'GET', body = null) {
  const headers = {};
  if (body !== null) headers['Content-Type'] = 'application/json';
  if (csrf && method !== 'GET') headers['X-CSRF-Token'] = csrf;
  try {
    const res = await fetch(path, {method, credentials: 'same-origin', headers,
      ...(body !== null ? {body: JSON.stringify(body)} : {})});
    const result = await res.json();
    $('output').textContent = `${method} ${path} — HTTP ${res.status}\n${JSON.stringify(result, null, 2)}`;
    return {ok: res.ok, result};
  } catch (error) {
    $('output').textContent = `Network error: ${error.message}`;
    return {ok: false};
  }
}
async function refresh() {
  const r = await api('/api/me');
  csrf = r.ok ? r.result.csrf_token : null;
  $('status').textContent = r.ok ? `Signed in as ${r.result.user.username} (${r.result.user.role})` : 'Not authenticated';
}
async function auth(path) {
  const username = $('username').value, password = $('password').value;
  if (!username || !password) return $('auth').reportValidity();
  const r = await api(path, 'POST', {username, password});
  if (r.ok && path === '/api/login') {
    $('password').value = '';
    await refresh();
  }
}
$('register').addEventListener('click', () => auth('/api/register'));
$('login').addEventListener('click', () => auth('/api/login'));
$('public').addEventListener('click', () => api('/api/public'));
$('profile').addEventListener('click', refresh);
$('admin').addEventListener('click', () => api('/api/admin/users'));
$('logout').addEventListener('click', async () => {
  const r = await api('/api/logout', 'POST');
  if (r.ok) { csrf = null; $('status').textContent = 'Not authenticated'; }
});
refresh();
