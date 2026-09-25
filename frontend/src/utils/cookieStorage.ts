/**
 * MediKiosk Cookie Storage Utility
 * ================================
 * 
 * Strict Privacy & Session Management:
 * Enforces pure cookie-based storage with zero usage of localStorage / sessionStorage,
 * as required by clinical security specifications.
 */

export const cookieStorage = {
  /**
   * Set a browser cookie with expiration and SameSite security.
   */
  set(name: string, value: string, days: number = 1): void {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
  },

  /**
   * Retrieve a cookie by name.
   */
  get(name: string): string | null {
    const nameEQ = `${encodeURIComponent(name)}=`;
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      c = c.trim();
      if (c.indexOf(nameEQ) === 0) {
        return decodeURIComponent(c.substring(nameEQ.length));
      }
    }
    return null;
  },

  /**
   * Remove a cookie immediately.
   */
  remove(name: string): void {
    document.cookie = `${encodeURIComponent(name)}=; Max-Age=-99999999; path=/; SameSite=Lax`;
  },

  /**
   * Save a JSON-serializable object into a cookie.
   */
  setJSON<T>(name: string, data: T, days: number = 1): void {
    try {
      const jsonString = JSON.stringify(data);
      this.set(name, jsonString, days);
    } catch (err) {
      console.error('Failed to serialize cookie data:', err);
    }
  },

  /**
   * Parse a JSON object from a cookie.
   */
  getJSON<T>(name: string): T | null {
    const val = this.get(name);
    if (!val) return null;
    try {
      return JSON.parse(val) as T;
    } catch {
      return null;
    }
  },

  /**
   * Clear all MediKiosk related session cookies.
   */
  clearAllKioskCookies(): void {
    const keys = ['medikiosk_session', 'medikiosk_patient', 'medikiosk_language', 'medikiosk_consent', 'medikiosk_mode'];
    keys.forEach(k => this.remove(k));
  },

  clearAll(): void {
    this.clearAllKioskCookies();
  },

  setPatient(patient: any): void {
    this.setJSON('medikiosk_patient', patient);
  },

  setLanguage(lang: string): void {
    this.set('medikiosk_language', lang);
  },

  setConsent(consent: boolean): void {
    this.set('medikiosk_consent', consent ? 'true' : 'false');
  },

  setSessionId(sessionId: string): void {
    this.set('medikiosk_session', sessionId);
  }
};
