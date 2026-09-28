/* ==============================================
   ARIANNA AI — Advanced Multimodal Assistant
   Branded using "Arianna AI.pptx" design system
   ============================================== */

// ─── Config ───
const STORAGE_KEY = 'arianna_chats_v1';
const MAX_RECENTS = 25;
const DEFAULT_MODEL = 'gemini-3.8-flash';

const PERSONAS = {
    'default': { name: 'General Assistant', icon: 'auto_awesome' },
    'homework': { name: 'Homework Help', icon: 'menu_book' },
    'writing': { name: 'Writing Help', icon: 'edit_note' },
    'coding': { name: 'Coding Hints', icon: 'code' },
    'quick': { name: 'Quick Answers', icon: 'lightbulb' }
};

// ─── State ───
let chats = JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
let activeChatId = null;
let activeModel = DEFAULT_MODEL;
let activeAgentId = 'default';
let isGenerating = false;
let activeController = null;
let pendingAttachments = []; // Array of { name, mimeType, dataUrl }
let recognition = null;
let isListening = false;
let currentUtterance = null;
let activeSpeakingBtn = null;

// ─── DOM Elements ───
const welcomeScreen = document.getElementById('welcome-screen');
const messagesFeed = document.getElementById('messages-feed');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const recentsList = document.getElementById('recents-list');
const recentsSearch = document.getElementById('recents-search');
const currentTitle = document.getElementById('current-chat-title');
const modelSelectorBtn = document.getElementById('model-selector-btn');
const modelDisplay = document.getElementById('model-display');
const modelDropdown = document.getElementById('model-dropdown');
const sidebarEl = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle-mobile');
const chatArea = document.getElementById('chat-area');
const attachBtn = document.getElementById('attach-btn');
const fileInput = document.getElementById('file-input');
const attachmentPreviewBar = document.getElementById('attachment-preview-bar');
const voiceBtn = document.getElementById('voice-btn');
const modeBadge = document.getElementById('mode-badge');
const modeBadgeIcon = document.getElementById('mode-badge-icon');
const modeBadgeText = document.getElementById('mode-badge-text');
const modeBadgeReset = document.getElementById('mode-badge-reset');
const shareBtn = document.getElementById('share-btn');
const shareDropdown = document.getElementById('share-dropdown');
const exportMarkdownBtn = document.getElementById('export-markdown-btn');
const exportTextBtn = document.getElementById('export-text-btn');
const copyChatBtn = document.getElementById('copy-chat-btn');

// ─── Initialization ───
document.addEventListener('DOMContentLoaded', () => {
    renderRecents();
    initInputHandlers();
    initSuggestionCards();
    initModelDropdown();
    initSidebarToggle();
    initSidebarLinks();
    initAttachments();
    initVoiceInput();
    initShareDropdown();
    initRecentsSearch();
    showWelcome();
});

// ─── Welcome / Screen Switching ───
function showWelcome() {
    welcomeScreen.classList.remove('hidden');
    messagesFeed.classList.add('hidden');
    messagesFeed.innerHTML = '';
    currentTitle.textContent = 'New conversation';
    activeChatId = null;
    setPersona('default');
    clearAttachments();
}

function showChat() {
    welcomeScreen.classList.add('hidden');
    messagesFeed.classList.remove('hidden');
}

// ─── Persona / Mode Handling ───
function setPersona(agentId) {
    activeAgentId = PERSONAS[agentId] ? agentId : 'default';
    updateModeBadge();
}

function updateModeBadge() {
    if (!modeBadge) return;
    if (activeAgentId === 'default') {
        modeBadge.classList.add('hidden');
    } else {
        const info = PERSONAS[activeAgentId] || PERSONAS['default'];
        modeBadgeIcon.textContent = info.icon;
        modeBadgeText.textContent = info.name;
        modeBadge.classList.remove('hidden');
    }
}

modeBadgeReset?.addEventListener('click', (e) => {
    e.stopPropagation();
    setPersona('default');
    if (activeChatId && chats[activeChatId]) {
        chats[activeChatId].agent_id = 'default';
        saveChats();
    }
});

// ─── Chat Management ───
function createNewChat(firstMessage, agentId = activeAgentId) {
    const id = 'chat_' + Date.now();
    const title = firstMessage.slice(0, 44) + (firstMessage.length > 44 ? '…' : '');
    chats[id] = {
        id,
        title,
        agent_id: agentId,
        createdAt: Date.now(),
        messages: []
    };
    activeChatId = id;
    saveChats();
    renderRecents();
    currentTitle.textContent = title;
    return id;
}

