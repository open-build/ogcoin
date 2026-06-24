import {
  Asset,
  Horizon,
  Memo,
  Networks,
  Operation,
  StrKey,
  TransactionBuilder,
} from "@stellar/stellar-sdk";
import {
  getNetworkDetails,
  isConnected,
  requestAccess,
  signTransaction,
} from "@stellar/freighter-api";
import {
  Check,
  ChevronRight,
  Clipboard,
  Download,
  ExternalLink,
  FileKey,
  LoaderCircle,
  ReceiptText,
  RefreshCw,
  Send,
  ShieldCheck,
  TriangleAlert,
  Wallet,
  createElement,
  createIcons,
} from "lucide";

import { calculateImpactSplit, formatAssetAmount, parseAssetAmount } from "./impact-math.js";

const CONFIG = {
  assetCode: "OGC",
  issuer: "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57",
  treasury: "GDMAMIC6SBYCF4NUQ6RBTUIFB5WWWS3TTDHXNCOUOLDFEPK5XOOU525F",
  horizonUrl: "https://horizon.stellar.org",
  explorerUrl: "https://stellar.expert/explorer/public/tx",
  treasuryCap: "100",
  networkPassphrase: Networks.PUBLIC,
};

const FLOW_LABELS = {
  official_app_checkout: "Official app checkout",
  official_campaign: "Approved campaign",
  official_marketplace: "Approved marketplace",
  official_sponsorship: "Approved sponsorship",
};

const ICONS = {
  Check,
  ChevronRight,
  Clipboard,
  Download,
  ExternalLink,
  FileKey,
  LoaderCircle,
  ReceiptText,
  RefreshCw,
  Send,
  ShieldCheck,
  TriangleAlert,
  Wallet,
};

const server = new Horizon.Server(CONFIG.horizonUrl);
const asset = new Asset(CONFIG.assetCode, CONFIG.issuer);

const state = {
  mode: "freighter",
  source: "",
  prepared: null,
  receipt: null,
};

const elements = {};

function icon(name, className = "") {
  return createElement(ICONS[name], {
    width: 18,
    height: 18,
    "stroke-width": 2,
    class: className,
    "aria-hidden": "true",
  }).outerHTML;
}

function getErrorMessage(error) {
  if (error?.response?.data?.extras?.result_codes) {
    const codes = error.response.data.extras.result_codes;
    return `Stellar rejected the transaction: ${JSON.stringify(codes)}`;
  }

  return error?.message || error?.error || String(error || "Something went wrong.");
}

function truncateAddress(address) {
  return address ? `${address.slice(0, 8)}...${address.slice(-8)}` : "Not connected";
}

function isValidAddress(address) {
  return StrKey.isValidEd25519PublicKey(String(address || "").trim());
}

function findAssetBalance(account) {
  return account.balances.find(
    (balance) =>
      balance.asset_code === CONFIG.assetCode && balance.asset_issuer === CONFIG.issuer,
  );
}

function decimalToStroops(value) {
  return parseAssetAmount(String(value || "0"));
}

function availableAssetStroops(balance) {
  return decimalToStroops(balance.balance) - decimalToStroops(balance.selling_liabilities || "0");
}

function receivingCapacityStroops(balance) {
  return (
    decimalToStroops(balance.limit) -
    decimalToStroops(balance.balance) -
    decimalToStroops(balance.buying_liabilities || "0")
  );
}

function getNativeBalance(account) {
  return account.balances.find((balance) => balance.asset_type === "native");
}

function setStatus(message, type = "neutral") {
  elements.status.className = `checkout-status checkout-status--${type}`;
  elements.status.innerHTML =
    type === "error"
      ? `${icon("TriangleAlert")}<span>${message}</span>`
      : type === "success"
        ? `${icon("Check")}<span>${message}</span>`
        : `<span>${message}</span>`;
}

function setBusy(button, busy, busyLabel) {
  if (!button) return;
  button.disabled = busy;

  if (busy) {
    button.dataset.originalHtml = button.innerHTML;
    button.innerHTML = `${icon("LoaderCircle", "spin")}<span>${busyLabel}</span>`;
  } else if (button.dataset.originalHtml) {
    button.innerHTML = button.dataset.originalHtml;
    delete button.dataset.originalHtml;
  }
}

