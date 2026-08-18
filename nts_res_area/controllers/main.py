import json
from odoo.http import request, route
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from werkzeug.exceptions import  NotFound


class WebsiteSaleInherit(WebsiteSale):

    def _prepare_address_form_values(
        self, order_sudo, partner_sudo, address_type, use_delivery_as_billing, callback='', **kwargs
    ):
        result = super(WebsiteSaleInherit, self)._prepare_address_form_values(
            order_sudo, partner_sudo, address_type, use_delivery_as_billing, callback, **kwargs
        )
        # Add area_id to the result dictionary
        result['area_id'] = partner_sudo.area_id.id if partner_sudo else False
        result['state_areas'] = []
        if partner_sudo and partner_sudo.state_id:
            areas = request.env['res.area'].sudo().search([('state_id', '=', partner_sudo.state_id.id)])
            result['state_areas'] = areas
        return result
        

    def _parse_form_data(self, form_data):
        address_values , extra_form_data = super(WebsiteSaleInherit, self)._parse_form_data(form_data)
       
        if 'area_id' in extra_form_data:
            area_id = extra_form_data.pop('area_id', None)
            additional_notes = extra_form_data.pop('additional_notes', None)
            full_address = extra_form_data.pop('full_address', None)
            if full_address:
                address_values['full_address'] = full_address
            if additional_notes:
                address_values['additional_notes'] = additional_notes
            if area_id:
                area = request.env['res.area'].sudo().browse(int(area_id))
                if not area.exists():
                    raise NotFound('Area not found')
                address_values['area_id'] = area.id
        return address_values, extra_form_data

    @http.route('/shop/state_areas', type='json', auth='public')
    def get_state_areas(self, state_id):
        areas = request.env['res.area'].sudo().search([('state_id', '=', int(state_id))])
        return [{'id': area.id, 'name': area.name} for area in areas]

    def _get_mandatory_address_fields(self, country_sudo):
        """ Return the set of common mandatory address fields.

        :param res.country country_sudo: The country to use to build the set of mandatory fields.
        :return: The set of common mandatory address field names.
        :rtype: set
        """
        field_names = {'name', 'phone', 'country_id', 'state_id'}

        return field_names

    def _get_mandatory_billing_address_fields(self, country_sudo):
        """ Return the set of mandatory billing field names.

        :param res.country country_sudo: The country to use to build the set of mandatory fields.
        :return: The set of mandatory billing field names.
        :rtype: set
        """
        field_names = self._get_mandatory_address_fields(country_sudo)
        # Include the required billing fields from the portal logic.
        return field_names
