# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

import logging

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv, fields
from datetime import datetime

_logger = logging.getLogger(__name__)

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'etax.th']

    def _get_branch_id(self):
        """
        By default, core odoo do not provide branch_id field in
        account.invoice and account.payment.
        This method will check if branch_id is exist in model and return branch_id
        """
        if "branch_id" in self.env["account.invoice"]._fields:
            return self.branch_id.name

    def _get_po_number_payment_terms(self):
        """
        Case:   Invoice
                Credit/Debit Note
        """
        data = ["", ""]
        # Get po number and payment terms from invoice
        po_number = self.name
        payment_term = self.payment_term.name
        data[0] = po_number and po_number or ""
        data[1] = payment_term and payment_term or ""

        # Get po number in case of credit note, debit note
        if self.origin_invoice_id:
            po_number = self.origin_invoice_id.name
            data[0] = po_number and po_number or ""
        return data

    def _get_origin_data(self):
        """
        If invoice has origin invoice (e.g. credit note, debit note, replacement tax invoice)
        Query:  Get origin date_invoice
                    origin etax_doctype
        """
        # Case: Replacement Tax Invoice
        if self.replaced_entry_id:
            return (self.replaced_entry_id.date_invoice + "T00:00:00", self.replaced_entry_id.etax_doctype, self.replaced_entry_id.preprint_number)
        # Case: Credit Note, Debit Note
        if self.origin:
            self._cr.execute("SELECT date_invoice, etax_doctype FROM account_invoice WHERE preprint_number = %s::varchar",
                 (self.origin,))
            data = self._cr.fetchone()
            if data:
                # Date in INET should in format "%Y-%m-%dT%H:%M:%S"
                return (data[0] + "T00:00:00", data[1], self.origin)
        return ("", "", "")

    def _get_additional_amount(self):
        """
        In case of credit note, debit note or replacement tax invoice
        Get original untax amount for
            f36_original_total_amount = original_amount_untaxed
            f40_adjusted_information_amount = diff_amount_untaxed
            f38_line_total_amount = corrected_amount_untaxed
        """
        original_amount_untaxed = corrected_amount_untaxed = diff_amount_untaxed = 0.00
        if self.origin_invoice_id:
            original_amount_untaxed = self.origin_invoice_id.amount_untaxed
            diff_amount_untaxed = self.amount_untaxed
            # credit note
            if self.type == "out_refund":
                corrected_amount_untaxed = original_amount_untaxed - diff_amount_untaxed
            # debit note
            elif self.type == "out_invoice":
                corrected_amount_untaxed = original_amount_untaxed + diff_amount_untaxed
        if self.replaced_entry_id:
            original_amount_untaxed = 0.00
            diff_amount_untaxed = 0.00
            corrected_amount_untaxed = self.amount_untaxed
        return (original_amount_untaxed, diff_amount_untaxed, corrected_amount_untaxed)

    # in odoo v8 don't have this method
    # @api.depends("restrict_mode_hash_table", "state")
    # def _compute_show_reset_to_draft_button(self):
    #     res = super()._compute_show_reset_to_draft_button()
    #     # If etax signed, user can't just reset to draft.
    #     # User need to create replacement invoice, do the update and submit eTax again.
    #     for move in self.filtered(lambda m: m.etax_status == "success"):
    #         move.show_reset_to_draft_button = False
    #     return res

    def create_replacement_etax(self):
        """Create replacement document and cancel the old one"""
        self.ensure_one()
        if not (self.move_id.state == "posted" and self.etax_status == "success"):
            raise ValidationError(_("Only posted etax invoice can have a substitution"))
        res = self.with_context(include_business_fields=True).copy_data()
        res = self.with_context(
            **{
                "include_business_fields": True,
                "force_copy_stock_moves": True,
            }
        ).copy_data()
        old_number = self.preprint_number
        suffix = "-R"
        if suffix in old_number:
            [preprint_number, rev] = old_number.split(suffix)
            res[0]["preprint_number"] = "{}{}{}".format(preprint_number, suffix, int(rev) + 1)
        else:
            res[0]["preprint_number"] = "{}{}{}".format(old_number, suffix, 1)
        res[0]["reference_type"] = self.reference_type
        res[0]["date_invoice"] = self.date_invoice
        res[0]["date_due"] = self.date_due
        res[0]["doc_name_template"] = self.doc_name_template.id
        move = self.create(res[0])
        self.action_cancel_draft()
        self.signal_workflow('invoice_cancel')
        self.preprint_number = old_number  # Ensure name.
        return move
