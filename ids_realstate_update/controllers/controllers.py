# -*- coding: utf-8 -*-
# from odoo import http


# class IdsRealestateUpdate(http.Controller):
#     @http.route('/ids_realstate_update/ids_realstate_update', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ids_realstate_update/ids_realstate_update/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ids_realstate_update.listing', {
#             'root': '/ids_realstate_update/ids_realstate_update',
#             'objects': http.request.env['ids_realstate_update.ids_realstate_update'].search([]),
#         })

#     @http.route('/ids_realstate_update/ids_realstate_update/objects/<model("ids_realstate_update.ids_realstate_update"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ids_realstate_update.object', {
#             'object': obj
#         })

