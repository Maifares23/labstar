from odoo import models, fields, api, _
from odoo.http import request

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    is_free_delivery = fields.Boolean(string='Is Free Delivery')
    is_store_pickup = fields.Boolean(
        string='Is Store Pickup',
        compute='_compute_is_store_pickup',
        store=True,
        help="Automatically set to True if the delivery method name contains 'Store Pickup'"
    )
    store_pickup_address = fields.Text(string='Store Pickup Address')
    
    @api.depends('name', 'delivery_type')
    def _compute_is_store_pickup(self):
        for carrier in self:
            carrier.is_store_pickup = carrier.name and 'store pickup' in carrier.name.lower()
    
    def _get_stock_availability(self, order):
        """Check if all products in the order are available in stock."""
        for line in order.order_line:
            if line.product_id.type == 'product' and line.product_id.qty_available < line.product_uom_qty:
                return False
        return True
    
    def available_carriers(self, partner,order):
        """Override to filter out store pickup if products are not in stock."""
        carriers = super().available_carriers(partner,order)
        if not self.env.context.get('website_id'):
            return carriers
            
        order = self.env['sale.order'].sudo().search([
            ('partner_id', '=', partner.id),
            ('state', '=', 'draft'),
            ('website_id', '!=', False)
        ], limit=1)
        
        if not order:
            return carriers
            
        return carriers.filtered(lambda c: not c.is_store_pickup or c._get_stock_availability(order))
    
    def _is_available_for_order(self, order):
        """Check if the carrier is available for the order."""
        res = super()._is_available_for_order(order)
    
        if self.delivery_type == 'in_store':
            print(self.name)
            print(order._get_pickup_locations())

            try:
                order_sudo = request.website.sale_get_order()
                if not order_sudo:
                    return False
                    
                data = order_sudo._get_pickup_locations()
                
                if 'pickup_locations' in data:
                    locations = data['pickup_locations']
                    available_locations = []
                    
                    for location in locations:
                        additional_data = location.get('additional_data', {})
                        in_store_stock = additional_data.get('in_store_stock', {})
                        
                        # Only include locations that have stock available
                        if in_store_stock.get('in_stock', True):
                            available_locations.append(location)
                    print("vaialable_location", available_locations)
                    return len(available_locations) > 0
                elif 'error' in data:
                    return False
                    
            except Exception as e:
                return False
                
        return res