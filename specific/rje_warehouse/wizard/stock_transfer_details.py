# -*- coding: utf-8 -*-
from openerp import models, fields, api


class StockTransferDetails(models.TransientModel):
    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, fields):
        res = super(StockTransferDetails, self).default_get(fields)
        # Get description by product_id
        active_id = self._context.get('active_id', False)
        if active_id:
            picking = self.env['stock.picking'].browse(active_id)
            for line in res.get('item_ids', []):
                product_id = line['product_id']
                descs = picking.move_lines.filtered(
                    lambda l: l.product_id.id == product_id).mapped('name')
                line['description'] = '\n'.join(descs)
        return res


class StockTransferDetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    description = fields.Text(
        string='Description',
        readonly=True,
        help="All product descriptions separated by new line."
    )
