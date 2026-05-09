(function () {
  const SUPABASE_URL = "https://bniqmxbtvgwkaoswugds.supabase.co";
  const SUPABASE_ANON_KEY =
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJuaXFteGJ0dmd3a2Fvc3d1Z2RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzc4NTExMTYsImV4cCI6MjA5MzQyNzExNn0.VXjnGv3uV8A2XfAW5jOBAkxyzc9c9q6adrA64JfwrQs";

  if (!window.supabase || !window.supabase.createClient) {
    console.error("Supabase client not loaded");
    return;
  }

  const client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
      detectSessionInUrl: true
    }
  });

  let currentSession = null;
  let authReadyResolve;
  const authReady = new Promise((resolve) => {
    authReadyResolve = resolve;
  });

  const authState = {
    gateTitle: "Yonetici girisi gerekli",
    gateMessage:
      "Bu islem sadece senin yonetici oturumunla acik. Normal ziyaretciler siteyi giris yapmadan kullanmaya devam eder.",
    pendingResolve: null
  };

  function injectStyles() {
    if (document.getElementById("rp5-auth-style")) return;
    const style = document.createElement("style");
    style.id = "rp5-auth-style";
    style.textContent =
      ".rp5-authbar{display:flex;justify-content:center;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}" +
      ".rp5-authbtn{background:#1c2238;border:1px solid #2a3149;color:#00d4ff;padding:6px 12px;border-radius:8px;text-decoration:none;font-size:.8rem;font-weight:600;cursor:pointer}" +
      ".rp5-authbtn:hover{border-color:#00d4ff}" +
      ".rp5-authstatus{font-size:.78rem;color:#8c93a8}" +
      ".rp5-authoverlay{position:fixed;inset:0;background:rgba(0,0,0,.72);backdrop-filter:blur(10px);display:none;align-items:center;justify-content:center;padding:20px;z-index:9999}" +
      ".rp5-authoverlay.open{display:flex}" +
      ".rp5-authcard{width:min(440px,100%);background:#131829;border:1px solid #2a3149;border-radius:18px;padding:22px;color:#e8eaf0}" +
      ".rp5-authcard h2{margin:0 0 8px;font:800 26px/1.15 'Segoe UI',system-ui,sans-serif;color:#fff}" +
      ".rp5-authcard p{margin:0 0 16px;color:#8c93a8;font:14px/1.5 'Segoe UI',system-ui,sans-serif}" +
      ".rp5-authgrid{display:grid;gap:10px}" +
      ".rp5-authinput{width:100%;background:#1c2238;border:1px solid #2a3149;border-radius:10px;padding:11px 12px;color:#e8eaf0;font:14px/1.2 'Segoe UI',system-ui,sans-serif}" +
      ".rp5-authinput:focus{outline:none;border-color:#00d4ff}" +
      ".rp5-authactions{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}" +
      ".rp5-authprimary{background:#00d4ff;color:#0a0e1a;border:none;border-radius:10px;padding:10px 14px;font:700 14px/1 'Segoe UI',system-ui,sans-serif;cursor:pointer}" +
      ".rp5-authsecondary{background:#1c2238;color:#e8eaf0;border:1px solid #2a3149;border-radius:10px;padding:10px 14px;font:700 14px/1 'Segoe UI',system-ui,sans-serif;cursor:pointer}" +
      ".rp5-authnote{margin-top:12px;font:12px/1.45 'Segoe UI',system-ui,sans-serif;color:#8c93a8}" +
      ".rp5-autherror{margin-top:10px;color:#ff8f8f;font:12px/1.45 'Segoe UI',system-ui,sans-serif;display:none}" +
      ".rp5-lockscreen{max-width:720px;margin:48px auto;padding:24px;background:#131829;border:1px solid #2a3149;border-radius:16px}" +
      ".rp5-lockscreen h1{margin:0 0 12px;font-size:28px;color:#fff}" +
      ".rp5-lockscreen p{margin:0 0 16px;color:#cbd3e1;line-height:1.6}" +
      ".rp5-readonlyhint{font-size:.76rem;color:#8c93a8;margin-top:8px}";
    document.head.appendChild(style);
  }

  function ensureModal() {
    if (document.getElementById("rp5-auth-overlay")) return;
    injectStyles();
    const overlay = document.createElement("div");
    overlay.id = "rp5-auth-overlay";
    overlay.className = "rp5-authoverlay";
    overlay.innerHTML =
      '<div class="rp5-authcard">' +
      '<h2 id="rp5-auth-title">Yonetici girisi gerekli</h2>' +
      '<p id="rp5-auth-message">Bu alan yazma yetkisi istiyor.</p>' +
      '<div class="rp5-authgrid">' +
      '<input class="rp5-authinput" id="rp5-auth-email" type="email" placeholder="E-posta">' +
      '<input class="rp5-authinput" id="rp5-auth-password" type="password" placeholder="Sifre">' +
      "</div>" +
      '<div class="rp5-authactions">' +
      '<button class="rp5-authprimary" id="rp5-auth-submit">Giris yap</button>' +
      '<button class="rp5-authsecondary" id="rp5-auth-cancel">Kapat</button>' +
      "</div>" +
      '<div class="rp5-autherror" id="rp5-auth-error"></div>' +
      '<div class="rp5-authnote">Oturum tarayicida saklanir. Bir kez giris yaptiginda tekrar tekrar sorulmaz.</div>' +
      "</div>";
    document.body.appendChild(overlay);

    document
      .getElementById("rp5-auth-submit")
      .addEventListener("click", async function () {
        const email = document.getElementById("rp5-auth-email").value.trim();
        const password = document.getElementById("rp5-auth-password").value;
        const errorEl = document.getElementById("rp5-auth-error");
        errorEl.style.display = "none";
        if (!email || !password) {
          errorEl.textContent = "E-posta ve sifre gerekli.";
          errorEl.style.display = "block";
          return;
        }
        const result = await client.auth.signInWithPassword({ email, password });
        if (result.error) {
          errorEl.textContent = result.error.message;
          errorEl.style.display = "block";
          return;
        }
        closeAuthModal(true);
      });

    document
      .getElementById("rp5-auth-cancel")
      .addEventListener("click", function () {
        closeAuthModal(false);
      });
    overlay.addEventListener("click", function (event) {
      if (event.target === overlay) closeAuthModal(false);
    });
  }

  function openAuthModal(title, message) {
    ensureModal();
    authState.gateTitle = title || authState.gateTitle;
    authState.gateMessage = message || authState.gateMessage;
    document.getElementById("rp5-auth-title").textContent = authState.gateTitle;
    document.getElementById("rp5-auth-message").textContent =
      authState.gateMessage;
    document.getElementById("rp5-auth-error").style.display = "none";
    document.getElementById("rp5-auth-overlay").classList.add("open");
    document.getElementById("rp5-auth-email").focus();
  }

  function closeAuthModal(success) {
    const overlay = document.getElementById("rp5-auth-overlay");
    if (overlay) overlay.classList.remove("open");
    if (authState.pendingResolve) {
      authState.pendingResolve(!!success);
      authState.pendingResolve = null;
    }
  }

  function setAuthUi(session) {
    document.querySelectorAll("[data-auth-status]").forEach((el) => {
      el.textContent = session
        ? "Yonetici oturumu acik"
        : "Public mod: giris yapmadan okunabilir";
    });
    document.querySelectorAll("[data-auth-login]").forEach((el) => {
      el.textContent = session ? "Cikis yap" : "Yonetici girisi";
      el.onclick = async function () {
        if (currentSession) {
          await client.auth.signOut();
        } else {
          openAuthModal(
            "Yonetici girisi",
            "Yazma yetkileri ve yonetim ekranlari icin giris yap."
          );
        }
      };
    });
    document.querySelectorAll("[data-auth-required-link]").forEach((el) => {
      el.style.display = session ? "" : "none";
    });
  }

  async function requireAuth(options) {
    await authReady;
    if (currentSession) return true;
    const opts = options || {};
    openAuthModal(opts.title, opts.message);
    return new Promise((resolve) => {
      authState.pendingResolve = resolve;
    });
  }

  async function lockAdminPage(options) {
    const ok = await requireAuth(options);
    if (ok) return true;
    document.body.innerHTML =
      '<main class="rp5-lockscreen">' +
      "<h1>Yonetici girisi gerekli</h1>" +
      "<p>Bu sayfa veri yazma ve yonetim islemleri icin ayrildi. Normal kullanim icin siteyi giris yapmadan gezebilirsin; bu ekran icin yonetici oturumu gerekiyor.</p>" +
      '<p><a class="rp5-authbtn" href="index.html">Hub sayfasina don</a></p>' +
      "</main>";
    return false;
  }

  function injectAuthBar() {
    const targets = document.querySelectorAll("[data-auth-mount]");
    targets.forEach((target) => {
      if (target.querySelector(".rp5-authbar")) return;
      const wrap = document.createElement("div");
      wrap.className = "rp5-authbar";
      wrap.innerHTML =
        '<button class="rp5-authbtn" type="button" data-auth-login>Yonetici girisi</button>' +
        '<span class="rp5-authstatus" data-auth-status>Public mod: giris yapmadan okunabilir</span>';
      target.appendChild(wrap);
    });
  }

  client.auth.getSession().then(({ data }) => {
    currentSession = data.session || null;
    authReadyResolve();
    setAuthUi(currentSession);
  });

  client.auth.onAuthStateChange(function (_event, session) {
    currentSession = session || null;
    setAuthUi(currentSession);
  });

  document.addEventListener("DOMContentLoaded", function () {
    injectAuthBar();
    setAuthUi(currentSession);
  });

  window.rp5Auth = {
    client,
    requireAuth,
    lockAdminPage,
    getSession: function () {
      return currentSession;
    }
  };
})();
