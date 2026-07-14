(function () {
  const TOKEN_KEY = "estagios_academicos_token";
  const USER_KEY = "estagios_academicos_user";
  const COMPANY_TOKEN_KEY = "estagios_academicos_company_token";
  const COMPANY_KEY = "estagios_academicos_company";

  function cookie(name) {
    const value = document.cookie.split("; ").find((item) => item.startsWith(`${name}=`));
    return value ? decodeURIComponent(value.split("=").slice(1).join("=")) : "";
  }

  async function request(path, options = {}, tokenKey = TOKEN_KEY) {
    const headers = new Headers(options.headers || {});
    const token = localStorage.getItem(tokenKey) || sessionStorage.getItem(tokenKey);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
    if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes((options.method || 'GET').toUpperCase())) {
      headers.set("X-CSRFToken", cookie("csrftoken"));
    }
    let response;
    try {
      response = await fetch(path, {...options, headers, credentials: "same-origin"});
    } catch (_) {
      throw new Error("Não foi possível concluir a operação. Verifique sua conexão e tente novamente.");
    }
    let body = null;
    if (response.status !== 204) {
      try {
        const text = await response.text();
        body = text.trim() ? JSON.parse(text) : null;
      } catch (_) {
        body = null;
      }
    }
    if (!response.ok) {
      const error = new Error(body?.error?.message || "Não foi possível concluir a operação.");
      error.status = response.status;
      throw error;
    }
    return body?.data ?? null;
  }

  function storeSession(tokenKey, dataKey, data, persistent = true) {
    const storage = persistent ? localStorage : sessionStorage;
    localStorage.removeItem(tokenKey);
    sessionStorage.removeItem(tokenKey);
    storage.setItem(tokenKey, data.access_token);
    storage.setItem(dataKey, JSON.stringify(data.user ?? data.company));
  }

  function requireAuth(tokenKey, loginPath) {
    if (!localStorage.getItem(tokenKey) && !sessionStorage.getItem(tokenKey)) {
      window.location.replace(loginPath + "?next=" + encodeURIComponent(window.location.pathname + window.location.search));
      return false;
    }
    return true;
  }

  function initials(name) {
    const normalized = String(name || "").trim();
    if (!normalized) return "";
    return normalized.split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
  }

  function companyInitials(name) {
    const first = String(name || "").trim().split(/\s+/)[0] || "";
    return first.slice(0, 2).toUpperCase();
  }

  function safeNextPath(candidate, allowedPath, fallback) {
    if (typeof candidate !== "string" || !candidate.startsWith("/") || candidate.startsWith("//") || candidate.includes("\\")) {
      return fallback;
    }
    try {
      const url = new URL(candidate, window.location.origin);
      if (url.origin !== window.location.origin || !allowedPath.test(url.pathname)) return fallback;
      return url.pathname + url.search + url.hash;
    } catch (_) {
      return fallback;
    }
  }

  window.Platform = {
    request: (path, options) => request(path, options, TOKEN_KEY),
    storeSession: (data, persistent) => storeSession(TOKEN_KEY, USER_KEY, data, persistent),
    requireAuth: () => requireAuth(TOKEN_KEY, "/aluno/"),
    safeNextPath: (candidate) => safeNextPath(candidate, /^\/(?:aluno(?:\/|$)|vagas(?:\/|$)|perfil(?:\/|$))/, "/vagas/"),
    initials,
    TOKEN_KEY,
    USER_KEY,
  };

  window.Company = {
    request: (path, options) => request(path, options, COMPANY_TOKEN_KEY),
    storeSession: (data, persistent) => storeSession(COMPANY_TOKEN_KEY, COMPANY_KEY, data, persistent),
    requireAuth: () => requireAuth(COMPANY_TOKEN_KEY, "/empresa/"),
    safeNextPath: (candidate) => safeNextPath(candidate, /^\/empresa(?:\/|$)/, "/empresa/vagas/"),
    initials: companyInitials,
    TOKEN_KEY: COMPANY_TOKEN_KEY,
    COMPANY_KEY,
  };
})();
