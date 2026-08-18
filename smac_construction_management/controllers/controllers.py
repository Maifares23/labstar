# -*- coding: utf-8 -*-
# from odoo import http


# class SmacConstructionManagement(http.Controller):
#     @http.route('/smac_construction_management/smac_construction_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/smac_construction_management/smac_construction_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('smac_construction_management.listing', {
#             'root': '/smac_construction_management/smac_construction_management',
#             'objects': http.request.env['smac_construction_management.smac_construction_management'].search([]),
#         })

#     @http.route('/smac_construction_management/smac_construction_management/objects/<model("smac_construction_management.smac_construction_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('smac_construction_management.object', {
#             'object': obj
#         })
