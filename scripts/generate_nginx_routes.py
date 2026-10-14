"""Write nginx redirects and file mappings for the service hierarchy."""

from pathlib import Path

from service_routes import CATEGORIES, SERVICE_ROUTES


ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.tga-uae.com/"


def main() -> None:
    lines = ["# Generated from scripts/service_routes.py. Keep old bookmarks working."]
    for stem, route in sorted(SERVICE_ROUTES.items()):
        for old_path in (stem, f"{stem}.html"):
            lines.append(f"location = /{old_path} {{ return 301 {SITE}{route}$is_args$args; }}")
    lines.append("")
    lines.append("# Serve only the defined category and service URLs.")
    for category in CATEGORIES:
        lines.append(
            f"location = /services/{category} {{ rewrite ^ /categories/{category}.html break; try_files $uri =404; }}"
        )
    for stem, route in sorted(SERVICE_ROUTES.items()):
        lines.append(
            f"location = /{route} {{ rewrite ^ /{stem}.html break; try_files $uri =404; }}"
        )
    lines.append("location ^~ /categories/ { return 404; }")
    (ROOT / "deploy" / "service-routes.inc").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
