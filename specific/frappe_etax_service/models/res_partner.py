# -*- coding: utf-8 -*-
##############################################################################
# Copyright 2023 Ecosoft
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
##############################################################################


from openerp.osv import osv, fields


class res_partner(osv.osv):
    """ Inherits partner and adds contract information in the partner form """
    _inherit = 'res.partner'

    _columns = {
        'email_etax': fields.char('Email for e-Tax'),
    }
