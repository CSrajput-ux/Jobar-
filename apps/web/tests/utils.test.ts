import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { cn, formatSalary, formatTimeAgo } from "../lib/utils.ts";

describe("Frontend Utils Test Suite", () => {
  test("cn merges class names properly", () => {
    const res = cn("px-2 py-1", "bg-red-500", "text-white");
    assert.match(res, /px-2/);
    assert.match(res, /bg-red-500/);
    assert.match(res, /text-white/);
  });

  test("cn resolves conflicting tailwind classes", () => {
    const res = cn("px-2 px-4", "text-red-500 text-blue-500");
    assert.equal(res, "px-4 text-blue-500");
  });

  test("cn handles conditional and falsy values", () => {
    const isTrue = true;
    const isFalse = false;
    const res = cn("base-class", isTrue && "active", isFalse && "hidden", null, undefined);
    assert.equal(res, "base-class active");
  });

  test("formatSalary returns provided salary string or fallback", () => {
    assert.equal(formatSalary("$120k - $150k"), "$120k - $150k");
    assert.equal(formatSalary(""), "Competitive");
    assert.equal(formatSalary(undefined), "Competitive");
  });

  test("formatTimeAgo handles valid dates and fallbacks", () => {
    assert.equal(formatTimeAgo(undefined), "Recently");
    assert.equal(formatTimeAgo(""), "Recently");

    const justNow = new Date().toISOString();
    assert.equal(formatTimeAgo(justNow), "Just now");

    const fourHoursAgo = new Date(Date.now() - 4 * 3600 * 1000).toISOString();
    assert.equal(formatTimeAgo(fourHoursAgo), "4h ago");

    const threeDaysAgo = new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString();
    assert.equal(formatTimeAgo(threeDaysAgo), "3d ago");
  });
});