function loadChat(id) {
    if (!chats[id]) return;
    activeChatId = id;
    const session = chats[id];
    currentTitle.textContent = session.title;
    setPersona(session.agent_id || 'default');
    messagesFeed.innerHTML = '';
    showChat();
    clearAttachments();

    session.messages.forEach(msg => {
        renderMessage(msg.role, msg.content, msg.attachments || [], msg.thoughtTime || null, false);
    });
    scrollToBottom();
    highlightRecent(id);
    if (window.innerWidth < 768) sidebarEl.classList.remove('open');
}

function deleteChat(id, e) {
    e.stopPropagation();
    if (!chats[id]) return;
    delete chats[id];
    saveChats();
    renderRecents();
    if (activeChatId === id) {
        showWelcome();
    }
}

function renderRecents(filterText = '') {
    recentsList.innerHTML = '';
    const query = filterText.toLowerCase().trim();
    const sorted = Object.values(chats)
        .filter(c => !query || c.title.toLowerCase().includes(query))
        .sort((a, b) => b.createdAt - a.createdAt)
        .slice(0, MAX_RECENTS);

    if (sorted.length === 0) {
        const empty = document.createElement('div');
        empty.style.cssText = 'padding: 10px; font-size: 11px; color: var(--text-3); text-align: center;';
        empty.textContent = query ? 'No matching chats' : 'No chats yet';
        recentsList.appendChild(empty);
        return;
    }

    sorted.forEach(chat => {
        const item = document.createElement('div');
        item.className = 'recent-item' + (chat.id === activeChatId ? ' active' : '');
        item.dataset.chatId = chat.id;

        const titleSpan = document.createElement('span');
        titleSpan.className = 'recent-item-title';
        titleSpan.textContent = chat.title;

        const delBtn = document.createElement('button');
        delBtn.className = 'recent-item-del';
        delBtn.title = 'Delete chat';
        delBtn.innerHTML = '<span class="material-symbols-rounded">delete</span>';
        delBtn.addEventListener('click', (e) => deleteChat(chat.id, e));

        item.appendChild(titleSpan);
        item.appendChild(delBtn);
        item.addEventListener('click', () => loadChat(chat.id));
        recentsList.appendChild(item);
    });
}

function initRecentsSearch() {
    recentsSearch?.addEventListener('input', (e) => {
        renderRecents(e.target.value);
    });
}

function highlightRecent(id) {
    document.querySelectorAll('.recent-item').forEach(el => {
        el.classList.toggle('active', el.dataset.chatId === id);
    });
}

function saveChats() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(chats)); }
    catch (e) { console.warn('LocalStorage quota exceeded'); }
}

// ─── Attachments (Images / Multimodal) ───
function initAttachments() {
    attachBtn?.addEventListener('click', () => fileInput?.click());

    fileInput?.addEventListener('change', (e) => {
        handleFiles(e.target.files);
        fileInput.value = '';
    });

    // Paste images from clipboard
    document.addEventListener('paste', (e) => {
        const items = e.clipboardData?.items;
        if (!items) return;
        const imageFiles = [];
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.startsWith('image/')) {
                const file = items[i].getAsFile();
                if (file) imageFiles.push(file);
            }
        }
        if (imageFiles.length > 0) {
            handleFiles(imageFiles);
        }
    });

    // Drag and drop onto chat area
    ['dragenter', 'dragover'].forEach(name => {
        document.body.addEventListener(name, (e) => e.preventDefault(), false);
    });
    document.body.addEventListener('drop', (e) => {
        e.preventDefault();
        if (e.dataTransfer?.files?.length > 0) {
            handleFiles(e.dataTransfer.files);
        }
    });
}

function handleFiles(files) {
    Array.from(files).forEach(file => {
        if (!file.type.startsWith('image/')) return;
        if (file.size > 10 * 1024 * 1024) {
            alert('Images must be smaller than 10MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            pendingAttachments.push({
                name: file.name,
                mimeType: file.type,
                dataUrl: e.target.result
            });
            renderAttachmentPreviews();
            updateSendBtn();
        };
        reader.readAsDataURL(file);
    });
}

