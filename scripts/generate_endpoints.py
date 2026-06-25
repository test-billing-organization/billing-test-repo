#!/usr/bin/env python3
"""Generate many self-contained Flask "billing" service modules with realistic,
varied, access-control-relevant endpoint handlers.

Purpose: produce a large pool of *distinct* endpoint handlers so that an AI SAST
pipeline (augur2) which fans out one analysis batch per ~20 detected endpoints
sees a wide fan-out. Every handler is valid Python, has a distinct route path and
function name, and embeds one realistic vulnerability shape (IDOR, missing-authz
mutation, mass-assignment, price/amount manipulation, raw SQL f-string injection,
or broken/commented-out access control).

Usage:
    python scripts/generate_endpoints.py

Knobs (top of file):
    NUM_FILES          number of service modules to emit under services/
    HANDLERS_PER_FILE  route handlers per module

Output is deterministic: each file is seeded with random.Random(file_index), so
re-running produces byte-identical files. To scale up, raise NUM_FILES /
HANDLERS_PER_FILE. NUM_FILES * HANDLERS_PER_FILE is the total endpoint count;
augur2 caps at ~2800 endpoints, so keep the product comfortably under that.
"""

import os
import random

# --------------------------------------------------------------------------- #
# Knobs
# --------------------------------------------------------------------------- #
NUM_FILES = 150
HANDLERS_PER_FILE = 10

# --------------------------------------------------------------------------- #
# Pools — kept large so files are not near-identical.
# --------------------------------------------------------------------------- #
RESOURCES = [
    "customers", "invoices", "subscriptions", "payments", "refunds", "credits",
    "ledgers", "payouts", "coupons", "discounts", "plans", "seats",
    "usage_records", "webhooks", "disputes", "statements", "wallets",
    "transfers", "entitlements", "tax_rates", "price_books", "dunning_attempts",
    "mandates", "settlements", "chargebacks", "balances", "accounts",
    "billing_runs", "credit_notes", "line_items", "proration_events", "quotes",
    "orders", "fees", "rebates", "holds", "reserves", "adjustments",
    "reconciliations", "remittances", "invoicing_profiles", "gateways",
    "merchant_accounts", "subledgers", "journal_entries", "billing_cycles",
    "promo_codes", "gift_cards", "vouchers", "tax_exemptions",
]

# Singularize for variable / column / field names.
SINGULAR = {
    "customers": "customer", "invoices": "invoice", "subscriptions": "subscription",
    "payments": "payment", "refunds": "refund", "credits": "credit",
    "ledgers": "ledger", "payouts": "payout", "coupons": "coupon",
    "discounts": "discount", "plans": "plan", "seats": "seat",
    "usage_records": "usage_record", "webhooks": "webhook", "disputes": "dispute",
    "statements": "statement", "wallets": "wallet", "transfers": "transfer",
    "entitlements": "entitlement", "tax_rates": "tax_rate",
    "price_books": "price_book", "dunning_attempts": "dunning_attempt",
    "mandates": "mandate", "settlements": "settlement", "chargebacks": "chargeback",
    "balances": "balance", "accounts": "account", "billing_runs": "billing_run",
    "credit_notes": "credit_note", "line_items": "line_item",
    "proration_events": "proration_event", "quotes": "quote", "orders": "order",
    "fees": "fee", "rebates": "rebate", "holds": "hold", "reserves": "reserve",
    "adjustments": "adjustment", "reconciliations": "reconciliation",
    "remittances": "remittance", "invoicing_profiles": "invoicing_profile",
    "gateways": "gateway", "merchant_accounts": "merchant_account",
    "subledgers": "subledger", "journal_entries": "journal_entry",
    "billing_cycles": "billing_cycle", "promo_codes": "promo_code",
    "gift_cards": "gift_card", "vouchers": "voucher",
    "tax_exemptions": "tax_exemption",
}

# Column name pools, varied per resource via hash so SQL columns differ.
ID_COLUMNS = ["id", "record_id", "ref", "uid", "row_id"]
OWNER_COLUMNS = ["owner_id", "account_id", "tenant_id", "org_id", "user_id", "merchant_id"]
AMOUNT_FIELDS = ["amount", "amount_cents", "total", "balance", "value", "gross_amount"]
STATUS_VALUES = ["pending", "open", "settled", "void", "posted", "captured"]


