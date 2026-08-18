from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)
    id_no = fields.Char(
        string='ID No.',
        required=False)
    id_type = fields.Char(
        string='ID Type.',
        required=False)
    cr_no = fields.Char(
        string='CR No.',
        required=False)
    fax_no = fields.Char(
        string='Fax No.',
        required=False)
    is_broker = fields.Boolean(
        string='Broker',
        required=False)
    tca_cr_issued_at = fields.Char(
        string='CR issued at',
        required=False
    )
    tca_license_number = fields.Char(
        string='License Number',
        required=False
    )
    tca_commercial_activities = fields.Char(
        string='Commercial Activities',
        required=False
    )
    tca_tenant_business = fields.Char(
        string='The tenant can modify the business',
        required=False
    )
    tca_license_issue_place = fields.Char(
        string='License Issue Place',
        required=False
    )
    td_unified_number = fields.Char(
        string='Unified Number',
        required=False)
    td_cr_date = fields.Date(
        string='CR Date',
        required=False)
    td_organization_type = fields.Char(
        string='Organization Type',
        required=False)
    td_cr_no = fields.Char(
        string='CR No',
        required=False)
    td_issued_by = fields.Char(
        string='Issued by',
        required=False)
    issuing_authority = fields.Char(
        string='Electricity meter account number',
        required=False)
    registry_issuing_place = fields.Char(
        string='Registry Issuing Place',
        required=False)
    unified_number = fields.Char(
        string='Unified Number',
        required=False)

