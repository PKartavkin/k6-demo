import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import encoding from 'k6/encoding';

// Custom metrics
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');
const requestCount = new Counter('requests');

// Test configuration
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
    errors: ['rate<0.01'],
  },
};

// Base URL and credentials
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const API_USER = __ENV.API_USER || 'admin';
const API_PASSWORD = __ENV.API_PASSWORD || 'password';

// Create auth header using K6's built-in encoding
const authHeader = `Basic ${encoding.b64encode(`${API_USER}:${API_PASSWORD}`)}`;

// Common request params with auth
const authParams = {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': authHeader,
  },
};

// Simplified authenticated request helper
function authenticatedRequest(method, url, payload = null) {
  const params = { ...authParams };
  let response;
  
  if (payload) {
    response = http.request(method, url, JSON.stringify(payload), params);
  } else {
    response = http.request(method, url, null, params);
  }
  
  requestCount.add(1);
  requestDuration.add(response.timings.duration);
  errorRate.add(response.status >= 400);
  
  return response;
}

export default function () {
  // Create a new note
  const createPayload = {
    title: `Note ${__VU}-${__ITER}`,
    content: `This is test note content created by virtual user ${__VU} in iteration ${__ITER}`,
  };
  
  const createResponse = authenticatedRequest('POST', `${BASE_URL}/notes`, createPayload);
  const createCheck = check(createResponse, {
    'create note status is 201': (r) => r.status === 201,
    'create note has id': (r) => {
      const body = JSON.parse(r.body);
      return body.id !== undefined;
    },
  });
  
  if (!createCheck) {
    console.error(`Failed to create note: ${createResponse.status} - ${createResponse.body}`);
    sleep(1);
    return;
  }
  
  const noteId = JSON.parse(createResponse.body).id;
  sleep(1);
  
  // Get the created note
  const getResponse = authenticatedRequest('GET', `${BASE_URL}/notes/${noteId}`);
  check(getResponse, {
    'get note status is 200': (r) => r.status === 200,
    'get note has correct id': (r) => {
      const body = JSON.parse(r.body);
      return body.id === noteId;
    },
  });
  sleep(1);
  
  // Update the note
  const updatePayload = {
    title: `Updated Note ${__VU}-${__ITER}`,
    content: `Updated content for note ${noteId}`,
  };
  
  const updateResponse = authenticatedRequest('PUT', `${BASE_URL}/notes/${noteId}`, updatePayload);
  check(updateResponse, {
    'update note status is 200': (r) => r.status === 200,
    'update note has updated title': (r) => {
      const body = JSON.parse(r.body);
      return body.title === updatePayload.title;
    },
  });
  sleep(1);
  
  // Get all notes (list endpoint)
  const listResponse = authenticatedRequest('GET', `${BASE_URL}/notes`);
  check(listResponse, {
    'list notes status is 200': (r) => r.status === 200,
    'list notes returns array': (r) => {
      const body = JSON.parse(r.body);
      return Array.isArray(body);
    },
  });
  sleep(1);
  
  // Delete the note
  const deleteResponse = authenticatedRequest('DELETE', `${BASE_URL}/notes/${noteId}`);
  check(deleteResponse, {
    'delete note status is 200': (r) => deleteResponse.status === 200,
  });
  sleep(1);
}

export function handleSummary(data) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const resultsDir = __ENV.RESULTS_DIR || '/app/results';
  
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    [`${resultsDir}/summary-${timestamp}.json`]: JSON.stringify(data),
  };
}

function textSummary(data, options = {}) {
  const indent = options.indent || '';
  const enableColors = options.enableColors || false;
  
  let summary = '\n';
  summary += `${indent}✓ Test completed\n\n`;
  summary += `${indent}Scenarios:\n`;
  summary += `${indent}  ✓ default: ${data.metrics.iterations.values.count} iterations\n\n`;
  
  summary += `${indent}HTTP Metrics:\n`;
  if (data.metrics.http_req_duration) {
    summary += `${indent}  http_req_duration: avg=${data.metrics.http_req_duration.values.avg.toFixed(2)}ms, min=${data.metrics.http_req_duration.values.min.toFixed(2)}ms, max=${data.metrics.http_req_duration.values.max.toFixed(2)}ms\n`;
  }
  if (data.metrics.http_req_failed) {
    summary += `${indent}  http_req_failed: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%\n`;
  }
  
  summary += `\n${indent}Custom Metrics:\n`;
  if (data.metrics.errors) {
    summary += `${indent}  errors: ${(data.metrics.errors.values.rate * 100).toFixed(2)}%\n`;
  }
  if (data.metrics.requests) {
    summary += `${indent}  requests: ${data.metrics.requests.values.count}\n`;
  }
  
  return summary;
}

