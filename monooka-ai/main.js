import "./style.css";

const API_BASE = "http://localhost:8000/api";

// Elements
const chatInput = document.getElementById("chat-input");
const sendBtn = document.getElementById("send-btn");
const messagesList = document.getElementById("messages-list");
const welcomeScreen = document.getElementById("welcome-screen");
const themeToggle = document.getElementById("theme-toggle");
const menuBtn = document.getElementById("menu-btn");
const mobileMenuBtn = document.getElementById("mobile-menu-btn");
const sidebar = document.getElementById("sidebar");
const historyList = document.getElementById("history-list");
const contextSelect = document.getElementById("context-select");
const newChatBtn = document.getElementById("new-chat-btn");

let currentChatId = null;

// Initialization
async function init() {
	await loadHistory();
	// Optionally create a default empty chat on load
	// await createNewChat();
}

// Auto-resize textarea
chatInput.addEventListener("input", function () {
	this.style.height = "auto";
	this.style.height = `${this.scrollHeight}px`;

	if (this.value.trim().length > 0) {
		sendBtn.removeAttribute("disabled");
	} else {
		sendBtn.setAttribute("disabled", "true");
	}
});

// Handle enter key to send
chatInput.addEventListener("keydown", (e) => {
	if (e.key === "Enter" && !e.shiftKey) {
		e.preventDefault();
		sendMessage();
	}
});

sendBtn.addEventListener("click", sendMessage);
newChatBtn.addEventListener("click", createNewChat);

// Theme Toggle
let isDark = true;
themeToggle.addEventListener("click", () => {
	isDark = !isDark;
	if (isDark) {
		document.body.removeAttribute("data-theme");
	} else {
		document.body.setAttribute("data-theme", "light");
	}
});

// Sidebar Toggle (Desktop & Mobile)
menuBtn.addEventListener("click", () => sidebar.classList.toggle("collapsed"));
mobileMenuBtn.addEventListener("click", () => sidebar.classList.toggle("open"));

document.addEventListener("click", (e) => {
	if (
		window.innerWidth <= 768 &&
		sidebar.classList.contains("open") &&
		!sidebar.contains(e.target) &&
		e.target !== mobileMenuBtn &&
		!mobileMenuBtn.contains(e.target)
	) {
		sidebar.classList.remove("open");
	}
});

// API Calls
async function loadHistory() {
	try {
		const res = await fetch(`${API_BASE}/history`);
		const history = await res.json();
		renderHistory(history);
	} catch (e) {
		console.error("Failed to load history", e);
	}
}

function renderHistory(history) {
	historyList.innerHTML = "";
	history.forEach((chat) => {
		const div = document.createElement("div");
		div.className = `history-item ${chat.id === currentChatId ? "active" : ""}`;
		div.textContent = chat.title || "New Chat";
		div.onclick = () => loadChat(chat.id);
		historyList.appendChild(div);
	});
}

async function createNewChat() {
	const context = contextSelect.value;
	try {
		const res = await fetch(`${API_BASE}/chat`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ context }),
		});
		const chat = await res.json();
		currentChatId = chat.id;

		// Clear UI
		messagesList.innerHTML = "";
		welcomeScreen.style.display = "flex";
		welcomeScreen.innerHTML = `
			<h1 class="welcome-title">Hello, Elina</h1>
			<p class="welcome-subtitle">Testing context: ${context}.ipynb</p>
		`;

		await loadHistory(); // refresh sidebar
	} catch (e) {
		console.error("Failed to create chat", e);
	}
}

async function loadChat(chatId) {
	try {
		const res = await fetch(`${API_BASE}/chat/${chatId}`);
		const chat = await res.json();
		currentChatId = chat.id;

		messagesList.innerHTML = "";
		welcomeScreen.style.display = chat.messages.length ? "none" : "flex";

		// Update context select to match this chat
		contextSelect.value = chat.context;

		chat.messages.forEach((msg) => {
			appendMessage(msg.role, msg.content);
		});
		await loadHistory(); // update active state in sidebar
	} catch (e) {
		console.error("Failed to load chat", e);
	}
}

async function sendMessage() {
	const text = chatInput.value.trim();
	if (!text) return;

	if (!currentChatId) {
		await createNewChat();
	}

	welcomeScreen.style.display = "none";
	appendMessage("user", text);

	chatInput.value = "";
	chatInput.style.height = "auto";
	sendBtn.setAttribute("disabled", "true");
	scrollToBottom();

	const typingId = showTypingIndicator();

	try {
		const res = await fetch(`${API_BASE}/message`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ chat_id: currentChatId, content: text }),
		});

		removeTypingIndicator(typingId);

		if (res.ok) {
			const data = await res.json();
			appendMessage("bot", data.message);
		} else {
			appendMessage("bot", "Error communicating with server.");
		}

		await loadHistory(); // update title if changed
	} catch (e) {
		removeTypingIndicator(typingId);
		appendMessage("bot", "Network error.");
		console.error(e);
	}
}

function appendMessage(role, text) {
	const messageDiv = document.createElement("div");
	messageDiv.className = `message ${role === "assistant" ? "bot" : role}`;

	const initial = role === "user" ? "E" : "M";

	messageDiv.innerHTML = `
    <div class="avatar">${initial}</div>
    <div class="message-content">${escapeHTML(text)}</div>
  `;

	messagesList.appendChild(messageDiv);
	scrollToBottom();
}

function showTypingIndicator() {
	const id = `typing-${Date.now()}`;
	const messageDiv = document.createElement("div");
	messageDiv.className = "message bot";
	messageDiv.id = id;

	messageDiv.innerHTML = `
    <div class="avatar">M</div>
    <div class="message-content">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;

	messagesList.appendChild(messageDiv);
	scrollToBottom();
	return id;
}

function removeTypingIndicator(id) {
	const element = document.getElementById(id);
	if (element) {
		element.remove();
	}
}

function scrollToBottom() {
	const chatContainer = document.getElementById("chat-container");
	chatContainer.scrollTop = chatContainer.scrollHeight;
}

function escapeHTML(str) {
	return str
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;")
		.replace(/\n/g, "<br>");
}

init();
