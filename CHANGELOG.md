## 1.1.1 (2026-01-25)

### Fix

- **api**: Rework ErrorResponse schema to make docs more sensible and indicate what errors are expected for a given endpoint
- **postgres**: Add required postgres import to INSTALLED_APPS
- **docker**: Ensure collectstatic runs without inputs

## 1.1.0 (2024-10-15)

### Feat

- **whitenoise**: Integrate whitenoise for serving static files via gunicorn

### Fix

- **docker**: Ensure pipx is added to PATH
- **schema**: Ensure card_count falls back to 0 if not provided by scryfall or mtgjson

### Refactor

- **StatusCode**: Add OK status code "200"
- **docker**: Optimize Dockerfile, remove deprecated dockerignore targets
- **api**: Minor changes to response object schemas
- **poetry,readme**: Update project dependencies, update README
- **cli/update**: Remove "v" from mtg-vectors metadata version
- **hexproof**: Update submodule
- **submodule**: Ensure we use the "main" branch submodule hexproof
- **submodule**: Update hexproof
- **submodule**: Add hexproof submodule to repository

## 1.0.0 (2024-08-15)

### Feat

- **project**: Rework project using new hexproof submodule
- **symbols/package**: Added endpoint for downloading latest symbols package
- **SymbolCollectionWatermark,Meta**: Implement watermark symbol collection and metadata models
- **api**: Reworked the project, added support for Set and Set Symbol endpoints
- **api**: Implemented API key model, key commands, and key retrieval endpoint

### Fix

- **get_meta**: Update schema response type
- **meta**: Ensure /meta/resource endpoint works
- **STATIC_URL**: Ensure static assets can be accessed
- **TypedDict,NotRequired**: Ensure Python 3.10 is supported by importing TypedDict and NotRequired from typing_extensions
- **django**: Add support for staticroot
- **NinjaAPI**: Fix route resolving
- **gunicorn**: Fix typo for gunicorn wsgi implementation
- **mkdir**: Call mkdir on parent for linux support
- **pyproject.toml**: Remove unnecessary line

### Refactor

- **git**: Update .gitignore
- **.idea**: Remove JetBrains directory
- **commands**: Implement --force and --clear args to 'sync_sets'
- **Set**: Refactor some TextField fields to CharField
- **PrettyJSON**: Implement a PrettyJSON renderer with baked in "pretty" toggle support for JSON API returns
- **gitignore**: Add static root to gitignore, rename staticroot -> static
- **TypedDict**: Import TypedDict from typing_extensions for < Python3.11 support
- **NotRequired**: Import NotRequired from typing_extensions for < Python 3.11 support
- **gitignore**: Remove db.json from repository
- **admin**: Add Keyring to admin panel
