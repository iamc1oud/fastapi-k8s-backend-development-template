import http from "k6/http";
import { check } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  vus: 2,
  duration: "10s",
  thresholds: {
    http_req_failed: ["rate==0"],
    http_req_duration: ["p(95)<300"],
  },
};

export default function () {
  const health = http.get(`${BASE_URL}/healthz`);
  check(health, { "healthz 200": (r) => r.status === 200 });

  const ready = http.get(`${BASE_URL}/readyz`);
  check(ready, { "readyz 200": (r) => r.status === 200 });

  const list = http.get(`${BASE_URL}/tasks`);
  check(list, { "tasks 200": (r) => r.status === 200 });
}
