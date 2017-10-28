# -*- coding: utf-8 -*-
from openerp import fields, models, _, exceptions, api


class AccessRight(models.TransientModel):
    _name = "access.right"

    access_right = fields.Many2one('access.access',
                                   string='Meta Group',
                                   type="Selection")

    @api.multi
    def apply_access(self):
        active_ids = self._context.get('active_ids')
        for g in self:
            if self._context and active_ids and g.access_right:
                users = self.env['res.users'].browse(active_ids)
                for user_rec in users:
                    user_rec.groups_id = [(6, 0, g.access_right.groups_id.ids)]
                    user_rec.last_meta_group_id = g.access_right
                    user_rec.last_meta_group_date = fields.Datetime.now()
            else:
                raise exceptions.Warning(
                    _('Please create a Meta Group via '
                      'Settings --> Users --> Meta Groups.'))
