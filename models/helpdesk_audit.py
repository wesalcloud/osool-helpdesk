# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpdeskAudit(models.Model):
    _name = 'helpdesk.audit'
    _description = 'Helpdesk Ticket Audit Log'
    _order = 'timestamp desc'
    
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', string='User', required=True)
    action = fields.Char(string='Action', required=True)
    description = fields.Text(string='Description')
    old_value = fields.Text(string='Old Value')
    new_value = fields.Text(string='New Value')
    timestamp = fields.Datetime(string='Timestamp', required=True, default=fields.Datetime.now)