def _table(res: str) -> str:
    return res


def _fn(verb: str, res_singular: str, n: int) -> str:
    return f"{verb}_{res_singular}_{n}"


# --------------------------------------------------------------------------- #
# Handler templates. Each returns (route_decorator, function_source).
# `rng` is the per-file Random; `path` is the unique URL path; `fn` the unique
# function name; `res` the resource (plural), `sing` singular.
# Each template embeds exactly one vuln shape and a docstring naming it.
# --------------------------------------------------------------------------- #

def t_idor_get(rng, path, fn, res, sing):
    idcol = rng.choice(ID_COLUMNS)
    cols = f"{idcol}, {sing}_name, {rng.choice(OWNER_COLUMNS)}, {rng.choice(AMOUNT_FIELDS)}"
    deco = f'@app.route("{path}/<int:{sing}_id>", methods=["GET"])'
    body = f'''def {fn}({sing}_id):
    """IDOR: fetches a {sing} by id with no ownership/authz check, so any caller
    can read any tenant's {sing}."""
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute("SELECT {cols} FROM {_table(res)} WHERE {idcol} = ?", ({sing}_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({{"error": "{sing} not found"}}), 404
    return jsonify({{"{idcol}": row[0], "name": row[1], "owner": row[2], "amount": row[3]}})'''
    return deco, body


def t_idor_delete(rng, path, fn, res, sing):
    idcol = rng.choice(ID_COLUMNS)
    deco = f'@app.route("{path}/<int:{sing}_id>", methods=["DELETE"])'
    body = f'''def {fn}({sing}_id):
    """IDOR + missing authz: deletes any {sing} by id without checking the caller
    owns it or has a role."""
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM {_table(res)} WHERE {idcol} = ?", ({sing}_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return jsonify({{"deleted": deleted, "{sing}_id": {sing}_id}})'''
    return deco, body


def t_mass_assignment(rng, path, fn, res, sing):
    idcol = rng.choice(ID_COLUMNS)
    deco = f'@app.route("{path}/<int:{sing}_id>", methods=["PUT"])'
    body = f'''def {fn}({sing}_id):
    """Mass assignment: every key in the JSON body is written straight to the
    {sing} columns, so a caller can set protected fields like {rng.choice(OWNER_COLUMNS)}
    or status."""
    payload = request.json or {{}}
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    for field, val in payload.items():
        cur.execute(f"UPDATE {_table(res)} SET {{field}} = ? WHERE {idcol} = ?", (val, {sing}_id))
    conn.commit()
    conn.close()
    return jsonify({{"updated": list(payload.keys()), "{sing}_id": {sing}_id}})'''
    return deco, body


def t_unauth_refund(rng, path, fn, res, sing):
    amt = rng.choice(AMOUNT_FIELDS)
    deco = f'@app.route("{path}/<int:{sing}_id>/refund", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Missing authz on money movement: triggers a refund for a client-supplied
    amount with no role check and no validation that the amount <= original."""
    {amt} = request.json.get("{amt}", 0)
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute(
        "UPDATE {_table(res)} SET status = 'refunded', refunded_{amt} = ? WHERE id = ?",
        ({amt}, {sing}_id),
    )
    conn.commit()
    conn.close()
    return jsonify({{"status": "refunded", "{sing}_id": {sing}_id, "{amt}": {amt}}})'''
    return deco, body


def t_unauth_transfer(rng, path, fn, res, sing):
    amt = rng.choice(AMOUNT_FIELDS)
    deco = f'@app.route("{path}/<int:{sing}_id>/transfer", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Missing authz: moves funds from one {sing} to an arbitrary destination
    chosen by the caller, with no ownership or admin check."""
    dest = request.json.get("destination_id")
    {amt} = request.json.get("{amt}", 0)
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute("UPDATE {_table(res)} SET balance = balance - ? WHERE id = ?", ({amt}, {sing}_id))
    cur.execute("UPDATE {_table(res)} SET balance = balance + ? WHERE id = ?", ({amt}, dest))
    conn.commit()
    conn.close()
    return jsonify({{"from": {sing}_id, "to": dest, "{amt}": {amt}}})'''
    return deco, body


def t_price_manipulation(rng, path, fn, res, sing):
    deco = f'@app.route("{path}/<int:{sing}_id>/adjust", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Price manipulation: trusts a client-supplied discount and final price,
    applying them with no server-side recompute or bounds check."""
    discount_pct = float(request.json.get("discount_pct", 0))
    final_price = float(request.json.get("final_price", 0))
    list_price = float(request.json.get("list_price", final_price))
    charged = final_price - (final_price * discount_pct / 100.0)
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute("UPDATE {_table(res)} SET charged_amount = ? WHERE id = ?", (charged, {sing}_id))
    conn.commit()
    conn.close()
    return jsonify({{"{sing}_id": {sing}_id, "list_price": list_price, "charged": charged}})'''
    return deco, body


