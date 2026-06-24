import test from "node:test";
import assert from "node:assert/strict";

import {
  calculateImpactSplit,
  formatAssetAmount,
  parseAssetAmount,
} from "../src/impact-math.js";

test("splits 100 OGC into 95 OGC and 5 OGC", () => {
  assert.deepEqual(calculateImpactSplit("100"), {
    grossStroops: 1_000_000_000n,
    recipientStroops: 950_000_000n,
    contributionStroops: 50_000_000n,
    gross: "100",
    recipient: "95",
    contribution: "5",
  });
});

test("preserves all stroops when rounding the contribution", () => {
  const split = calculateImpactSplit("1.0000001");
  assert.equal(split.recipientStroops + split.contributionStroops, split.grossStroops);
  assert.equal(split.recipient, "0.9500001");
  assert.equal(split.contribution, "0.05");
});

test("rejects values above the pilot cap", () => {
  assert.throws(() => calculateImpactSplit("100.0000001"), /limited to 100 OGC/);
});

test("rejects values too small for a meaningful split", () => {
  assert.throws(() => calculateImpactSplit("0.0000001"), /minimum routed payment/);
});

test("parses and formats Stellar asset precision", () => {
  assert.equal(parseAssetAmount("12.3456789"), 123_456_789n);
  assert.equal(formatAssetAmount(123_456_789n), "12.3456789");
  assert.throws(() => parseAssetAmount("1.12345678"), /7 decimal places/);
});
