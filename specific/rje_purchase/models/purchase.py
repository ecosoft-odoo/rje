# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    attention = fields.Char(
        string='Attention',
    )
    approved_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
    )
    requested_employee_id = fields.Many2one(
        'hr.employee',
        string='Requested by',
    )
    shipment_count = fields.Integer(
        string='Incoming Shipments',
        compute='_compute_shipment_count',
    )
    amount_discount = fields.Float(
        string='Discount (Amt.)',
        related='order_line.amount_discount',
    )
    percent_discount = fields.Float(
        string='Discount (%)',
        related='order_line.percent_discount',
    )

    @api.multi
    def _compute_shipment_count(self):
        Group = self.env['procurement.group']
        Picking = self.env['stock.picking']
        for rec in self:
            # Shipment
            groups = Group.search([('name', '=', rec.name)])
            pickings = Picking.search([('group_id', 'in', groups.ids)])
            rec.shipment_count = len(pickings)

    @api.multi
    def view_picking(self):
        """ Change po.picking_ids to picking with same procurement group """
        self.ensure_one()
        action = super(PurchaseOrder, self).view_picking()
        action.update({'domain': False, 'views': False, 'res_id': False})
        Group = self.env['procurement.group']
        Picking = self.env['stock.picking']
        Data = self.env['ir.model.data']

        groups = Group.search([('name', '=', self.name)])
        pickings = Picking.search([('group_id', 'in', groups.ids)])

        if len(pickings) > 1:
            action['domain'] = [('id', '=', pickings.ids)]
        else:
            res = Data.get_object_reference('stock', 'view_picking_form')
            action['views'] = [(res and res[1] or False, 'form')]
            action['res_id'] = pickings.ids and pickings.ids[0] or False
        return action


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    amount_discount = fields.Float(
        string='Discount (Amt.)',
    )
    percent_discount = fields.Float(
        string='Discount (%)',
    )

    @api.onchange('amount_discount', 'price_unit', 'product_qty')
    def _onchange_amount_discount(self):
        if self._context.get('by_amount_discount', False):
            self.percent_discount = False
            price_subtotal = self.price_unit * self.product_qty
            if not price_subtotal:
                self.discount = 0.0
            else:
                self.discount = self.amount_discount / price_subtotal * 100.0

    @api.onchange('percent_discount')
    def _onchange_discount_percent(self):
        if self._context.get('by_percent_discount', False):
            self.amount_discount = False
            self.discount = self.percent_discount
