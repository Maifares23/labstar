# Odoo 18 Upgrade Notes

- Migrated window action view modes from `tree` to `list`.
- Removed `search` from action `view_mode` values.
- Migrated the construction project Kanban template from `kanban-box` to `card`.
- Migrated the configuration view to the Odoo 18 `app` / `block` / `setting` structure.
- Updated the manifest and explicit dependencies for Odoo 18.
- Fixed multi-record `create()` implementations.
- Fixed missing `UserError` imports and computed-field assignments.
- Added safer invoice sequence creation and workflow-stage validation.
- Preserved existing model names, field names, menu IDs, action IDs, and view IDs for database upgrades.

A full runtime installation test still requires an Odoo 18 server and PostgreSQL database with the target database data.
