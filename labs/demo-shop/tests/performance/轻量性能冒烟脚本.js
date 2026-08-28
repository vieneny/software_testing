import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = __ENV.DEMO_BASE_URL || 'http://127.0.0.1:8000';

export const options = {
  scenarios: {
    browse_products: {
      executor: 'constant-vus',
      vus: Number(__ENV.VUS || 3),
      duration: __ENV.DURATION || '20s',
      gracefulStop: '5s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<300'],
    checks: ['rate>0.99'],
  },
};

export default function () {
  const response = http.get(`${baseUrl}/api/products`, {
    tags: { operation: 'list_products' },
    timeout: '3s',
  });

  check(response, {
    'list returns 200': (res) => res.status === 200,
    'list is not empty': (res) => {
      try {
        return res.json().length > 0;
      } catch (_) {
        return false;
      }
    },
  });
  sleep(1);
}
