# -*- coding: utf-8 -*-
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # Customer type
    customer_type = fields.Selection([
        ('employee', 'Employee'),
        ('tenant', 'Tenant'),
        ('vvip_tenant', 'VVIP Tenant'),
        ('external', 'External Customer'),
    ], string='Customer Type')
    
    # Ticket statistics
    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    
    def _compute_ticket_count(self):
        for partner in self:
            partner.ticket_count = self.env['helpdesk.ticket'].search_count([
                ('partner_id', '=', partner.id)
            ])
    
    def action_view_tickets(self):
        """View tickets for this partner"""
        return {
            'name': f'Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }
    
    def unlink(self):
        """Override to fix the wesalcx_genesys_cti_connector bug with missing _logger"""
        # Log deletion (fixing the missing _logger from wesalcx module)
        for record in self:
            _logger.info(f"Deleting partner: {record.id} - {record.name}")
        return super(ResPartner, self).unlink()
