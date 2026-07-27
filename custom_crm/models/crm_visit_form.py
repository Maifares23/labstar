# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


VISIT_TYPE_SELECTION = [
    ("rapid_test", "Rapid Test"),
    ("ubt", "UBT"),
    ("clia", "CLIA"),
    ("elisa", "ELISA"),
    ("consumables", "Consumables"),
    ("poct", "POCT"),
]


class CrmVisitForm(models.Model):
    _name = "crm.visit.form"
    _description = "CRM Visit Form"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(
        string="Visit Reference",
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
        tracking=True,
    )
    visit_date = fields.Date(
        string="Visit Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    visit_type = fields.Selection(
        selection=VISIT_TYPE_SELECTION,
        string="Type",
        required=True,
        tracking=True,
    )

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer Name",
        required=True,
        tracking=True,
    )
    address = fields.Text(string="Address", tracking=True)
    contact_person = fields.Char(string="Contact Person", tracking=True)
    contact_number = fields.Char(string="Contact Number", tracking=True)
    email_address = fields.Char(string="Mail Address", tracking=True)
    note = fields.Char( tracking=True)

    rapid_test_line_ids = fields.One2many(
        comodel_name="crm.visit.rapid.test.line",
        inverse_name="visit_id",
        string="Rapid Test Items",
        copy=True,
    )
    ubt_line_ids = fields.One2many(
        comodel_name="crm.visit.ubt.line",
        inverse_name="visit_id",
        string="UBT Items",
        copy=True,
    )
    clia_line_ids = fields.One2many(
        comodel_name="crm.visit.clia.line",
        inverse_name="visit_id",
        string="CLIA Items",
        copy=True,
    )
    elisa_line_ids = fields.One2many(
        comodel_name="crm.visit.elisa.line",
        inverse_name="visit_id",
        string="ELISA Items",
        copy=True,
    )
    consumables_line_ids = fields.One2many(
        comodel_name="crm.visit.consumables.line",
        inverse_name="visit_id",
        string="Consumables Items",
        copy=True,
    )
    poct_line_ids = fields.One2many(
        comodel_name="crm.visit.poct.line",
        inverse_name="visit_id",
        string="POCT Items",
        copy=True,
    )

    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )

    @api.onchange("customer_id")
    def _onchange_customer_id(self):
        for record in self:
            partner = record.customer_id
            if not partner:
                record.address = False
                record.contact_number = False
                record.email_address = False
                continue

            address_parts = [
                partner.street,
                partner.street2,
                partner.city,
                partner.state_id.name if partner.state_id else False,
                partner.zip,
                partner.country_id.name if partner.country_id else False,
            ]
            record.address = ", ".join(part for part in address_parts if part)
            record.contact_number = partner.phone
            record.email_address = partner.email

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "crm.visit.form"
                ) or _("New")
        return super().create(vals_list)


class CrmVisitLineBase(models.AbstractModel):
    _name = "crm.visit.line.base"
    _description = "CRM Visit Line Base"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    visit_id = fields.Many2one(
        comodel_name="crm.visit.form",
        string="Visit Form",
        required=True,
        ondelete="cascade",
        index=True,
    )
    item_name = fields.Char(string="Item Name", required=True)
    current_supplier_id = fields.Char(
        string="Current Supplier",
    )
    price = fields.Monetary(
        string="Price",
        required=True,
        currency_field="currency_id",
    )
    currency_id = fields.Many2one(
        related="visit_id.company_id.currency_id",
        string="Currency",
        store=True,
        readonly=True,
    )

    @api.constrains("price")
    def _check_price(self):
        for line in self:
            if line.price < 0:
                raise ValidationError(_("Price cannot be negative."))


class CrmVisitQuantityLineBase(models.AbstractModel):
    _name = "crm.visit.quantity.line.base"
    _description = "CRM Visit Quantity Line Base"
    _inherit = "crm.visit.line.base"

    qty = fields.Float(
        string="Qty",
        required=True,
        default=1.0,
        digits=(16, 2),
    )

    @api.constrains("qty")
    def _check_quantity(self):
        for line in self:
            if line.qty <= 0:
                raise ValidationError(_("Quantity must be greater than zero."))


class CrmVisitRapidTestLine(models.Model):
    _name = "crm.visit.rapid.test.line"
    _description = "CRM Visit Rapid Test Item"
    _inherit = "crm.visit.quantity.line.base"


class CrmVisitUbtLine(models.Model):
    _name = "crm.visit.ubt.line"
    _description = "CRM Visit UBT Item"
    _inherit = "crm.visit.line.base"


class CrmVisitCliaLine(models.Model):
    _name = "crm.visit.clia.line"
    _description = "CRM Visit CLIA Item"
    _inherit = "crm.visit.quantity.line.base"


class CrmVisitElisaLine(models.Model):
    _name = "crm.visit.elisa.line"
    _description = "CRM Visit ELISA Item"
    _inherit = "crm.visit.line.base"


class CrmVisitConsumablesLine(models.Model):
    _name = "crm.visit.consumables.line"
    _description = "CRM Visit Consumables Item"
    _inherit = "crm.visit.quantity.line.base"


class CrmVisitPoctLine(models.Model):
    _name = "crm.visit.poct.line"
    _description = "CRM Visit POCT Item"
    _inherit = "crm.visit.quantity.line.base"
