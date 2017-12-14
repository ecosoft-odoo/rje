# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_uop_qty_receive = fields.Float(
        string='Quantity (UoP Receive)',
    )
