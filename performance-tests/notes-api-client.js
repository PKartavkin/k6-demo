import http from 'k6/http';
import { check } from 'k6';
import encoding from 'k6/encoding';
import { parseBody } from './utils.js';

/**
 * Notes API Client
 * Provides functions to interact with the Notes API
 */
export class NotesApiClient {
  constructor(baseUrl, username, password) {
    this.baseUrl = baseUrl;
    this.authParams = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Basic ${encoding.b64encode(`${username}:${password}`)}`,
      },
    };
  }

  /**
   * Creates a new note
   * @param {string} title - Note title
   * @param {string} content - Note content
   * @returns {string|null} - Note ID if successful, null otherwise
   */
  createNote(title, content) {
    const payload = { title, content };
    const res = http.post(`${this.baseUrl}/notes`, JSON.stringify(payload), { params: this.authParams });
    const body = parseBody(res);

    if (!check(res, {
      'create note status is 201': (r) => r.status === 201,
      'create note has id': () => body?.id !== undefined,
    })) {
      console.error(`Failed to create note: ${res.status} - ${res.body}`);
      return null;
    }

    return body.id;
  }

  /**
   * Retrieves a note by ID
   * @param {string} noteId - Note ID
   * @returns {object|null} - Note object if successful, null otherwise
   */
  getNote(noteId) {
    const res = http.get(`${this.baseUrl}/notes/${noteId}`, { params: this.authParams });
    const body = parseBody(res);

    check(res, {
      'get note status is 200': (r) => r.status === 200,
      'get note has correct id': () => body?.id === noteId,
    });

    return body;
  }

  /**
   * Updates an existing note
   * @param {string} noteId - Note ID
   * @param {string} title - Updated title
   * @param {string} content - Updated content
   * @returns {object|null} - Updated note object if successful, null otherwise
   */
  updateNote(noteId, title, content) {
    const payload = { title, content };
    const res = http.put(`${this.baseUrl}/notes/${noteId}`, JSON.stringify(payload), { params: this.authParams });
    const body = parseBody(res);

    check(res, {
      'update note status is 200': (r) => r.status === 200,
      'update note has updated title': () => body?.title === title,
    });

    return body;
  }

  /**
   * Lists all notes
   * @returns {array} - Array of notes
   */
  listNotes() {
    const res = http.get(`${this.baseUrl}/notes`, { params: this.authParams });
    const body = parseBody(res);

    check(res, {
      'list notes status is 200': (r) => r.status === 200,
      'list notes returns array': () => Array.isArray(body),
    });

    return body;
  }

  /**
   * Deletes a note by ID
   * @param {string} noteId - Note ID
   * @returns {boolean} - True if successful, false otherwise
   */
  deleteNote(noteId) {
    const res = http.del(`${this.baseUrl}/notes/${noteId}`, null, { params: this.authParams });
    
    const success = check(res, {
      'delete note status is 200': (r) => r.status === 200,
    });

    return success;
  }
}