function renderAttachmentPreviews() {
    if (!attachmentPreviewBar) return;
    attachmentPreviewBar.innerHTML = '';

    if (pendingAttachments.length === 0) {
        attachmentPreviewBar.classList.add('hidden');
        return;
    }

    attachmentPreviewBar.classList.remove('hidden');
    pendingAttachments.forEach((att, idx) => {
        const card = document.createElement('div');
        card.className = 'attachment-thumb-card';

        const img = document.createElement('img');
        img.src = att.dataUrl;
        img.alt = att.name;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'attachment-remove-btn';
        removeBtn.title = 'Remove image';
        removeBtn.innerHTML = '<span class="material-symbols-rounded">close</span>';
        removeBtn.addEventListener('click', () => {
            pendingAttachments.splice(idx, 1);
            renderAttachmentPreviews();
            updateSendBtn();
        });

        card.appendChild(img);
        card.appendChild(removeBtn);
        attachmentPreviewBar.appendChild(card);
    });
}

function clearAttachments() {
    pendingAttachments = [];
    renderAttachmentPreviews();
    updateSendBtn();
}

// ─── Voice Input (Speech-to-Text) ───
function initVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceBtn.style.opacity = '0.5';
        voiceBtn.title = 'Speech recognition not supported in this browser';
        return;
    }

    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        isListening = true;
        voiceBtn.classList.add('recording');
        voiceBtn.title = 'Listening… Click to stop';
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        userInput.value = transcript;
        autoResize();
        updateSendBtn();
    };

    recognition.onerror = () => {
        isListening = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.title = 'Voice input (speech-to-text)';
    };

    recognition.onend = () => {
        isListening = false;
        voiceBtn.classList.remove('recording');
        voiceBtn.title = 'Voice input (speech-to-text)';
    };

    voiceBtn.addEventListener('click', () => {
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
}

// ─── Text-to-Speech (Read Aloud) ───
function toggleSpeech(contentDiv, speakBtn) {
    if (!('speechSynthesis' in window)) {
        alert('Text-to-speech is not supported in this browser.');
        return;
    }

    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        if (activeSpeakingBtn) {
            activeSpeakingBtn.classList.remove('speaking');
            const icon = activeSpeakingBtn.querySelector('.material-symbols-rounded');
            if (icon) icon.textContent = 'volume_up';
        }
        if (activeSpeakingBtn === speakBtn) {
            activeSpeakingBtn = null;
            return;
        }
    }

    const textToSpeak = contentDiv?.innerText || '';
    if (!textToSpeak.trim()) return;

    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    const icon = speakBtn.querySelector('.material-symbols-rounded');
    speakBtn.classList.add('speaking');
    if (icon) icon.textContent = 'stop_circle';
    activeSpeakingBtn = speakBtn;

    utterance.onend = () => {
        speakBtn.classList.remove('speaking');
        if (icon) icon.textContent = 'volume_up';
        activeSpeakingBtn = null;
    };

    utterance.onerror = () => {
        speakBtn.classList.remove('speaking');
        if (icon) icon.textContent = 'volume_up';
        activeSpeakingBtn = null;
    };

    window.speechSynthesis.speak(utterance);
}

// ─── Render Message ───
function renderMessage(role, content, attachments = [], thoughtTime = null, animate = true) {
    const row = document.createElement('div');
    row.className = `msg-row ${role}`;
    if (!animate) row.style.animation = 'none';

    // AI avatar
    if (role === 'ai') {
        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.innerHTML = '<img src="AI_logo.png" alt="Arianna" class="msg-avatar-img">';
        row.appendChild(avatar);
    }

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';

    // Render attachments if user message
    if (role === 'user' && attachments && attachments.length > 0) {
        const grid = document.createElement('div');
        grid.className = 'msg-attachment-grid';
        attachments.forEach(att => {
            const img = document.createElement('img');
            img.src = att.dataUrl;
            img.alt = att.name || 'Uploaded image';
            img.className = 'msg-attachment-img';
            img.addEventListener('click', () => window.open(att.dataUrl, '_blank'));
            grid.appendChild(img);
        });
        bubble.appendChild(grid);
    }

    if (role === 'ai') {
        // Content (thought label excluded)
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-content';
        contentDiv.innerHTML = formatMarkdown(content);
        bubble.appendChild(contentDiv);
        bubble.appendChild(buildActionButtons(contentDiv));
    } else {
        const textP = document.createElement('p');
        textP.style.margin = '0';
        textP.textContent = content;
        bubble.appendChild(textP);
    }

    row.appendChild(bubble);
    messagesFeed.appendChild(row);
    return bubble;
}

