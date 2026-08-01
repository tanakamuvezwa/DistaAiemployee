/**
 * DistaMate — AI Chat Component (Streaming)
 */

import AI from '../ai.js';
import Auth from '../auth.js';
import { escapeHtml, avatarInitials, autoResizeTextarea } from '../ui.js';

let _chatHistory = []; // { role: 'user'|'assistant', content: string }
let _workspaceContext = '';

export function initChat(userProfile) {
  const chatInput   = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send-btn');
  const chatPanel   = document.getElementById('chat-panel');
  const chatCloseBtn = document.getElementById('chat-close-btn');
  const toggleBtn   = document.getElementById('chat-toggle-btn');

  // Toggle chat panel
  toggleBtn?.addEventListener('click', () => {
    chatPanel?.classList.toggle('hidden');
  });
  chatCloseBtn?.addEventListener('click', () => {
    chatPanel?.classList.add('hidden');
  });

  // Send on Enter (Shift+Enter = newline)
  chatInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  chatInput?.addEventListener('input', () => autoResizeTextarea(chatInput));
  chatSendBtn?.addEventListener('click', sendMessage);

  // User avatar initials in chat
  if (userProfile) {
    _workspaceContext = `User: ${userProfile.name} (${userProfile.email})`;
  }

  // Export for external access
window.chat = {
  sendSuggestion,
  appendVoiceMessage(text) {
    // Show voice-triggered user message in chat panel
    const panel = document.getElementById('chat-panel');
    panel?.classList.remove('hidden');
    appendMessage('user', `🎙️ ${text}`);
  },
  appendVoiceReply(text) {
    appendMessage('ai', text);
  },
};
}

function sendSuggestion(text) {
  const input = document.getElementById('chat-input');
  if (input) { input.value = text; }
  const panel = document.getElementById('chat-panel');
  panel?.classList.remove('hidden');
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const text = input?.value?.trim();
  if (!text || !input) return;

  input.value = '';
  input.style.height = 'auto';

  // Hide suggestions
  document.getElementById('chat-suggestions')?.remove();

  appendMessage('user', text);
  _chatHistory.push({ role: 'user', content: text });

  // Keep last 10 messages for context
  if (_chatHistory.length > 20) _chatHistory = _chatHistory.slice(-20);

  const aiMsgEl = appendMessage('ai', '', true); // streaming placeholder
  setStatus('Thinking...');

  try {
    let fullResponse = '';

    const stream = AI.chatStream(_chatHistory, _workspaceContext);
    for await (const chunk of stream) {
      fullResponse += chunk;
      aiMsgEl.innerHTML = formatAIMessage(fullResponse);
      scrollChatToBottom();
    }

    _chatHistory.push({ role: 'assistant', content: fullResponse });
    setStatus('Ready');
  } catch (e) {
    aiMsgEl.innerHTML = `<span style="color:var(--color-danger)">Error: ${escapeHtml(e.message)}</span>`;
    setStatus('Error');
    setTimeout(() => setStatus('Ready'), 3000);
  }
}

function appendMessage(role, text, isStreaming = false) {
  const messagesEl = document.getElementById('chat-messages');
  if (!messagesEl) return null;

  const msgEl = document.createElement('div');
  msgEl.className = `chat-message ${role}`;

  const avatar = role === 'ai'
    ? `<div class="msg-avatar ai-avatar-sm">DM</div>`
    : `<div class="msg-avatar user-avatar-sm" style="background:var(--color-primary);color:white">Me</div>`;

  const content = isStreaming
    ? `<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`
    : (role === 'ai' ? formatAIMessage(text) : escapeHtml(text));

  msgEl.innerHTML = `${avatar}<div class="msg-content">${content}</div>`;
  messagesEl.appendChild(msgEl);
  scrollChatToBottom();

  return msgEl.querySelector('.msg-content');
}

function formatAIMessage(text) {
  if (!text) return '';
  return text
    // Bold **text**
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic *text*
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Inline code `text`
    .replace(/`([^`]+)`/g, '<code style="font-family:var(--font-mono);font-size:11px;background:var(--color-surface3);padding:1px 5px;border-radius:4px">$1</code>')
    // Bullet points (lines starting with - or •)
    .replace(/^[-•]\s+(.+)$/gm, '<li>$1</li>')
    // Numbered lists
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul style="padding-left:16px;margin:6px 0">${match}</ul>`)
    // Line breaks
    .replace(/\n\n/g, '</p><p style="margin-top:8px">')
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(.+)$/, '<p>$1</p>');
}

function scrollChatToBottom() {
  const msgs = document.getElementById('chat-messages');
  if (msgs) msgs.scrollTop = msgs.scrollHeight;
}

function setStatus(status) {
  const el = document.getElementById('chat-status');
  if (el) {
    el.textContent = status;
    el.style.color = status === 'Thinking...' ? 'var(--color-warning)' : status === 'Error' ? 'var(--color-danger)' : 'var(--color-accent)';
  }
}
