from __future__ import annotations

import importlib
import os
import pkgutil
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PACKAGE = "app"


def configured_environment() -> None:
    os.environ.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")


def module_names() -> list[str]:
    names = ["main"]
    for module_info in pkgutil.walk_packages([str(ROOT / APP_PACKAGE)], prefix=f"{APP_PACKAGE}."):
        names.append(module_info.name)
    return sorted(set(names))


def import_modules() -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []

    for module_name in module_names():
        try:
            importlib.import_module(module_name)
        except Exception:
            failures.append((module_name, traceback.format_exc()))

    return failures


def validate_app() -> list[str]:
    errors: list[str] = []

    main_module = importlib.import_module("main")
    app = getattr(main_module, "app", None)
    if app is None:
        return ["main.py does not expose an app instance."]

    from fastapi.routing import APIRoute

    routes = [route for route in app.routes if isinstance(route, APIRoute)]
    if not routes:
        errors.append("No API routes were registered on the FastAPI app.")

    seen: dict[tuple[str, tuple[str, ...]], list[str]] = {}
    for route in routes:
        key = (route.path, tuple(sorted(route.methods or [])))
        seen.setdefault(key, []).append(route.name)

    duplicates = {key: names for key, names in seen.items() if len(names) > 1}
    for (path, methods), names in duplicates.items():
        errors.append(
            f"Duplicate route registration for {path} [{', '.join(methods)}]: {', '.join(names)}"
        )

    schema = app.openapi()
    if not schema.get("paths"):
        errors.append("OpenAPI schema was generated but contains no paths.")

    return errors


def main() -> int:
    configured_environment()

    import_failures = import_modules()
    if import_failures:
        print("Module import failures detected:", file=sys.stderr)
        for module_name, failure in import_failures:
            print(f"\n--- {module_name} ---", file=sys.stderr)
            print(failure, file=sys.stderr)
        return 1

    validation_errors = validate_app()
    if validation_errors:
        print("Application health check failed:", file=sys.stderr)
        for error in validation_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("Application health check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())