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
const curriculumContainer = document.getElementById("curriculum-container");

let currentChatId = null;
let curriculumData = [];

// Initialization
async function init() {
	const params = new URLSearchParams(window.location.search);
	const initialLesson = params.get("lesson");
	if (initialLesson) {
		currentChatId = initialLesson;
	}
	
	await loadCurriculum();
	
	if (currentChatId) {
		let foundLesson = null;
		for (const proj of curriculumData) {
			for (const l of proj.lessons) {
				if (l.id === currentChatId) {
					foundLesson = l;
					break;
				}
			}
		}
		if (foundLesson) {
			await loadChat(foundLesson.id, foundLesson.title);
		}
	}
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
sendBtn.addEventListener("click", sendMessage);

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
// API Calls
async function loadCurriculum() {
	try {
		const res = await fetch(`${API_BASE}/curriculum`);
		curriculumData = await res.json();
		renderCurriculum();
	} catch (e) {
		console.error("Failed to load curriculum", e);
	}
}

function renderCurriculum() {
	curriculumContainer.innerHTML = "";
	curriculumData.forEach((proj) => {
		const projDiv = document.createElement("div");
		projDiv.className = "curriculum-project";
		
		const header = document.createElement("div");
		header.className = "project-header";
		header.innerHTML = `
			<div class="title-wrapper">
				<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
					<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
				</svg>
				<span title="${proj.title}">${proj.title}</span>
			</div>
			<svg class="chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
				<polyline points="6 9 12 15 18 9"></polyline>
			</svg>
		`;
		
		const lessonsList = document.createElement("div");
		lessonsList.className = "lessons-list";
		
		// Simple accordion toggle
		header.onclick = () => {
			lessonsList.classList.toggle("open");
			header.classList.toggle("open");
		};
		
		proj.lessons.forEach((lesson) => {
			const item = document.createElement("div");
			item.className = `lesson-item ${lesson.id === currentChatId ? "active" : ""}`;
			item.textContent = lesson.title;
			item.title = lesson.title;
			item.onclick = (e) => {
				e.stopPropagation();
				loadChat(lesson.id, lesson.title);
			};
			lessonsList.appendChild(item);
		});
		
		// Auto open project containing the active lesson or the first project
		const isActiveProject = proj.lessons.some(l => l.id === currentChatId);
		if (isActiveProject || (!currentChatId && curriculumData.indexOf(proj) === 0)) {
			lessonsList.classList.add("open");
			header.classList.add("open");
		}
		
		projDiv.appendChild(header);
		projDiv.appendChild(lessonsList);
		curriculumContainer.appendChild(projDiv);
	});
}

async function loadChat(lessonId, lessonTitle) {
	try {
		// Update URL without page reload
		window.history.pushState({}, "", "?lesson=" + lessonId);
		
		const res = await fetch(`${API_BASE}/chat/${lessonId}`);
		if (!res.ok) throw new Error("Failed to load chat");
		const chat = await res.json();
		
		currentChatId = chat.id;

		messagesList.innerHTML = "";
		welcomeScreen.style.display = chat.messages.length ? "none" : "flex";

		if (!chat.messages.length) {
			welcomeScreen.innerHTML = `
				<h1 class="welcome-title">${lessonTitle || chat.title}</h1>
				<p class="welcome-subtitle">Testing context: ${chat.context}</p>
			`;
		}

		chat.messages.forEach((msg) => {
			appendMessage(msg.role, msg.content);
		});
		
		// Update active state in sidebar
		renderCurriculum();
		
		if (window.innerWidth <= 768) {
			sidebar.classList.remove("open");
		}
	} catch (e) {
		console.error("Failed to load chat", e);
	}
}

async function sendMessage() {
	const text = chatInput.value.trim();
	if (!text) return;

	if (!currentChatId) {
		alert("Please select a lesson from the sidebar first.");
		return;
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

		await loadCurriculum(); // update active state if changed
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
    <div class="message-content markdown-body">${marked.parse(text)}</div>
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


init();