function resetPrepared() {
  state.prepared = null;
  state.receipt = null;
  elements.reviewActions.hidden = true;
  elements.xdrPanel.hidden = true;
  elements.receiptPanel.hidden = true;
  elements.prepareButton.hidden = false;
  elements.prepareButton.disabled = false;
  elements.reviewBadge.textContent = "Draft";
  elements.reviewBadge.className = "status-badge status-badge--draft";
}

function updateMode(mode) {
  state.mode = mode;
  state.source = "";
  resetPrepared();

  elements.modeButtons.forEach((button) => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });

  elements.freighterPanel.hidden = mode !== "freighter";
  elements.manualPanel.hidden = mode !== "manual";
  elements.signButton.hidden = mode !== "freighter";
  elements.manualActions.hidden = mode !== "manual";

  if (mode === "manual") {
    setStatus("Enter the payer public address to prepare an unsigned mainnet XDR.");
  } else {
    setStatus("Connect Freighter to prepare a payment. The site never receives your secret key.");
  }

  updateSourceDisplay();
  updateReview();
}

function updateSourceDisplay() {
  elements.connectedAddress.textContent = truncateAddress(state.source);
  elements.connectedAddress.title = state.source || "";
  elements.walletState.textContent = state.source ? "Connected" : "Not connected";
  elements.walletState.className = state.source
    ? "status-badge status-badge--ready"
    : "status-badge status-badge--draft";
  elements.connectButton.innerHTML = state.source
    ? `${icon("RefreshCw")}<span>Change account</span>`
    : `${icon("Wallet")}<span>Connect Freighter</span>`;
}

function updateReview() {
  let split;

  try {
    split = calculateImpactSplit(elements.amount.value || "0");
  } catch {
    split = { gross: "0", recipient: "0", contribution: "0" };
  }

  elements.reviewGross.textContent = `${split.gross} OGC`;
  elements.reviewRecipientAmount.textContent = `${split.recipient} OGC`;
  elements.reviewContribution.textContent = `${split.contribution} OGC`;
  elements.reviewRecipient.textContent = elements.recipient.value.trim()
    ? truncateAddress(elements.recipient.value.trim())
    : "Not set";
  elements.reviewFlow.textContent = FLOW_LABELS[elements.flowType.value] || "Not set";
  elements.reviewReference.textContent = elements.reference.value.trim() || "Not set";
  elements.reviewSource.textContent = state.source
    ? truncateAddress(state.source)
    : state.mode === "manual" && elements.manualSource.value.trim()
      ? truncateAddress(elements.manualSource.value.trim())
      : "Not connected";
}

function validateForm() {
  const recipient = elements.recipient.value.trim();
  const reference = elements.reference.value.trim();
  const source =
    state.mode === "manual" ? elements.manualSource.value.trim() : state.source.trim();

  if (!isValidAddress(source)) {
    throw new Error(
      state.mode === "manual"
        ? "Enter a valid payer Stellar G-address."
        : "Connect a valid Freighter account first.",
    );
  }

  if (!isValidAddress(recipient)) {
    throw new Error("Enter a valid recipient Stellar G-address.");
  }

  if (recipient === CONFIG.issuer) {
    throw new Error("The issuer account cannot receive its own OGC asset.");
  }

  if (recipient === CONFIG.treasury) {
    throw new Error("Choose a recipient other than the impact treasury.");
  }

  if (source === recipient) {
    throw new Error("The payer and recipient must be different accounts.");
  }

  if (!/^[A-Za-z0-9._-]{1,20}$/.test(reference)) {
    throw new Error("Use a public-safe reference of 1-20 letters, numbers, dots, dashes, or underscores.");
  }

  if (!FLOW_LABELS[elements.flowType.value]) {
    throw new Error("Choose an approved official payment flow.");
  }

  if (!elements.refundAcknowledgement.checked) {
    throw new Error("Confirm that you understand the displayed refund terms.");
  }

  return {
    source,
    recipient,
    reference,
    flowType: elements.flowType.value,
    split: calculateImpactSplit(elements.amount.value),
  };
}

