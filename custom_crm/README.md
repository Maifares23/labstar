# Custom CRM Visit Form (`custom_crm`)

Odoo 19 addon that adds **Visit Forms** under the CRM application.

## Main fields

- Visit Reference (automatic sequence)
- Visit Date
- Type: Rapid Test, UBT, CLIA, ELISA, Consumables, POCT
- Customer Name
- Address
- Contact Person
- Contact Number
- Mail Address

## Dedicated One2many sections

Each visit type has its own One2many field and its own line model:

- Rapid Test: Item Name, Current Supplier, Qty, Price
- UBT: Item Name, Current Supplier, Price
- CLIA: Item Name, Current Supplier, Qty, Price
- ELISA: Item Name, Current Supplier, Price
- Consumables: Item Name, Current Supplier, Qty, Price
- POCT: Item Name, Current Supplier, Qty, Price

`current_supplier_id` is a Char field in all item models.

Only the section matching the selected Type is displayed in the form.

The customer address, phone, and email are automatically proposed when a customer is selected and can still be edited.

## Installation

1. Copy `custom_crm` into your custom addons path.
2. Restart Odoo.
3. Update the Apps List.
4. Search for **Custom CRM Visit Form** and install it.
5. Open **CRM → Visit Forms**.

Command-line update example:

```bash
./odoo-bin -d DATABASE_NAME -u custom_crm --stop-after-init
```
