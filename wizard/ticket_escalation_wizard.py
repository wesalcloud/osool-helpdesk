# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TicketEscalationWizard(models.TransientModel):
    _name = 'helpdesk.ticket.escalation.wizard'
    _description = 'Ticket Escalation Wizard'
    
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', required=True, readonly=True)
    escalation_reason = fields.Text(string='Escalation Reason', required=True)
    escalate_to_team = fields.Many2one('helpdesk.team', string='Escalate to Team')
    escalate_to_user = fields.Many2one('res.users', string='Escalate to User')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Medium'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='New Priority')
    notify_customer = fields.Boolean(string='Notify Customer', default=True)
    
    def action_escalate(self):
        """Escalate the ticket"""
        self.ensure_one()
        
        vals = {}
        if self.escalate_to_team:
            vals['team_id'] = self.escalate_to_team.id
        if self.escalate_to_user:
            vals['user_id'] = self.escalate_to_user.id
        if self.priority:
            vals['priority'] = self.priority
        
        self.ticket_id.write(vals)
        
        # Create audit log
        self.ticket_id._create_audit_log(
            'escalated',
            f'Ticket escalated: {self.escalation_reason}'
        )
        
        # Post message on ticket
        self.ticket_id.message_post(
            body=f'<p><strong>Ticket Escalated</strong></p><p>{self.escalation_reason}</p>',
            message_type='notification',
            subtype_xmlid='mail.mt_note',
        )
        
        # Send notification
        if self.notify_customer:
            template = self.env.ref('osool_helpdesk.email_template_ticket_escalated', raise_if_not_found=False)
            if template:
                template.send_mail(self.ticket_id.id, force_send=True)
        
        return {'type': 'ir.actions.act_window_close'}