function ensureTrustline(account, label) {
  const balance = findAssetBalance(account);

  if (!balance) {
    throw new Error(`${label} does not have an OGC trustline.`);
  }

  if (balance.is_authorized === false) {
    throw new Error(`${label}'s OGC trustline is not authorized.`);
  }

  return balance;
}

async function validateAccounts(form) {
  const [sourceAccount, recipientAccount, treasuryAccount, latestLedger, baseFee] =
    await Promise.all([
      server.loadAccount(form.source),
      server.loadAccount(form.recipient),
      server.loadAccount(CONFIG.treasury),
      server.ledgers().order("desc").limit(1).call(),
      server.fetchBaseFee(),
    ]);

  const sourceTrustline = ensureTrustline(sourceAccount, "The payer");
  const recipientTrustline = ensureTrustline(recipientAccount, "The recipient");
  const treasuryTrustline = ensureTrustline(treasuryAccount, "The impact treasury");

  if (availableAssetStroops(sourceTrustline) < form.split.grossStroops) {
    throw new Error(
      `The payer has ${formatAssetAmount(availableAssetStroops(sourceTrustline))} available OGC, which is below the gross payment.`,
    );
  }

  if (receivingCapacityStroops(recipientTrustline) < form.split.recipientStroops) {
    throw new Error("The recipient OGC trustline does not have enough receiving capacity.");
  }

  if (receivingCapacityStroops(treasuryTrustline) < form.split.contributionStroops) {
    throw new Error("The impact treasury OGC trustline does not have enough receiving capacity.");
  }

  const treasuryAfter =
    decimalToStroops(treasuryTrustline.balance) + form.split.contributionStroops;
  if (treasuryAfter > decimalToStroops(CONFIG.treasuryCap)) {
    throw new Error(
      `This payment would exceed the pilot treasury balance cap of ${CONFIG.treasuryCap} OGC.`,
    );
  }

  const nativeBalance = getNativeBalance(sourceAccount);
  const baseReserve = Number(latestLedger.records[0]?.base_reserve_in_stroops || 5_000_000);
  const reserveEntries =
    2 + sourceAccount.subentry_count + sourceAccount.num_sponsoring - sourceAccount.num_sponsored;
  const minimumNativeStroops = BigInt(Math.max(reserveEntries, 2) * baseReserve);
  const feeStroops = BigInt(baseFee * 2);
  const nativeAvailable =
    decimalToStroops(nativeBalance?.balance || "0") -
    decimalToStroops(nativeBalance?.selling_liabilities || "0") -
    minimumNativeStroops;

  if (nativeAvailable < feeStroops) {
    throw new Error("The payer does not have enough available XLM above reserve for transaction fees.");
  }

  return { sourceAccount, baseFee };
}

function buildTransaction(form, accountData) {
  return new TransactionBuilder(accountData.sourceAccount, {
    fee: String(accountData.baseFee),
    networkPassphrase: CONFIG.networkPassphrase,
  })
    .addOperation(assetPayment(form.recipient, form.split.recipient))
    .addOperation(assetPayment(CONFIG.treasury, form.split.contribution))
    .addMemo(Memo.text(`OGC:${form.reference}`))
    .setTimeout(900)
    .build();
}

function assetPayment(destination, amount) {
  return Operation.payment({
    destination,
    asset,
    amount,
  });
}

async function preparePayment() {
  const form = validateForm();
  const accountData = await validateAccounts(form);
  const transaction = buildTransaction(form, accountData);

  state.source = form.source;
  state.prepared = {
    ...form,
    xdr: transaction.toXDR(),
    preparedAt: new Date().toISOString(),
  };

  elements.reviewBadge.textContent = "Ready for authorization";
  elements.reviewBadge.className = "status-badge status-badge--ready";
  elements.prepareButton.hidden = true;
  elements.reviewActions.hidden = state.mode !== "freighter";
  elements.xdrPanel.hidden = false;
  elements.xdrOutput.value = state.prepared.xdr;
  elements.manualActions.hidden = state.mode !== "manual";
  elements.signButton.hidden = state.mode !== "freighter";
  updateSourceDisplay();
  updateReview();

  setStatus(
    state.mode === "freighter"
      ? "Checks passed. Review both payment operations before asking Freighter to sign."
      : "Checks passed. The unsigned XDR is ready for offline or external signing.",
    "success",
  );
}

