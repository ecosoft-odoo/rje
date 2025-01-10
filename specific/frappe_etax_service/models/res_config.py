# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################


from openerp import api
from openerp.osv import fields, osv
from openerp.tools.safe_eval import safe_eval


class account_config_settings(osv.osv_memory):
    _inherit = 'account.config.settings'

    _columns = {
        'frappe_server_url': fields.char('Frappe Server URL'),
        'frappe_auth_token': fields.char('Frappe Auth Token'),
        'is_send_etax_email': fields.boolean('Send Email'),
        'replacement_lock_date': fields.integer('Replacement Lock Date'),
    }

    @api.onchange('replacement_lock_date')
    def _onchange_replacement_lock_date(self):
        if self.replacement_lock_date > 30:
            self.replacement_lock_date = 1

    def get_default_frappe_server_parameter(self, cr, uid, fields, context=None):
        icp = self.pool.get('ir.config_parameter')
        # we use safe_eval on the result, since the value of the parameter is a nonempty string
        return {
            'frappe_server_url': safe_eval(icp.get_param(cr, uid, 'frappe_etax_service.frappe_server_url', 'False')),
            'frappe_auth_token': safe_eval(icp.get_param(cr, uid, 'frappe_etax_service.frappe_auth_token', 'False')),
            'is_send_etax_email': safe_eval(icp.get_param(cr, uid, 'frappe_etax_service.is_send_etax_email', 'False')),
            'replacement_lock_date': safe_eval(icp.get_param(cr, uid, 'frappe_etax_service.replacement_lock_date', 1)),
        }

    def set_frappe_server_parameter(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context=context)
        icp = self.pool.get('ir.config_parameter')
        icp.set_param(cr, uid, 'frappe_etax_service.frappe_server_url', repr(config.frappe_server_url))
        icp.set_param(cr, uid, 'frappe_etax_service.frappe_auth_token', repr(config.frappe_auth_token))
        icp.set_param(cr, uid, 'frappe_etax_service.is_send_etax_email', repr(config.is_send_etax_email))
        icp.set_param(cr, uid, 'frappe_etax_service.replacement_lock_date', repr(config.replacement_lock_date))