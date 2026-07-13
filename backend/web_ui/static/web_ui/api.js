(function () {
  const TOKEN_KEY = "estagios_academicos_token";
  const USER_KEY = "estagios_academicos_user";

  function cookie(name) {
    const value = document.cookie.split("; ").find((item) => item.startsWith(`${name}=`));
    return value ? decodeURIComponent(value.split("=").slice(1).join("=")) : "";
  }

  async function request(path, options = {}) {
    const headers = new Headers(options.headers || {});
    const token = localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes((options.method || 'GET').toUpperCase())) {
      headers.set("X-CSRFToken", cookie("csrftoken"));
    }
    const response = await fetch(path, {...options, headers, credentials: "same-origin"});
    let body = null;
    if (response.status !== 204) body = await response.json();
    if (!response.ok) {
      const error = new Error(body?.error?.message || "Não foi possível concluir a operação.");
      error.status = response.status;
      throw error;
    }
    return body?.data ?? null;
  }

  function storeSession(data, persistent = true) {
    const storage = persistent ? localStorage : sessionStorage;
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    storage.setItem(TOKEN_KEY, data.access_token);
    storage.setItem(USER_KEY, JSON.stringify(data.user));
  }

  function requireAuth() {
    if (!localStorage.getItem(TOKEN_KEY) && !sessionStorage.getItem(TOKEN_KEY)) {
      window.location.replace("/?next=" + encodeURIComponent(window.location.pathname));
      return false;
    }
    return true;
  }

  function initials(name) {
    const normalized = String(name || "").trim();
    if (!normalized) return "";
    return normalized.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
  }

  window.Platform = {request, storeSession, requireAuth, initials, TOKEN_KEY, USER_KEY};
})();
