#!/usr/bin/env python3
"""
Local OGCoin operator console.

This mini app combines the safest parts of the tools folder into a local web UI:
- live legitimacy checks for the Stellar asset and SEP-1 metadata
- recipient CSV validation and optional trustline checks
- unsigned home_domain XDR generation
- promotion and wallet/trustline copy helpers

It never asks for or stores secret keys, and it does not submit transactions.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import textwrap
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


TOOL_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TOOL_DIR.parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

ASSET_CODE = "OGC"
ISSUER = "GDSIFZE6L35WW2VMI2GDEA44HO34QNAAXTC473ZQDQZEUM2HGCC6GY57"
DISTRIBUTION_ACCOUNT = "GDD6IVZJVY3ZFWJ5T5BCZDURLF64ZTQJDDR5X5A7XEDJYTEC6ISDGWZB"
OPERATIONS_ACCOUNT = "GBZAC66WWHFU2FEOG5KECSEVR6EJO7BYK63UGB52SENDN4JEJTJEVK5L"
HOME_DOMAIN = "www.opengreencoin.com"
HORIZON_URL = "https://horizon.stellar.org"
STELLAR_TOML_URL = f"https://{HOME_DOMAIN}/.well-known/stellar.toml"
TRUST_URL = f"https://{HOME_DOMAIN}/trust.html"
GOVERNANCE_URL = f"https://{HOME_DOMAIN}/governance.html"
TRANSPARENCY_URL = f"https://{HOME_DOMAIN}/transparency.html"
TRANSPARENCY_DATA_URL = f"https://{HOME_DOMAIN}/data/transparency-log.json"
STELLAR_EXPERT_ASSET_URL = (
    f"https://stellar.expert/explorer/public/asset/{ASSET_CODE}-{ISSUER}"
)
STELLAR_EXPERT_API_URL = (
    f"https://api.stellar.expert/explorer/public/asset/{ASSET_CODE}-{ISSUER}"
)


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>OGCoin Local Console</title>
  <style>
    :root {
      --blue: #1b5fa3;
      --blue-dark: #144a84;
      --green: #1f9f6a;
      --orange: #f9943b;
      --ink: #172033;
      --muted: #627085;
      --line: #d9e1ec;
      --panel: #ffffff;
      --page: #f5f7fa;
      --bad: #b42318;
      --warn: #a15c07;
      --good: #067647;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--page);
    }
    header {
      background: linear-gradient(135deg, var(--blue-dark), var(--blue));
      color: white;
      padding: 24px;
      border-bottom: 4px solid var(--orange);
    }
    header .wrap, main {
      max-width: 1180px;
      margin: 0 auto;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 30px;
      letter-spacing: 0;
    }
    h2 {
      font-size: 18px;
      margin: 0 0 14px;
      letter-spacing: 0;
    }
    h3 {
      font-size: 15px;
      margin: 0 0 8px;
      letter-spacing: 0;
    }
    p { line-height: 1.5; }
    code, pre {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }
    main { padding: 24px; }
    .subtle { color: #dceafe; margin: 0; max-width: 820px; }
    .grid {
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 16px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 8px 22px rgba(23, 32, 51, 0.06);
    }
    .span-4 { grid-column: span 4; }
    .span-6 { grid-column: span 6; }
    .span-8 { grid-column: span 8; }
    .span-12 { grid-column: span 12; }
    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 16px;
    }
    button, .button-link {
      border: 1px solid transparent;
      border-radius: 6px;
      padding: 9px 12px;
      background: var(--blue);
      color: white;
      font-weight: 700;
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      min-height: 38px;
    }
    button.secondary, .button-link.secondary {
      background: white;
      color: var(--blue);
      border-color: var(--blue);
    }
    button.orange { background: var(--orange); }
    button:disabled { opacity: .55; cursor: not-allowed; }
    .status-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid var(--line);
    }
    .status-row:last-child { border-bottom: 0; }
    .badge {
      border-radius: 999px;
      padding: 4px 9px;
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    .badge.good { background: #dcfae6; color: var(--good); }
    .badge.warn { background: #fef0c7; color: var(--warn); }
    .badge.bad { background: #fee4e2; color: var(--bad); }
    .badge.neutral { background: #e8eef7; color: var(--blue-dark); }
    .metric {
      font-size: 26px;
      font-weight: 800;
      margin-top: 6px;
    }
    .muted { color: var(--muted); }
    .small { font-size: 13px; }
    textarea, input, select {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px;
      font: inherit;
      background: white;
      color: var(--ink);
    }
    textarea { min-height: 190px; resize: vertical; }
    label {
      display: block;
      font-weight: 700;
      margin-bottom: 6px;
    }
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 12px;
    }
    .checkbox-line {
      display: flex;
      gap: 8px;
      align-items: center;
      margin: 10px 0 14px;
      color: var(--muted);
    }
    .checkbox-line input { width: auto; }
    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #101828;
      color: #f9fafb;
      border-radius: 8px;
      padding: 14px;
      max-height: 320px;
      overflow: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      background: white;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }
    th { color: var(--muted); font-size: 12px; }
    .table-wrap { overflow: auto; max-height: 360px; border: 1px solid var(--line); border-radius: 8px; }
    .copy-list {
      display: grid;
      gap: 10px;
    }
    .copy-item {
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
    }
    .split {
      display: flex;
      justify-content: space-between;
      align-items: start;
      gap: 12px;
    }
    a { color: var(--blue); }
    @media (max-width: 820px) {
      .span-4, .span-6, .span-8 { grid-column: span 12; }
      .form-row { grid-template-columns: 1fr; }
      header, main { padding-left: 16px; padding-right: 16px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <h1>OGCoin Local Console</h1>
      <p class="subtle">A local-only dashboard for legitimacy checks, distribution prep, and public campaign copy. No secret keys. No transaction submission.</p>
    </div>
  </header>
  <main>
    <section class="toolbar">
      <button id="refreshStatus">Run Live Check</button>
      <a class="button-link secondary" href="http://localhost:8000/admin/" target="_blank" rel="noreferrer">Open ForgeWeb</a>
      <a class="button-link secondary" href="https://www.opengreencoin.com/" target="_blank" rel="noreferrer">Live Site</a>
      <a class="button-link secondary" href="__TRUST_URL__" target="_blank" rel="noreferrer">Trust Page</a>
      <a class="button-link secondary" href="__GOVERNANCE_URL__" target="_blank" rel="noreferrer">Governance</a>
      <a class="button-link secondary" href="__TRANSPARENCY_URL__" target="_blank" rel="noreferrer">Transparency</a>
      <a class="button-link secondary" href="__STELLAR_EXPERT_ASSET_URL__" target="_blank" rel="noreferrer">StellarExpert</a>
    </section>

    <section class="grid" aria-label="Legitimacy overview">
      <div class="panel span-4">
        <h2>Asset</h2>
        <div class="muted small">Issuer</div>
        <div class="small"><code>__ISSUER__</code></div>
        <div id="assetMetric" class="metric">Checking</div>
        <div id="assetMeta" class="muted small">Waiting for live check.</div>
      </div>
      <div class="panel span-4">
        <h2>Metadata</h2>
        <div class="muted small">SEP-1</div>
        <div class="small"><code>__STELLAR_TOML_URL__</code></div>
        <div id="tomlMetric" class="metric">Checking</div>
        <div id="tomlMeta" class="muted small">Waiting for live check.</div>
      </div>
      <div class="panel span-4">
        <h2>Market</h2>
        <div class="muted small">OGC/XLM liquidity</div>
        <div class="small"><code>Stellar DEX</code></div>
        <div id="marketMetric" class="metric">Checking</div>
        <div id="marketMeta" class="muted small">Waiting for live check.</div>
      </div>

      <div class="panel span-8">
        <div class="split">
          <h2>Readiness Checklist</h2>
          <span id="lastChecked" class="muted small"></span>
        </div>
        <div id="checklist"></div>
      </div>
      <div class="panel span-4">
        <h2>Important Accounts</h2>
        <div class="status-row"><span>Issuer</span><code class="small">__ISSUER_SHORT__</code></div>
        <div class="status-row"><span>Distribution</span><code class="small">__DISTRIBUTION_SHORT__</code></div>
        <div class="status-row"><span>Operations</span><code class="small">__OPERATIONS_SHORT__</code></div>
        <p class="muted small">Keep the issuer cold. Use distribution, treasury, and market-making accounts for operational work.</p>
      </div>
    </section>

    <section class="grid" style="margin-top:16px" aria-label="Distribution tools">
      <div class="panel span-8">
        <h2>Recipient Validator</h2>
        <p class="muted small">Paste CSV with <code>address</code> and optional <code>amount</code>, or paste one Stellar address per line. Online checks verify account existence and OGC trustlines.</p>
        <label for="recipientText">Recipients</label>
        <textarea id="recipientText" spellcheck="false" placeholder="address,amount,memo&#10;G...,1.5,airdrop"></textarea>
        <div class="form-row">
          <div>
            <label for="minAmount">Default minimum OGC</label>
            <input id="minAmount" value="1">
          </div>
          <div>
            <label for="maxAmount">Default maximum OGC</label>
            <input id="maxAmount" value="3">
          </div>
        </div>
        <label class="checkbox-line">
          <input id="onlineChecks" type="checkbox">
          Check live accounts and OGC trustlines. This can be slower for large lists.
        </label>
        <div class="toolbar">
          <button id="validateRecipients">Validate Recipients</button>
          <button id="downloadValid" class="secondary" disabled>Download Valid CSV</button>
        </div>
        <div id="recipientSummary" class="muted small">No recipients validated yet.</div>
        <div class="table-wrap" style="margin-top:12px">
          <table>
            <thead><tr><th>#</th><th>Address</th><th>Amount</th><th>Status</th><th>Notes</th></tr></thead>
            <tbody id="recipientRows"><tr><td colspan="5" class="muted">Results will appear here.</td></tr></tbody>
          </table>
        </div>
      </div>

      <div class="panel span-4">
        <h2>Distribution Plan</h2>
        <div id="distributionPlan" class="muted small">Validate recipients to estimate airdrop totals and batch count.</div>
        <pre id="distributionCommands">python tools/airdrop_distribution.py</pre>
      </div>
    </section>

    <section class="grid" style="margin-top:16px" aria-label="Legitimacy actions">
      <div class="panel span-6">
        <h2>Home Domain XDR</h2>
        <p class="muted small">Generate an unsigned transaction to link the issuer account to <code>www.opengreencoin.com</code>. Sign it separately with the issuer account.</p>
        <div class="form-row">
          <div>
            <label for="homeDomain">Home domain</label>
            <input id="homeDomain" value="__HOME_DOMAIN__">
          </div>
          <div>
            <label for="network">Network</label>
            <select id="network"><option value="public">public</option><option value="testnet">testnet</option></select>
          </div>
        </div>
        <button id="generateXdr" class="orange">Generate Unsigned XDR</button>
        <pre id="xdrOutput">No XDR generated yet.</pre>
      </div>

      <div class="panel span-6">
        <h2>Promotion Copy</h2>
        <p class="muted small">Use plain utility language. Avoid profit, investment, guaranteed liquidity, or fixed redemption claims.</p>
        <div id="promoCopy" class="copy-list"></div>
      </div>
    </section>
  </main>

  <script>
    const state = { validRows: [] };
    const $ = (selector) => document.querySelector(selector);

    function badge(status) {
      const label = status === 'good' ? 'OK' : status === 'warn' ? 'Needs Work' : status === 'bad' ? 'Blocked' : 'Info';
      return `<span class="badge ${status || 'neutral'}">${label}</span>`;
    }

    function shortKey(value) {
      if (!value || value.length < 14) return value || '';
      return `${value.slice(0, 7)}...${value.slice(-6)}`;
    }

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { 'Content-Type': 'application/json' },
        ...options
      });
      const data = await response.json();
      if (!response.ok || data.error) {
        throw new Error(data.error || `Request failed: ${response.status}`);
      }
      return data;
    }

    function renderStatus(data) {
      $('#lastChecked').textContent = `Last checked ${new Date(data.generated_at).toLocaleString()}`;
      $('#assetMetric').textContent = data.asset.exists ? 'Live' : 'Missing';
      $('#assetMeta').textContent = data.asset.exists
        ? `${data.asset.accounts_authorized || 0} authorized trustlines, ${data.asset.claimable_balances_amount || '0'} claimable OGC`
        : data.asset.error || 'Asset not found in Horizon.';
      $('#tomlMetric').textContent = data.toml.reachable ? 'Published' : 'Missing';
      $('#tomlMeta').textContent = data.toml.reachable
        ? `Issuer listed: ${data.toml.contains_issuer ? 'yes' : 'no'}, asset listed: ${data.toml.contains_asset ? 'yes' : 'no'}`
        : data.toml.error || 'Not reachable yet.';
      $('#marketMetric').textContent = data.market.has_liquidity ? 'Liquid' : 'No Market';
      $('#marketMeta').textContent = `${data.market.bid_count || 0} bids, ${data.market.ask_count || 0} asks, ${data.market.pool_count || 0} pools`;
      $('#checklist').innerHTML = data.readiness.map(item => `
        <div class="status-row">
          <div>
            <strong>${item.title}</strong>
            <div class="muted small">${item.detail}</div>
          </div>
          ${badge(item.status)}
        </div>
      `).join('');
    }

    async function loadStatus() {
      $('#refreshStatus').disabled = true;
      $('#refreshStatus').textContent = 'Checking...';
      try {
        renderStatus(await api('/api/status'));
      } catch (error) {
        $('#checklist').innerHTML = `<div class="status-row"><span>${error.message}</span>${badge('bad')}</div>`;
      } finally {
        $('#refreshStatus').disabled = false;
        $('#refreshStatus').textContent = 'Run Live Check';
      }
    }

    function renderRecipients(data) {
      state.validRows = data.rows.filter(row => row.valid);
      $('#downloadValid').disabled = state.validRows.length === 0;
      $('#recipientSummary').textContent =
        `${data.summary.total} total, ${data.summary.valid} valid, ${data.summary.invalid} invalid, ${data.summary.with_trustline} with trustline.`;
      $('#distributionPlan').innerHTML = `
        <div class="status-row"><span>Valid recipients</span><strong>${data.summary.valid}</strong></div>
        <div class="status-row"><span>Estimated OGC needed</span><strong>${data.plan.estimated_total}</strong></div>
        <div class="status-row"><span>Suggested batches</span><strong>${data.plan.suggested_batches}</strong></div>
        <p class="muted small">Use this as a prep step. Actual airdrops should still be dry-run and signed from a controlled distribution account.</p>
      `;
      $('#distributionCommands').textContent = data.plan.commands.join('\\n');
      $('#recipientRows').innerHTML = data.rows.length ? data.rows.map(row => `
        <tr>
          <td>${row.index}</td>
          <td><code>${shortKey(row.address)}</code></td>
          <td>${row.amount || ''}</td>
          <td>${row.valid ? badge(row.status === 'ready' ? 'good' : 'warn') : badge('bad')}</td>
          <td>${row.notes.join('; ')}</td>
        </tr>
      `).join('') : '<tr><td colspan="5" class="muted">No rows found.</td></tr>';
    }

    async function validateRecipients() {
      $('#validateRecipients').disabled = true;
      $('#validateRecipients').textContent = 'Validating...';
      try {
        const data = await api('/api/validate-recipients', {
          method: 'POST',
          body: JSON.stringify({
            text: $('#recipientText').value,
            online: $('#onlineChecks').checked,
            min_amount: $('#minAmount').value,
            max_amount: $('#maxAmount').value
          })
        });
        renderRecipients(data);
      } catch (error) {
        $('#recipientSummary').textContent = error.message;
      } finally {
        $('#validateRecipients').disabled = false;
        $('#validateRecipients').textContent = 'Validate Recipients';
      }
    }

    function downloadValidCsv() {
      const rows = [['address', 'amount', 'memo'], ...state.validRows.map(row => [row.address, row.amount || '', row.memo || ''])];
      const csv = rows.map(row => row.map(cell => `"${String(cell).replaceAll('"', '""')}"`).join(',')).join('\\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'ogc_valid_recipients.csv';
      link.click();
      URL.revokeObjectURL(url);
    }

    async function generateXdr() {
      $('#generateXdr').disabled = true;
      $('#xdrOutput').textContent = 'Generating...';
      try {
        const data = await api('/api/home-domain-xdr', {
          method: 'POST',
          body: JSON.stringify({
            issuer: '__ISSUER__',
            home_domain: $('#homeDomain').value,
            network: $('#network').value
          })
        });
        $('#xdrOutput').textContent = `${data.xdr}\\n\\nSign with issuer account, then submit.\\n${data.signer_url}`;
      } catch (error) {
        $('#xdrOutput').textContent = error.message;
      } finally {
        $('#generateXdr').disabled = false;
      }
    }

    async function loadPromo() {
      const data = await api('/api/promo');
      $('#promoCopy').innerHTML = data.items.map(item => `
        <div class="copy-item">
          <div class="split">
            <h3>${item.title}</h3>
            <button class="secondary" data-copy="${encodeURIComponent(item.body)}">Copy</button>
          </div>
          <p class="small">${item.body}</p>
        </div>
      `).join('');
      document.querySelectorAll('[data-copy]').forEach(button => {
        button.addEventListener('click', () => navigator.clipboard.writeText(decodeURIComponent(button.dataset.copy)));
      });
    }

    $('#refreshStatus').addEventListener('click', loadStatus);
    $('#validateRecipients').addEventListener('click', validateRecipients);
    $('#downloadValid').addEventListener('click', downloadValidCsv);
    $('#generateXdr').addEventListener('click', generateXdr);
    loadStatus();
    loadPromo();
  </script>
</body>
</html>
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def http_json(url: str, timeout: int = 15) -> tuple[dict[str, Any] | None, str | None]:
    try:
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "OGCoinConsole/1.0"})
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}: {exc.reason}"
    except (URLError, TimeoutError, ValueError) as exc:
        return None, str(exc)


def http_text(url: str, timeout: int = 15) -> tuple[str | None, str | None]:
    try:
        request = Request(url, headers={"Accept": "text/plain", "User-Agent": "OGCoinConsole/1.0"})
        with urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace"), None
    except HTTPError as exc:
        return None, f"HTTP {exc.code}: {exc.reason}"
    except (URLError, TimeoutError) as exc:
        return None, str(exc)


def decimal_or_none(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if amount <= 0 or amount.as_tuple().exponent < -7:
        return None
    return amount


def is_valid_stellar_address(address: str) -> bool:
    address = (address or "").strip()
    try:
        from stellar_sdk import StrKey

        return StrKey.is_valid_ed25519_public_key(address)
    except Exception:
        return bool(re.fullmatch(r"G[A-Z2-7]{55}", address))


def account_trustline_status(address: str) -> dict[str, Any]:
    data, error = http_json(f"{HORIZON_URL}/accounts/{address}", timeout=12)
    if error:
        return {"exists": False, "has_trustline": False, "error": error}
    balances = data.get("balances", []) if data else []
    has_trustline = any(
        balance.get("asset_code") == ASSET_CODE and balance.get("asset_issuer") == ISSUER
        for balance in balances
    )
    return {
        "exists": True,
        "has_trustline": has_trustline,
        "error": None,
    }


def build_status() -> dict[str, Any]:
    issuer_data, issuer_error = http_json(f"{HORIZON_URL}/accounts/{ISSUER}")
    asset_data, asset_error = http_json(
        f"{HORIZON_URL}/assets?asset_code={ASSET_CODE}&asset_issuer={ISSUER}"
    )
    order_book_data, order_book_error = http_json(
        f"{HORIZON_URL}/order_book?"
        f"selling_asset_type=credit_alphanum4&selling_asset_code={ASSET_CODE}"
        f"&selling_asset_issuer={ISSUER}&buying_asset_type=native&limit=20"
    )
    expert_data, expert_error = http_json(STELLAR_EXPERT_API_URL)
    toml_text, toml_error = http_text(STELLAR_TOML_URL)
    trust_text, trust_error = http_text(TRUST_URL)
    governance_text, governance_error = http_text(GOVERNANCE_URL)
    transparency_text, transparency_error = http_text(TRANSPARENCY_URL)
    transparency_data, transparency_data_error = http_json(TRANSPARENCY_DATA_URL)

    asset_record: dict[str, Any] = {}
    if asset_data:
        records = asset_data.get("_embedded", {}).get("records", [])
        asset_record = records[0] if records else {}

    bids = order_book_data.get("bids", []) if order_book_data else []
    asks = order_book_data.get("asks", []) if order_book_data else []
    pool_count = int(asset_record.get("num_liquidity_pools") or 0)
    contains_issuer = bool(toml_text and ISSUER in toml_text)
    contains_asset = bool(toml_text and f'code="{ASSET_CODE}"' in toml_text and f'issuer="{ISSUER}"' in toml_text)
    home_domain = issuer_data.get("home_domain") if issuer_data else None
    thresholds = issuer_data.get("thresholds", {}) if issuer_data else {}
    signers = issuer_data.get("signers", []) if issuer_data else []
    master_signer = next((signer for signer in signers if signer.get("key") == ISSUER), {})
    master_weight = int(master_signer.get("weight") or 0)
    high_threshold = int(thresholds.get("high_threshold") or 0)
    total_signer_weight = sum(int(signer.get("weight") or 0) for signer in signers)
    active_signer_count = sum(1 for signer in signers if int(signer.get("weight") or 0) > 0)
    issuer_hardened = (
        active_signer_count >= 2
        and high_threshold > master_weight
        and total_signer_weight >= high_threshold
    )

    readiness = [
        {
            "title": "Mainnet asset exists",
            "status": "good" if asset_record else "bad",
            "detail": asset_error if not asset_record else "Horizon returns the OGC asset record.",
        },
        {
            "title": "SEP-1 stellar.toml is live",
            "status": "good" if toml_text and contains_issuer and contains_asset else "bad",
            "detail": "Issuer and OGC entry are listed." if toml_text and contains_issuer and contains_asset else (toml_error or "Missing issuer or asset entry."),
        },
        {
            "title": "Issuer home_domain is set",
            "status": "good" if home_domain == HOME_DOMAIN else "bad",
            "detail": f"Current home_domain: {home_domain or 'not set'}",
        },
        {
            "title": "Public trust and risk page is live",
            "status": "good" if trust_text and "Trust, Risk, and Governance" in trust_text else "warn",
            "detail": (
                "Verification, risk, governance, liquidity, and payroll disclosures are published."
                if trust_text and "Trust, Risk, and Governance" in trust_text
                else (trust_error or "Deploy trust.html before broad promotion.")
            ),
        },
        {
            "title": "Issuer and treasury governance policy is live",
            "status": "good" if governance_text and "Issuer and Treasury Governance" in governance_text else "warn",
            "detail": (
                "Issuer, supply, signer, treasury, distribution, and liquidity guardrails are published."
                if governance_text and "Issuer and Treasury Governance" in governance_text
                else (governance_error or "Deploy governance.html before broad promotion.")
            ),
        },
        {
            "title": "Transparency log is live",
            "status": (
                "good"
                if transparency_text
                and "Transparency Log" in transparency_text
                and transparency_data
                and transparency_data.get("entries")
                else "warn"
            ),
            "detail": (
                f"{len(transparency_data.get('entries', []))} public records in the machine-readable log."
                if transparency_text
                and "Transparency Log" in transparency_text
                and transparency_data
                and transparency_data.get("entries")
                else (transparency_error or transparency_data_error or "Deploy transparency.html and data/transparency-log.json.")
            ),
        },
        {
            "title": "Trading liquidity exists",
            "status": "good" if bids or asks or pool_count else "bad",
            "detail": f"{len(bids)} bids, {len(asks)} asks, {pool_count} liquidity pools.",
        },
        {
            "title": "Trustline adoption",
            "status": "good" if int(asset_record.get("accounts", {}).get("authorized") or 0) >= 10 else "warn",
            "detail": f"{asset_record.get('accounts', {}).get('authorized', 0)} authorized trustlines.",
        },
        {
            "title": "Issuer supply governance",
            "status": "good" if issuer_hardened or master_weight == 0 else "warn",
            "detail": (
                f"Master signer weight {master_weight}, high threshold {high_threshold}, "
                f"{active_signer_count} active signer(s), total signer weight {total_signer_weight}. "
                + (
                    "Issuer signer policy is hardened; do not make fixed-supply claims until an issuer-lock or supply policy is separately approved."
                    if issuer_hardened
                    else "Interim policy is published; complete signer hardening before making fixed-supply claims."
                )
            ),
        },
        {
            "title": "StellarExpert rating",
            "status": "good" if (expert_data or {}).get("rating", {}).get("average", 0) >= 3 else "warn",
            "detail": (
                f"Average rating {(expert_data or {}).get('rating', {}).get('average', 'unavailable')}. "
                f"{expert_error or 'Improve metadata, liquidity, and usage to raise confidence.'}"
            ),
        },
    ]

    return {
        "generated_at": now_iso(),
        "issuer": {
            "exists": bool(issuer_data),
            "home_domain": home_domain,
            "thresholds": thresholds,
            "master_weight": master_weight,
            "total_signer_weight": total_signer_weight,
            "active_signer_count": active_signer_count,
            "error": issuer_error,
        },
        "asset": {
            "exists": bool(asset_record),
            "accounts_authorized": asset_record.get("accounts", {}).get("authorized"),
            "claimable_balances_amount": asset_record.get("claimable_balances_amount"),
            "balances_authorized": asset_record.get("balances", {}).get("authorized"),
            "error": asset_error,
        },
        "toml": {
            "url": STELLAR_TOML_URL,
            "reachable": bool(toml_text),
            "contains_issuer": contains_issuer,
            "contains_asset": contains_asset,
            "error": toml_error,
        },
        "trust_page": {
            "url": TRUST_URL,
            "reachable": bool(trust_text),
            "contains_disclosures": bool(trust_text and "Trust, Risk, and Governance" in trust_text),
            "error": trust_error,
        },
        "governance_page": {
            "url": GOVERNANCE_URL,
            "reachable": bool(governance_text),
            "contains_policy": bool(governance_text and "Issuer and Treasury Governance" in governance_text),
            "error": governance_error,
        },
        "transparency_page": {
            "url": TRANSPARENCY_URL,
            "data_url": TRANSPARENCY_DATA_URL,
            "reachable": bool(transparency_text),
            "contains_log": bool(transparency_text and "Transparency Log" in transparency_text),
            "record_count": len((transparency_data or {}).get("entries", [])) if transparency_data else 0,
            "error": transparency_error or transparency_data_error,
        },
        "market": {
            "has_liquidity": bool(bids or asks or pool_count),
            "bid_count": len(bids),
            "ask_count": len(asks),
            "pool_count": pool_count,
            "error": order_book_error,
        },
        "stellar_expert": {
            "data": expert_data or {},
            "error": expert_error,
        },
        "readiness": readiness,
    }


ADDRESS_FIELDS = [
    "address",
    "stellar_address",
    "stellaraddress",
    "public_key",
    "publickey",
    "your stellar address (public key)",
]


def normalized_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def parse_recipient_rows(text: str) -> list[dict[str, str]]:
    text = (text or "").strip()
    if not text:
        return []

    sample = text.splitlines()[0]
    has_csv_shape = "," in sample or "\t" in sample or ";" in sample
    if not has_csv_shape:
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = re.split(r"\s+", line)
            rows.append({"address": parts[0], "amount": parts[1] if len(parts) > 1 else "", "memo": ""})
        return rows

    stream = io.StringIO(text)
    try:
        dialect = csv.Sniffer().sniff(text[:2048])
    except csv.Error:
        dialect = csv.excel

    first_line = next(csv.reader(io.StringIO(text), dialect), [])
    normalized_headers = {normalized_key(header) for header in first_line}
    has_header = bool(normalized_headers.intersection({normalized_key(field) for field in ADDRESS_FIELDS}))

    stream.seek(0)
    if has_header:
        reader = csv.DictReader(stream, dialect=dialect)
        parsed = []
        for raw_row in reader:
            normalized = {normalized_key(key or ""): (value or "").strip() for key, value in raw_row.items()}
            address = ""
            for field in ADDRESS_FIELDS:
                address = normalized.get(normalized_key(field), "")
                if address:
                    break
            parsed.append(
                {
                    "address": address,
                    "amount": normalized.get("amount", ""),
                    "memo": normalized.get("memo", ""),
                }
            )
        return parsed

    reader = csv.reader(stream, dialect)
    return [
        {
            "address": row[0].strip() if len(row) > 0 else "",
            "amount": row[1].strip() if len(row) > 1 else "",
            "memo": row[2].strip() if len(row) > 2 else "",
        }
        for row in reader
        if row
    ]


def validate_recipients(payload: dict[str, Any]) -> dict[str, Any]:
    rows = parse_recipient_rows(payload.get("text", ""))
    online = bool(payload.get("online"))
    min_amount = decimal_or_none(payload.get("min_amount")) or Decimal("1")
    max_amount = decimal_or_none(payload.get("max_amount")) or Decimal("3")
    average_amount = (min_amount + max_amount) / Decimal("2")

    results: list[dict[str, Any]] = []
    valid_count = 0
    invalid_count = 0
    trustline_count = 0

    for index, row in enumerate(rows, start=1):
        address = row.get("address", "").strip()
        amount_text = row.get("amount", "").strip()
        amount = decimal_or_none(amount_text) if amount_text else average_amount
        notes: list[str] = []
        valid = True
        status = "format-only"

        if not is_valid_stellar_address(address):
            valid = False
            notes.append("Invalid Stellar public key.")
        if amount is None:
            valid = False
            notes.append("Invalid amount. Use a positive number with at most 7 decimal places.")
        if row.get("memo") and len(row["memo"].encode("utf-8")) > 28:
            valid = False
            notes.append("Memo is longer than Stellar's 28-byte text memo limit.")

        if valid and online:
            live = account_trustline_status(address)
            if not live["exists"]:
                valid = False
                notes.append(f"Account not ready: {live['error']}")
            elif live["has_trustline"]:
                trustline_count += 1
                status = "ready"
                notes.append("Account exists and has OGC trustline.")
            else:
                status = "needs-trustline"
                notes.append("Account exists but does not have OGC trustline.")
        elif valid:
            notes.append("Format valid. Run online checks before distribution.")

        if valid:
            valid_count += 1
        else:
            invalid_count += 1

        results.append(
            {
                "index": index,
                "address": address,
                "amount": str(amount) if amount is not None else amount_text,
                "memo": row.get("memo", ""),
                "valid": valid,
                "status": status,
                "notes": notes,
            }
        )

    estimated_total = average_amount * Decimal(valid_count)
    chunk_size = 25
    suggested_batches = (valid_count + chunk_size - 1) // chunk_size if valid_count else 0
    commands = [
        "python tools/ogcoin_console.py",
        "python tools/validate_and_fix_recipients.py",
        "python tools/airdrop_dry_run.py",
        "# Only after dry-run, signer review, and treasury approval:",
        "python tools/airdrop_distribution.py",
    ]

    return {
        "summary": {
            "total": len(rows),
            "valid": valid_count,
            "invalid": invalid_count,
            "with_trustline": trustline_count,
        },
        "plan": {
            "estimated_total": f"{estimated_total:.7f}".rstrip("0").rstrip("."),
            "suggested_batches": suggested_batches,
            "commands": commands,
        },
        "rows": results,
    }


def generate_home_domain_xdr(payload: dict[str, Any]) -> dict[str, str]:
    try:
        from create_home_domain_xdr import NETWORKS, build_home_domain_xdr
    except Exception as exc:
        raise RuntimeError(f"Unable to import XDR helper: {exc}") from exc

    issuer = (payload.get("issuer") or ISSUER).strip()
    home_domain = (payload.get("home_domain") or HOME_DOMAIN).strip()
    network = (payload.get("network") or "public").strip()
    if network not in NETWORKS:
        raise ValueError("Unsupported network.")
    if not is_valid_stellar_address(issuer):
        raise ValueError("Invalid issuer public key.")
    if not re.fullmatch(r"[a-zA-Z0-9.-]+", home_domain):
        raise ValueError("Invalid home domain.")

    return {
        "xdr": build_home_domain_xdr(issuer=issuer, home_domain=home_domain, network=network),
        "signer_url": NETWORKS[network]["lab"],
    }


def promo_items() -> dict[str, list[dict[str, str]]]:
    trustline = f"{ASSET_CODE}:{ISSUER}"
    return {
        "items": [
            {
                "title": "Short Launch Copy",
                "body": (
                    "OGCoin (OGC) is a Stellar mainnet asset from Open Build for open source funding, "
                    "developer education, and transparent community grants. Add the OGC trustline and follow the public ledger."
                ),
            },
            {
                "title": "Trustline Instructions",
                "body": (
                    f"To receive OGC, add a custom Stellar asset trustline. Asset code: {ASSET_CODE}. "
                    f"Issuer: {ISSUER}. Network: Stellar public network."
                ),
            },
            {
                "title": "Risk Disclosure",
                "body": (
                    "OGC is experimental, not anchored to fiat or equity, and early markets may be illiquid. "
                    "Do not treat OGC as a promise of profit, redemption, salary value, or ownership in Open Build."
                ),
            },
            {
                "title": "Asset Identifier",
                "body": trustline,
            },
            {
                "title": "Explorer Link",
                "body": STELLAR_EXPERT_ASSET_URL,
            },
        ]
    }


def render_html() -> bytes:
    html = (
        HTML.replace("__ISSUER__", ISSUER)
        .replace("__ISSUER_SHORT__", f"{ISSUER[:7]}...{ISSUER[-6:]}")
        .replace("__DISTRIBUTION_SHORT__", f"{DISTRIBUTION_ACCOUNT[:7]}...{DISTRIBUTION_ACCOUNT[-6:]}")
        .replace("__OPERATIONS_SHORT__", f"{OPERATIONS_ACCOUNT[:7]}...{OPERATIONS_ACCOUNT[-6:]}")
        .replace("__HOME_DOMAIN__", HOME_DOMAIN)
        .replace("__STELLAR_TOML_URL__", STELLAR_TOML_URL)
        .replace("__TRUST_URL__", TRUST_URL)
        .replace("__GOVERNANCE_URL__", GOVERNANCE_URL)
        .replace("__TRANSPARENCY_URL__", TRANSPARENCY_URL)
        .replace("__STELLAR_EXPERT_ASSET_URL__", STELLAR_EXPERT_ASSET_URL)
    )
    return html.encode("utf-8")


class OGCoinConsoleHandler(BaseHTTPRequestHandler):
    server_version = "OGCoinConsole/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text: str, content_type: str = "text/plain; charset=utf-8", status: int = 200) -> None:
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            body = render_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/status":
            self.send_json(build_status())
            return
        if parsed.path == "/api/promo":
            self.send_json(promo_items())
            return
        if parsed.path == "/api/template.csv":
            self.send_text("address,amount,memo\nG...,1,airdrop\n", "text/csv; charset=utf-8")
            return
        if parsed.path == "/health":
            self.send_json({"status": "ok", "time": now_iso()})
            return
        self.send_json({"error": "Not found"}, status=404)

    def do_POST(self) -> None:
        try:
            payload = self.read_json_body()
            parsed = urlparse(self.path)
            if parsed.path == "/api/validate-recipients":
                self.send_json(validate_recipients(payload))
                return
            if parsed.path == "/api/home-domain-xdr":
                self.send_json(generate_home_domain_xdr(payload))
                return
            self.send_json({"error": "Not found"}, status=404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, status=400)

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()


def run(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), OGCoinConsoleHandler)
    url_host = "localhost" if host in {"127.0.0.1", "0.0.0.0"} else host
    print(
        textwrap.dedent(
            f"""
            OGCoin Local Console running.

            URL: http://{url_host}:{port}/
            Scope: local checks, recipient prep, unsigned XDR generation.
            Safety: no secret keys, no transaction submission.

            Press Ctrl+C to stop.
            """
        ).strip()
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nOGCoin Local Console stopped.")
    finally:
        server.server_close()


def format_status_markdown(status: dict[str, Any]) -> str:
    lines = [
        "# OGCoin Status Check",
        "",
        f"- Checked: {status['generated_at']}",
        f"- Issuer home_domain: `{status['issuer'].get('home_domain') or 'not set'}`",
        f"- Authorized trustlines: `{status['asset'].get('accounts_authorized')}`",
        f"- OGC/XLM bids: `{status['market'].get('bid_count')}`",
        f"- OGC/XLM asks: `{status['market'].get('ask_count')}`",
        f"- Liquidity pools: `{status['market'].get('pool_count')}`",
        "",
        "## Readiness",
        "",
    ]
    for item in status["readiness"]:
        lines.append(f"- **{item['title']}**: `{item['status']}` - {item['detail']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local OGCoin operator console.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host. Defaults to 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8787, help="Bind port. Defaults to 8787.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run one public status check and print it instead of starting the web console.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format for --check. Defaults to markdown.",
    )
    parser.add_argument("--output", help="Optional file path for --check output.")
    args = parser.parse_args()
    if args.check:
        status = build_status()
        output = (
            json.dumps(status, indent=2)
            if args.format == "json"
            else format_status_markdown(status)
        )
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    run(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
