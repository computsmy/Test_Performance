# -*- coding: utf-8 -*-
# from odoo import http


# class ChequesLogs(http.Controller):
#     @http.route('/cheques_management/cheques_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cheques_management/cheques_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cheques_management.listing', {
#             'root': '/cheques_management/cheques_management',
#             'objects': http.request.env['cheques_management.cheques_management'].search([]),
#         })

#     @http.route('/cheques_management/cheques_management/objects/<model("cheques_management.cheques_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cheques_management.object', {
#             'object': obj
#         })
