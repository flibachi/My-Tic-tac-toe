const els = {
    authForm: document.querySelector("#authForm"),
    loginInput: document.querySelector("#loginInput"),
    passwordInput: document.querySelector("#passwordInput"),
    registerButton: document.querySelector("#registerButton"),
    logoutButton: document.querySelector("#logoutButton"),
    authStatus: document.querySelector("#authStatus"),
    sessionLabel: document.querySelector("#sessionLabel"),
    modeButtons: document.querySelectorAll("[data-mode]"),
    opponentInput: document.querySelector("#opponentInput"),
    createGameButton: document.querySelector("#createGameButton"),
    refreshGamesButton: document.querySelector("#refreshGamesButton"),
    waitingGames: document.querySelector("#waitingGames"),
    gameIdInput: document.querySelector("#gameIdInput"),
    loadGameButton: document.querySelector("#loadGameButton"),
    gameTitle: document.querySelector("#gameTitle"),
    board: document.querySelector("#board"),
    stateText: document.querySelector("#stateText"),
    youText: document.querySelector("#youText"),
    turnText: document.querySelector("#turnText"),
    playerOne: document.querySelector("#playerOne"),
    playerTwo: document.querySelector("#playerTwo"),
    userLookupInput: document.querySelector("#userLookupInput"),
    lookupUserButton: document.querySelector("#lookupUserButton"),
    userLookupResult: document.querySelector("#userLookupResult"),
    toast: document.querySelector("#toast"),
};

const state = {
    login: localStorage.getItem("ttt_login") || "",
    password: localStorage.getItem("ttt_password") || "",
    userId: localStorage.getItem("ttt_user_id") || "",
    mode: "COMPUTER",
    game: null,
};

function authHeader() {
    const bytes = new TextEncoder().encode(`${state.login}:${state.password}`);
    const binary = Array.from(bytes, (byte) => String.fromCharCode(byte)).join("");
    return `Basic ${btoa(binary)}`;
}

async function api(path, options = {}) {
    const headers = {
        "Content-Type": "application/json",
        ...(options.auth === false ? {} : { Authorization: authHeader() }),
        ...options.headers,
    };
    const response = await fetch(path, { ...options, headers });
    const text = await response.text();
    const payload = text ? JSON.parse(text) : null;
    if (!response.ok) {
        throw new Error(payload?.error || payload?.message || `HTTP ${response.status}`);
    }
    return payload;
}

function toast(message, isError = false) {
    els.toast.textContent = message;
    els.toast.classList.toggle("error", isError);
    els.toast.classList.add("show");
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => els.toast.classList.remove("show"), 2600);
}

function saveSession(login, password, userId) {
    state.login = login;
    state.password = password;
    state.userId = userId;
    localStorage.setItem("ttt_login", login);
    localStorage.setItem("ttt_password", password);
    localStorage.setItem("ttt_user_id", userId);
    renderSession();
}

function clearSession() {
    state.login = "";
    state.password = "";
    state.userId = "";
    state.game = null;
    localStorage.removeItem("ttt_login");
    localStorage.removeItem("ttt_password");
    localStorage.removeItem("ttt_user_id");
    renderSession();
    renderGame();
    renderWaiting([]);
}

function renderSession() {
    const isOnline = Boolean(state.userId);
    els.authStatus.textContent = isOnline ? "online" : "offline";
    els.authStatus.classList.toggle("online", isOnline);
    els.sessionLabel.textContent = isOnline ? `${state.login} · ${state.userId}` : "Гость";
    els.loginInput.value = state.login;
    els.passwordInput.value = state.password;
}

