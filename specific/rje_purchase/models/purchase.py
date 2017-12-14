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
    shipment_count = fields.Integer(
        string='Incoming Shipments',
        compute='_compute_shipment_count',
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
