/**
 * DistaMate — Google Sheets API Wrapper
 */

import Auth from './auth.js';
import { DEMO_SHEET } from './demo-data.js';

const Sheets = {
  BASE: 'https://sheets.googleapis.com/v4/spreadsheets',

  async getSpreadsheet(sheetId) {
    if (Auth.isDemoMode()) return DEMO_SHEET.meta;
    return Auth.request(`${this.BASE}/${sheetId}?includeGridData=false`);
  },

  async getSheetValues(sheetId, range = 'Sheet1') {
    if (Auth.isDemoMode()) return DEMO_SHEET.values;
    const data = await Auth.request(`${this.BASE}/${sheetId}/values/${encodeURIComponent(range)}`);
    return data.values || [];
  },

  async updateCell(sheetId, range, value) {
    if (Auth.isDemoMode()) throw new Error('Cannot update cells in Demo mode.');
    return Auth.request(`${this.BASE}/${sheetId}/values/${encodeURIComponent(range)}?valueInputOption=USER_ENTERED`, {
      method: 'PUT',
      body: JSON.stringify({ values: [[value]] })
    });
  },

  async appendRow(sheetId, sheetName, values) {
    if (Auth.isDemoMode()) throw new Error('Cannot append rows in Demo mode.');
    return Auth.request(`${this.BASE}/${sheetId}/values/${encodeURIComponent(sheetName)}:append?valueInputOption=USER_ENTERED`, {
      method: 'POST',
      body: JSON.stringify({ values: [values] })
    });
  },

  // Parse spreadsheet ID from URL
  parseSheetId(input) {
    const match = input.match(/\/spreadsheets\/d\/([a-zA-Z0-9_-]+)/);
    return match ? match[1] : input.trim();
  },

  getSheetNames(meta) {
    return (meta?.sheets || []).map(s => s.properties?.title || 'Sheet');
  },

  // Convert rows array to {headers, rows}
  parseValues(values) {
    if (!values || values.length === 0) return { headers: [], rows: [] };
    const [headers, ...rows] = values;
    return { headers: headers || [], rows: rows || [] };
  }
};

export default Sheets;