function buildActionButtons(contentDiv) {
    const actions = document.createElement('div');
    actions.className = 'msg-actions';
    actions.innerHTML = `
        <button class="msg-action-btn" title="Copy">
            <span class="material-symbols-rounded">content_copy</span>
        </button>
        <button class="msg-action-btn" title="Read aloud">
            <span class="material-symbols-rounded">volume_up</span>
        </button>
        <button class="msg-action-btn" title="Like">
            <span class="material-symbols-rounded">thumb_up</span>
        </button>
        <button class="msg-action-btn" title="Dislike">
            <span class="material-symbols-rounded">thumb_down</span>
        </button>
    `;

    // Copy handler
    actions.querySelector('[title="Copy"]').addEventListener('click', (e) => {
        const text = contentDiv?.innerText || '';
        navigator.clipboard.writeText(text).catch(() => { });
        const icon = e.currentTarget.querySelector('.material-symbols-rounded');
        icon.textContent = 'check';
        setTimeout(() => { icon.textContent = 'content_copy'; }, 2000);
    });

    // Read aloud handler
    const readBtn = actions.querySelector('[title="Read aloud"]');
    readBtn.addEventListener('click', () => toggleSpeech(contentDiv, readBtn));

    // Like / Dislike handlers
    const likeBtn = actions.querySelector('[title="Like"]');
    const dislikeBtn = actions.querySelector('[title="Dislike"]');

    likeBtn.addEventListener('click', () => {
        likeBtn.classList.toggle('active-like');
        dislikeBtn.classList.remove('active-dislike');
    });

    dislikeBtn.addEventListener('click', () => {
        dislikeBtn.classList.toggle('active-dislike');
        likeBtn.classList.remove('active-like');
    });

    return actions;
}

// ─── Friendly Error Parser ───
function parseFriendlyError(rawMsg) {
    const msg = (rawMsg || '').toString();
    const upper = msg.toUpperCase();
    const is503 = upper.includes('503') || upper.includes('UNAVAILABLE') || upper.includes('HIGH DEMAND');
    const is429 = upper.includes('429') || upper.includes('RESOURCE_EXHAUSTED') || upper.includes('QUOTA');
    const isKeyError = upper.includes('API_KEY') || upper.includes('401') || upper.includes('403') || upper.includes('UNAUTHORIZED');

    if (is503) {
        return {
            icon: 'cloud_sync',
            title: 'High Demand on Google AI Servers',
            desc: 'Google’s Gemini servers are experiencing high demand. Multi-model retries timed out, but spikes usually clear up in a few seconds.',
            canRetry: true
        };
    }
    if (is429) {
        return {
            icon: 'hourglass_top',
            title: 'Rate Limit Reached',
            desc: 'Requests are coming in too quickly for the current free tier quota. Please wait a moment before trying again.',
            canRetry: true
        };
    }
    if (isKeyError) {
        return {
            icon: 'key_off',
            title: 'API Key Configuration Issue',
            desc: 'Please verify that your GEMINI_API_KEY in backend/.env is valid and active.',
            canRetry: false
        };
    }

    let cleanDesc = msg;
    const jsonMatch = msg.match(/'message':\s*'([^']+)'/) || msg.match(/"message":\s*"([^"]+)"/);
    if (jsonMatch && jsonMatch[1]) {
        cleanDesc = jsonMatch[1];
    }

    return {
        icon: 'error_outline',
        title: 'Connection Issue',
        desc: cleanDesc || 'An unexpected error occurred while communicating with the AI model.',
        canRetry: true
    };
}

