# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from odoo.tools.translate import html_translate
from odoo.tools import float_is_zero




class Product(models.Model):
    _inherit = "product.product"

    def _website_price(self):

        #import pdb;pdb.set_trace()

        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'
        ret = 'total_included'

        for p, p2 in zip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.taxes_id.sudo().filtered(lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            price_without_pricelist = taxes.compute_all(p.list_price, pricelist.currency_id)[ret]
            p.website_price_difference = False if float_is_zero(price_without_pricelist - p.website_price, precision_rounding=pricelist.currency_id.rounding) else True
            p.website_public_price = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]
