# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class AccountBankReceipt(models.Model):
    _inherit = "account.bank.receipt"

    name = fields.Char(
        states={'draft': [('readonly', False)]},
        required=True,
    )

    @api.multi
    def validate_bank_receipt(self):
        """ Overwrite """
        am_obj = self.env['account.move']
        aml_obj = self.env['account.move.line']
        for receipt in self:

            # # Create document number
            # refer_type = 'bank_receipt'
            # doctype = receipt.env['res.doctype'].get_doctype(refer_type)
            # fiscalyear_id = receipt.env['account.fiscalyear'].find()
            # receipt = receipt.with_context(doctype_id=doctype.id,
            #                                fiscalyear_id=fiscalyear_id)
            # name = receipt.env['ir.sequence'].next_by_code(
            #     'account.bank.receipt')
            # receipt.write({'name': name})

            move_vals = self._prepare_account_move_vals(receipt)
            move = am_obj.create(move_vals)
            total_debit = 0.0
            total_amount_currency = 0.0
            to_reconcile_lines = []
            for line in receipt.bank_intransit_ids:
                total_debit += line.debit
                total_amount_currency += line.amount_currency
                line_vals = self._prepare_move_line_vals(line)
                line_vals['move_id'] = move.id
                move_line = aml_obj.create(line_vals)
                to_reconcile_lines.append(line + move_line)

            # Create counter-part
            if not receipt.partner_bank_id:
                raise UserError(_("Missing Bank Account"))
            if not receipt.bank_account_id:
                raise UserError(
                    _("Missing Account for Bank Receipt on the journal '%s'.")
                    % receipt.partner_bank_id.journal_id.name)

            counter_vals = self._prepare_counterpart_move_lines_vals(
                receipt, total_debit, total_amount_currency)
            counter_vals['move_id'] = move.id
            aml_obj.create(counter_vals)

            move.post()
            receipt.write({'state': 'done',
                           'move_id': move.id,
                           'validate_user_id': self.env.user.id,
                           'validate_date': fields.Date.context_today(self),
                           })
            # We have to reconcile after post()
            for reconcile_lines in to_reconcile_lines:
                reconcile_lines.reconcile()
        return True
