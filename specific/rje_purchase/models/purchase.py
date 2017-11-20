# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    attention = fields.Char(
        string='Attention',
        track_visibility='onchange',
        readonly=True,
        states={'draft': [('readonly', False)],
                'sent': [('readonly', False)]},
    )
    approved_employee_id = fields.Many2one('hr.employee',
        string='Approved by',
    )