// ─── Stream AI response ───
async function streamAIMessage(userText, attachments = []) {
    isGenerating = true;
    updateSendBtn();

    const session = chats[activeChatId];
    const currentAgent = session?.agent_id || activeAgentId || 'default';

    // Create AI row with typing indicator
    const row = document.createElement('div');
    row.className = 'msg-row ai';

    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.innerHTML = '<img src="AI_logo.png" alt="Arianna" class="msg-avatar-img">';
    row.appendChild(avatar);

    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';

    const thinkingLoader = createThinkingLoader();
    bubble.appendChild(thinkingLoader);

    row.appendChild(bubble);
    messagesFeed.appendChild(row);
    scrollToBottom();

    activeController = new AbortController();
    const signal = activeController.signal;
    let responseText = '';

    // Prepare message payload formatted for backend
    const payloadMessages = session.messages.map(m => {
        const item = { role: m.role, content: m.content };
        if (m.attachments && m.attachments.length > 0) {
            item.attachments = m.attachments.map(a => ({
                mime_type: a.mimeType,
                data: a.dataUrl.includes(',') ? a.dataUrl.split(',')[1] : a.dataUrl
            }));
        }
        return item;
    });

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                messages: payloadMessages,
                agent_id: currentAgent
            }),
            signal
        });

        if (!response.ok) {
            thinkingLoader.remove();
            const err = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
            throw new Error(err.detail || `Server error ${response.status}`);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-content';
        bubble.appendChild(contentDiv);

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let loaderRemoved = false;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith('data: ')) continue;

                let payload;
                try { payload = JSON.parse(trimmed.slice(6)); }
                catch (e) { continue; }

                if (payload.error) throw new Error(payload.error);
                if (payload.text) {
                    if (!loaderRemoved) {
                        thinkingLoader.remove();
                        loaderRemoved = true;
                    }
                    responseText += payload.text;
                    contentDiv.innerHTML = formatMarkdown(responseText);
                    scrollToBottom();
                }
            }
        }

        if (!loaderRemoved) thinkingLoader.remove();
        bubble.appendChild(buildActionButtons(contentDiv));

        if (responseText) {
            session.messages.push({ role: 'ai', content: responseText });
            saveChats();
        }

    } catch (error) {
        thinkingLoader?.remove();
        if (error.name === 'AbortError') {
            const cd = bubble.querySelector('.ai-content');
            if (responseText) {
                if (cd) {
                    cd.innerHTML = formatMarkdown(responseText + ' *(stopped)*');
                    bubble.appendChild(buildActionButtons(cd));
                }
                session.messages.push({ role: 'ai', content: responseText + ' *(stopped)*' });
                saveChats();
            } else {
                const stoppedNotice = document.createElement('div');
                stoppedNotice.className = 'stopped-notice';
                stoppedNotice.style.cssText = 'font-size: 13px; color: var(--text-3); font-style: italic; margin-top: 4px;';
                stoppedNotice.textContent = 'Generation stopped.';
                bubble.appendChild(stoppedNotice);
            }
        } else {
            const existingTyping = bubble.querySelector('.typing-indicator');
            if (existingTyping) existingTyping.remove();

            const errInfo = parseFriendlyError(error.message);
            const errEl = document.createElement('div');
            errEl.className = 'error-card';
            errEl.innerHTML = `
                <div class="error-card-top">
                    <span class="material-symbols-rounded error-card-icon">${errInfo.icon}</span>
                    <div class="error-card-body">
                        <span class="error-card-title">${errInfo.title}</span>
                        <p class="error-card-desc">${errInfo.desc}</p>
                    </div>
                </div>
                ${errInfo.canRetry ? `
                <div class="error-card-actions">
                    <button class="retry-btn" type="button">
                        <span class="material-symbols-rounded">refresh</span>
                        Retry message
                    </button>
                </div>` : ''}
            `;

            if (errInfo.canRetry) {
                const retryBtn = errEl.querySelector('.retry-btn');
                retryBtn?.addEventListener('click', async () => {
                    row.remove();
                    await streamAIMessage(userText, attachments);
                });
            }

            bubble.appendChild(errEl);
            scrollToBottom();
        }
    } finally {
        isGenerating = false;
        activeController = null;
        updateSendBtn();
    }
}

// ─── Submit Message ───
async function submitMessage() {
    const text = userInput.value.trim();
    const hasAttachments = pendingAttachments.length > 0;
    if ((!text && !hasAttachments) || isGenerating) return;

    const promptText = text || 'Please inspect the attached image(s).';
    const currentAttachments = [...pendingAttachments];

    if (!activeChatId) {
        createNewChat(promptText, activeAgentId);
        showChat();
    }

    userInput.value = '';
    clearAttachments();
    autoResize();
    updateSendBtn();

    chats[activeChatId].messages.push({
        role: 'user',
        content: promptText,
        attachments: currentAttachments
    });
    saveChats();

    renderMessage('user', promptText, currentAttachments);
    scrollToBottom();

    await streamAIMessage(promptText, currentAttachments);
}

