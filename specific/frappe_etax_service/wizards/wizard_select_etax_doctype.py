# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################

from openerp import models, api, _
from openerp.exceptions import ValidationError
from openerp.osv import osv, fields



class WizardSelectEtaxDoctype(osv.osv_memory):
    _name = 'wizard.select.etax.doctype'
    _columns = {
        'frappe_server_url': fields.char('ETax Server', readonly=True,),
        'doc_name_template': fields.many2one('doc.type', 'Invoice template', required=True, ),
        'type': fields.selection(
            [
                ('out_invoice', 'Customer Invoice'),
                ('out_refund', 'Customer Credit Note'),
                ('out_invoice_debit', 'Customer Debit Note'),
                ('receipt', 'Customer Payment'),
            ],
            'Type',
        ),
        'run_background': fields.boolean('Run in Background'),
    }

    def default_get(self, cr, uid, fields, context=None):
        res = super(WizardSelectEtaxDoctype, self).default_get(cr, uid, fields, context=None)
        if context is None:
            context = {}
        res_model = context.get('active_model')
        active_ids = context.get('active_ids', False)
        moves = self.pool.get(res_model).browse(cr, uid, active_ids, context=context)
        type = list(set(moves.mapped('type')))
        # is_debit = list(
        #     set(moves.mapped(lambda move: move.debit_origin_id and True or False))
        # )
        template = moves.mapped('doc_name_template')
        template = False if len(template) > 1 else template
        # if len(type) > 1 or len(is_debit) > 1:
        #     raise ValidationError(_('Multiple move types not allowed'))
        type = type and type[0] or False
        # is_debit = is_debit and is_debit[0] or False
        # if type == 'out_invoice' and is_debit:
        #     type = 'out_invoice_debit'
        res.update(
            {
                'frappe_server_url': str(self.pool['ir.config_parameter'].get_param(cr, uid, 'frappe_etax_service.frappe_server_url', default=False)),
                'type': type,
                'doc_name_template': template.id,
                'run_background': len(moves) > 1,
            }
        )
        # Validation
        if type not in ['out_invoice', 'out_refund', 'out_invoice_debit', 'receipt']:
            raise ValidationError(_('Only customer invoice can sign eTax'))
        return res

    def sign_etax_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res_model = context.get('active_model')
        active_ids = context.get('active_ids', False)
        moves = self.pool.get(res_model).browse(cr, uid, active_ids, context=context)
        wizard = self.browse(cr, uid, ids, context=context)
        self.pre_etax_validate(moves)
        for move in moves:
            doc_name_template = wizard.doc_name_template
            move.update(
                {
                    'etax_doctype': doc_name_template.doctype_code,
                    'doc_name_template': doc_name_template,
                    'is_send_frappe': True,
                }
            )
            if wizard.run_background:
                move.etax_status = 'to_process'
            else:
                move.sign_etax()

    def pre_etax_validate(self, invoices):
        # Already under processing or succeed
        invalid = invoices.filtered(
            lambda inv: inv.etax_status in ['success', 'processing']
        )
        if invalid:
            raise ValidationError(
                _('%s, eTax status is in Processing/Success')
                % ', '.join(invalid.mapped('preprint_number'))
            )
        # Not in valid customer invoice type
        invalid = invoices.filtered(
            lambda inv: inv.type in ['inv_invoice', 'inv_refund']
        )
        if invalid:
            raise ValidationError(
                _('%s type not valid\nOnly customer invoices can sign eTax')
                % ', '.join(invalid.mapped('preprint_number'))
            )
        # Not posted
        invalid = invoices.filtered(lambda inv: inv.move_id.state != 'posted')
        if invalid:
            raise ValidationError(
                _('Some invoices are not posted and cannot sign eTax')
            )
        # No tax invoice
        invalid = invoices.filtered(lambda inv: not inv.tax_line)
        if invalid:
            raise ValidationError(
                _('%s has no tax invoice') % ', '.join(invalid.mapped('preprint_number'))
            )
