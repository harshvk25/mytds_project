# instructor/task_templates.py (enhanced with Round 2)
import hashlib
import json
import base64
from datetime import datetime

TASK_TEMPLATES = {
    "sum-of-sales": {
        "brief": "Publish a single-page site that fetches data.csv from attachments, sums its sales column, sets the title to 'Sales Summary ${seed}', displays the total inside #total-sales, and loads Bootstrap 5 from jsdelivr.",
        "attachments": [
            {
                "name": "data.csv",
                "url": "data:text/csv;base64,${seed_data}"
            }
        ],
        "checks": [
            "js: document.title === 'Sales Summary ${seed}'",
            "js: !!document.querySelector('link[href*=\"bootstrap\"]')",
            "js: Math.abs(parseFloat(document.querySelector('#total-sales').textContent) - ${result}) < 0.01"
        ],
        "round2": [
            {
                "brief": "Add a Bootstrap table #product-sales that lists each product with its total sales and keeps #total-sales accurate after render.",
                "checks": [
                    "js: document.querySelectorAll('#product-sales tbody tr').length >= 1",
                    "js: (() => { const rows = [...document.querySelectorAll('#product-sales tbody tr td:last-child')]; const sum = rows.reduce((acc, cell) => acc + parseFloat(cell.textContent), 0); return Math.abs(sum - ${result}) < 0.01; })()"
                ]
            },
            {
                "brief": "Introduce a currency select #currency-picker that converts the computed total using rates.json from attachments and mirrors the active currency inside #total-currency.",
                "attachments": [
                    {
                        "name": "rates.json",
                        "url": "data:application/json;base64,${seed_data}"
                    }
                ],
                "checks": [
                    "js: !!document.querySelector('#currency-picker option[value=\"USD\"]')",
                    "js: !!document.querySelector('#total-currency')"
                ]
            }
        ]
    },
    "markdown-to-html": {
        "brief": "Publish a static page that converts input.md from attachments to HTML with marked, renders it inside #markdown-output, and loads highlight.js for code blocks.",
        "attachments": [
            {
                "name": "input.md",
                "url": "data:text/markdown;base64,${seed_data}"
            }
        ],
        "checks": [
            "js: !!document.querySelector('script[src*=\"marked\"]')",
            "js: !!document.querySelector('script[src*=\"highlight.js\"]')",
            "js: document.querySelector('#markdown-output').innerHTML.includes('<h')"
        ],
        "round2": [
            {
                "brief": "Add tabs #markdown-tabs that switch between rendered HTML in #markdown-output and the original Markdown in #markdown-source while keeping content in sync.",
                "checks": [
                    "js: document.querySelectorAll('#markdown-tabs button').length >= 2",
                    "js: document.querySelector('#markdown-source').textContent.trim().length > 0"
                ]
            },
            {
                "brief": "Support loading Markdown from a ?url= parameter when present and fall back to the attachment otherwise, showing the active source in #markdown-source-label.",
                "checks": [
                    "js: document.querySelector('#markdown-source-label').textContent.length > 0",
                    "js: !!document.querySelector('script').textContent.includes('fetch(')"
                ]
            }
        ]
    },
    "github-user-created": {
        "brief": "Publish a Bootstrap page with form id='github-user-${seed}' that fetches a GitHub username, optionally uses ?token=, and displays the account creation date in YYYY-MM-DD UTC inside #github-created-at.",
        "checks": [
            "js: document.querySelector('#github-user-${seed}').tagName === 'FORM'",
            "js: document.querySelector('#github-created-at').textContent.includes('20')",
            "js: !!document.querySelector('script').textContent.includes('https://api.github.com/users/')"
        ],
        "round2": [
            {
                "brief": "Show an aria-live alert #github-status that reports when a lookup starts, succeeds, or fails.",
                "checks": [
                    "js: document.querySelector('#github-status').getAttribute('aria-live') === 'polite'",
                    "js: !!document.querySelector('script').textContent.includes('github-status')"
                ]
            },
            {
                "brief": "Display the account age in whole years inside #github-account-age alongside the creation date.",
                "checks": [
                    "js: parseInt(document.querySelector('#github-account-age').textContent, 10) >= 0",
                    "js: document.querySelector('#github-account-age').textContent.toLowerCase().includes('years')"
                ]
            }
        ]
    }
}


def generate_seed_data(email, hour_seed):
    """Generate deterministic seed data based on email and hour"""
    seed_str = f"{email}-{hour_seed}-round2"  # Different from Round 1
    return base64.b64encode(seed_str.encode()).decode('utf-8')


def generate_result(seed_data):
    """Generate deterministic result for validation"""
    return float(int(hashlib.md5(seed_data.encode()).hexdigest()[:8], 16)) % 1000


def get_template_task(template_id, email, hour_seed, round_num=1, variant=0):
    """Get a task template with parameters filled in"""
    if template_id not in TASK_TEMPLATES:
        raise ValueError(f"Template {template_id} not found")

    template = TASK_TEMPLATES[template_id]
    seed_data = generate_seed_data(email, hour_seed)
    result = generate_result(seed_data)

    if round_num == 1:
        brief = template["brief"].replace("${seed}", hour_seed).replace("${seed_data}", seed_data)
        checks = [check.replace("${seed}", hour_seed).replace("${result}", str(result))
                  for check in template["checks"]]
        attachments = template.get("attachments", [])

        # Replace seed data in attachments
        for attachment in attachments:
            attachment["url"] = attachment["url"].replace("${seed_data}", seed_data)

    else:
        round2_variants = template.get("round2", [])
        if not round2_variants:
            raise ValueError(f"No round 2 variants for template {template_id}")

        variant_data = round2_variants[variant % len(round2_variants)]

        brief = variant_data["brief"].replace("${seed}", hour_seed).replace("${seed_data}", seed_data)
        checks = [check.replace("${seed}", hour_seed).replace("${result}", str(result))
                  for check in variant_data["checks"]]
        attachments = variant_data.get("attachments", [])

        # Replace seed data in attachments
        for attachment in attachments:
            attachment["url"] = attachment["url"].replace("${seed_data}", seed_data)

    return {
        "brief": brief,
        "attachments": attachments,
        "checks": checks
    }
