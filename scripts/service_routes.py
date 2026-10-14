"""Canonical categories and URLs for TGA service pages."""

from __future__ import annotations


CATEGORIES = {
    "business-setup": {
        "label": "Business setup & company changes",
        "summary": "Plan a new UAE company, choose the right structure and keep licence and corporate information current as the business evolves.",
        "pages": (
            "business-setup", "business-setup-pro", "business-structure-advisory",
            "company-setup-pro-services", "company-licensing",
        ),
    },
    "pro-visas": {
        "label": "PRO, visas & employee services",
        "summary": "Coordinate company administration, immigration, employee transactions and supporting documents with a clear view of the next step.",
        "pages": (
            "pro-services", "employee-pro", "visa-immigration", "labour-mohre",
            "golden-visa-assistance", "liquidation-process-assistance",
            "document-clearing", "poa-registration-assistance", "police-clearance",
        ),
    },
    "accounting-finance": {
        "label": "Accounting, finance & payroll",
        "summary": "Build reliable financial records, practical reporting and payroll processes that support informed business decisions.",
        "pages": (
            "accounting-bookkeeping-audit", "accounting-bookkeeping",
            "audit-assurance-assistance", "ifrs-studies-impact-assessments",
            "finance-operations", "payroll-hr",
        ),
    },
    "tax-transfer-pricing": {
        "label": "Tax & transfer pricing",
        "summary": "Work through UAE tax registrations, filings, VAT and transfer pricing with advice grounded in your actual transactions.",
        "pages": (
            "tax-advisory-transfer-pricing", "tax-advisory",
            "tax-registration-annual-filing", "vat-registration-filing",
            "corporate-tax-registration-filing",
            "transfer-pricing-studies-benchmarking", "international-transfer-pricing",
        ),
    },
    "compliance-governance": {
        "label": "Compliance & governance",
        "summary": "Organise AML duties, ownership records, internal controls and governance processes in ways your team can maintain.",
        "pages": (
            "aml-compliance", "aml-compliance-assistance", "goaml-registration-support",
            "client-kyc-due-diligence", "ubo-support", "aml-risk-assessments-policies",
            "sanctions-pep-screening", "ongoing-monitoring-records",
            "str-sar-reporting-support", "aml-training-review-readiness",
            "governance-operations",
        ),
    },
    "trade-ip": {
        "label": "Trade & IP coordination",
        "summary": "Bring together customs, import and export paperwork, and trademark application information with appropriate specialists.",
        "pages": ("trade-ip",),
    },
    "banking-wills": {
        "label": "Banking & will registration",
        "summary": "Prepare information for business banking enquiries and coordinate the practical steps involved in will registration.",
        "pages": ("banking-wills", "bank-account-opening-assistance", "will-registration-assistance"),
    },
}

SPECIAL_LEAVES = {
    "business-setup": "company-formation",
    "trade-ip": "trade-ip-coordination",
    "banking-wills": "banking-will-registration",
}

SERVICE_ROUTES = {
    stem: f"services/{category}/{SPECIAL_LEAVES.get(stem, stem)}"
    for category, details in CATEGORIES.items()
    for stem in details["pages"]
}


def category_for_stem(stem: str) -> str:
    for category, details in CATEGORIES.items():
        if stem in details["pages"]:
            return category
    raise KeyError(stem)