// ─── Input Handlers ───
function initInputHandlers() {
    userInput.addEventListener('input', () => { autoResize(); updateSendBtn(); });
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); submitMessage(); }
    });
    sendBtn.addEventListener('click', (e) => {
        e.preventDefault();
        if (isGenerating) {
            if (activeController) activeController.abort();
            isGenerating = false;
            updateSendBtn();
        } else {
            submitMessage();
        }
    });
    newChatBtn.addEventListener('click', () => {
        if (isGenerating && activeController) activeController.abort();
        showWelcome();
    });
}

function initSuggestionCards() {
    const cardPersonaMap = {
        'Homework Help 📚': 'homework',
        'Writing Help ✍️': 'writing',
        'Coding Hints 💻': 'coding',
        'Quick Answers 💡': 'quick'
    };

    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            const titleEl = card.querySelector('.suggestion-title');
            const title = titleEl ? titleEl.textContent.trim() : '';

            if (cardPersonaMap[title]) {
                setPersona(cardPersonaMap[title]);
            }

            userInput.value = prompt;
            autoResize();
            updateSendBtn();
            userInput.focus();
        });
    });
}

function initSidebarLinks() {
    const linkMap = {
        'btn-homework': { prompt: 'Help me understand this math problem:', persona: 'homework' },
        'btn-writing': { prompt: 'Help me write and edit:', persona: 'writing' },
        'btn-coding': { prompt: 'Review my code and help fix bugs:', persona: 'coding' },
        'btn-history': { prompt: '', persona: 'default', isHistory: true }
    };

    Object.entries(linkMap).forEach(([id, config]) => {
        const el = document.getElementById(id);
        if (!el) return;
        el.addEventListener('click', () => {
            if (config.isHistory) {
                recentsSearch?.focus();
                return;
            }
            setPersona(config.persona);
            userInput.value = config.prompt;
            autoResize();
            updateSendBtn();
            userInput.focus();
            if (window.innerWidth < 768) sidebarEl.classList.remove('open');
        });
    });
}

function initModelDropdown() {
    modelSelectorBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        shareDropdown?.classList.add('hidden');
        const rect = modelSelectorBtn.getBoundingClientRect();
        modelDropdown.style.top = (rect.bottom + 8) + 'px';
        modelDropdown.style.right = '14px';
        modelDropdown.style.left = 'auto';
        modelDropdown.classList.toggle('hidden');
    });

    document.querySelectorAll('.dropdown-item:not(.dropdown-item--disabled)').forEach(item => {
        item.addEventListener('click', () => {
            activeModel = item.dataset.model;
            modelDisplay.textContent = item.dataset.label;

            document.querySelectorAll('.dropdown-item').forEach(i => {
                i.classList.toggle('active', i === item);
                const chk = i.querySelector('.dropdown-check');
                if (chk) chk.remove();
            });

            const chk = document.createElement('span');
            chk.className = 'material-symbols-rounded dropdown-check';
            chk.textContent = 'check_circle';
            item.appendChild(chk);

            modelDropdown.classList.add('hidden');
        });
    });

    document.addEventListener('click', (e) => {
        if (!modelDropdown.contains(e.target) && e.target !== modelSelectorBtn) {
            modelDropdown.classList.add('hidden');
        }
    });
}

// ─── Export / Share Dropdown ───
function initShareDropdown() {
    shareBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        modelDropdown?.classList.add('hidden');
        const rect = shareBtn.getBoundingClientRect();
        shareDropdown.style.top = (rect.bottom + 8) + 'px';
        shareDropdown.style.right = '14px';
        shareDropdown.style.left = 'auto';
        shareDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!shareDropdown.contains(e.target) && e.target !== shareBtn) {
            shareDropdown.classList.add('hidden');
        }
    });

    exportMarkdownBtn?.addEventListener('click', () => {
        exportConversation('markdown');
        shareDropdown.classList.add('hidden');
    });

    exportTextBtn?.addEventListener('click', () => {
        exportConversation('text');
        shareDropdown.classList.add('hidden');
    });

    copyChatBtn?.addEventListener('click', () => {
        copyConversation();
        shareDropdown.classList.add('hidden');
    });
}

