# -*- coding: utf-8 -*-
from odoo import http

# class Fixed(http.Controller):
#     @http.route('/fixed/fixed/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fixed/fixed/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fixed.listing', {
#             'root': '/fixed/fixed',
#             'objects': http.request.env['fixed.fixed'].search([]),
#         })

#     @http.route('/fixed/fixed/objects/<model("fixed.fixed"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fixed.object', {
#             'object': obj
#         })