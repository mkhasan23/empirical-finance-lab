import { defineConfig, devices } from "@playwright/test";

const stage7BaseUrl = "http://127.0.0.1:4173/empirical-finance-lab/";

export default defineConfig({
  testDir: "./tests",
  testMatch: "stage7.spec.ts",
  timeout: 300_000,
  expect: { timeout: 120_000 },
  fullyParallel: false,
  workers: 1,
  reporter: "line",
  use: {
    baseURL: stage7BaseUrl,
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run preview:pages",
    url: stage7BaseUrl,
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
