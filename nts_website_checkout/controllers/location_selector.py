from odoo.http import request, route
from odoo.addons.website_sale_collect.controllers.delivery import InStoreDelivery


class CustomInStoreDelivery(InStoreDelivery):

    @route()
    def website_sale_get_pickup_locations(self, zip_code=None, **kwargs):
        """ Override of `website_sale` to set the pickup in store delivery method on the order in
        order to retrieve pickup locations when called from the the product page.
        """


        # Check if there's an active order
        order = request.website.sale_get_order()
        if not order:
            return {'error': "No pick-up points are available for this delivery address."}
        try:
            res = super().website_sale_get_pickup_locations(zip_code, **kwargs)
            locations = res.get('pickup_locations', [])
            res_locations = {'pickup_locations': []}
            
            for location in locations:
                additional_data = location.get('additional_data', {})
                in_store_stock = additional_data.get('in_store_stock', {})
                
                # Only include locations that have stock available
                if in_store_stock.get('in_stock', True):
                    res_locations['pickup_locations'].append(location)

            if len(res_locations['pickup_locations']) > 0:
                return res_locations
            return {'error': "No pick-up points are available for this delivery address."}

        except Exception as e:
            return {'error': "No pick-up points are available for this delivery address."}