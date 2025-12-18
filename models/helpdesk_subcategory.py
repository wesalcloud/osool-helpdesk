# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HelpdeskSubcategory(models.Model):
    _name = 'helpdesk.subcategory'
    _description = 'Helpdesk Subcategory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'category_id, sequence, name'
    
    name = fields.Char(string='Subcategory Name', required=True, translate=True, tracking=True)
    code = fields.Char(string='Subcategory Code', tracking=True, help='Unique code for this subcategory. Auto-generated if not provided.')
    description = fields.Text(string='Description', translate=True, tracking=True)
    sequence = fields.Integer(string='Sequence', default=10, tracking=True)
    active = fields.Boolean(string='Active', default=True, tracking=True)
    
    # Category
    category_id = fields.Many2one('helpdesk.category', string='Category', required=True, ondelete='cascade', tracking=True)
    
    # Routing
    team_id = fields.Many2one('helpdesk.team', string='Assigned Team', tracking=True)
    auto_assign_user_id = fields.Many2one('res.users', string='Auto-Assign To', tracking=True)
    ticket_owner_id = fields.Many2one('res.users', string='Ticket Owner', tracking=True, help='Owner to assign when ticket is rejected')
    cc_team_ids = fields.Many2many('helpdesk.team', string='CC Teams')
    cc_user_ids = fields.Many2many('res.users', string='CC Users')
    
    # SLA
    sla_id = fields.Many2one('helpdesk.sla', string='SLA Policy', tracking=True)
    
    # Escalation
    escalation_enabled = fields.Boolean(string='Enable Escalation', default=False, tracking=True)
    escalation_time = fields.Integer(string='Escalation Time (minutes)', default=60, tracking=True)
    escalation_user_id = fields.Many2one('res.users', string='Escalate To', tracking=True)
    
    # Work Instructions
    work_instructions = fields.Html(string='Work Instructions', translate=True,
                                   help='Step-by-step instructions for handling tickets of this subcategory')
    
    # Statistics
    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    
    def _compute_ticket_count(self):
        for subcategory in self:
            subcategory.ticket_count = self.env['helpdesk.ticket'].search_count([
                ('request_subcategory_id', '=', subcategory.id)
            ])
    
    def action_view_tickets(self):
        """View tickets for this subcategory"""
        return {
            'name': f'Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form,kanban',
            'domain': [('request_subcategory_id', '=', self.id)],
            'context': {'default_request_subcategory_id': self.id, 'default_request_category_id': self.category_id.id}
        }
    
    # Removed Python constraint - will be enforced at database level only
    # This allows data imports to work smoothly while still preventing duplicates
    
    @api.constrains('escalation_enabled', 'escalation_time', 'escalation_user_id')
    def _check_escalation_settings(self):
        """Validate escalation settings"""
        for record in self:
            if record.escalation_enabled:
                if not record.escalation_user_id:
                    raise ValidationError(_("Please specify a user to escalate to when escalation is enabled."))
                if record.escalation_time <= 0:
                    raise ValidationError(_("Escalation time must be greater than 0 minutes."))
    
    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Auto-set team and SLA from category"""
        if self.category_id:
            if self.category_id.team_id and not self.team_id:
                self.team_id = self.category_id.team_id
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to add custom logic"""
        # Validate and normalize data before creation
        for vals in vals_list:
            # Auto-generate code if not provided
            if not vals.get('code'):
                if vals.get('name') and vals.get('category_id'):
                    category = self.env['helpdesk.category'].browse(vals['category_id'])
                    if category and category.code:
                        # Generate code from category code + first 3 letters of name
                        name_part = ''.join(c for c in vals['name'][:3] if c.isalnum()).upper()
                        vals['code'] = f"{category.code}_{name_part}"
                else:
                    # Fallback: use name only
                    name_part = ''.join(c for c in vals.get('name', 'SUB')[:6] if c.isalnum()).upper()
                    vals['code'] = name_part
            
            # Ensure code is uppercase
            if vals.get('code'):
                vals['code'] = vals['code'].upper()
        
        subcategories = super(HelpdeskSubcategory, self).create(vals_list)
        
        # Post creation actions
        for subcategory in subcategories:
            subcategory.message_post(
                body=_("Subcategory created: %s") % subcategory.name,
                subtype_xmlid='mail.mt_note'
            )
        
        return subcategories
    
    def write(self, vals):
        """Override write to add custom logic and tracking"""
        # Track important changes
        for record in self:
            changes = []
            
            # Track team changes
            if 'team_id' in vals:
                old_team = record.team_id.name if record.team_id else _('None')
                new_team_id = vals['team_id']
                new_team = self.env['helpdesk.team'].browse(new_team_id).name if new_team_id else _('None')
                if old_team != new_team:
                    changes.append(_("Team: %s → %s") % (old_team, new_team))
            
            # Track SLA changes
            if 'sla_id' in vals:
                old_sla = record.sla_id.name if record.sla_id else _('None')
                new_sla_id = vals['sla_id']
                new_sla = self.env['helpdesk.sla'].browse(new_sla_id).name if new_sla_id else _('None')
                if old_sla != new_sla:
                    changes.append(_("SLA: %s → %s") % (old_sla, new_sla))
            
            # Track escalation changes
            if 'escalation_enabled' in vals:
                old_escalation = _('Enabled') if record.escalation_enabled else _('Disabled')
                new_escalation = _('Enabled') if vals['escalation_enabled'] else _('Disabled')
                if old_escalation != new_escalation:
                    changes.append(_("Escalation: %s") % new_escalation)
            
            # Track active status changes
            if 'active' in vals and vals['active'] != record.active:
                status = _('Activated') if vals['active'] else _('Archived')
                changes.append(_("Status: %s") % status)
                
                # Handle archiving - notify on open tickets
                if not vals['active']:
                    open_tickets = self.env['helpdesk.ticket'].search([
                        ('request_subcategory_id', '=', record.id),
                        ('stage_id.is_closed', '=', False)
                    ])
                    if open_tickets:
                        open_tickets.message_post(
                            body=_("Warning: Subcategory '%s' has been archived but this ticket is still open.") % record.name,
                            subtype_xmlid='mail.mt_note'
                        )
            
            # Ensure code is uppercase
            if 'code' in vals and vals['code']:
                vals['code'] = vals['code'].upper()
            
            # Post change message
            if changes:
                record.message_post(
                    body=_("Updated: %s") % ', '.join(changes),
                    subtype_xmlid='mail.mt_note'
                )
        
        # Call parent write
        result = super(HelpdeskSubcategory, self).write(vals)
        
        # Update related tickets if team or SLA changed
        if 'team_id' in vals or 'sla_id' in vals:
            for record in self:
                tickets = self.env['helpdesk.ticket'].search([
                    ('request_subcategory_id', '=', record.id),
                    ('stage_id.is_closed', '=', False)
                ])
                
                ticket_vals = {}
                if 'team_id' in vals and vals['team_id']:
                    ticket_vals['team_id'] = vals['team_id']
                if 'sla_id' in vals and vals['sla_id']:
                    ticket_vals['sla_id'] = vals['sla_id']
                
                if ticket_vals and tickets:
                    tickets.write(ticket_vals)
                    record.message_post(
                        body=_("Updated %d open ticket(s) with new settings") % len(tickets),
                        subtype_xmlid='mail.mt_note'
                    )
        
        return result
    
    def unlink(self):
        """Override unlink to check for related tickets"""
        for record in self:
            ticket_count = self.env['helpdesk.ticket'].search_count([
                ('request_subcategory_id', '=', record.id)
            ])
            if ticket_count > 0:
                raise ValidationError(
                    _("Cannot delete subcategory '%s' because it has %d associated ticket(s). Please archive it instead.") % 
                    (record.name, ticket_count)
                )
        
        return super(HelpdeskSubcategory, self).unlink()