def t_raw_sql_list(rng, path, fn, res, sing):
    owner = rng.choice(OWNER_COLUMNS)
    deco = f'@app.route("{path}", methods=["GET"])'
    body = f'''def {fn}():
    """Raw SQL injection: the {owner} filter is concatenated into the query via an
    f-string instead of being parameterized."""
    {owner} = request.args.get("{owner}", "")
    status = request.args.get("status", "{rng.choice(STATUS_VALUES)}")
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute(
        f"SELECT * FROM {_table(res)} WHERE {owner} = '{{{owner}}}' AND status = '{{status}}'"
    )
    rows = cur.fetchall()
    conn.close()
    return jsonify({{"{res}": rows, "count": len(rows)}})'''
    return deco, body


def t_broken_admin_check(rng, path, fn, res, sing):
    deco = f'@app.route("{path}/<int:{sing}_id>/approve", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Broken access control: the admin gate is commented out, so any caller can
    approve and post a {sing}."""
    user = request.headers.get("X-User-Role", "viewer")
    # if user != "admin":
    #     return jsonify({{"error": "forbidden"}}), 403
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute("UPDATE {_table(res)} SET status = 'approved', approved_by = ? WHERE id = ?", (user, {sing}_id))
    conn.commit()
    conn.close()
    return jsonify({{"status": "approved", "{sing}_id": {sing}_id, "by": user}})'''
    return deco, body


def t_wrong_authz(rng, path, fn, res, sing):
    deco = f'@app.route("{path}/<int:{sing}_id>/void", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Broken access control: the role check uses `or` so it is always true,
    letting any caller void a {sing}."""
    role = request.headers.get("X-Role", "")
    # Logic bug: `or` makes this condition always truthy.
    if role == "admin" or role != "admin":
        conn = sqlite3.connect("billing.db")
        cur = conn.cursor()
        cur.execute("UPDATE {_table(res)} SET status = 'void' WHERE id = ?", ({sing}_id,))
        conn.commit()
        conn.close()
        return jsonify({{"status": "void", "{sing}_id": {sing}_id}})
    return jsonify({{"error": "forbidden"}}), 403'''
    return deco, body


def t_idor_credit(rng, path, fn, res, sing):
    amt = rng.choice(AMOUNT_FIELDS)
    deco = f'@app.route("{path}/<int:{sing}_id>/credit", methods=["POST"])'
    body = f'''def {fn}({sing}_id):
    """Missing authz: issues account credit of a caller-supplied amount to any
    {sing} id with no ownership or limit check."""
    {amt} = request.json.get("{amt}", 0)
    reason = request.json.get("reason", "manual")
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO {_table(res)}_credits ({sing}_id, {amt}, reason) VALUES (?, ?, ?)",
        ({sing}_id, {amt}, reason),
    )
    conn.commit()
    conn.close()
    return jsonify({{"credited": {amt}, "{sing}_id": {sing}_id, "reason": reason}})'''
    return deco, body


def t_idor_export(rng, path, fn, res, sing):
    idcol = rng.choice(ID_COLUMNS)
    deco = f'@app.route("{path}/<int:{sing}_id>/export", methods=["GET"])'
    body = f'''def {fn}({sing}_id):
    """IDOR: returns the full {sing} record (including internal fields) for any id
    without checking the requester is the owner."""
    conn = sqlite3.connect("billing.db")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {_table(res)} WHERE {idcol} = {{{sing}_id}}")
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({{"error": "not found"}}), 404
    return jsonify({{"{sing}": list(row)}})'''
    return deco, body


TEMPLATES = [
    t_idor_get,
    t_idor_delete,
    t_mass_assignment,
    t_unauth_refund,
    t_unauth_transfer,
    t_price_manipulation,
    t_raw_sql_list,
    t_broken_admin_check,
    t_wrong_authz,
    t_idor_credit,
    t_idor_export,
]


def generate_file(file_index: int) -> tuple[str, str, list[str]]:
    """Return (filename, source, paths) for a single service module."""
    rng = random.Random(file_index)

    # Pick a primary resource for the module name; make it unique across files
    # by suffixing the file index when the same base resource recurs.
    base_res = RESOURCES[file_index % len(RESOURCES)]
    cohort = file_index // len(RESOURCES)
    module_res = base_res if cohort == 0 else f"{base_res}_{cohort}"

    header = (
        '"""Auto-generated billing service module: '
        f'{module_res}.\n\n'
        "Self-contained Flask app exposing access-control-relevant endpoints. Each\n"
        "handler embeds a realistic vulnerability for SAST detection. Generated by\n"
        'scripts/generate_endpoints.py — do not edit by hand."""\n'
        "import sqlite3\n"
        "from flask import Flask, request, jsonify\n\n"
        "app = Flask(__name__)\n\n\n"
    )

    handlers: list[str] = []
    paths: list[str] = []

    # Shuffle a working pool of resources for path variety within the file,
    # always prefixed with the module's unique namespace so paths never collide
    # across files.
    pool = RESOURCES[:]
    rng.shuffle(pool)

    used_paths: set[str] = set()
    for n in range(HANDLERS_PER_FILE):
        template = TEMPLATES[(file_index + n) % len(TEMPLATES)]
        # Sub-resource for the path: vary per handler but keep it unique within
        # the module's namespace.
        sub = pool[n % len(pool)]
        sing = SINGULAR[sub]

        # Unique path namespace: /<module_res>/<sub>/<n> guarantees global
        # uniqueness because module_res is unique per file and n is unique per
        # handler within the file.
        path = f"/{module_res}/{sub}/{n}"
        # Defensive: ensure no collision (cannot happen given construction, but
        # keep deterministic fallback).
        suffix = 0
        candidate = path
        while candidate in used_paths:
            suffix += 1
            candidate = f"{path}_{suffix}"
        path = candidate
        used_paths.add(path)

        fn_verb = template.__name__.replace("t_", "")
        fn = _fn(fn_verb, sing, n)

        deco, body = template(rng, path, fn, sub, sing)
        handlers.append(f"{deco}\n{body}\n")
        paths.append(path)

    footer = '\n\nif __name__ == "__main__":\n    app.run(debug=True)\n'
    source = header + "\n\n".join(handlers) + footer
    filename = f"{module_res}_service.py"
    return filename, source, paths


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    out_dir = os.path.join(repo_root, "services")
    os.makedirs(out_dir, exist_ok=True)

    # Package marker.
    init_path = os.path.join(out_dir, "__init__.py")
    with open(init_path, "w", encoding="utf-8") as fh:
        fh.write("")

    all_paths: list[str] = []
    written = 0
    for i in range(NUM_FILES):
        filename, source, paths = generate_file(i)
        with open(os.path.join(out_dir, filename), "w", encoding="utf-8") as fh:
            fh.write(source)
        all_paths.extend(paths)
        written += 1

    unique = len(set(all_paths))
    print(f"Generated {written} files in {out_dir}/")
    print(f"Total handlers: {len(all_paths)}")
    print(f"Unique paths: {unique} (duplicates: {len(all_paths) - unique})")


if __name__ == "__main__":
    main()
