# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Configration(models.TransientModel):
    _inherit = 'res.config.settings'

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True, config_parameter='nthub_realestate.location_id')

    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True, config_parameter='nthub_realestate.location_dest_id')
    reservation_days = fields.Integer(string='Days to release units reservation',
                                      related='company_id.reservation_days', readonly=0, store=True
                                      )

    ownership_settlement_account = fields.Many2one('account.account', 'OwnerShip Settlement Account',
                                                   related='company_id.ownership_settlement_account', readonly=0,
                                                   store=True)
    ownership_maintenance_account = fields.Many2one('account.account', 'OwnerShip Maintain Account',
                                                    related='company_id.ownership_maintenance_account', readonly=0,
                                                    store=True)
    ownership_delay_account = fields.Many2one('account.account', 'OwnerShip Delay Account',
                                              related='company_id.ownership_delay_account', readonly=0, store=True)
    ownership_extras_account = fields.Many2one('account.account', 'OwnerShip Extras Account',
                                               related='company_id.ownership_extras_account', readonly=0, store=True)
    rental_settlement_account = fields.Many2one('account.account', 'Rental Settlement Account',
                                                related='company_id.rental_settlement_account', readonly=0, store=True)
    retainer_account_id = fields.Many2one('account.account', 'Retainer Account',
                                          related='company_id.retainer_account_id', readonly=0, store=True)
    invoice_account_id = fields.Many2one('account.account', 'Brokerage Account',
                                         related='company_id.invoice_account_id', readonly=0, store=True)
    invoice_journal_id = fields.Many2one('account.journal', 'Invoice Journal',
                                         related='company_id.invoice_journal_id', readonly=0, store=True)
    electricity_account_id = fields.Many2one('account.account', 'Electricity Account',
                                             related='company_id.electricity_account_id', readonly=0, store=True)
    general_service_account_id = fields.Many2one('account.account', 'General Service Account',
                                                 related='company_id.general_service_account_id', readonly=0,
                                                 store=True)
    gas_account_id = fields.Many2one('account.account', 'Gas Account',
                                     related='company_id.gas_account_id', readonly=0, store=True)
    water_account_id = fields.Many2one('account.account', 'Water Account',
                                       related='company_id.water_account_id', readonly=0, store=True)
    rental_account_id = fields.Many2one(
        'account.account', string="Deposit Account (Liability)",
        domain=[('deprecated', '=', False)],
        related='company_id.rental_account_id', readonly=0, store=True
    )
    discount_invoice_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Discount Invoice Vat',
        required=False,
        related='company_id.discount_invoice_tax_id', readonly=0, store=True

    )


class ResCompany(models.Model):
    _inherit = 'res.company'
    reservation_days = fields.Integer(string='Days to release units reservation')

    ownership_settlement_account = fields.Many2one('account.account', 'OwnerShip Settlement Account',
                                                   )
    ownership_maintenance_account = fields.Many2one('account.account', 'OwnerShip Maintain Account',
                                                    )
    ownership_delay_account = fields.Many2one('account.account', 'OwnerShip Delay Account',
                                              )
    ownership_extras_account = fields.Many2one('account.account', 'OwnerShip Extras Account',
                                               )
    rental_settlement_account = fields.Many2one('account.account', 'Rental Settlement Account',
                                                )
    retainer_account_id = fields.Many2one('account.account', 'Retainer Account',
                                          )
    invoice_account_id = fields.Many2one('account.account', 'Brokerage Account',
                                         )
    invoice_journal_id = fields.Many2one('account.journal', 'Invoice Journal',
                                         )
    electricity_account_id = fields.Many2one('account.account', 'Electricity Account',
                                             )
    general_service_account_id = fields.Many2one('account.account', 'General Service Account',
                                                 )
    gas_account_id = fields.Many2one('account.account', 'Gas Account',
                                     )
    water_account_id = fields.Many2one('account.account', 'Water Account',
                                       )
    rental_account_id = fields.Many2one(
        'account.account', string="Deposit Account (Liability)",
        domain=[('deprecated', '=', False)],

    )
    discount_invoice_tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Discount Invoice Vat',
        required=False,


    )
