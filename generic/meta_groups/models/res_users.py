# -*- coding: utf-8 -*-
from openerp import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    last_meta_group_id = fields.Many2one(
        'access.access',
        string='Last Updated Meta Group',
        readonly=True,
    )
    last_meta_group_date = fields.Datetime(
        string='Date Updated Meta Group',
        readonly=True,
    )
