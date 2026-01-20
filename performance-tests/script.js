import { sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';
import http from 'k6/http';
import { NotesApiClient } from './notes-api-client.js';

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const API_USER = __ENV.API_USER || 'admin';
const API_PASSWORD = __ENV.API_PASSWORD || 'password';
const THINK_TIME = parseFloat(__ENV.THINK_TIME || '1');

export const options = {
  stages: [
    { duration: '10s', target: 20, startVUs: 10 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests should be below 500ms, 99% below 1000ms
    http_req_failed: ['rate<0.01'], // Error rate should be less than 1%
  },
};

// Initialize API client
const apiClient = new NotesApiClient(BASE_URL, API_USER, API_PASSWORD);

// Main test function
export default function () {
  // Create a new note
  const title = `Note ${__VU}-${__ITER}`;
  const content = `This is test note content created by virtual user ${__VU} in iteration ${__ITER}`;
  
  const noteId = apiClient.createNote(title, content);
  if (!noteId) {
    sleep(THINK_TIME);
    return;
  }

  sleep(THINK_TIME);

  // Get the created note
  apiClient.getNote(noteId);
  sleep(THINK_TIME);

  // Update the note
  const updatedTitle = `Updated Note ${__VU}-${__ITER}`;
  const updatedContent = `Updated content for note ${noteId}`;
  apiClient.updateNote(noteId, updatedTitle, updatedContent);
  sleep(THINK_TIME);

  // Get all notes (list endpoint)
  apiClient.listNotes();
  sleep(THINK_TIME);

  // Delete the note
  apiClient.deleteNote(noteId);
  sleep(THINK_TIME);
}

// Results handler
// Note: Test results are now written to InfluxDB via K6's built-in output
// MongoDB is no longer used for storing test results
export function handleSummary(data) {
  return {
    stdout: textSummary(data, { enableColors: true }),
  };
}