async function connectFreighter() {
  const connection = await isConnected();

  if (connection.error || !connection.isConnected) {
    throw new Error(
      "Freighter was not detected. Install or unlock the extension, then try again, or use Manual XDR.",
    );
  }

  const access = await requestAccess();
  if (access.error || !isValidAddress(access.address)) {
    throw new Error(access.error?.message || "Freighter did not provide a valid account.");
  }

  const network = await getNetworkDetails();
  if (network.error) {
    throw new Error(network.error.message || "Could not read the Freighter network.");
  }

  if (network.networkPassphrase !== CONFIG.networkPassphrase) {
    throw new Error("Switch Freighter to the Stellar Public Network (Mainnet), then reconnect.");
  }

  state.source = access.address;
  resetPrepared();
  updateSourceDisplay();
  updateReview();
  setStatus("Freighter is connected to Stellar Mainnet.", "success");
}

async function signAndSubmit() {
  if (!state.prepared) {
    throw new Error("Prepare and review the payment before signing.");
  }

  const network = await getNetworkDetails();
  if (network.error || network.networkPassphrase !== CONFIG.networkPassphrase) {
    throw new Error("Freighter must be connected to Stellar Mainnet.");
  }

  const signed = await signTransaction(state.prepared.xdr, {
    networkPassphrase: CONFIG.networkPassphrase,
    address: state.prepared.source,
  });

  if (signed.error || !signed.signedTxXdr) {
    throw new Error(signed.error?.message || "Freighter did not sign the transaction.");
  }

  if (signed.signerAddress && signed.signerAddress !== state.prepared.source) {
    throw new Error("Freighter signed with a different account. No transaction was submitted.");
  }

  const transaction = TransactionBuilder.fromXDR(signed.signedTxXdr, CONFIG.networkPassphrase);
  const result = await server.submitTransaction(transaction);
  const receipt = {
    schema_version: "0.1",
    policy_version: "0.1",
    network: "Stellar Public Network",
    asset: `${CONFIG.assetCode}:${CONFIG.issuer}`,
    flow_type: state.prepared.flowType,
    reference: state.prepared.reference,
    payer: state.prepared.source,
    recipient: state.prepared.recipient,
    treasury: CONFIG.treasury,
    gross_ogc: state.prepared.split.gross,
    recipient_ogc: state.prepared.split.recipient,
    contribution_ogc: state.prepared.split.contribution,
    transaction_hash: result.hash,
    ledger: result.ledger,
    submitted_at: new Date().toISOString(),
  };

  state.receipt = receipt;
  showReceipt(receipt);
}

function showReceipt(receipt) {
  elements.reviewBadge.textContent = "Submitted";
  elements.reviewBadge.className = "status-badge status-badge--submitted";
  elements.reviewActions.hidden = true;
  elements.receiptPanel.hidden = false;
  elements.receiptHash.textContent = receipt.transaction_hash;
  elements.receiptLedger.textContent = String(receipt.ledger);
  elements.receiptLink.href = `${CONFIG.explorerUrl}/${receipt.transaction_hash}`;
  setStatus("The atomic 95/5 payment was accepted by Stellar Mainnet.", "success");
}

async function copyText(value, successMessage) {
  await navigator.clipboard.writeText(value);
  setStatus(successMessage, "success");
}

