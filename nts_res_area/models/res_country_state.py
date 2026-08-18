from odoo import models, fields

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    # Add your custom fields or methods here
    area_ids = fields.One2many(
        'res.area',
        'state_id',
        string='Areas',
    )
    show_in_website = fields.Boolean(
        default=True,
        help="If checked, this state will be shown in the website's area selection."
    )
    language = fields.Selection(
        selection=[
            ('en_US', 'English'),
            ('ar_001', 'Arabic'),
        ],
        string='Language Code',
        help="The language code for this state, used for localization purposes."
    )
