import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";

export const options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "1m", target: 20 },
    { duration: "30s", target: 50 },
    { duration: "1m", target: 50 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<200", "p(99)<500"],
    "http_req_duration{endpoint:list}": ["p(95)<200"],
    "http_req_duration{endpoint:create}": ["p(95)<200"],
    "http_req_duration{endpoint:get}": ["p(95)<100"],
  },
};

export default function () {
  const createRes = http.post(
    `${BASE_URL}/tasks`,
    JSON.stringify({
      name: `k6-task-${__VU}-${__ITER}`,
      description: "created by k6 load test",
      completed: false,
    }),
    {
      headers: { "Content-Type": "application/json" },
      tags: { endpoint: "create" },
    }
  );
  check(createRes, {
    "create status 200": (r) => r.status === 200,
  });

  const taskId = createRes.json("id");

  const listRes = http.get(`${BASE_URL}/tasks`, {
    tags: { endpoint: "list" },
  });
  check(listRes, { "list status 200": (r) => r.status === 200 });

  if (taskId) {
    const getRes = http.get(`${BASE_URL}/tasks/${taskId}`, {
      tags: { endpoint: "get" },
    });
    check(getRes, { "get status 200": (r) => r.status === 200 });

    const patchRes = http.patch(
      `${BASE_URL}/tasks/${taskId}`,
      JSON.stringify({ name: "updated", description: null, completed: true }),
      {
        headers: { "Content-Type": "application/json" },
        tags: { endpoint: "update" },
      }
    );
    check(patchRes, { "patch status 200": (r) => r.status === 200 });

    const deleteRes = http.del(`${BASE_URL}/tasks/${taskId}`, null, {
      tags: { endpoint: "delete" },
    });
    check(deleteRes, { "delete status 204": (r) => r.status === 204 });
  }

  sleep(1);
}
