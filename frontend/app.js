/**
 * Javascript logic for the IPTV Frontend.
 * Responsible for handling state (JWT), navigation, and API interactions.
 * Built with clean code practices: small functions, clear naming.
 */

const API_BASE_URL = "http://127.0.0.1:8000";

// DOM Elements
const elements = {
    views: {
        login: document.getElementById("login-view"),
        dashboard: document.getElementById("dashboard-view")
    },
    login: {
        form: document.getElementById("login-form"),
        btnText: document.querySelector("#login-btn .btn-text"),
        loader: document.querySelector("#login-btn .loader"),
        error: document.getElementById("login-error")
    },
    dashboard: {
        badge: document.getElementById("user-badge"),
        channelsContainer: document.getElementById("channels-container"),
        error: document.getElementById("global-error"),
        logoutBtn: document.getElementById("logout-btn")
    }
};

/**
 * Initializes the application by checking existing authentication state.
 */
function initApp() {
    const token = localStorage.getItem("iptv_token");
    if (token) {
        verifyTokenAndLoadDashboard(token);
    }
    setupEventListeners();
}

/**
 * Binds DOM events to handler functions.
 */
function setupEventListeners() {
    elements.login.form.addEventListener("submit", handleLoginSubmit);
    elements.dashboard.logoutBtn.addEventListener("click", handleLogout);
}

/**
 * Handles the login form submission.
 */
async function handleLoginSubmit(event) {
    event.preventDefault();
    hideError(elements.login.error);
    setLoadingState(true);

    const formData = new FormData(event.target);
    const params = new URLSearchParams(formData);

    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: params.toString()
        });

        if (!response.ok) {
            throw new Error("Credenciais inválidas");
        }

        const data = await response.json();
        localStorage.setItem("iptv_token", data.access_token);
        
        await verifyTokenAndLoadDashboard(data.access_token);
    } catch (error) {
        showError(elements.login.error, error.message);
    } finally {
        setLoadingState(false);
    }
}

/**
 * Verifies the JWT token and loads the dashboard if valid.
 */
async function verifyTokenAndLoadDashboard(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/me`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error("Sessão expirada");
        }

        const userData = await response.json();
        elements.dashboard.badge.textContent = `Perfil: ${userData.perfil.toUpperCase()}`;
        
        await fetchAndRenderChannels(token);
        switchView("dashboard");
    } catch (error) {
        handleLogout();
    }
}

/**
 * Fetches the available channels from the API and renders them in the grid.
 */
async function fetchAndRenderChannels(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/channels`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!response.ok) {
            throw new Error("Falha ao carregar canais");
        }

        const channels = await response.json();
        renderChannels(channels);
    } catch (error) {
        showError(elements.dashboard.error, error.message);
    }
}

/**
 * Generates the HTML for the channel cards.
 */
function renderChannels(channels) {
    elements.dashboard.channelsContainer.innerHTML = "";
    
    channels.forEach(channel => {
        const card = document.createElement("div");
        card.className = "channel-card";
        card.innerHTML = `
            <span class="channel-icon">▶</span>
            <h3>${channel.nome}</h3>
            <button class="btn-primary" style="width: 100%; margin-top: 1rem;">Assistir</button>
        `;
        
        card.addEventListener("click", () => handlePlayChannel(channel.id));
        elements.dashboard.channelsContainer.appendChild(card);
    });
}

/**
 * Initiates the playback process by requesting the .m3u file.
 * Handles the WAN115K specific bottlenecks (HTTP 429).
 */
async function handlePlayChannel(channelId) {
    hideError(elements.dashboard.error);
    const token = localStorage.getItem("iptv_token");
    
    try {
        const response = await fetch(`${API_BASE_URL}/play/${channelId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.status === 429) {
            const errData = await response.json();
            throw new Error(errData.detail);
        }

        if (!response.ok) {
            throw new Error("Erro ao iniciar a transmissão. Tente novamente.");
        }

        // Handles the file download automatically
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `canal_${channelId}.m3u`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);

    } catch (error) {
        showError(elements.dashboard.error, error.message);
    }
}

/**
 * Logs the user out and clears state.
 */
function handleLogout() {
    localStorage.removeItem("iptv_token");
    elements.login.form.reset();
    hideError(elements.login.error);
    hideError(elements.dashboard.error);
    switchView("login");
}

/* --- UI Utility Functions --- */

function switchView(viewName) {
    elements.views.login.classList.remove("active");
    elements.views.dashboard.classList.remove("active");
    
    setTimeout(() => {
        elements.views[viewName].classList.add("active");
    }, 10);
}

function setLoadingState(isLoading) {
    if (isLoading) {
        elements.login.btnText.classList.add("hidden");
        elements.login.loader.classList.remove("hidden");
        elements.login.form.querySelectorAll("input, button").forEach(el => el.disabled = true);
    } else {
        elements.login.btnText.classList.remove("hidden");
        elements.login.loader.classList.add("hidden");
        elements.login.form.querySelectorAll("input, button").forEach(el => el.disabled = false);
    }
}

function showError(element, message) {
    element.textContent = message;
    element.classList.remove("hidden");
}

function hideError(element) {
    element.classList.add("hidden");
    element.textContent = "";
}

// Bootstrap
document.addEventListener("DOMContentLoaded", initApp);