function shortId(value) {
    if (!value) return "-";
    if (value === "COMPUTER") return "COMPUTER";
    return value.length > 12 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

function getMyMark(game) {
    if (!game || !state.userId) return "-";
    if (game.player1_id === state.userId) return game.player1_mark || "X";
    if (game.player2_id === state.userId) return game.player2_mark || "O";
    return "наблюдатель";
}

function readableState(game) {
    if (!game) return "-";
    if (game.state === "WAITING") return "ожидание второго игрока";
    if (game.state === "DRAW") return "ничья";
    if (game.state?.startsWith("WIN:")) {
        const winner = game.state.slice(4);
        return winner === state.userId ? "вы победили" : `победил ${shortId(winner)}`;
    }
    if (game.state?.startsWith("TURN:")) {
        const turn = game.state.slice(5);
        return turn === state.userId ? "ваш ход" : `ходит ${shortId(turn)}`;
    }
    return game.state || "-";
}

function canMove(row, col) {
    const game = state.game;
    return Boolean(
        game &&
        game.board?.[row]?.[col] === 0 &&
        game.state === `TURN:${state.userId}` &&
        getMyMark(game) !== "наблюдатель",
    );
}

function markToValue(mark) {
    return mark === "X" ? 1 : 2;
}

function valueToMark(value) {
    if (value === 1) return "X";
    if (value === 2) return "O";
    return "";
}

function renderBoard() {
    const board = state.game?.board || [[0, 0, 0], [0, 0, 0], [0, 0, 0]];
    els.board.replaceChildren();
    board.forEach((row, rowIndex) => {
        row.forEach((value, colIndex) => {
            const cell = document.createElement("button");
            const mark = valueToMark(value);
            cell.type = "button";
            cell.className = `cell ${mark.toLowerCase()}`;
            cell.textContent = mark;
            cell.disabled = !canMove(rowIndex, colIndex);
            cell.setAttribute("aria-label", mark || `Ход ${rowIndex + 1}:${colIndex + 1}`);
            cell.addEventListener("click", () => makeMove(rowIndex, colIndex));
            els.board.append(cell);
        });
    });
}

function renderGame() {
    const game = state.game;
    els.gameTitle.textContent = game ? shortId(game.id) : "Партия не выбрана";
    els.gameIdInput.value = game?.id || els.gameIdInput.value;
    els.stateText.textContent = readableState(game);
    els.youText.textContent = getMyMark(game);
    els.turnText.textContent = game?.state?.startsWith("TURN:")
        ? shortId(game.state.slice(5))
        : "-";
    els.playerOne.textContent = game?.player1_id || "-";
    els.playerTwo.textContent = game?.player2_id || "-";
    renderBoard();
}

function renderWaiting(games) {
    els.waitingGames.replaceChildren();
    if (!games.length) {
        const empty = document.createElement("div");
        empty.className = "user-card";
        empty.textContent = "Нет открытых партий";
        els.waitingGames.append(empty);
        return;
    }
    games.forEach((game) => {
        const item = document.createElement("article");
        item.className = "waiting-item";
        item.innerHTML = `<code>${game.id}</code><span>Создатель: ${shortId(game.player1_id)}</span>`;
        const join = document.createElement("button");
        join.type = "button";
        join.textContent = "Подключиться";
        join.disabled = game.player1_id === state.userId;
        join.addEventListener("click", () => joinGame(game.id));
        item.append(join);
        els.waitingGames.append(item);
    });
}

async function login() {
    const loginValue = els.loginInput.value.trim();
    const passwordValue = els.passwordInput.value;
    state.login = loginValue;
    state.password = passwordValue;
    const payload = await api("/auth/login", { method: "POST", auth: true });
    saveSession(loginValue, passwordValue, payload.user_id);
    toast("Вход выполнен");
    refreshGames();
}

async function register() {
    const loginValue = els.loginInput.value.trim();
    const passwordValue = els.passwordInput.value;
    await api("/auth/register", {
        method: "POST",
        auth: false,
        body: JSON.stringify({ login: loginValue, password: passwordValue }),
    });
    toast("Пользователь создан");
    await login();
}

async function createGame() {
    const opponent = els.opponentInput.value.trim();
    const payload = await api("/game", {
        method: "POST",
        body: JSON.stringify({
            mode: state.mode,
            ...(opponent ? { opponent_user_id: opponent } : {}),
        }),
    });
    state.game = payload;
    renderGame();
    refreshGames();
    toast("Игра создана");
}

async function refreshGames() {
    if (!state.userId) return renderWaiting([]);
    const games = await api("/game/available");
    renderWaiting(games);
}

async function joinGame(gameId) {
    await api(`/game/${gameId}/join`, { method: "POST" });
    await loadGame(gameId);
    await refreshGames();
    toast("Вы подключились к игре");
}

async function loadGame(gameId = els.gameIdInput.value.trim()) {
    if (!gameId) return;
    state.game = await api(`/game/${encodeURIComponent(gameId)}`);
    renderGame();
    toast("Партия загружена");
}

async function makeMove(row, col) {
    const nextBoard = state.game.board.map((line) => [...line]);
    nextBoard[row][col] = markToValue(getMyMark(state.game));
    const payload = await api(`/game/${state.game.id}`, {
        method: "POST",
        body: JSON.stringify({ board: nextBoard }),
    });
    state.game = { ...state.game, ...payload };
    renderGame();
}

async function lookupUser() {
    const userId = els.userLookupInput.value.trim();
    if (!userId) return;
    const user = await api(`/user/${encodeURIComponent(userId)}`);
    els.userLookupResult.textContent = `${user.login} · ${user.id}`;
}

function wireEvents() {
    els.authForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            await login();
        } catch (error) {
            toast(error.message, true);
        }
    });
    els.registerButton.addEventListener("click", async () => {
        try {
            await register();
        } catch (error) {
            toast(error.message, true);
        }
    });
    els.logoutButton.addEventListener("click", () => {
        clearSession();
        toast("Сессия очищена");
    });
    els.modeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            state.mode = button.dataset.mode;
            els.modeButtons.forEach((item) => item.classList.toggle("active", item === button));
        });
    });
    els.createGameButton.addEventListener("click", async () => {
        try {
            await createGame();
        } catch (error) {
            toast(error.message, true);
        }
    });
    els.refreshGamesButton.addEventListener("click", async () => {
        try {
            await refreshGames();
        } catch (error) {
            toast(error.message, true);
        }
    });
    els.loadGameButton.addEventListener("click", async () => {
        try {
            await loadGame();
        } catch (error) {
            toast(error.message, true);
        }
    });
    els.lookupUserButton.addEventListener("click", async () => {
        try {
            await lookupUser();
        } catch (error) {
            els.userLookupResult.textContent = error.message;
            toast(error.message, true);
        }
    });
}

wireEvents();
renderSession();
renderGame();
if (state.userId) {
    refreshGames().catch((error) => toast(error.message, true));
}
