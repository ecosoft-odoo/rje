# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

from openerp import _
from openerp.osv import osv
from openerp.exceptions import ValidationError


class account_voucher(osv.osv):
    _name = "account.voucher"
    _inherit = ["account.voucher", "etax.th"]

    def action_cancel_draft(self, cr, uid, ids, context=None):
        vouchers = self.browse(cr, uid, ids, context=context)
        if any(voucher.etax_status in ("success", "processing", "to_process") for voucher in vouchers):
            raise osv.except_osv(
                _("Validation Error"),
                _(
                    "Cannot reset to draft, eTax submission already started "
                    "or succeeded.\n"
                    "You should do the refund process instead."
                )
            )
        return super(account_voucher, self).action_cancel_draft(cr, uid, ids, context=context)

    # def _get_branch_id(self, cr, uid, ids, context=None):
    #     """
    #     By default, core openerp do not provide branch_id field in
    #     account.invoice and account.voucher.
    #     This method will check if branch_id is exist in model and return branch_id
    #     """
    #     vouchers = self.browse(cr, uid, ids, context=context)
    #     for voucher in vouchers:
    #         if voucher.reconciled_invoice_ids:
    #             if "branch_id" in self.pool.get("account.invoice")._columns:
    #                 return voucher.reconciled_invoice_ids[0].branch_id.name
    #     return False
