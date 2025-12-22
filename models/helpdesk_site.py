# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskSite(models.Model):
    _name = 'helpdesk.site'
    _description = 'Helpdesk Site'
    _inherit = ['mail.thread']
    _order = 'name'
    
    name = fields.Char(string='Site Name', required=True, tracking=True)
    code = fields.Char(string='Site Code', tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Related counts - computed from Many2many relationship
    department_count = fields.Integer(string='Department Count', compute='_compute_department_count')
    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    open_ticket_count = fields.Integer(string='Open Tickets', compute='_compute_ticket_count')
    closed_ticket_count = fields.Integer(string='Closed Tickets', compute='_compute_ticket_count')
    
    # Notification emails for Project Managers
    notified_email_ids = fields.One2many(
        'helpdesk.site.notified.email', 
        'site_id', 
        string='CC Notification Emails',
        help='Project Managers and other recipients to be CC\'d on department notifications',
        context={'active_test': False}
    )
    
    @api.depends('name')
    def _compute_department_count(self):
        """Count departments associated with this site via Many2many"""
        for site in self:
            site.department_count = self.env['helpdesk.team.department'].search_count([('site_ids', 'in', site.id)])
    
    def copy(self, default=None):
        """Override copy to duplicate notification emails"""
        default = dict(default or {})
        new_site = super(HelpdeskSite, self).copy(default)
        
        # Copy notification emails
        for email in self.notified_email_ids:
            email.copy({'site_id': new_site.id})
        
        return new_site
    
    def _compute_ticket_count(self):
        """Compute total tickets for all departments under this site"""
        for site in self:
            tickets = self.env['helpdesk.ticket'].search([
                ('site_id', '=', site.id)
            ])
            site.ticket_count = len(tickets)
            
            # Count open tickets (not closed or canceled)
            open_tickets = self.env['helpdesk.ticket'].search([
                ('site_id', '=', site.id),
                ('stage_id.fold', '=', False)
            ])
            site.open_ticket_count = len(open_tickets)
            
            # Count closed tickets (folded stages are considered closed)
            closed_tickets = self.env['helpdesk.ticket'].search([
                ('site_id', '=', site.id),
                ('stage_id.fold', '=', True)
            ])
            site.closed_ticket_count = len(closed_tickets)
    
    def action_view_tickets(self):
        """Open tickets for this site"""
        self.ensure_one()
        return {
            'name': f'Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form,kanban',
            'domain': [('site_id', '=', self.id)],
            'context': {'default_site_id': self.id},
        }
