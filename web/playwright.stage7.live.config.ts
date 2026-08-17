import { defineConfig, devices } from "@playwright/test";

const rawLiveUrl = process.env.EFL_STAGE7_LIVE_URL;
if (!rawLiveUrl) {
  throw new Error("EFL_STAGE7_LIVE_URL is required for the deployed-site gate");
}

const liveUrl = new URL(rawLiveUrl);
if (
  liveUrl.protocol !== "https:" ||
  liveUrl.hostname !== "mkhasan23.github.io" ||
  liveUrl.pathname !== "/empirical-finance-lab/" ||
  liveUrl.search !== "" ||
  liveUrl.hash !== ""
) {
  throw new Error(`unexpected Stage VII live URL: ${liveUrl.href}`);
}

export default defineConfig({
  testDir: "./tests-live",
  testMatch: "stage7.live.spec.ts",
  timeout: 300_000,
  expect: { timeout: 120_000 },
  fullyParallel: false,
  workers: 1,
  reporter: "line",
  use: {
    baseURL: liveUrl.href,
    trace: "retain-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});
