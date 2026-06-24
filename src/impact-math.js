const STROOPS_PER_UNIT = 10_000_000n;
const CONTRIBUTION_PERCENT = 5n;
const PERCENT_BASE = 100n;
const MINIMUM_GROSS_STROOPS = 20n;
const MAXIMUM_GROSS_STROOPS = 100n * STROOPS_PER_UNIT;

export function parseAssetAmount(value) {
  const normalized = String(value ?? "").trim();

  if (!/^\d+(?:\.\d{1,7})?$/.test(normalized)) {
    throw new Error("Enter an OGC amount with no more than 7 decimal places.");
  }

  const [whole, fraction = ""] = normalized.split(".");
  return BigInt(whole) * STROOPS_PER_UNIT + BigInt(fraction.padEnd(7, "0"));
}

export function formatAssetAmount(stroops) {
  const value = BigInt(stroops);
  const whole = value / STROOPS_PER_UNIT;
  const fraction = (value % STROOPS_PER_UNIT).toString().padStart(7, "0").replace(/0+$/, "");
  return fraction ? `${whole}.${fraction}` : whole.toString();
}

export function calculateImpactSplit(value) {
  const grossStroops = typeof value === "bigint" ? value : parseAssetAmount(value);

  if (grossStroops < MINIMUM_GROSS_STROOPS) {
    throw new Error("The minimum routed payment is 0.000002 OGC.");
  }

  if (grossStroops > MAXIMUM_GROSS_STROOPS) {
    throw new Error("Pilot routed payments are limited to 100 OGC.");
  }

  const contributionStroops =
    (grossStroops * CONTRIBUTION_PERCENT + PERCENT_BASE / 2n) / PERCENT_BASE;
  const recipientStroops = grossStroops - contributionStroops;

  return {
    grossStroops,
    recipientStroops,
    contributionStroops,
    gross: formatAssetAmount(grossStroops),
    recipient: formatAssetAmount(recipientStroops),
    contribution: formatAssetAmount(contributionStroops),
  };
}

export const impactLimits = {
  minimumGross: formatAssetAmount(MINIMUM_GROSS_STROOPS),
  maximumGross: formatAssetAmount(MAXIMUM_GROSS_STROOPS),
};
