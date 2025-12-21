# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskTeamDepartment(models.Model):
    _name = 'helpdesk.team.department'
    _description = 'Helpdesk Team Department'
    _inherit = ['mail.thread']
    _order = 'name'
    
    name = fields.Char(string='Department Name', required=True, tracking=True)
    code = fields.Char(string='Department Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Site relationship
    site_id = fields.Many2one('helpdesk.site', string='Site', tracking=True)
    
    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    open_ticket_count = fields.Integer(string='Open Tickets', compute='_compute_ticket_count')
    closed_ticket_count = fields.Integer(string='Closed Tickets', compute='_compute_ticket_count')
    
    # Notification emails for this department
    notified_email_ids = fields.One2many(
        'helpdesk.department.notified.email',
        'department_id',
        string='Notification Emails',
        help='Email addresses to notify when tickets are assigned to this department',
        context={'active_test': False}
    )
    
    def copy(self, default=None):
        """Override copy to duplicate notification emails"""
        default = dict(default or {})
        new_dept = super(HelpdeskTeamDepartment, self).copy(default)
        
        # Copy notification emails
        for email in self.notified_email_ids:
            email.copy({'department_id': new_dept.id})
        
        return new_dept
    
    def _compute_ticket_count(self):
        """Compute total tickets for all teams under this department"""
        for dept in self:
            tickets = self.env['helpdesk.ticket'].search([
                ('team_department_id', '=', dept.id)
            ])
            dept.ticket_count = len(tickets)
            
            # Count open tickets (not closed or canceled)
            open_tickets = self.env['helpdesk.ticket'].search([
                ('team_department_id', '=', dept.id),
                ('stage_id.fold', '=', False)
            ])
            dept.open_ticket_count = len(open_tickets)
            
            # Count closed tickets (folded stages are considered closed)
            closed_tickets = self.env['helpdesk.ticket'].search([
                ('team_department_id', '=', dept.id),
                ('stage_id.fold', '=', True)
            ])
            dept.closed_ticket_count = len(closed_tickets)
    
    def action_view_tickets(self):
        """Open tickets for this department"""
        self.ensure_one()
        return {
            'name': f'Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form,kanban',
            'domain': [('team_department_id', '=', self.id)],
            'context': {'default_team_department_id': self.id},
        }
