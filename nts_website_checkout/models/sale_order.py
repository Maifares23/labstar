from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    custom_in_store_stock = fields.Boolean(string='Custom In Store Stock', default=True)

    def _get_pickup_locations(self, zip_code=None, country=None, **kwargs):
        res = super(SaleOrder, self)._get_pickup_locations(zip_code, country, **kwargs)
        if 'pickup_locations' in res:
            locations = res['pickup_locations']
            res_locations = {'pickup_locations': []}
            for location in locations:
                if 'additional_data' in location :
                    if 'in_store_stock' in location['additional_data'] and 'in_stock' in location['additional_data']['in_store_stock'] and not location['additional_data']['in_store_stock']['in_stock']:
                        continue
                res_locations['pickup_locations'].append(location)
                if res_locations['pickup_locations'] == []:
                    self.custom_in_store_stock = False
            return res_locations
            
        return res



        