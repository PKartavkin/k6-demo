import http from 'k6/http';
import { check, sleep } from 'k6';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

// Configuration
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const API_USER = __ENV.API_USER || 'admin';
const API_PASSWORD = __ENV.API_PASSWORD || 'password';
const THINK_TIME = parseFloat(__ENV.THINK_TIME || '1');

export const options = {
  stages: [
    { duration: '30s', target: 10 },  // Ramp up to 10 users
    { duration: '1m', target: 10 },   // Stay at 10 users
    { duration: '30s', target: 20 },  // Ramp up to 20 users
    { duration: '1m', target: 20 },   // Stay at 20 users
    { duration: '30s', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests should be below 500ms, 99% below 1000ms
    http_req_failed: ['rate<0.01'], // Error rate should be less than 1%
  },
};

// Auth setup
const authParams = {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Basic ${btoa(`${API_USER}:${API_PASSWORD}`)}`,
  },
};

// Helper functions
function parseBody(response) {
  try {
    return JSON.parse(response.body);
  } catch {
    return null;
  }
}

function createNote() {
  const payload = {
    title: `Note ${__VU}-${__ITER}`,
    content: `This is test note content created by virtual user ${__VU} in iteration ${__ITER}`,
  };
  
  const res = http.post(`${BASE_URL}/notes`, JSON.stringify(payload), { params: authParams });
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

function getNote(noteId) {
  const res = http.get(`${BASE_URL}/notes/${noteId}`, { params: authParams });
  const body = parseBody(res);
  
  check(res, {
    'get note status is 200': (r) => r.status === 200,
    'get note has correct id': () => body?.id === noteId,
  });
}

function updateNote(noteId) {
  const payload = {
    title: `Updated Note ${__VU}-${__ITER}`,
    content: `Updated content for note ${noteId}`,
  };
  
  const res = http.put(`${BASE_URL}/notes/${noteId}`, JSON.stringify(payload), { params: authParams });
  const body = parseBody(res);
  
  check(res, {
    'update note status is 200': (r) => r.status === 200,
    'update note has updated title': () => body?.title === payload.title,
  });
}

function listNotes() {
  const res = http.get(`${BASE_URL}/notes`, { params: authParams });
  const body = parseBody(res);
  
  check(res, {
    'list notes status is 200': (r) => r.status === 200,
    'list notes returns array': () => Array.isArray(body),
  });
}

function deleteNote(noteId) {
  const res = http.del(`${BASE_URL}/notes/${noteId}`, null, { params: authParams });
  check(res, {
    'delete note status is 200': (r) => r.status === 200,
  });
}

// Main test function
export default function () {
  // Create a new note
  const noteId = createNote();
  if (!noteId) {
    sleep(THINK_TIME);
    return;
  }
  
  sleep(THINK_TIME);
  
  // Get the created note
  getNote(noteId);
  sleep(THINK_TIME);
  
  // Update the note
  updateNote(noteId);
  sleep(THINK_TIME);
  
  // Get all notes (list endpoint)
  listNotes();
  sleep(THINK_TIME);
  
  // Delete the note
  deleteNote(noteId);
  sleep(THINK_TIME);
}

// Results handler
export function handleSummary(data) {
  const timestamp = new Date().toISOString();
  const testId = `test-${timestamp.replace(/[:.]/g, '-')}`;
  
  // Prepare summary payload
  const resultPayload = {
    test_id: testId,
    timestamp: timestamp,
    metrics: data.metrics || {},
    full_results: data,
    summary: {
      iterations: data.metrics?.iterations?.values?.count || 0,
      http_reqs: data.metrics?.http_reqs?.values?.count || 0,
      avg_duration: data.metrics?.http_req_duration?.values?.avg || 0,
      p95_duration: data.metrics?.http_req_duration?.values?.['p(95)'] || 0,
      error_rate: (data.metrics?.http_req_failed?.values?.rate || 0) * 100,
    },
  };
  
  // Save to MongoDB via notes-server API
  const saveResponse = http.post(
    `${BASE_URL}/test-results`,
    JSON.stringify(resultPayload),
    {
      headers: { 'Content-Type': 'application/json' },
    }
  );
  
  if (saveResponse.status === 201) {
    console.log(`✓ Test results saved to MongoDB with ID: ${testId}`);
  } else {
    console.error(`✗ Failed to save results: ${saveResponse.status} - ${saveResponse.body}`);
  }
  
  return {
    stdout: textSummary(data, { enableColors: true }),
  };
}
