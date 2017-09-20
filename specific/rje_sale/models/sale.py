# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    attention = fields.Char(
        string='Attention',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
    )
    preprint_number = fields.Char(
        string='Preprint Number',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
    )
    day_delivery_term = fields.Char(
        string='Day Delivery Term',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
    ).
    drawing_number = fields.Char(
        string='Drwaing Number',
        related='order_line.drawing_number',
    )

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    drawing_number = fields.Char(
        string='Drawing Number',
    )
