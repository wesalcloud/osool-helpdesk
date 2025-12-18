# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskSite(models.Model):
    _name = 'helpdesk.site'
    _description = 'Helpdesk Site'
    _order = 'name'
    
    name = fields.Char(string='Site Name', required=True, tracking=True)
    code = fields.Char(string='Site Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Related counts
    department_ids = fields.One2many('helpdesk.team.department', 'site_id', string='Departments')
    department_count = fields.Integer(string='Department Count', compute='_compute_department_count')
    
    @api.depends('department_ids')
    def _compute_department_count(self):
        for site in self:
            site.department_count = len(site.department_ids)
