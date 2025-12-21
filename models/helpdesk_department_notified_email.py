# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskDepartmentNotifiedEmail(models.Model):
    _name = 'helpdesk.department.notified.email'
    _description = 'Helpdesk Department Notified Email'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    department_id = fields.Many2one('helpdesk.team.department', string='Department', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    active = fields.Boolean(string='Active', default=True)


class HelpdeskSiteNotifiedEmail(models.Model):
    _name = 'helpdesk.site.notified.email'
    _description = 'Helpdesk Site Notified Email'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    site_id = fields.Many2one('helpdesk.site', string='Site', required=True, ondelete='cascade')
    name = fields.Char(string='Name/Role', required=True, help='e.g. Project Manager, Site Manager')
    email = fields.Char(string='Email', required=True)
    active = fields.Boolean(string='Active', default=True)
