# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskSLA(models.Model):
    _inherit = 'helpdesk.sla'
    
    # Response and Resolution Times
    response_time = fields.Integer(string='Response Time (minutes)', default=15)
    resolution_time = fields.Integer(string='Resolution Time (minutes)', default=480)
    
    # SLA Type
    sla_type = fields.Selection([
        ('standard', 'Standard'),
        ('priority', 'Priority'),
        ('vvip', 'VVIP'),
    ], string='SLA Type', default='standard')
    
    # Priority for tickets using this SLA
    ticket_priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1', help='Default priority for tickets using this SLA')
    
    # Working hours consideration
    use_working_hours = fields.Boolean(string='Use Working Hours', default=True)
    
    # Escalation
    auto_escalate = fields.Boolean(string='Auto Escalate on Breach', default=True)
    escalation_user_id = fields.Many2one('res.users', string='Escalate To')
