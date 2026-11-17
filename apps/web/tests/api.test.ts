import { test, describe, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { api } from "../lib/api.ts";

describe("Frontend API Client Test Suite", () => {
  const originalFetch = globalThis.fetch;

  afterEach(() => {
    globalThis.fetch = originalFetch;
  });

  test("api.getJobs queries /jobs endpoint with correct query string", async () => {
    let capturedUrl = "";
    globalThis.fetch = async (url: any, init?: any) => {
      capturedUrl = String(url);
      return new Response(JSON.stringify([{ id: "job-1", title: "Software Engineer" }]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };

    const jobs = await api.getJobs("limit=10&location=Remote");
    assert.match(capturedUrl, /\/jobs\?limit=10&location=Remote$/);
    assert.equal(jobs.length, 1);
    assert.equal(jobs[0].title, "Software Engineer");
  });

  test("api.createApplication sends POST with JSON body", async () => {
    let capturedMethod = "";
    let capturedBody = "";
    globalThis.fetch = async (url: any, init?: any) => {
      capturedMethod = init?.method || "GET";
      capturedBody = String(init?.body || "");
      return new Response(JSON.stringify({ id: "app-123", status: "QUEUED_FOR_APPROVAL" }), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      });
    };

    const result = await api.createApplication("job-999", "QUEUED_FOR_APPROVAL");
    assert.equal(capturedMethod, "POST");
    assert.deepEqual(JSON.parse(capturedBody), { jobId: "job-999", status: "QUEUED_FOR_APPROVAL" });
    assert.equal(result.id, "app-123");
  });

  test("api throws error on non-ok HTTP response", async () => {
    globalThis.fetch = async () => {
      return new Response(JSON.stringify({ detail: "Job not found" }), {
        status: 404,
        statusText: "Not Found",
        headers: { "Content-Type": "application/json" },
      });
    };

    await assert.rejects(
      async () => {
        await api.getJob("non-existent");
      },
      (err: any) => {
        return err.message.includes("404");
      }
    );
  });

  test("api.getPlatforms queries platforms endpoint", async () => {
    let capturedUrl = "";
    globalThis.fetch = async (url: any) => {
      capturedUrl = String(url);
      return new Response(JSON.stringify([{ id: "linkedin", name: "LinkedIn" }]), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };

    const platforms = await api.getPlatforms();
    assert.match(capturedUrl, /\/platforms$/);
    assert.equal(platforms.length, 1);
    assert.equal(platforms[0].id, "linkedin");
  });

  test("api.getSecurityStatus queries audit status", async () => {
    let capturedUrl = "";
    globalThis.fetch = async (url: any) => {
      capturedUrl = String(url);
      return new Response(JSON.stringify({ killSwitchActive: false }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };

    const status = await api.getSecurityStatus();
    assert.match(capturedUrl, /\/audit\/status$/);
    assert.equal(status.killSwitchActive, false);
  });
});
