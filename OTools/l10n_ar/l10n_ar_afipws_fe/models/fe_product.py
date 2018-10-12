# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError,ValidationError


class ProductProduct(models.Model):
	_inherit = 'product.product'

	codigo_ncm = fields.Char('Codigo NCM')
