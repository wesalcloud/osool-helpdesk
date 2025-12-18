# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    
    # Team Department
    team_department_id = fields.Many2one('helpdesk.team.department', string='Team Department', tracking=True)
    
    # Department Site (related field)
    department_site_id = fields.Many2one('helpdesk.site', string='Department Site', related='team_department_id.site_id', readonly=True, store=True)
    
    # Notified Emails List
    notified_email_ids = fields.One2many('helpdesk.team.notified.email', 'team_id', string='Notified Emails', context={'active_test': False})
    
    # Contact Information
    team_email = fields.Char(string='Team Email')
    team_phone = fields.Char(string='Team Phone')
    team_whatsapp = fields.Char(string='Team WhatsApp')
    
    # Department Type
    department_type = fields.Selection([
        ('technical', 'Technical'),
        ('administrative', 'Administrative'),
        ('customer_service', 'Customer Service'),
        ('security', 'Security'),
        ('hr', 'Human Resources'),
        ('procurement', 'Procurement'),
        ('marketing', 'Marketing'),
    ], string='Department Type')
    
    # Work hours
    work_hours_start = fields.Float(string='Work Hours Start', default=8.0)
    work_hours_end = fields.Float(string='Work Hours End', default=17.0)
    
    # SLA settings
    default_sla_id = fields.Many2one('helpdesk.sla', string='Default SLA')
