/**
 * DistaMate — Unified AI Module (Google Gemini + OpenRouter Dual Support)
 * Intelligently routes requests to Gemini REST API or OpenRouter API.
 */

import Config from './config.js';

const AI = {

  // ── Core: single-shot generation ─────────────────────────────
  async _call(messages, systemPrompt) {
    const geminiKey     = Config.GEMINI_API_KEY;
    const openrouterKey = Config.OPENROUTER_API_KEY;

    if (!geminiKey && !openrouterKey) {
      throw new Error('No AI key configured. Please add a Gemini or OpenRouter key in Settings.');
    }

    // Determine primary provider
    if (openrouterKey && (!geminiKey || openrouterKey.startsWith('sk-or-'))) {
      try {
        return await this._callOpenRouter(messages, systemPrompt, openrouterKey);
      } catch (err) {
        if (geminiKey) return await this._callGemini(messages, systemPrompt, geminiKey);
        throw err;
      }
    }

    try {
      return await this._callGemini(messages, systemPrompt, geminiKey);
    } catch (err) {
      if (openrouterKey) return await this._callOpenRouter(messages, systemPrompt, openrouterKey);
      throw err;
    }
  },

  // ── Gemini REST API ──────────────────────────────────────────
  async _callGemini(messages, systemPrompt, key) {
    const model = Config.AI_MODEL || 'gemini-2.0-flash';
    const url   = `${Config.GEMINI_BASE_URL}/models/${model}:generateContent?key=${key}`;

    const contents = messages.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }));

    const body = {
      systemInstruction: systemPrompt ? { parts: [{ text: systemPrompt }] } : undefined,
      contents,
      generationConfig: { temperature: 0.5, maxOutputTokens: 1200 },
      safetySettings: [
        { category: 'HARM_CATEGORY_HARASSMENT',        threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_HATE_SPEECH',       threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_NONE' },
      ],
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || `Gemini API error ${res.status}`);
    }

    const data = await res.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
    if (!text) throw new Error('Gemini returned empty response.');
    return text;
  },

  // ── OpenRouter API ───────────────────────────────────────────
  async _callOpenRouter(messages, systemPrompt, key) {
    const url = `${Config.OPENROUTER_BASE_URL}/chat/completions`;
    const model = 'google/gemini-2.0-flash-001';

    const body = {
      model,
      messages: [
        ...(systemPrompt ? [{ role: 'system', content: systemPrompt }] : []),
        ...messages,
      ],
      temperature: 0.5,
      max_tokens: 1200,
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'http://localhost:3000',
        'X-Title': 'DistaAiEmployee',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || `OpenRouter API error ${res.status}`);
    }

    const data = await res.json();
    const text = data.choices?.[0]?.message?.content;
    if (!text) throw new Error('OpenRouter returned empty response.');
    return text;
  },

  // ── Core: streaming generation ────────────────────────────────
  async *_stream(messages, systemPrompt) {
    const key = Config.GEMINI_API_KEY || Config.OPENROUTER_API_KEY;
    if (!key) throw new Error('No AI key configured.');

    if (Config.OPENROUTER_API_KEY && Config.OPENROUTER_API_KEY.startsWith('sk-or-')) {
      yield* this._streamOpenRouter(messages, systemPrompt, Config.OPENROUTER_API_KEY);
      return;
    }

    yield* this._streamGemini(messages, systemPrompt, key);
  },

  async *_streamGemini(messages, systemPrompt, key) {
    const model = Config.AI_MODEL || 'gemini-2.0-flash';
    const url   = `${Config.GEMINI_BASE_URL}/models/${model}:streamGenerateContent?alt=sse&key=${key}`;

    const contents = messages.map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }));

    const body = {
      systemInstruction: systemPrompt ? { parts: [{ text: systemPrompt }] } : undefined,
      contents,
      generationConfig: { temperature: 0.6, maxOutputTokens: 2000 },
      safetySettings: [
        { category: 'HARM_CATEGORY_HARASSMENT',        threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_HATE_SPEECH',       threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT', threshold: 'BLOCK_NONE' },
        { category: 'HARM_CATEGORY_DANGEROUS_CONTENT', threshold: 'BLOCK_NONE' },
      ],
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || `Gemini stream error ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const jsonStr = trimmed.slice(5).trim();
        if (jsonStr === '[DONE]') return;
        try {
          const chunk = JSON.parse(jsonStr);
          const text  = chunk.candidates?.[0]?.content?.parts?.[0]?.text;
          if (text) yield text;
        } catch { /* skip malformed */ }
      }
    }
  },

  async *_streamOpenRouter(messages, systemPrompt, key) {
    const url = `${Config.OPENROUTER_BASE_URL}/chat/completions`;
    const body = {
      model: 'google/gemini-2.0-flash-001',
      messages: [
        ...(systemPrompt ? [{ role: 'system', content: systemPrompt }] : []),
        ...messages,
      ],
      stream: true,
    };

    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error?.message || `OpenRouter stream error ${res.status}`);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed.startsWith('data:')) continue;
        const jsonStr = trimmed.slice(5).trim();
        if (jsonStr === '[DONE]') return;
        try {
          const chunk = JSON.parse(jsonStr);
          const text  = chunk.choices?.[0]?.delta?.content;
          if (text) yield text;
        } catch { /* skip */ }
      }
    }
  },

  // ── Classify email priority ───────────────────────────────────
  async classifyEmail({ subject, snippet, sender }) {
    const system = `You are an email priority classifier. Respond ONLY with a valid JSON object (no markdown) with:
- priority: "urgent", "action", or "info"
- reason: one sentence max 12 words
- actionItem: brief action string or null`;

    const msg = `From: ${sender}\nSubject: ${subject}\nPreview: ${snippet}`;
    try {
      const raw = await this._call([{ role: 'user', content: msg }], system);
      const cleaned = raw.replace(/```json|```/g, '').trim();
      return JSON.parse(cleaned);
    } catch {
      return { priority: 'info', reason: 'Could not classify', actionItem: null };
    }
  },

  // ── Summarize email thread ────────────────────────────────────
  async summarizeThread(messages) {
    const system = `Summarize this email thread. Respond ONLY with valid JSON (no markdown):
{ "summary": "...", "keyPoints": ["..."], "actionRequired": true/false, "suggestedReply": "..." }`;

    const threadText = messages.map(m => `From: ${m.from}\n${m.body}`).join('\n\n---\n\n');
    try {
      const raw = await this._call([{ role: 'user', content: threadText }], system);
      return JSON.parse(raw.replace(/```json|```/g, '').trim());
    } catch {
      return { summary: 'Unable to summarize.', keyPoints: [], actionRequired: false, suggestedReply: '' };
    }
  },

  // ── Draft email reply ─────────────────────────────────────────
  async draftReply({ thread, userInstruction = '' }) {
    const system = `You are a professional email assistant named DistaMate. 
Draft a concise, professional reply. Use proper greeting and sign-off. 
Output ONLY the email body — no extra commentary.`;

    const threadText = thread.map(m => `From: ${m.from}\n${m.body}`).join('\n\n---\n\n');
    const content = userInstruction
      ? `Thread:\n${threadText}\n\nInstruction: ${userInstruction}`
      : `Draft a professional reply to:\n\n${threadText}`;

    return this._call([{ role: 'user', content }], system);
  },

  // ── Summarize document ────────────────────────────────────────
  async summarizeDocument(docText) {
    const system = `You are a document analyst. Respond ONLY with valid JSON (no markdown):
{ "summary": "...", "keyPoints": ["..."], "actionItems": ["..."], "keyPeople": ["..."], "deadlines": ["..."] }`;

    const truncated = docText.length > 8000 ? docText.slice(0, 8000) + '...[truncated]' : docText;
    try {
      const raw = await this._call([{ role: 'user', content: truncated }], system);
      return JSON.parse(raw.replace(/```json|```/g, '').trim());
    } catch {
      return { summary: 'Unable to analyze.', keyPoints: [], actionItems: [], keyPeople: [], deadlines: [] };
    }
  },

  // ── Analyze spreadsheet ───────────────────────────────────────
  async analyzeSheet(headers, rows) {
    const system = `You are a data analyst. Respond ONLY with valid JSON (no markdown):
{ "summary": "...", "insights": ["..."], "suggestedFormulas": [{ "name": "...", "formula": "...", "description": "..." }] }`;

    const preview = [headers, ...rows.slice(0, 20)].map(r => r.join('\t')).join('\n');
    try {
      const raw = await this._call([{ role: 'user', content: `Data:\n${preview}` }], system);
      return JSON.parse(raw.replace(/```json|```/g, '').trim());
    } catch {
      return { summary: 'Unable to analyze sheet.', insights: [], suggestedFormulas: [] };
    }
  },

  // ── General workspace chat (streaming) ───────────────────────
  async *chatStream(messages, workspaceContext = '') {
    const system = `You are DistaMate, an intelligent AI workspace assistant integrated with Google Workspace (Gmail, Drive, Docs, Sheets).
${workspaceContext ? `Context:\n${workspaceContext}\n` : ''}
Help users summarize emails, search files, extract document insights, and analyze spreadsheets. Be concise and actionable.`;

    yield* this._stream(messages, system);
  },

  // ── Reformulate Drive search query ───────────────────────────
  async reformulateSearchQuery(naturalQuery) {
    const system = `Convert natural language to a Google Drive search query string. Return ONLY the query, nothing else.
Examples: "budget spreadsheet last month" → "budget type:spreadsheet"`;
    try {
      const result = await this._call([{ role: 'user', content: naturalQuery }], system);
      return result.trim().replace(/^["']|["']$/g, '');
    } catch {
      return naturalQuery;
    }
  },
};

export default AI;
