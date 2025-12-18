# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ==========================================
    # Tenant Classification
    # ==========================================
    is_tenant = fields.Boolean(
        string="Is Tenant",
        default=False,
        tracking=True,
        help="Enable this option if this contact represents a tenant."
    )

    site_code = fields.Selection(
        selection=[
            ('gm', 'GM - Grand Mall'),
            ('ish', 'ISH - Ishbiliyah'),
            ('ot', 'OT - Other'),
            ('dc', 'DC - Distribution Center'),
            ('da', 'DA - Distribution Area'),
            ('dq', 'DQ - Distribution Quarter'),
            ('gbp', 'GBP - Grand Business Park'),
        ],
        string="Site",
        tracking=True,
        help="Select the site this tenant belongs to."
    )

    vip_status = fields.Selection(
        selection=[
            ('regular', 'Regular'),
            ('vip', 'VIP'),
            ('vvip', 'VVIP'),
        ],
        string="VIP Level",
        default='regular',
        tracking=True,
        help="VIP classification of the tenant."
    )

    tenant_type = fields.Selection(
        selection=[
            ('owner', 'Owner'),
            ('retail', 'Retail'),
            ('office', 'Office'),
            ('residential', 'Residential'),
        ],
        string="Tenant Type",
        tracking=True,
        help="Specify the tenant category."
    )

    tenant_status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('suspended', 'Suspended'),
            ('pending', 'Pending Approval'),
        ],
        string="Tenant Status",
        default='active',
        tracking=True,
        help="Current status of the tenant."
    )

    # ==========================================
    # Identity & Names
    # ==========================================
    arabic_full_name = fields.Char(
        string="Arabic Full Name",
        help="Full name in Arabic"
    )

    brand_name = fields.Char(
        string="Brand / Trade Name",
        index=True,
        help="Commercial or brand name used by the tenant"
    )

    company_registered_name = fields.Char(
        string="Registered Company Name",
        help="Official registered company name"
    )

    building_name = fields.Char(
        string="Building Name / Location",
        help="Building or location identifier"
    )

    unit_number = fields.Char(
        string="Unit Number",
        help="Specific unit or shop number"
    )

    floor_number = fields.Char(
        string="Floor Number",
        help="Floor where the unit is located"
    )

    # ==========================================
    # Contact Information
    # ==========================================
    phone_primary = fields.Char(
        string="Primary Phone",
        help="Main contact phone number"
    )

    phone_secondary = fields.Char(
        string="Secondary Phone",
        help="Alternative contact phone number"
    )

    email_primary = fields.Char(
        string="Primary Email",
        help="Main contact email address"
    )

    email_secondary = fields.Char(
        string="Secondary Email",
        help="Alternative contact email address"
    )

    email_tertiary = fields.Char(
        string="Tertiary Email",
        help="Third contact email address"
    )

    email_quaternary = fields.Char(
        string="Quaternary Email",
        help="Fourth contact email address"
    )

    email_quinary = fields.Char(
        string="Quinary Email",
        help="Fifth contact email address"
    )

    # ==========================================
    # Contract & Business Information
    # ==========================================
    contract_number = fields.Char(
        string="Contract Number",
        help="Lease or contract reference number"
    )

    contract_start_date = fields.Date(
        string="Contract Start Date",
        tracking=True
    )

    contract_end_date = fields.Date(
        string="Contract End Date",
        tracking=True
    )

    contract_active = fields.Boolean(
        string="Contract Active",
        compute="_compute_contract_active",
        store=True,
        help="Automatically determined based on contract dates"
    )

    business_category = fields.Selection(
        selection=[
            ('fashion', 'Fashion & Apparel'),
            ('food', 'Food & Beverage'),
            ('electronics', 'Electronics'),
            ('services', 'Services'),
            ('entertainment', 'Entertainment'),
            ('health', 'Health & Beauty'),
            ('home', 'Home & Furniture'),
            ('other', 'Other'),
        ],
        string="Business Category",
        help="Type of business operated by the tenant"
    )

    # ==========================================
    # Tickets & Support
    # ==========================================
    ticket_count = fields.Integer(
        string="Ticket Count",
        compute="_compute_ticket_count"
    )
    
    helpdesk_ticket_count = fields.Integer(
        string="Helpdesk Ticket Count",
        compute="_compute_helpdesk_ticket_count"
    )
    
    customer_type = fields.Selection(
        selection=[
            ('employee', 'Employee'),
            ('tenant', 'Tenant'),
            ('vvip_tenant', 'VVIP Tenant'),
            ('external', 'External Customer'),
        ],
        string='Customer Type',
        help="Classification of customer type"
    )

    # ==========================================
    # Notes & Documents
    # ==========================================
    tenant_notes = fields.Text(
        string="Tenant Notes",
        help="Additional notes about this tenant"
    )

    # ==========================================
    # Computed Fields
    # ==========================================
    @api.depends('contract_start_date', 'contract_end_date')
    def _compute_contract_active(self):
        """Determine if contract is currently active based on dates"""
        today = fields.Date.today()
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                record.contract_active = (
                    record.contract_start_date <= today <= record.contract_end_date
                )
            else:
                record.contract_active = False

    def _compute_helpdesk_ticket_count(self):
        """Count helpdesk tickets for this tenant"""
        for record in self:
            record.helpdesk_ticket_count = self.env['helpdesk.ticket'].search_count([
                ('partner_id', '=', record.id)
            ])
    
    def _compute_ticket_count(self):
        """Count tickets for compatibility with existing code"""
        for record in self:
            record.ticket_count = self.env['helpdesk.ticket'].search_count([
                ('partner_id', '=', record.id)
            ])

    # ==========================================
    # Constraints & Validation
    # ==========================================
    @api.constrains('email_primary', 'email_secondary', 'email_tertiary', 
                    'email_quaternary', 'email_quinary')
    def _check_email_format(self):
        """Validate email format"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for record in self:
            emails = [
                ('email_primary', record.email_primary),
                ('email_secondary', record.email_secondary),
                ('email_tertiary', record.email_tertiary),
                ('email_quaternary', record.email_quaternary),
                ('email_quinary', record.email_quinary),
            ]
            for field_name, email in emails:
                if email and not email_pattern.match(email):
                    raise ValidationError(
                        _('Invalid email format in %s: %s') % (field_name.replace('_', ' ').title(), email)
                    )

    @api.constrains('contract_start_date', 'contract_end_date')
    def _check_contract_dates(self):
        """Ensure contract end date is after start date"""
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                if record.contract_end_date < record.contract_start_date:
                    raise ValidationError(
                        _('Contract end date must be after start date.')
                    )

    @api.constrains('phone_primary', 'phone_secondary')
    def _check_phone_format(self):
        """Basic phone number validation"""
        phone_pattern = re.compile(r'^[\d\s\+\-\(\)]+$')
        for record in self:
            phones = [
                ('phone_primary', record.phone_primary),
                ('phone_secondary', record.phone_secondary),
            ]
            for field_name, phone in phones:
                if phone and not phone_pattern.match(phone):
                    raise ValidationError(
                        _('Invalid phone format in %s: %s') % (field_name.replace('_', ' ').title(), phone)
                    )

    # ==========================================
    # Actions & Smart Buttons
    # ==========================================
    def action_view_helpdesk_tickets(self):
        """Open helpdesk tickets for this tenant"""
        self.ensure_one()
        return {
            'name': _('Helpdesk Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'default_partner_name': self.name,
                'default_partner_email': self.email or self.email_primary,
                'default_partner_phone': self.phone or self.phone_primary,
            },
        }
    
    def action_view_tickets(self):
        """View tickets for this partner - compatibility method"""
        return {
            'name': f'Tickets - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id}
        }

    def action_create_ticket(self):
        """Quick action to create a ticket for this tenant"""
        self.ensure_one()
        return {
            'name': _('Create Ticket'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.id,
                'default_partner_name': self.name,
                'default_partner_email': self.email or self.email_primary,
                'default_partner_phone': self.phone or self.phone_primary,
            },
            'target': 'current',
        }

    # ==========================================
    # CRUD Overrides
    # ==========================================
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to sync primary email/phone with standard fields"""
        for vals in vals_list:
            if vals.get('is_tenant'):
                # Sync primary contact info with standard Odoo fields
                if vals.get('email_primary') and not vals.get('email'):
                    vals['email'] = vals['email_primary']
                if vals.get('phone_primary') and not vals.get('phone'):
                    vals['phone'] = vals['phone_primary']
                    
        return super().create(vals_list)

    def write(self, vals):
        """Override write to sync primary email/phone with standard fields"""
        if vals.get('email_primary'):
            vals['email'] = vals['email_primary']
        if vals.get('phone_primary'):
            vals['phone'] = vals['phone_primary']
            
        return super().write(vals)

    # ==========================================
    # Display Name
    # ==========================================
    def name_get(self):
        """Custom display name for tenants"""
        result = []
        for record in self:
            if record.is_tenant:
                name_parts = []
                if record.brand_name:
                    name_parts.append(record.brand_name)
                elif record.company_registered_name:
                    name_parts.append(record.company_registered_name)
                else:
                    name_parts.append(record.name or '')
                    
                if record.unit_number:
                    name_parts.append(f"[Unit: {record.unit_number}]")
                    
                if record.site_code:
                    name_parts.append(f"({dict(record._fields['site_code'].selection).get(record.site_code, '')})")
                    
                display_name = ' '.join(name_parts)
            else:
                display_name = record.name or ''
                
            result.append((record.id, display_name))
        return result
