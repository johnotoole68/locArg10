# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from werkzeug.exceptions import Forbidden

from odoo import http, tools, _
from odoo.http import request
from odoo.addons.base.ir.ir_qweb.fields import nl2br
from odoo.addons.website.models.website import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.exceptions import ValidationError
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)

PPG = 20  # Products Per Page
PPR = 4   # Products Per Row



class WebsiteSaleAr(WebsiteSale):

    def _get_mandatory_billing_fields(self):
        return ["name", "email", "street", "city", "country_id","main_id_number","main_id_category_id"]

    def _get_mandatory_shipping_fields(self):
        return ["name", "street", "city", "country_id"]

    #@http.route()
    #def shop(self, page=0, category=None, search='', ppg=False, **post):

    #@http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True)
    @http.route()
    def address(self, **kw):
        #import pdb; pdb.set_trace()
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        def_country_id = order.partner_id.country_id
        values, errors = {}, {}

        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                def_country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1)
            else:
                def_country_id = request.website.user_id.sudo().country_id
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                else:
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    if partner_id in shippings.mapped('id'):
                        mode = ('edit', 'shipping')
                    else:
                        return Forbidden()
                if mode:
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                mode = ('new', 'shipping')
            else: # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw:
            pre_values = self.values_preprocess(order, mode, kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)

                if mode[1] == 'billing':
                    order.partner_id = partner_id
                    order.onchange_partner_id()
                elif mode[1] == 'shipping':
                    order.partner_shipping_id = partner_id

                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        country = 'country_id' in values and values['country_id'] != '' and request.env['res.country'].browse(int(values['country_id']))
        id_category = 'main_id_category_id' in values and values['main_id_category_id']!= '' and request.env['res.partner.id_category'].browse(int(values['main_id_category_id']))
        country = country and country.exists() or def_country_id
        render_values = {
            'partner_id': partner_id,
            'mode': mode,
            'checkout': values,
            'country': country,
            'countries': country.get_website_sale_countries(mode=mode[1]),
            'id_category': id_category,
            'id_categories': request.env['res.partner'].get_website_sale_id_categories(mode=mode[1]),
            "states": country.get_website_sale_states(mode=mode[1]),
            'error': errors,
            'callback': kw.get('callback'),
        }
        return request.render("website_sale.address", render_values)