function exportConversation(format) {
    if (!activeChatId || !chats[activeChatId]) {
        alert('Start or open a conversation first to export.');
        return;
    }
    const session = chats[activeChatId];
    let content = '';

    if (format === 'markdown') {
        content += `# ${session.title}\n*Exported from Arianna AI on ${new Date().toLocaleDateString()}*\n\n---\n\n`;
        session.messages.forEach(m => {
            const roleName = m.role === 'user' ? '👤 **You**' : '🤖 **Arianna**';
            content += `${roleName}:\n${m.content}\n\n`;
        });
        downloadFile(`${session.title.slice(0, 20).replace(/[^a-zA-Z0-9]/g, '_')}.md`, content, 'text/markdown');
    } else {
        content += `${session.title}\nDate: ${new Date().toLocaleString()}\n\n`;
        session.messages.forEach(m => {
            const roleName = m.role === 'user' ? 'You' : 'Arianna';
            content += `[${roleName}]\n${m.content}\n\n`;
        });
        downloadFile(`${session.title.slice(0, 20).replace(/[^a-zA-Z0-9]/g, '_')}.txt`, content, 'text/plain');
    }
}

function copyConversation() {
    if (!activeChatId || !chats[activeChatId]) {
        alert('Start or open a conversation first to copy.');
        return;
    }
    const session = chats[activeChatId];
    let transcript = `Conversation: ${session.title}\n\n`;
    session.messages.forEach(m => {
        transcript += `[${m.role === 'user' ? 'You' : 'Arianna'}]\n${m.content}\n\n`;
    });
    navigator.clipboard.writeText(transcript).then(() => {
        alert('Conversation copied to clipboard!');
    }).catch(() => { });
}

function downloadFile(filename, text, mimeType) {
    const blob = new Blob([text], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

function initSidebarToggle() {
    sidebarToggle?.addEventListener('click', () => sidebarEl.classList.toggle('open'));
    document.addEventListener('click', (e) => {
        if (window.innerWidth < 768 && sidebarEl.classList.contains('open')) {
            if (!sidebarEl.contains(e.target) && e.target !== sidebarToggle) {
                sidebarEl.classList.remove('open');
            }
        }
    });
}

// ─── Helpers ───
function autoResize() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 200) + 'px';
}

function updateSendBtn() {
    const icon = sendBtn.querySelector('.material-symbols-rounded');
    if (isGenerating) {
        sendBtn.disabled = false;
        sendBtn.classList.add('stop-mode');
        sendBtn.title = 'Stop generating';
        if (icon) icon.textContent = 'square';
    } else {
        sendBtn.classList.remove('stop-mode');
        sendBtn.title = 'Send message';
        if (icon) icon.textContent = 'arrow_upward';
        const hasText = userInput.value.trim().length > 0;
        const hasAtt = pendingAttachments.length > 0;
        sendBtn.disabled = !hasText && !hasAtt;
    }
}

function scrollToBottom() {
    chatArea.scrollTop = chatArea.scrollHeight;
}

function createThinkingLoader() {
    const el = document.createElement('div');
    el.className = 'ai-thinking-loader';
    el.innerHTML = `
        <div class="thinking-icon-orb">
            <span class="material-symbols-rounded thinking-icon">psychology</span>
            <div class="thinking-glow-ring"></div>
        </div>
        <div class="thinking-content">
            <span class="thinking-text">Arianna is thinking</span>
            <div class="thinking-dots">
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
                <span class="thinking-dot"></span>
            </div>
        </div>
    `;
    return el;
}

function createTypingIndicator() {
    const el = document.createElement('div');
    el.className = 'typing-indicator';
    el.innerHTML = `<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>`;
    return el;
}

// ─── Markdown Formatter ───
function formatMarkdown(text) {
    if (!text) return '';

    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
        `<pre><code class="language-${lang}">${code.trim()}</code></pre>`
    );
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    const parts = html.split(/(<pre[\s\S]*?<\/pre>)/g);
    for (let i = 0; i < parts.length; i++) {
        if (!parts[i].startsWith('<pre')) {
            let seg = parts[i].trim();
            if (seg) {
                seg = seg.replace(/\*\*([\s\S]*?)\*\*/g, '<strong>$1</strong>');
                seg = seg.replace(/^\s*[-*]\s+(.*)$/gm, '<li>$1</li>');
                seg = seg.replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');
                const pars = seg.split(/\n\n+/);
                parts[i] = pars.map(p => {
                    if (p.startsWith('<ul>') || p.startsWith('<li>')) return p;
                    return `<p>${p.replace(/\n/g, '<br>')}</p>`;
                }).join('');
            }
        }
    }
    return parts.join('');
}