function downloadJson(data, filename) {
  const blob = new Blob([`${JSON.stringify(data, null, 2)}\n`], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function downloadText(value, filename) {
  const blob = new Blob([`${value}\n`], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function bindAsync(button, callback, busyLabel) {
  button.addEventListener("click", async () => {
    setBusy(button, true, busyLabel);
    try {
      await callback();
    } catch (error) {
      setStatus(getErrorMessage(error), "error");
    } finally {
      setBusy(button, false);
      if (button === elements.connectButton) {
        updateSourceDisplay();
      }
    }
  });
}

function applyQueryParameters() {
  const params = new URLSearchParams(window.location.search);
  const recipient = params.get("recipient");
  const amount = params.get("amount");
  const flow = params.get("flow");
  const reference = params.get("reference");

  if (recipient) elements.recipient.value = recipient;
  if (amount) elements.amount.value = amount;
  if (flow && FLOW_LABELS[flow]) elements.flowType.value = flow;
  if (reference) elements.reference.value = reference.slice(0, 20);
}

function initialize() {
  Object.assign(elements, {
    form: document.querySelector("#impact-checkout-form"),
    modeButtons: [...document.querySelectorAll("[data-mode]")],
    freighterPanel: document.querySelector("#freighter-panel"),
    manualPanel: document.querySelector("#manual-panel"),
    connectButton: document.querySelector("#connect-wallet"),
    connectedAddress: document.querySelector("#connected-address"),
    walletState: document.querySelector("#wallet-state"),
    manualSource: document.querySelector("#manual-source"),
    recipient: document.querySelector("#recipient"),
    amount: document.querySelector("#gross-amount"),
    flowType: document.querySelector("#flow-type"),
    reference: document.querySelector("#flow-reference"),
    refundAcknowledgement: document.querySelector("#refund-acknowledgement"),
    prepareButton: document.querySelector("#prepare-payment"),
    reviewGross: document.querySelector("#review-gross"),
    reviewRecipientAmount: document.querySelector("#review-recipient-amount"),
    reviewContribution: document.querySelector("#review-contribution"),
    reviewSource: document.querySelector("#review-source"),
    reviewRecipient: document.querySelector("#review-recipient"),
    reviewFlow: document.querySelector("#review-flow"),
    reviewReference: document.querySelector("#review-reference"),
    reviewBadge: document.querySelector("#review-badge"),
    reviewActions: document.querySelector("#review-actions"),
    signButton: document.querySelector("#sign-submit"),
    manualActions: document.querySelector("#manual-actions"),
    xdrPanel: document.querySelector("#xdr-panel"),
    xdrOutput: document.querySelector("#xdr-output"),
    copyXdrButton: document.querySelector("#copy-xdr"),
    downloadXdrButton: document.querySelector("#download-xdr"),
    receiptPanel: document.querySelector("#receipt-panel"),
    receiptHash: document.querySelector("#receipt-hash"),
    receiptLedger: document.querySelector("#receipt-ledger"),
    receiptLink: document.querySelector("#receipt-link"),
    downloadReceiptButton: document.querySelector("#download-receipt"),
    status: document.querySelector("#checkout-status"),
  });

  applyQueryParameters();
  createIcons({
    icons: {
      Wallet,
      FileKey,
      ShieldCheck,
    },
  });
  updateMode("freighter");
  updateSourceDisplay();
  updateReview();

  elements.modeButtons.forEach((button) => {
    button.addEventListener("click", () => updateMode(button.dataset.mode));
  });

  [elements.recipient, elements.amount, elements.flowType, elements.reference, elements.manualSource]
    .filter(Boolean)
    .forEach((input) => {
      input.addEventListener("input", () => {
        resetPrepared();
        updateReview();
      });
      input.addEventListener("change", () => {
        resetPrepared();
        updateReview();
      });
    });

  elements.refundAcknowledgement.addEventListener("change", resetPrepared);
  elements.form.addEventListener("submit", (event) => event.preventDefault());

  bindAsync(elements.connectButton, connectFreighter, "Connecting");
  bindAsync(elements.prepareButton, preparePayment, "Checking accounts");
  bindAsync(elements.signButton, signAndSubmit, "Waiting for Freighter");

  elements.copyXdrButton.addEventListener("click", () => {
    if (state.prepared) copyText(state.prepared.xdr, "Unsigned XDR copied.");
  });
  elements.downloadXdrButton.addEventListener("click", () => {
    if (state.prepared) downloadText(state.prepared.xdr, `ogc-${state.prepared.reference}.xdr.txt`);
  });
  elements.downloadReceiptButton.addEventListener("click", () => {
    if (state.receipt) {
      downloadJson(state.receipt, `ogc-${state.receipt.reference}-${state.receipt.transaction_hash}.json`);
    }
  });
}

initialize();
