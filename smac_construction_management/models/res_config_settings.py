# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    stage_policy = fields.Selection(
        selection=[
            ('next_stage', 'Next Stage'),
            ('send_mail', 'Send Mail'),
        ],
        string='Stage Policy',
        config_parameter='stage_policy',
    )
