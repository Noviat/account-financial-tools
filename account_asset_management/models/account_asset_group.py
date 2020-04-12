# Copyright 2009-2020 Noviat
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class AccountAssetGroup(models.Model):
    _name = 'account.asset.group'
    _description = 'Asset Group'
    _order = 'code, name'
    _parent_store = True

    name = fields.Char(string='Name', size=64, required=True, index=True)
    code = fields.Char(index=True)
    parent_path = fields.Char(index=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self._default_company_id())
    parent_id = fields.Many2one(
        comodel_name='account.asset.group',
        string='Parent Asset Group',
        ondelete='restrict')
    child_ids = fields.One2many(
        comodel_name='account.asset.group',
        inverse_name='parent_id',
        string='Child Asset Groups')

    @api.model
    def _default_company_id(self):
        return self.env['res.company']._company_default_get('account.asset')

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            name = rec.code + ' ' + rec.name
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100,
                     name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = [
                '|',
                ('code', '=ilike', name.split(' ')[0] + '%'),
                ('name', operator, name)
            ]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        rec_ids = self._search(
            expression.AND([domain, args]), limit=limit,
            access_rights_uid=name_get_uid)
        return self.browse(rec_ids).name_get()
