from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    unified_number = fields.Char(
        string='Unified Number',
        required=False)
    cr_date = fields.Date(
        string='CR Date',
        required=False)
    organization_type = fields.Char(
        string='Organization Type',
        required=False)
    cr_no = fields.Char(
        string='CR No',
        required=False)
    issued_by = fields.Char(
        string='Issued by',
        required=False)
