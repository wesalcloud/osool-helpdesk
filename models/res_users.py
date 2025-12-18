# -*- coding: utf-8 -*-
from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # Agent-specific fields
    is_helpdesk_agent = fields.Boolean(string='Is Helpdesk Agent', default=False)
    helpdesk_team_ids = fields.Many2many('helpdesk.team', string='Helpdesk Teams')
    max_tickets = fields.Integer(string='Max Concurrent Tickets', default=10)
    
    # Statistics
    assigned_ticket_count = fields.Integer(string='Assigned Tickets', compute='_compute_ticket_stats')
    closed_ticket_count = fields.Integer(string='Closed Tickets', compute='_compute_ticket_stats')
    
    def _compute_ticket_stats(self):
        for user in self:
            user.assigned_ticket_count = self.env['helpdesk.ticket'].search_count([
                ('user_id', '=', user.id),
                ('status', 'not in', ['closed', 'cancelled'])
            ])
            user.closed_ticket_count = self.env['helpdesk.ticket'].search_count([
                ('user_id', '=', user.id),
                ('status', '=', 'closed')
            ])
