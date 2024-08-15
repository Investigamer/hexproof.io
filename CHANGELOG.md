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
