/**
 * DistaMate — Configuration
 * API keys and OAuth credentials
 */

const Config = {
  // Gemini AI (Set via Settings panel or localStorage)
  GEMINI_API_KEY: '',
  GEMINI_BASE_URL: 'https://generativelanguage.googleapis.com/v1beta',
  AI_MODEL: 'gemini-2.0-flash',

  // Google OAuth2 (Set via Settings panel or localStorage)
  GOOGLE_CLIENT_ID: '',

  // Google API Scopes
  GOOGLE_SCOPES: [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email',
  ].join(' '),

  // Discovery docs for Google APIs
  DISCOVERY_DOCS: [
    'https://www.googleapis.com/discovery/v1/apis/gmail/v1/rest',
    'https://www.googleapis.com/discovery/v1/apis/drive/v3/rest',
    'https://docs.googleapis.com/$discovery/rest?version=v1',
    'https://sheets.googleapis.com/$discovery/rest?version=v4',
  ],

  // Persistence keys
  STORAGE_KEYS: {
    CLIENT_ID: 'dm_google_client_id',
    GEMINI_KEY: 'dm_gemini_key',
    AI_MODEL: 'dm_ai_model',
    THEME: 'dm_theme',
    CHAT_HISTORY: 'dm_chat_history',
  },

  // Load persisted settings
  load() {
    const savedClientId = localStorage.getItem(this.STORAGE_KEYS.CLIENT_ID);
    if (savedClientId) this.GOOGLE_CLIENT_ID = savedClientId;
    // If nothing saved, keep the hardcoded default above

    const savedKey = localStorage.getItem(this.STORAGE_KEYS.GEMINI_KEY);
    if (savedKey) this.GEMINI_API_KEY = savedKey;

    const savedModel = localStorage.getItem(this.STORAGE_KEYS.AI_MODEL);
    if (savedModel) this.AI_MODEL = savedModel;
  },

  save() {
    if (this.GOOGLE_CLIENT_ID) localStorage.setItem(this.STORAGE_KEYS.CLIENT_ID, this.GOOGLE_CLIENT_ID);
    if (this.GEMINI_API_KEY) localStorage.setItem(this.STORAGE_KEYS.GEMINI_KEY, this.GEMINI_API_KEY);
    if (this.AI_MODEL) localStorage.setItem(this.STORAGE_KEYS.AI_MODEL, this.AI_MODEL);
  }
};

export default Config;
