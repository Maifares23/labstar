from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
import math
from datetime import datetime, timedelta
from hijri_converter import convert
from odoo.exceptions import ValidationError, UserError


class RentalContract(models.Model):
    _inherit = 'rental.contract'

    brokerage_fee = fields.Float(
        string='Brokerage Fee (Not included in total contract amount)',
        required=False)
    security_deposit = fields.Float(
        string='Security Deposit (Not included in total contract amount)',
        required=False)
    waste_removal_fee = fields.Float(
        string='Waste Removal Fee (Not included in total contract amount)',
        required=False)
    engineering_supervision_fee = fields.Float(
        string='Engineering Supervision Fee (Not included in total contract amount)',
        required=False)
    unit_finishing_fee = fields.Float(
        string='Unit Finishing Fee (Not included in total contract amount)',
        required=False)
    retainer_fee = fields.Float(
        string='Retainer Fee (Included in total contract amount)',
        required=False)
    is_retainer_fee = fields.Boolean(
        string='Retainer Fee',
        required=False)
    gas_annual_mount = fields.Float(
        string='Gas Annual Amount',
        required=False)
    electricity_annual_mount = fields.Float(
        string='Electricity Annual Amount',
        required=False)
    water_annual_mount = fields.Float(
        string='Water Annual Amount',
        required=False)
    general_services_mount = fields.Float(
        string='General Services Amount',
        required=False)
    number_of_rent_payments = fields.Integer(
        string='Number of Rent Payments',
        required=False, compute="get_payments_rent_numbers", store=True)
    rental_value = fields.Float(
        string='Rental Value',
        required=False)
    fd_rent_payment_cycle = fields.Selection(
        string='Rent payment cycle',
        selection=[
            ('monthly', 'Monthly'),
            ('quarter', 'Quarter'),
            ('four_month', 'اربع شهور'),
            ('half_year', 'Half Year'),
            ('year', 'Year'),
        ],
        required=False, )

    fd_no = fields.Char(
        string='No.',
        required=False)
    fd_id_cr_number = fields.Char(
        string='ID/CR Number',
        required=False)
    fd_id_type = fields.Char(
        string=' ID Type',
        required=False)
    fd_vat = fields.Char(
        string='Vat number',
        required=False)
    fd_general_services_included = fields.Float(
        string='General Services Included',
        required=False)
    fd_general_services_amount = fields.Float(
        string='General Services Amount',
        required=False)
    rental_value_with_tax = fields.Float(
        string='Rental Fee(Vat)',
        required=False, compute="get_rental_value_with_tax", inverse="_inverse_rental_value_with_tax", store=True)
    tax_id = fields.Many2one(
        comodel_name='account.tax',
        string='Vat',
        required=False)
    price_per_meter = fields.Float(
        string='Price per Meter',
        required=False, compute="get_price_per_meter", store=True)
    contract_no = fields.Char(
        string='Contract No',
        required=False)
    contract_type = fields.Char(
        string='Contract Type',
        required=False)
    contract_sealing_location = fields.Char(
        string='Contract Sealing Location',
        required=False)
    is_contract_conditional = fields.Selection(
        string='Contract is Conditional',
        selection=[('yes', 'Yes'),
                   ('no', 'No'), ],
        required=False, )
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
    vat = fields.Char(
        string='Vat',
        required=False)

    lrd_owner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Lessor Rep Name',
        required=False, domain="[('is_owner','=',True)]")
    lrd_id_no = fields.Char(
        string='Id No',
        required=False)
    lrd_email = fields.Char(
        string='Email',
        required=False)
    lrd_vat = fields.Char(
        string='Vat',
        required=False)
    lrd_national_address = fields.Char(
        string='National Address',
        required=False)
    lrd_nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)
    lrd_id_type = fields.Char(
        string=' ID Type',
        required=False)
    lrd_mobile_no = fields.Char(
        string='Mobile No',
        required=False)
    td_unified_number = fields.Char(
        string='Unified Number',
        required=False)
    td_cr_date = fields.Date(
        string='CR Date',
        required=False)
    td_vat = fields.Char(
        string='Vat',
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
    trd_tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Tenant Rep Name',
        required=False, domain="[('is_tenant','=',True)]")
    trd_vat = fields.Char(
        string='Vat',
        required=False)
    trd_id_no = fields.Char(
        string='Id No',
        required=False)
    trd_email = fields.Char(
        string='Email',
        required=False)
    trd_national_address = fields.Char(
        string='National Address',
        required=False)

    trd_nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)
    trd_id_type = fields.Char(
        string=' ID Type',
        required=False)
    trd_mobile_no = fields.Char(
        string='Mobile No',
        required=False)
    bbd_cr_no = fields.Char(
        string='Cr No',
        required=False)
    bbd_fax_no = fields.Char(
        string='Fax No.',
        required=False)
    bbd_brokerage_entity_id = fields.Many2one(
        comodel_name='res.partner',
        string='Brokerage Entity Name',
        required=False, domain="[('is_broker','=',True)]")

    bbd_brokerage_entity_Address = fields.Char(
        string='Brokerage Entity Address',
        required=False)
    bbd_landline_no = fields.Char(
        string='Landline No',
        required=False)

    broker_id = fields.Many2one(
        comodel_name='res.partner',
        string='Broker Name',
        required=False, domain="[('is_broker','=',True)]")
    bbd_id_no = fields.Char(
        string='Id No',
        required=False)
    bbd_email = fields.Char(
        string='Email',
        required=False)

    bbd_nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
        required=False)
    bbd_id_type = fields.Char(
        string=' ID Type',
        required=False)
    bbd_mobile_no = fields.Char(
        string='Mobile No',
        required=False)
    tdd_issuer = fields.Char(
        string='Issuer',
        required=False)
    tdd_place_issue = fields.Char(
        string='Place of Issue',
        required=False)
    tdd_deed_title = fields.Char(
        string='Title Deed No',
        required=False)
    tdd_issue_date = fields.Date(
        string='Issue Date (Gregorian)',
        required=False
    )

    tdd_issue_date_hijri = fields.Char(
        string='Issue Date (Hijri)', )
    units_number = fields.Integer(
        string='Number of Units',
        required=False)
    parking_lots_number = fields.Integer(
        string='Number of Parking Lots',
        required=False)
    elevators_number = fields.Integer(
        string=' Number of Elevators',
        required=False)
    rud_unit_direction = fields.Char(
        string='Unit direction',
        required=False)
    rud_mezzanine = fields.Char(
        string='Mezzanine',
        required=False)
    rud_special_sign_specification = fields.Char(
        string=' Special sign specification',
        required=False)
    rud_unit_length = fields.Char(
        string='Unit length',
        required=False)
    rud_parking_lots_number = fields.Integer(
        string='Number of parking Lots',
        required=False)
    rud_sign_location = fields.Char(
        string='Sign location',
        required=False)
    rud_ac_types = fields.Char(
        string='AC types',
        required=False)
    rud_number_of_aC_units = fields.Integer(
        string='Number of AC units',
        required=False)
    rud_electricity_meter_number = fields.Char(
        string='Electricity meter number',
        required=False)
    rud_current_meter_reading = fields.Char(
        string='Current meter reading',
        required=False)
    rud_Water_meter_number = fields.Char(
        string='Water meter number',
        required=False)
    rud_water_current_meter_reading = fields.Char(
        string='Water Current meter reading',
        required=False)
    rud_gas_meter_number = fields.Char(
        string='Gas meter number',
        required=False)
    rud_gas_current_meter_reading = fields.Char(
        string='Gas Current meter reading',
        required=False)
    rud_unit_finishing = fields.Char(
        string='Unit finishing',
        required=False)
    rud_furnished = fields.Char(
        string='Furnished',
        required=False)
    rud_sign_area = fields.Char(
        string='Sign Area',
        required=False)
    rud_insurance_policy_number = fields.Char(
        string='Insurance Policy number',
        required=False)

    tca_tenant_id = fields.Many2one(
        comodel_name='res.partner',
        string='Name',
        required=False, domain="[('is_tenant','=',True)]")
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
    tca_cr_no = fields.Char(
        string='CR no.',
        required=False
    )
    tca_cr_issued_date = fields.Date(
        string='CR issued date',
        required=False
    )
    tca_license_issue_place = fields.Char(
        string='License Issue Place',
        required=False
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        required=False, compute="get_invoice_count")
    amount_untaxed = fields.Float(compute='_check_amounts', string='Rental Value', )
    total_service = fields.Float(compute='_check_amounts', string='Service Amount Total', )
    total_service_tax = fields.Float(compute='_check_amounts', string='Service Total Tax', )
    total_vat = fields.Float(compute='_check_amounts', string='Total Vat', )
    is_increased_rent = fields.Boolean(
        string='Is Increased Rent',
        required=False)
    increased_rent_type = fields.Selection(
        string='Increased Rent Type',
        selection=[('fixed', 'Fixed'),
                   ('ratio', 'Ratio'),
                   ('fixed_ratio', 'Fixed and Ratio'),
                   ('flexable', 'Flexable Installment'),
                   ],
        required=False, )
    fixed_amount = fields.Float(
        string='Fixed Amount',
        required=False)
    payment_rental = fields.Float(
        string='Payment Rental',
        required=False)
    increase_line_ids = fields.One2many(
        comodel_name='increase.ratio.line',
        inverse_name='rental_id',
        string='Increase Line',
        required=False)
    flexable_installment_ids = fields.One2many(
        comodel_name='flexable.installment',
        inverse_name='rental_id',
        string='Flexable Installment',
        required=False)
    issuing_authority = fields.Char(string="Issuing Authority")
    place_of_issue = fields.Char(string="Place of Issue")
    electricity_meter_account = fields.Char(string="Electricity meter account number")
    electricity_meter_location = fields.Char(string="Electricity meter location number")
    document_number = fields.Char(string="Document Number")
    property_type_id = fields.Many2one('rs.project.type')
    property_status_id = fields.Many2one('rs.project.status')

    unactive1 = fields.Boolean(
        string='Unactive1',
        required=False, copy=False)
    unactive2 = fields.Boolean(
        string='unactive2',
        required=False, copy=False)
    contract_down_payment_id = fields.Many2one('contract.down.payment', string="Down Payment", readonly=True,
                                               copy=False)
    is_approve = fields.Boolean(
        string='Is Approve',
        required=False, copy=False)
    is_second_approve = fields.Boolean(
        string='Is Second Approve',
        required=False, copy=False)
    credit_note_id = fields.Many2one('account.move', string="Credit Note", readonly=True)
    unactive_date = fields.Date(
        string='Unactive Date',
        required=False, copy=False)
    tdd_check_number = fields.Char(
        string='Check number',
        required=False)
    tdd_check_type = fields.Char(
        string='Check Type',
        required=False)

    def _apply_business_logic(self):
        self._onchange_increased_rent_type()
        self.onchange_project_owner()
        self.onchange_company_data()
        self.onchange_trd_tenant()
        self.onchange_broker()
        self.onchange_company()
        self.onchange_partner()
        self.onchange_rental_fee()
        self.onchange_brokerage_entity()
        self.get_data_rs_project()
        self.onchange_unit()
        self.onchange_rs_project_unit()
        self._onchange_rental_date_from()

    @api.model
    def create(self, values):
        res = super().create(values)
        res._apply_business_logic()
        return res

    @api.model
    def _cron_set_data(self):
        for rental in self:
            rental._onchange_increased_rent_type()
            rental.onchange_project_owner()
            rental.onchange_company_data()
            rental.onchange_trd_tenant()
            rental.onchange_broker()
            rental.onchange_company()
            rental.onchange_partner()
            rental.onchange_rental_fee()
            rental.onchange_brokerage_entity()
            rental.get_data_rs_project()
            # rental.onchange_unit()
            rental.onchange_rs_project_unit()
            rental._onchange_rental_date_from()

    def action_unactive(self):
        for rental in self:
            rental = rental.sudo()
            if not rental.unactive_date:
                raise ValidationError(_("PLease Set Unactive Date"))
            rental.state = 'approve_unactive'

    def approve_unactive(self):
        for rental in self:
            rental = rental.sudo()
            rental.state = 'second_approve_unactive'

    def final_unactive(self):
        for rental in self:
            rental = rental.sudo()
            line_ids = rental.rental_line_ids.filtered(lambda x: x.invoice_id and x.invoice_id.state == 'draft')
            invoice_ids = self.env['account.move'].sudo().search([('rental_id', '=', self.id), ('state', '=', "draft")])
            if invoice_ids:
                for invoice in invoice_ids:
                    invoice.button_cancel()
            if line_ids:
                for line in line_ids:
                    line.invoice_id.button_cancel()
            if not rental.unactive_date:
                raise ValidationError(_("PLease Set Unactive Date"))
            rental.state = 'unactive'
            contract_down_payment_id = rental.contract_down_payment_id
            if contract_down_payment_id and contract_down_payment_id.remaining_amount > 0:
                credit_note = contract_down_payment_id.create_credit_note()
                rental.credit_note_id = credit_note

    @api.onchange("increased_rent_type")
    def _onchange_increased_rent_type(self):
        for rental in self:
            if rental.increased_rent_type and rental.increased_rent_type == 'flexable':
                rental.recurring_interval = 0

    def get_invoice_count(self):
        for rental in self:
            invoice_ids = self.env['account.move'].sudo().search([('rental_id', '=', self.id)])
            rental.invoice_count = len(invoice_ids) if invoice_ids else 0

    @api.depends("rental_line_ids")
    def get_payments_rent_numbers(self):
        for rental in self:
            rental.number_of_rent_payments = len(rental.rental_line_ids) if rental.rental_line_ids else 0

    @api.onchange("lrd_owner_id")
    def onchange_project_owner(self):
        for rental in self:
            rental.lrd_id_no = False
            rental.lrd_email = False
            rental.lrd_national_address = False
            rental.lrd_nationality_id = False
            rental.lrd_id_type = False
            rental.lrd_mobile_no = False
            rental.lrd_vat = False
            if rental.lrd_owner_id:
                owner_id = rental.lrd_owner_id
                rental.lrd_id_no = owner_id.id_no
                rental.lrd_email = owner_id.email
                rental.lrd_national_address = f"{owner_id.street if owner_id.street else ''} {owner_id.city if owner_id.city else ''} {owner_id.country_id.name if owner_id.country_id else ''}"
                rental.lrd_nationality_id = owner_id.nationality_id
                rental.lrd_id_type = owner_id.id_type
                rental.lrd_mobile_no = owner_id.mobile
                rental.lrd_vat = owner_id.vat

    @api.onchange("company_id")
    def onchange_company_data(self):
        for rental in self:
            rental.cr_no = False
            if rental.company_id:
                company_id = rental.company_id
                rental.cr_no = company_id.company_registry
                rental.unified_number = company_id.unified_number
                rental.organization_type = company_id.organization_type
                rental.issued_by = company_id.issued_by
                rental.cr_date = company_id.cr_date
                rental.vat = company_id.vat

    @api.onchange("trd_tenant_id")
    def onchange_trd_tenant(self):
        for rental in self:
            rental.td_cr_no = False
            rental.trd_id_no = False
            rental.trd_email = False
            rental.trd_national_address = False
            rental.trd_nationality_id = False
            rental.trd_id_type = False
            rental.trd_mobile_no = False
            rental.trd_vat = False
            if rental.trd_tenant_id:
                tenant_id = rental.trd_tenant_id
                rental.td_cr_no = tenant_id.cr_no
                rental.trd_id_no = tenant_id.id_no
                rental.trd_email = tenant_id.email
                rental.trd_vat = tenant_id.vat
                rental.trd_national_address = f"{tenant_id.street if tenant_id.street else ''} {tenant_id.city if tenant_id.city else ''} {tenant_id.country_id.name if tenant_id.country_id else ''}"
                rental.trd_nationality_id = tenant_id.nationality_id
                rental.trd_id_type = tenant_id.id_type
                rental.trd_mobile_no = tenant_id.mobile

    @api.onchange("broker_id")
    def onchange_broker(self):
        for rental in self:
            rental.bbd_id_no = False
            rental.bbd_email = False
            rental.bbd_nationality_id = False
            rental.bbd_id_type = False
            rental.bbd_mobile_no = False
            if rental.broker_id:
                broker_id = rental.broker_id
                rental.bbd_id_no = broker_id.id_no
                rental.bbd_email = broker_id.email
                rental.bbd_nationality_id = broker_id.nationality_id
                rental.bbd_id_type = broker_id.id_type
                rental.bbd_mobile_no = broker_id.mobile
                # rental.bbd_fax_no = broker_id.fax_no

    @api.onchange("company_id")
    def onchange_company(self):
        for rental in self:
            rental.unified_number = False
            rental.cr_date = False
            rental.organization_type = False
            rental.cr_no = False
            rental.issued_by = False
            rental.vat = False
            if rental.company_id:
                company_id = rental.company_id
                rental.unified_number = company_id.unified_number
                rental.cr_date = company_id.cr_date
                rental.organization_type = company_id.organization_type
                rental.cr_no = company_id.cr_no
                rental.issued_by = company_id.issued_by
                rental.vat = company_id.vat

    @api.onchange("partner_id")
    def onchange_partner(self):
        for rental in self:
            rental.tca_cr_issued_at = False
            rental.tca_license_number = False
            rental.tca_commercial_activities = False
            rental.tca_license_issue_place = False
            rental.td_cr_date = False
            rental.td_organization_type = False
            rental.td_issued_by = False
            rental.td_cr_no = False
            rental.fd_id_type = False
            rental.fd_vat = False
            rental.fd_id_cr_number = False
            rental.td_unified_number = False
            rental.electricity_meter_account = False
            rental.td_vat = False
            if rental.partner_id:
                partner_id = rental.partner_id
                rental.tca_cr_issued_at = partner_id.tca_cr_issued_at
                rental.electricity_meter_account = partner_id.issuing_authority
                rental.tca_license_number = partner_id.tca_license_number
                rental.tca_commercial_activities = partner_id.tca_commercial_activities
                rental.tca_license_issue_place = partner_id.tca_license_issue_place
                rental.td_cr_date = partner_id.td_cr_date
                rental.td_organization_type = partner_id.td_organization_type
                rental.td_issued_by = partner_id.td_issued_by
                rental.td_cr_no = partner_id.cr_no
                rental.fd_id_type = partner_id.id_type
                rental.fd_vat = partner_id.vat
                rental.fd_id_cr_number = partner_id.cr_no
                rental.td_vat = partner_id.vat
                rental.td_unified_number = partner_id.unified_number

    @api.onchange("bbd_brokerage_entity_id")
    def onchange_brokerage_entity(self):
        for rental in self:
            rental.bbd_brokerage_entity_Address = False
            rental.bbd_landline_no = False
            rental.bbd_fax_no = False
            rental.bbd_cr_no = False
            if rental.bbd_brokerage_entity_id:
                brokerage_entity_id = rental.bbd_brokerage_entity_id
                rental.bbd_brokerage_entity_Address = f"{brokerage_entity_id.street if brokerage_entity_id.street else ''} {brokerage_entity_id.city if brokerage_entity_id.city else ''} {brokerage_entity_id.country_id.name if brokerage_entity_id.country_id else ''}"
                rental.bbd_landline_no = brokerage_entity_id.phone
                rental.bbd_fax_no = brokerage_entity_id.fax_no
                rental.bbd_cr_no = brokerage_entity_id.cr_no

    @api.depends("tax_id", "rental_fee")
    def get_rental_value_with_tax(self):
        for rental in self:
            if rental.tax_id:
                tax_type = rental.tax_id.price_include_override
                if tax_type != 'tax_included':
                    rental.rental_value_with_tax = rental.rental_fee * (1 + rental.tax_id.amount * 0.01)
                else:
                    # الضريبة included → rental_fee = rental_value_with_tax
                    rental.rental_value_with_tax = rental.rental_fee
            else:
                rental.rental_value_with_tax = rental.rental_fee

    def _inverse_rental_value_with_tax(self):
        for rental in self:
            if rental.tax_id:
                tax_type = rental.tax_id.price_include_override
                if tax_type != 'tax_included' and rental.rental_value_with_tax:
                    rental.rental_fee = rental.rental_value_with_tax / (1 + rental.tax_id.amount * 0.01)
                else:
                    rental.rental_fee = rental.rental_value_with_tax

    @api.onchange('rental_value_with_tax')
    def _onchange_rental_value_with_tax(self):
        for rental in self:
            if rental.tax_id and rental.rental_value_with_tax:
                tax_type = rental.tax_id.price_include_override
                if tax_type != 'tax_included':
                    tax_factor = 1 + rental.tax_id.amount * 0.01
                    rental.rental_fee = rental.rental_value_with_tax / tax_factor
                else:
                    rental.rental_fee = rental.rental_value_with_tax
    # def _inverse_rental_value_with_tax(self):
    #     for rental in self:
    #         if rental.tax_id:
    #             rental_value_with_tax = rental.rental_value_with_tax
    #             if rental.tax_id:
    #                 tax_factor = 1 + rental.tax_id.amount * 0.01
    #                 rental.rental_fee = rental_value_with_tax / tax_factor
    #
    # @api.onchange('rental_value_with_tax')
    # def _onchange_rental_value_with_tax(self):
    #     for rental in self:
    #         if rental.tax_id and rental.rental_value_with_tax:
    #             tax_factor = 1 + rental.tax_id.amount * 0.01
    #             rental.rental_fee = rental.rental_value_with_tax / tax_factor
    #
    # @api.depends("tax_id", "rental_fee")
    # def get_rental_value_with_tax(self):
    #     for rental in self:
    #         type = rental.tax_id.price_include_override
    #         rental.rental_value_with_tax = (
    #                                                rental.tax_id.amount * .01 + 1) * rental.rental_fee if rental.tax_id and type != 'tax_included' else rental.rental_fee

    @api.depends("rental_fee", "rs_project_area")
    def get_price_per_meter(self):
        for rental in self:
            rental.price_per_meter = rental.rental_fee / rental.rs_project_area if rental.rs_project_area > 0 else 0

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    @api.onchange("rental_fee")
    def onchange_rental_fee(self):
        for rental in self:
            min_rental_fee = rental.rs_project_unit.min_rental_fee
            if rental.rental_fee < min_rental_fee:
                raise ValidationError(_(f"Please Set Fee >= {min_rental_fee}"))

    @api.onchange("rs_project_unit")
    def onchange_rs_project_unit(self):
        for rental in self:
            rental.issuing_authority = False
            rental.place_of_issue = False
            rental.document_number = False
            rental.rud_unit_direction = False
            rental.rud_mezzanine = False
            rental.rud_special_sign_specification = False
            rental.rud_unit_length = False
            rental.rud_parking_lots_number = False
            rental.rud_sign_location = False
            rental.rud_sign_area = False
            rental.rud_ac_types = False
            rental.rud_number_of_aC_units = False
            rental.rud_unit_finishing = False
            rental.rud_furnished = False
            rental.rud_electricity_meter_number = False
            rental.rud_Water_meter_number = False
            rental.rud_gas_meter_number = False
            rental.rud_insurance_policy_number = False
            rental.electricity_meter_location = False
            rental.analytic_account_id = False
            rs_project_unit = rental.rs_project_unit
            if rs_project_unit:
                rental.issuing_authority = rs_project_unit.issuing_authority
                rental.place_of_issue = rs_project_unit.place_of_issue
                rental.electricity_meter_location = rs_project_unit.place_of_issue
                rental.document_number = rs_project_unit.document_number
                rental.rud_unit_direction = rs_project_unit.rud_unit_direction
                rental.rud_mezzanine = rs_project_unit.rud_mezzanine
                rental.rud_special_sign_specification = rs_project_unit.rud_special_sign_specification
                rental.rud_unit_length = rs_project_unit.rud_unit_length
                rental.rud_parking_lots_number = rs_project_unit.rud_parking_lots_number
                rental.rud_sign_location = rs_project_unit.rud_sign_location
                rental.rud_sign_area = rs_project_unit.rud_sign_area
                rental.rud_ac_types = rs_project_unit.rud_ac_types
                rental.rud_number_of_aC_units = rs_project_unit.rud_number_of_aC_units
                rental.rud_unit_finishing = rs_project_unit.rud_unit_finishing
                rental.rud_furnished = rs_project_unit.rud_furnished
                rental.rud_electricity_meter_number = rs_project_unit.electricity_meter
                rental.rud_Water_meter_number = rs_project_unit.water_meter
                rental.rud_gas_meter_number = rs_project_unit.gas_meter
                rental.rud_insurance_policy_number = rs_project_unit.insurance_policy_number
                rental.analytic_account_id = rs_project_unit.analytic_account_id

    @api.onchange("rs_project")
    def get_data_rs_project(self):
        for rental in self:
            rental.tdd_issuer = False
            rental.tdd_place_issue = False
            rental.tdd_deed_title = False
            rental.units_number = False
            rental.parking_lots_number = False
            rental.property_owner_id = False
            rental.elevators_number = False
            rental.property_type_id = False
            rental.property_status_id = False
            rental.tdd_check_number = False
            rental.tdd_check_type = False

            rs_project = rental.rs_project
            if rs_project:
                rental.tdd_issuer = rs_project.issuer
                rental.tdd_place_issue = rs_project.issue_place
                rental.tdd_deed_title = rs_project.title_deed_no
                rental.units_number = len(rs_project.subproperties_ids)
                rental.parking_lots_number = rs_project.parking_lots_number
                rental.property_owner_id = rs_project.partner_id
                rental.elevators_number = rs_project.elevators_number
                rental.property_type_id = rs_project.property_type.id
                rental.property_status_id = rs_project.property_status.id
                rental.tdd_check_number = rs_project.check_number
                rental.tdd_check_type = rs_project.check_type

    @api.onchange("rental_fee", "recurring_interval", "date_from", "date_to", "periodicity")
    def get_rental_fee(self):
        for rec in self:
            if rec.periodicity and rec.date_from and rec.date_to:
                date_from = rec.date_from
                date_to = rec.date_to
                periodicity = rec.periodicity
                if periodicity == 'days':
                    total_days = (date_to - date_from).days
                    fractional_days = int(rec.recurring_interval)
                    if fractional_days > 0:
                        fractional_fee = rec.rental_fee / total_days * fractional_days
                        rec.payment_rental = fractional_fee
                elif periodicity == 'weeks':
                    total_weeks = (date_to - date_from).days // 7
                    fractional_week = int(rec.recurring_interval)
                    if fractional_week > 0:
                        fractional_fee = rec.rental_fee / math.ceil(total_weeks) * fractional_week
                        rec.payment_rental = fractional_fee
                elif periodicity == 'months':
                    months_diff = (date_to.year - date_from.year) * 12 + date_to.month - date_from.month
                    day_from = int(date_from.strftime('%d'))
                    day_to = int(date_to.strftime('%d'))
                    total_months = months_diff
                    if day_to > day_from:
                        total_months = months_diff + round(((day_to - day_from) / 30), 4)
                    elif day_from > day_to:
                        total_months = months_diff - round(((day_from - day_to) / 30), 4)
                    fractional_months = int(rec.recurring_interval)
                    if fractional_months > 0:
                        month_amount = rec.rental_fee / 12
                        fractional_fee = month_amount * fractional_months
                        rec.payment_rental = fractional_fee
                elif periodicity == 'years':
                    years_diff = (date_to.year - date_from.year) + ((date_to.month - date_from.month) / 12)
                    day_from = int(date_from.strftime('%d'))
                    day_to = int(date_to.strftime('%d'))
                    total_year = years_diff

                    if day_to > day_from:
                        total_year = years_diff + round(((day_to - day_from) / 365), 4)
                    elif day_from > day_to:
                        total_year = years_diff - round(((day_from - day_to) / 365), 4)
                    fractional_years = int(rec.recurring_interval)
                    if fractional_years > 0:
                        fractional_fee = rec.rental_fee / math.ceil(total_year) * fractional_years
                        rec.payment_rental = rec.rental_fee

    @api.onchange("date_from")
    def _onchange_rental_date_from(self):
        for rental in self:
            if rental.date_from:
                rental.tdd_issue_date = rental.date_from
                gregorian_date = rental.tdd_issue_date
                hijri_date = convert.Gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day).to_hijri()
                rental.tdd_issue_date_hijri = str(datetime(hijri_date.year, hijri_date.month,
                                                           hijri_date.day).date())

    def get_consumptions_fee(self, amount):
        for rec in self:
            if rec.periodicity and rec.date_from and rec.date_to:
                date_from = rec.date_from
                date_to = rec.date_to
                periodicity = rec.periodicity
                fractional_fee = 0
                if periodicity == 'days':
                    total_days = (date_to - date_from).days
                    fractional_days = int(rec.recurring_interval)
                    if fractional_days > 0:
                        fractional_fee = amount / total_days * fractional_days
                elif periodicity == 'weeks':
                    total_weeks = (date_to - date_from).days // 7
                    fractional_week = int(rec.recurring_interval)
                    if fractional_week > 0:
                        fractional_fee = amount / math.ceil(total_weeks) * fractional_week
                elif periodicity == 'months':
                    months_diff = (date_to.year - date_from.year) * 12 + date_to.month - date_from.month
                    day_from = int(date_from.strftime('%d'))
                    day_to = int(date_to.strftime('%d'))
                    total_months = months_diff
                    if day_to > day_from:
                        total_months = months_diff + round(((day_to - day_from) / 30), 4)
                    elif day_from > day_to:
                        total_months = months_diff - round(((day_from - day_to) / 30), 4)
                    fractional_months = int(rec.recurring_interval)
                    if fractional_months > 0:
                        month_amount = amount / math.ceil(total_months)
                        fractional_fee = month_amount * fractional_months
                elif periodicity == 'years':
                    years_diff = (date_to.year - date_from.year) + ((date_to.month - date_from.month) / 12)
                    day_from = int(date_from.strftime('%d'))
                    day_to = int(date_to.strftime('%d'))
                    total_year = years_diff
                    if day_to > day_from:
                        total_year = years_diff + round(((day_to - day_from) / 365), 4)
                    elif day_from > day_to:
                        total_year = years_diff - round(((day_from - day_to) / 365), 4)
                    fractional_years = int(rec.recurring_interval)
                    if fractional_years > 0:
                        fractional_fee = amount / math.ceil(total_year) * fractional_years
                return fractional_fee

    def get_friction(self, date_from, date_to):
        for rec in self:
            if rec.periodicity and date_from and date_to:
                periodicity = rec.periodicity
                fractional = 0
                if periodicity == 'months':
                    fractional_months = 12 / int(rec.recurring_interval)
                    if fractional_months > 0:
                        fractional = math.ceil(fractional_months)

                elif periodicity == 'years':
                    fractional = 1
                return fractional

    def action_cancel(self):
        res = super().action_cancel()
        for rental in self:
            rental = rental.sudo()
            invoice_ids = self.env['account.move'].sudo().search(
                [('move_type', '=', 'out_invoice'), ('rental_id', '=', rental.id)])
            if invoice_ids:
                for invoice in invoice_ids:
                    invoice.button_draft()
                    invoice.button_cancel()
            if rental.state == 'approve':
                rental.action_draft()
                rental.state = 'draft'
            if rental.state == 'second_approve':
                rental.action_draft()
                rental.state = 'approve'

    def view_invoices(self):
        for rental in self:
            rental = rental.sudo()
            return {
                'name': _('Invoice'),
                'view_type': 'list',
                'view_mode': 'list,form',
                'domain': [('rental_id', '=', rental.id)],
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'target': 'current',
            }

    # @api.model
    def _action_server_confirm(self):
        for rental in self:
            rental.sudo().action_approve()
            rental.sudo().action_second_approve()
            rental.sudo().action_confirm()

    @api.model
    def cron_posted_contract_invoice(self):
        today = fields.Date.context_today(self)
        line_ids = self.env['rental.contract.line'].sudo().search(
            [('invoice_id.state', '=', 'draft'), ('rental_contract_id.state', '=', 'confirmed'), ('date', '<=', today)])
        if line_ids:
            for line in line_ids:
                line.invoice_id.action_post()

    def set_down_payment(self):
        for rental in self:
            if not rental.contract_down_payment_id:
                down_payment = self.env['contract.down.payment'].sudo().search(
                    [('partner_id', '=', rental.partner_id.id), ('state', '=', 'done'),
                     ('contract_state', '=', 'available'), ('invoice_id', '!=', False)],
                    order='create_date asc',
                    limit=1
                )
                if down_payment:
                    rental.contract_down_payment_id = down_payment

    def action_confirm(self):
        res = super().action_confirm()
        for rental in self:
            rental = rental.sudo()
            today = fields.Date.context_today(self)
            invoice_account_id = self.env.company.invoice_account_id.id
            invoice_journal_id = self.env.company.invoice_journal_id.id
            electricity_account_id = self.env.company.electricity_account_id.id
            general_service_account_id = self.env.company.general_service_account_id.id
            water_account_id = self.env.company.water_account_id.id
            gas_account_id = self.env.company.gas_account_id.id
            if not invoice_account_id:
                raise ValidationError(_("Please Set Brokerage Account in Setting"))
            if not invoice_journal_id:
                raise ValidationError(_("Please Set Invoice Journal in Setting"))
            if not electricity_account_id:
                raise ValidationError(_("Please Set Electricity Account in Setting"))
            if not general_service_account_id:
                raise ValidationError(_("Please Set General Service Account in Setting"))
            if not water_account_id:
                raise ValidationError(_("Please Set Water Account in Setting"))
            if not gas_account_id:
                raise ValidationError(_("Please Set Gas Account in Setting"))
            if not invoice_account_id:
                raise ValidationError(_("Please Set Invoice Account in Setting"))
            invoice_lines = []
            analytic_account = rental.analytic_account_id
            tax_id = rental.tax_id
            if rental.brokerage_fee > 0:
                invoice_lines.append([0, 0, {
                    'account_id': invoice_account_id,
                    'name': _("Brockage Fee"),
                    'quantity': 1,
                    'price_unit': rental.brokerage_fee,
                    'tax_ids': [(4, tax_id.id)] if tax_id else False,
                    'analytic_distribution': {analytic_account.id: 100.0} if analytic_account else False
                }])
            if rental.waste_removal_fee > 0:
                invoice_lines.append([0, 0, {
                    'account_id': invoice_account_id,
                    'name': _("Waste Removal Fee"),
                    'quantity': 1,
                    'price_unit': rental.waste_removal_fee,
                    'tax_ids': [(4, tax_id.id)] if tax_id else False,
                    'analytic_distribution': {analytic_account.id: 100.0} if analytic_account else False
                }])
            if rental.engineering_supervision_fee > 0:
                invoice_lines.append([0, 0, {
                    'account_id': invoice_account_id,
                    'name': _("Engineering Supervision Fee"),
                    'quantity': 1,
                    'price_unit': rental.engineering_supervision_fee,
                    'tax_ids': [(4, tax_id.id)] if tax_id else False,
                    'analytic_distribution': {analytic_account.id: 100.0} if analytic_account else False
                }])
            if rental.unit_finishing_fee > 0:
                invoice_lines.append([0, 0, {
                    'account_id': invoice_account_id,
                    'name': _("Unit Finishing Fee"),
                    'quantity': 1,
                    'price_unit': rental.unit_finishing_fee,
                    'tax_ids': [(4, tax_id.id)] if tax_id else False,
                    'analytic_distribution': {analytic_account.id: 100.0} if analytic_account else False
                }])
            if invoice_lines:
                invoice = self.env['account.move'].sudo().create({
                    'move_type': 'out_invoice',
                    'invoice_date': rental.date,
                    'journal_id': invoice_journal_id,
                    'partner_id': rental.partner_id.id,
                    'rental_id': rental.id,
                    'invoice_line_ids': invoice_lines,
                })
            rental.set_down_payment()
            if rental.rental_line_ids:
                for line in rental.rental_line_ids:
                    line.tax_id = rental.tax_id
                    type = rental.tax_id.price_include_override
                    line.amount_with_tax = line.amount * (
                            1 + line.tax_id.amount * .01) if type != 'tax_included' else line.amount
                    end_date = ''
                    if rental.periodicity == 'months':
                        end_date = line.date + relativedelta(
                            months=rental.recurring_interval) - relativedelta(days=1)
                    elif rental.periodicity == 'years':
                        end_date = line.date + relativedelta(
                            years=rental.recurring_interval) - relativedelta(days=1)
                    move_id = line.invoice_id
                    first_move_id = rental.rental_line_ids[0]
                    if move_id and move_id.sudo().state == 'draft':
                        line.sudo().paid_down_payment()
                    if move_id and move_id.state == 'draft' and today > line.date:
                        print("!!!!!!@@@@Reference", rental.name, "Date", line.date)
                        lines = []
                        if rental.water_annual_mount > 0:
                            amount = rental.get_consumptions_fee(rental.water_annual_mount)
                            water_line = rental.prepare_move_line(amount, water_account_id,
                                                                  _('الحساب السنوى للمياه'), line.date, end_date)
                            lines.append([0, 0, water_line])
                        if rental.electricity_annual_mount > 0:
                            amount = rental.get_consumptions_fee(rental.electricity_annual_mount)
                            electricity_line = rental.prepare_move_line(amount, electricity_account_id,
                                                                        _('الحساب السنوى للكهرباء'), line.date,
                                                                        end_date)
                            lines.append([0, 0, electricity_line])
                        if rental.gas_annual_mount > 0:
                            amount = rental.get_consumptions_fee(rental.gas_annual_mount)
                            gas_line = rental.prepare_move_line(amount, gas_account_id,
                                                                _('الحساب السنوى للغاز'), line.date, end_date)
                            lines.append([0, 0, gas_line])
                        if rental.general_services_mount > 0:
                            amount = rental.get_consumptions_fee(rental.general_services_mount)
                            general_line = rental.prepare_move_line(amount, general_service_account_id,
                                                                    _('الحساب السنوى للخدمات العامة'), line.date,
                                                                    end_date)
                            lines.append([0, 0, general_line])
                        if lines:
                            move_id.update({
                                'invoice_line_ids': lines,
                            })
                        move_id.invoice_line_ids.update({
                            'analytic_distribution': {
                                rental.analytic_account_id.id: 100} if rental.analytic_account_id else False,
                        })
                        move_id.sudo().action_post()

        return res

    def calc_ann_inc(self, date_from, new_date, rental_fee, ann_inc):

        years_no = relativedelta(new_date, date_from).years
        percentage_amount = 0
        if self.increase_line_ids and self.increased_rent_type in ['ratio', 'fixed_ratio']:
            ratio_lines = self.increase_line_ids.filtered(lambda x: x.date.year == new_date.year)
            if ratio_lines:
                percentage_amount = ratio_lines[0].amount_total
        fixed_amount = self.fixed_amount
        ratio_amount = percentage_amount
        fractional = self.get_friction(date_from, new_date)
        fixed_fractional_amount = fixed_amount / fractional if fractional > 0 else 0
        ratio_fractional_amount = ratio_amount / fractional if fractional > 0 else 0
        new_rent_fee = rental_fee
        new_rent = new_rent_fee
        diff_date = new_date.year - self.date_from.year
        for y in range(years_no):
            new_rent = new_rent_fee + fixed_fractional_amount * diff_date if self.increased_rent_type == 'fixed' else new_rent_fee + ratio_fractional_amount if self.increased_rent_type in [
                'ratio', 'fixed_ratio'] else new_rent_fee
        return new_rent

    def action_calculate(self):
        for rec in self:
            rec = rec.sudo()
            if rec.increased_rent_type != 'flexable':
                rec.get_rental_fee()
                # rec.rental_line_ids = None
                for line in rec.rental_line_ids:
                    rec.write({'rental_line_ids': [(2, line.id, False)]})
                rental_fee = rec.payment_rental
                inc_rate = rec.ann_inc
                rental_lines = []
                if rec.periodicity and rec.date_from and rec.date_to:
                    n = 1
                    date_from = rec.date_from
                    date_to = rec.date_to
                    new_date = date_from
                    periodicity = rec.periodicity

                    if periodicity == 'days':
                        total_days = (date_to - date_from).days
                        full_days = int(total_days / int(rec.recurring_interval))
                        fractional_days = round((total_days / int(rec.recurring_interval)) - full_days, 4)
                        for d in range(1, full_days + 1):
                            rental_lines.append(
                                (0, 0, {
                                    'serial': d,
                                    'amount': rec.calc_ann_inc(rec.date_from, new_date, rental_fee, fractional_days),
                                    'date': new_date,
                                    'name': _('ايراد الايجار')
                                }))
                            d += 1
                            new_date += timedelta(days=int(rec.recurring_interval))
                    elif periodicity == 'weeks':
                        total_weeks = (date_to - date_from).days // 7
                        total_weeks = total_weeks / int(rec.recurring_interval)
                        full_weeks = math.ceil(total_weeks)
                        fractional_week = round(total_weeks - full_weeks, 4)

                        for w in range(1, full_weeks + 1):
                            rental_lines.append(
                                (0, 0, {
                                    'serial': w,
                                    'amount': rec.calc_ann_inc(rec.date_from, new_date, rental_fee, fractional_week),
                                    'date': new_date,
                                    'name': _('ايراد الايجار')
                                }))
                            w += int(rec.recurring_interval)
                            new_date += timedelta(weeks=int(rec.recurring_interval))
                    elif periodicity == 'months':
                        months_diff = (date_to.year - date_from.year) * 12 + date_to.month - date_from.month
                        day_from = int(date_from.strftime('%d'))
                        day_to = int(date_to.strftime('%d'))
                        total_months = months_diff
                        if day_to > day_from:
                            total_months = months_diff + round(((day_to - day_from) / 30), 4)
                        elif day_from > day_to:
                            total_months = months_diff - round(((day_from - day_to) / 30), 4)
                        total_months = total_months / int(rec.recurring_interval)
                        full_months = math.ceil(total_months)
                        fractional_months = round(total_months - full_months, 4)
                        for m in range(1, full_months + 1):
                            rental_lines.append(
                                (0, 0, {
                                    'serial': m,
                                    'amount': rec.calc_ann_inc(rec.date_from, new_date, rental_fee, fractional_months),
                                    'date': new_date,
                                    'name': _('ايراد الايجار')
                                }))
                            m += int(rec.recurring_interval)
                            new_date += relativedelta(months=int(rec.recurring_interval))
                    elif periodicity == 'years':
                        years_diff = (date_to.year - date_from.year) + ((date_to.month - date_from.month) / 12)
                        day_from = int(date_from.strftime('%d'))
                        day_to = int(date_to.strftime('%d'))
                        total_year = years_diff
                        if day_to > day_from:
                            total_year = years_diff + round(((day_to - day_from) / 365), 4)
                        elif day_from > day_to:
                            total_year = years_diff - round(((day_from - day_to) / 365), 4)
                        total_year = total_year / int(rec.recurring_interval)
                        int_years_diff = int(math.ceil(total_year))
                        fractional_years = round(total_year - int_years_diff, 4)
                        for y in range(1, + int_years_diff + 1):
                            rental_lines.append(
                                (0, 0, {
                                    'serial': y,
                                    'amount': rec.calc_ann_inc(rec.date_from, new_date, rental_fee, fractional_years),
                                    'date': new_date,
                                    'name': _('ايراد الايجار')
                                }))
                            y += int(rec.recurring_interval)
                            new_date += relativedelta(years=int(rec.recurring_interval))

                    rec.write({'rental_line_ids': rental_lines})
            else:
                installment_lines = []
                for installment in rec.flexable_installment_ids:
                    installment_lines.append([0, 0,
                                              {
                                                  'date': installment.date,
                                                  'amount': installment.amount,
                                                  'name': _("ايراد الايجار"),
                                              }
                                              ])
                rec.rental_line_ids = [(5, 0, 0)]
                rec.write({'rental_line_ids': installment_lines})
            for line in rec.rental_line_ids:
                line.tax_id = rec.tax_id
                type = rec.tax_id.price_include_override
                line.amount_with_tax = line.amount * (
                        1 + line.tax_id.amount * .01) if type != 'tax_included' else line.amount

    def action_approve(self):
        for rental in self:
            if rental.rental_fee <= 0:
                raise UserError(_('You can not Approve a contract with no rental fee!'))
            overlap_contracts = self.env['rental.contract'].sudo().search([
                ('rs_project_unit', '=', rental.rs_project_unit.id),
                ('state', '=', 'confirmed'),
                ('date_from', '<=', rental.date_to),
                ('date_to', '>=', rental.date_from),
            ], limit=1)

            if overlap_contracts:
                raise ValidationError(_("This unit is already rented during the selected period."))

            unactive_contract = self.env['rental.contract'].sudo().search([
                ('rs_project_unit', '=', rental.rs_project_unit.id),
                ('state', '=', 'unactive'),
                ('unactive_date', '>=', rental.date_from),
                ('unactive_date', '<=', rental.date_to),
            ], limit=1)
            if unactive_contract:
                raise ValidationError(_(
                    "This unit cannot be rented in this period because it has an unactive contract until %s."
                ) % unactive_contract.unactive_date)
            rental = rental.sudo()
            rental.state = 'approve'

    def action_second_approve(self):
        for rental in self:
            rental = rental.sudo()
            rental.state = 'second_approve'

    def prepare_move_line(self, amount, account_id, product_name, start_date, end_date):
        for rental in self:
            analytic_account = rental.analytic_account_id
            tax_id = rental.tax_id
            vals = {
                'name': f"{rental.name} - {product_name}",
                'quantity': 1,
                'account_id': account_id,
                'deferred_start_date': start_date,
                'deferred_end_date': end_date,
                'analytic_distribution': {analytic_account.id: 100.0} if analytic_account else False,
                'tax_ids': [(4, tax_id.id)] if tax_id else False,
                'price_unit': amount}
            return vals

    @api.depends('rental_line_ids', 'rental_line_ids.amount', 'rental_line_ids.amount_with_tax', 'gas_annual_mount',
                 'electricity_annual_mount', 'water_annual_mount', 'general_services_mount')
    def _check_amounts(self):
        for rental in self:
            total_paid = 0
            total_unpaid = 0
            amount_total = 0
            for line in rental.rental_line_ids:
                amount_total += line.amount
                total_unpaid += line.amount_residual
                total_paid += (line.amount - line.amount_residual)
            rental.paid = total_paid
            rental.balance = total_unpaid
            type = rental.tax_id.price_include_override
            amount_untaxed = sum(rental.rental_line_ids.mapped("amount"))
            amount_included = amount_untaxed - (
                    amount_untaxed * rental.tax_id.amount * 0.01)
            total_service = rental.gas_annual_mount + rental.electricity_annual_mount + rental.water_annual_mount + rental.general_services_mount
            total_service_included = total_service - (
                    total_service * rental.tax_id.amount * 0.01)
            rental.amount_untaxed = amount_untaxed if type != 'tax_included' else amount_included
            total_vat = amount_untaxed * rental.tax_id.amount * 0.01
            rental.total_vat = total_vat
            rental.total_service = total_service if type != 'tax_included' else total_service_included
            total_service_tax = total_service * rental.tax_id.amount * 0.01
            rental.total_service_tax = total_service_tax
            amount_total = rental.total_vat + rental.amount_untaxed + rental.total_service + rental.total_service_tax
            rental.amount_total = amount_total

    def unlink(self):
        """ Function which restrict the deletion of approved or submitted
                loan request"""
        user = self.env.user
        group_id = user.has_group('ids_realstate_update.contract_delete_access_group')
        if not group_id:
            raise ValidationError(_(
                "You Can't Have Access To Delete "))
        return super(RentalContract, self).unlink()
