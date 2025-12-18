# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    _order = 'id desc'
    
    # Caller Information
    interaction_mode = fields.Selection([
        ('internal', 'Internal'),
        ('osool_care', 'Osool Care'),
        ('customer', 'Customer'),
    ], string='Interaction Mode', tracking=True)
    
    caller_source = fields.Selection([
        ('voice', 'Voice Call'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('chat', 'Chat'),
        ('walkin', 'Walk-in'),
        ('selfservice', 'Self-service'),
    ], string='Channel', required=True, default='selfservice', tracking=True)
    
    ticket_phone = fields.Char(string='Ticket Phone', tracking=True)
    ticket_email = fields.Char(string='Ticket Email', tracking=True)
    email_content = fields.Html(string='Email Content', tracking=True, help='Email content received from customer')
    
    # Ticket Owner - User matching agent_email or ticket creator
    ticket_owner_id = fields.Many2one('res.users', string='Original Ticket Owner', tracking=True)
    
     
    # Team Department
    team_department_id = fields.Many2one('helpdesk.team.department', string='Assigned To', tracking=True)
    department_notified = fields.Boolean(string='Department Notified', default=False, tracking=True)
    
    # Site
    site_id = fields.Many2one('helpdesk.site', string='Site', tracking=True)
    
    # Dashboard Analytics Fields
    assign_date = fields.Datetime(string='First Assignment Date', tracking=True, help='Date when ticket was first assigned')
    close_date = fields.Datetime(string='Auto Close Date', compute='_compute_close_date', store=True, help='Date when ticket was closed (computed)')
    response_time_hours = fields.Float(string='Response Time (Hours)', compute='_compute_response_time', store=True, help='Time from creation to assignment in hours')
    resolution_time_hours = fields.Float(string='Resolution Time (Hours)', compute='_compute_resolution_time', store=True, help='Time from creation to closure in hours')
    
    # Rejection tracking
    reject_by = fields.Many2one('res.users', string='Rejected By', tracking=True)
    
    # Computed stage status fields for view conditions
    is_stage_new = fields.Boolean(string='Is New Stage', compute='_compute_stage_status', store=False)
    is_stage_assigned = fields.Boolean(string='Is Assigned Stage', compute='_compute_stage_status', store=False)
    is_stage_in_progress = fields.Boolean(string='Is In Progress Stage', compute='_compute_stage_status', store=False)
    
    # Genesys Integration Fields
    conversation_type = fields.Char(string='Conversation Type', readonly=True, tracking=True)
    conversation_id = fields.Char(string='Conversation ID', readonly=True, tracking=True)
    queue_name = fields.Char(string='Queue Name', readonly=True, tracking=True)
    agent_email = fields.Char(string='Agent Email', readonly=True, tracking=True)
    agent_name = fields.Char(string='Agent Name', readonly=True, tracking=True)
    source = fields.Char(string='Source', tracking=True)
    created_via = fields.Char(string='Created Via', compute='_compute_created_via', store=True)
    
    # Categories
    request_category_id = fields.Many2one('helpdesk.category', string='Category', tracking=True)
    request_subcategory_id = fields.Many2one('helpdesk.subcategory', string='Subcategory', tracking=True)
    
    @api.onchange('request_category_id')
    def _onchange_request_category_id(self):
        """Auto-set form_type based on category selection"""
        if self.request_category_id and self.request_category_id.form_type:
            self.form_type = self.request_category_id.form_type
        # Clear subcategory when category changes
        self.request_subcategory_id = False
    
    @api.onchange('site_id')
    def _onchange_site_id(self):
        """Clear department if site changes and department doesn't belong to new site"""
        if self.site_id and self.team_department_id:
            if self.team_department_id.site_id != self.site_id:
                self.team_department_id = False
    
    # Caller Information
    
    # Form Type
    form_type = fields.Selection([
        ('complaint', 'Complaint'),
        ('marketing', 'Marketing'),
        ('security', 'Security'),
        ('vvip_lift', 'VVIP Lift Booking'),
        ('regular_lift', 'Regular Lift Booking'),
        ('procurement', 'Procurement'),
        ('hr', 'HR'),
        ('announcement', 'Announcement'),
        ('maximo', 'Maximo'),
    ], string='Form Type', required=True, default='complaint', tracking=True)
    
    # Complaint specific fields
    complaint_type = fields.Selection([
        ('service', 'Service Issue'),
        ('product', 'Product Issue'),
        ('billing', 'Billing Issue'),
        ('staff', 'Staff Behavior'),
        ('other', 'Other'),
    ], string='Complaint Type', tracking=True)
    
    complaint_severity = fields.Selection([
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ], string='Severity', tracking=True)
    
    # Marketing specific fields
    marketing_campaign = fields.Char(string='Campaign Name', tracking=True)
    marketing_budget = fields.Float(string='Budget', tracking=True)
    marketing_start_date = fields.Date(string='Campaign Start Date', tracking=True)
    marketing_end_date = fields.Date(string='Campaign End Date', tracking=True)
    
    # Security specific fields
    security_incident_type = fields.Selection([
        ('access', 'Unauthorized Access'),
        ('theft', 'Theft'),
        ('vandalism', 'Vandalism'),
        ('threat', 'Security Threat'),
        ('other', 'Other'),
    ], string='Incident Type', tracking=True)
    
    security_location = fields.Char(string='Incident Location', tracking=True)
    security_witness = fields.Char(string='Witness Name', tracking=True)
    
    # Lift Booking specific fields
    lift_booking_date = fields.Datetime(string='Booking Date/Time', tracking=True)
    lift_size = fields.Selection([
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    ], string='Lift Size', tracking=True)
    
    lift_floor_from = fields.Char(string='From Floor', tracking=True)
    lift_floor_to = fields.Char(string='To Floor', tracking=True)
    lift_items_description = fields.Text(string='Items Description', tracking=True)
    
    # Procurement specific fields
    procurement_item = fields.Char(string='Item/Service', tracking=True)
    procurement_quantity = fields.Float(string='Quantity', tracking=True)
    procurement_budget = fields.Float(string='Estimated Budget', tracking=True)
    procurement_required_date = fields.Date(string='Required By', tracking=True)
    procurement_vendor = fields.Many2one('res.partner', string='Preferred Vendor', tracking=True)
    
    # HR specific fields
    hr_request_type = fields.Selection([
        ('leave', 'Leave Request'),
        ('recruitment', 'Recruitment'),
        ('training', 'Training'),
        ('payroll', 'Payroll Issue'),
        ('other', 'Other'),
    ], string='HR Request Type', tracking=True)
    
    hr_employee_id = fields.Many2one('res.users', string='Related Employee', tracking=True)
    hr_department = fields.Char(string='Department', tracking=True)
    
    # Announcement specific fields
    announcement_title = fields.Char(string='Announcement Title', tracking=True)
    announcement_content = fields.Html(string='Announcement Content', tracking=True)
    announcement_target_audience = fields.Selection([
        ('all', 'All'),
        ('employees', 'Employees Only'),
        ('tenants', 'Tenants Only'),
        ('vvip', 'VVIP Only'),
    ], string='Target Audience', tracking=True)
    
    announcement_publish_date = fields.Datetime(string='Publish Date', tracking=True)
    announcement_expiry_date = fields.Datetime(string='Expiry Date', tracking=True)
    
    # Maximo specific fields
    maximo_work_order = fields.Char(string='Maximo Work Order #', tracking=True)
    maximo_asset_id = fields.Char(string='Asset ID', tracking=True)
    maximo_location = fields.Char(string='Location', tracking=True)
    maximo_priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], string='Maximo Priority', tracking=True)
    
    # Extended Status
    status = fields.Selection([
        ('new', 'New'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('pending_internal', 'Pending Internal'),
        ('pending_customer', 'Pending Customer'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='new', required=True, tracking=True)
    
    # SLA Fields
    sla_id = fields.Many2one('helpdesk.sla', string='SLA Policy', tracking=True)
    sla_deadline = fields.Datetime(string='SLA Deadline', tracking=True)
    sla_failed = fields.Boolean(string='SLA Failed', compute='_compute_sla_failed', store=True)
    response_deadline = fields.Datetime(string='Response Deadline', tracking=True)
    resolution_deadline = fields.Datetime(string='Resolution Deadline', tracking=True)
    
    # Timestamps
    date_last_stage_update = fields.Datetime(string='Last Stage Update', readonly=True)
    date_assigned = fields.Datetime(string='Assignment Date', readonly=True, tracking=True)
    date_resolved = fields.Datetime(string='Resolution Date', readonly=True, tracking=True)
    date_closed = fields.Datetime(string='Closure Date', readonly=True, tracking=True)
    
    # Work Instructions
    work_instructions = fields.Html(string='Work Instructions', related='request_subcategory_id.work_instructions', readonly=True)
    
    # Internal Notes
    internal_notes = fields.Html(string='Internal Notes')
    resolution_notes = fields.Html(string='Resolution Notes', tracking=True)
    
    # Escalation
    escalated = fields.Boolean(string='Escalated', default=False, tracking=True)
    escalation_date = fields.Datetime(string='Escalation Date', tracking=True)
    escalation_reason = fields.Text(string='Escalation Reason', tracking=True)
    escalated_to_id = fields.Many2one('res.users', string='Escalated To', tracking=True)
    
    # Survey
    survey_id = fields.Many2one('survey.survey', string='Feedback Survey')
    survey_sent = fields.Boolean(string='Survey Sent', default=False, tracking=True)
    survey_completed = fields.Boolean(string='Survey Completed', default=False, tracking=True)
    survey_response_id = fields.Many2one('survey.user_input', string='Survey Response', tracking=True)
    
    # Audit Trail
    audit_log_ids = fields.One2many('helpdesk.audit', 'ticket_id', string='Audit Trail')
    
    # Access Control
    is_internal_request = fields.Boolean(string='Internal Request', default=False, tracking=True)
    is_external_request = fields.Boolean(string='External Request', default=True, tracking=True)
    requester_type = fields.Selection([
        ('employee', 'Osool Employee'),
        ('tenant', 'Osool Tenant'),
        ('vvip_tenant', 'Osool VVIP Tenant'),
        ('customer', 'External Customer'),
    ], string='Requester Type', tracking=True)
    
    # Computed fields
    days_open = fields.Integer(string='Days Open', compute='_compute_days_open', store=False)
    
    is_partner_tenant = fields.Boolean(
        string='Is Tenant',
        compute='_compute_is_partner_tenant',
        store=False,
        help='Check if the partner is a tenant'
    )
    
    # Related Tenant Fields (for display in Tenant Details tab)
    tenant_brand_name = fields.Char(related='partner_id.brand_name', string='Brand Name', readonly=True)
    tenant_site = fields.Many2one(related='partner_id.site', string='Tenant Site', readonly=True)
    tenant_building_name = fields.Char(related='partner_id.building_name', string='Building', readonly=True)
    tenant_unit_number = fields.Char(related='partner_id.unit_number', string='Unit Number', readonly=True)
    tenant_floor_number = fields.Char(related='partner_id.floor_number', string='Floor', readonly=True)
    tenant_vip_status = fields.Selection(related='partner_id.vip_status', string='VIP Status', readonly=True)
    tenant_status = fields.Selection(related='partner_id.tenant_status', string='Tenant Status', readonly=True)
    tenant_type = fields.Selection(related='partner_id.tenant_type', string='Tenant Type', readonly=True)
    tenant_business_category = fields.Selection(related='partner_id.business_category', string='Business Category', readonly=True)
    tenant_phone_primary = fields.Char(related='partner_id.phone_primary', string='Primary Phone', readonly=True)
    tenant_phone_secondary = fields.Char(related='partner_id.phone_secondary', string='Secondary Phone', readonly=True)
    tenant_email_primary = fields.Char(related='partner_id.email_primary', string='Primary Email', readonly=True)
    tenant_email_secondary = fields.Char(related='partner_id.email_secondary', string='Secondary Email', readonly=True)
    tenant_contract_number = fields.Char(related='partner_id.contract_number', string='Contract Number', readonly=True)
    tenant_contract_start_date = fields.Date(related='partner_id.contract_start_date', string='Contract Start', readonly=True)
    tenant_contract_end_date = fields.Date(related='partner_id.contract_end_date', string='Contract End', readonly=True)
    tenant_contract_active = fields.Boolean(related='partner_id.contract_active', string='Contract Active', readonly=True)
    
    @api.depends('partner_id', 'partner_id.is_tenant')
    def _compute_is_partner_tenant(self):
        """Check if the ticket partner is a tenant"""
        for ticket in self:
            ticket.is_partner_tenant = ticket.partner_id and ticket.partner_id.is_tenant
    
    @api.depends('source', 'create_uid')
    def _compute_created_via(self):
        """Compute the Created Via field based on source"""
        for ticket in self:
            if ticket.source and ticket.source.lower() == 'genesys':
                ticket.created_via = 'Genesys Cloud'
            else:
                user_name = ticket.create_uid.name if ticket.create_uid else 'Unknown'
                ticket.created_via = f'User: {user_name}'
    
    @api.depends('stage_id', 'stage_id.is_new', 'stage_id.is_assigned', 'stage_id.is_in_progress')
    def _compute_stage_status(self):
        """Compute stage status boolean fields for view conditions"""
        for ticket in self:
            ticket.is_stage_new = ticket.stage_id.is_new if ticket.stage_id else False
            ticket.is_stage_assigned = ticket.stage_id.is_assigned if ticket.stage_id else False
            ticket.is_stage_in_progress = ticket.stage_id.is_in_progress if ticket.stage_id else False
    
    @api.depends('stage_id', 'stage_id.fold')
    def _compute_close_date(self):
        """Compute close date when ticket reaches a closed/folded stage"""
        for ticket in self:
            if ticket.stage_id and ticket.stage_id.fold:
                if not ticket.close_date:
                    ticket.close_date = fields.Datetime.now()
            else:
                ticket.close_date = False
    
    @api.depends('create_date', 'assign_date')
    def _compute_response_time(self):
        """Compute response time in hours (create to assign)"""
        for ticket in self:
            if ticket.create_date and ticket.assign_date:
                delta = ticket.assign_date - ticket.create_date
                ticket.response_time_hours = delta.total_seconds() / 3600.0
            else:
                ticket.response_time_hours = 0.0
    
    @api.depends('create_date', 'close_date')
    def _compute_resolution_time(self):
        """Compute resolution time in hours (create to close)"""
        for ticket in self:
            if ticket.create_date and ticket.close_date:
                delta = ticket.close_date - ticket.create_date
                ticket.resolution_time_hours = delta.total_seconds() / 3600.0
            else:
                ticket.resolution_time_hours = 0.0
    
    @api.depends('create_date')
    def _compute_days_open(self):
        for ticket in self:
            if ticket.create_date:
                if ticket.status in ['closed', 'cancelled']:
                    if ticket.date_closed:
                        delta = ticket.date_closed - ticket.create_date
                        ticket.days_open = delta.days
                    else:
                        ticket.days_open = 0
                else:
                    delta = fields.Datetime.now() - ticket.create_date
                    ticket.days_open = delta.days
            else:
                ticket.days_open = 0
    
    @api.depends('sla_deadline')
    def _compute_sla_failed(self):
        now = fields.Datetime.now()
        for ticket in self:
            if ticket.sla_deadline:
                ticket.sla_failed = now > ticket.sla_deadline and ticket.status not in ['closed', 'resolved']
            else:
                ticket.sla_failed = False
    
    @api.onchange('request_category_id')
    def _onchange_category(self):
        if self.request_category_id:
            self.request_subcategory_id = False
            # Auto-assign team based on category
            if self.request_category_id.team_id:
                self.team_id = self.request_category_id.team_id
    
    @api.onchange('request_subcategory_id')
    def _onchange_subcategory(self):
        if self.request_subcategory_id:
            # Auto-assign based on routing rules
            if self.request_subcategory_id.auto_assign_user_id:
                self.user_id = self.request_subcategory_id.auto_assign_user_id
            if self.request_subcategory_id.team_id:
                self.team_id = self.request_subcategory_id.team_id
            
            # Set ticket owner from subcategory or category
            if self.request_subcategory_id.ticket_owner_id:
                self.ticket_owner_id = self.request_subcategory_id.ticket_owner_id
            elif self.request_category_id and self.request_category_id.ticket_owner_id:
                self.ticket_owner_id = self.request_category_id.ticket_owner_id
            
            # Set SLA
            if self.request_subcategory_id.sla_id:
                self.sla_id = self.request_subcategory_id.sla_id
                self._compute_sla_deadlines()
    
    def _compute_sla_deadlines(self):
        for ticket in self:
            if ticket.sla_id:
                now = fields.Datetime.now()
                if ticket.sla_id.response_time:
                    ticket.response_deadline = now + timedelta(minutes=ticket.sla_id.response_time)
                if ticket.sla_id.resolution_time:
                    ticket.resolution_deadline = now + timedelta(minutes=ticket.sla_id.resolution_time)
                    ticket.sla_deadline = ticket.resolution_deadline
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            
            # Decode URL-encoded email content if present and clean formatting
            if vals.get('email_content'):
                import urllib.parse
                import re
                # Decode URL encoding
                content = urllib.parse.unquote(vals['email_content'])
                # Remove quotation marks, asterisks, and special formatting characters
                content = content.replace('"', '').replace('*', '').replace('_', '').replace('~', '')
                content = content.replace('`', '').replace('=', '').replace('+', '').replace('-', '')
                # Convert line breaks to HTML
                content = content.replace('\r\n', '<br/>').replace('\n', '<br/>')
                vals['email_content'] = content
            
            # Persist form_type from selected category if provided (server-side, works for portal and backend)
            cat_id = vals.get('request_category_id')
            if cat_id and not vals.get('form_type'):
                cat = self.env['helpdesk.category'].browse(cat_id)
                if cat.exists() and cat.form_type:
                    vals['form_type'] = cat.form_type

            if vals.get('partner_id') and not vals.get('partner_name'):
                partner = self.env['res.partner'].browse(vals['partner_id'])
                vals.update({
                    'partner_name': partner.name if partner.name else '',
                    'partner_email': partner.email if partner.email else '',
                    'partner_phone': partner.phone if partner.phone else '',
                })
            
            # Handle Public user (no partner_id) - get from portal user
            if not vals.get('partner_id') and not vals.get('partner_name'):
                current_user = self.env.user
                if current_user.partner_id:
                    vals.update({
                        'partner_id': current_user.partner_id.id,
                        'partner_name': current_user.partner_id.name if current_user.partner_id.name else current_user.name,
                        'partner_email': current_user.partner_id.email if current_user.partner_id.email else current_user.email,
                        'partner_phone': current_user.partner_id.phone if current_user.partner_id.phone else '',
                    })
            
            vals['date_last_stage_update'] = fields.Datetime.now()
        
        tickets = super(HelpdeskTicket, self).create(vals_list)
        
        # Send notification email and log audit for each ticket
        for ticket in tickets:
            # Auto-assign user_id (Ticket Owner) based on agent_email or creator
            assigned_user = None
            
            # If agent_email is provided, find user with matching email
            if ticket.agent_email:
                agent_email_clean = ticket.agent_email.strip().lower()
                assigned_user = self.env['res.users'].sudo().search([('login', '=', agent_email_clean)], limit=1)
                if not assigned_user:
                    assigned_user = self.env['res.users'].sudo().search([('email', '=', agent_email_clean)], limit=1)
            
            # If no agent_email or no matching user found, assign to creator
            if not assigned_user:
                assigned_user = ticket.create_uid
            
            # Set user_id (Ticket Owner) and ticket_owner_id
            if assigned_user:
                self.env.cr.execute(
                    "UPDATE helpdesk_ticket SET user_id=%s WHERE id=%s",
                    (assigned_user.id, ticket.id)
                )
                ticket.invalidate_recordset(['user_id'])
                ticket.ticket_owner_id = assigned_user
                
            ticket._send_ticket_notification()
            ticket._log_audit_trail('create', 'Ticket created')
        
        return tickets
    
    def write(self, vals):
        # Track first assignment date
        if 'user_id' in vals and vals.get('user_id'):
            for ticket in self:
                if not ticket.assign_date:
                    vals['assign_date'] = fields.Datetime.now()
        
        # Check write access: Only ticket owner can modify (except managers/team leaders)
        current_user = self.env.user
        is_manager = current_user.has_group('osool_helpdesk.group_helpdesk_manager')
        is_team_leader = current_user.has_group('osool_helpdesk.group_helpdesk_team_leader')
        
        # Allow managers and team leaders to edit any ticket
        if not is_manager and not is_team_leader:
            for ticket in self:
                # Only the ticket owner (user_id) can edit
                if ticket.user_id and ticket.user_id != current_user:
                    raise UserError(_('Only the Ticket Owner can modify this ticket.'))
        
        # If category changes, align form_type accordingly to keep correct tab after save
        if 'request_category_id' in vals:
            cat_id = vals.get('request_category_id')
            if cat_id:
                cat = self.env['helpdesk.category'].browse(cat_id)
                if cat.exists() and cat.form_type:
                    # Align form_type to the category consistently when category changes
                    vals['form_type'] = cat.form_type

        # Check if stage is being changed
        stage_is_rejected = False
        stage_is_assigned = False
        
        if vals.get('stage_id'):
            stage = self.env['helpdesk.stage'].browse(vals['stage_id'])
            if stage.exists():
                # Check if moving to assigned stage
                if stage.is_assigned:
                    stage_is_assigned = True
                    # Validate department is selected before moving to assigned
                    for ticket in self:
                        if not ticket.team_department_id and not vals.get('team_department_id'):
                            raise UserError(_('Please select a Department before assigning the ticket.'))
                
                # Check if rejected
                try:
                    if stage.is_rejected:
                        stage_is_rejected = True
                        vals['status'] = 'rejected'
                except AttributeError:
                    if stage.name and stage.name.lower() == 'rejected':
                        stage_is_rejected = True
                        vals['status'] = 'rejected'
        
        if vals.get('status') == 'rejected':
            stage_is_rejected = True
        
        # Track status changes
        if 'status' in vals or 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.Datetime.now()
            
            if vals.get('status') == 'assigned' and not self.date_assigned:
                vals['date_assigned'] = fields.Datetime.now()
            elif vals.get('status') == 'resolved' and not self.date_resolved:
                vals['date_resolved'] = fields.Datetime.now()
            elif vals.get('status') == 'closed' and not self.date_closed:
                vals['date_closed'] = fields.Datetime.now()
        
        # Log audit trail - store old values before write
        old_values = {}
        for ticket in self:
            old_values[ticket.id] = {}
            for field in vals.keys():
                if field in ticket._fields:
                    field_value = ticket[field]
                    # Convert Many2one records to IDs for comparison
                    if hasattr(field_value, 'id'):
                        old_values[ticket.id][field] = field_value.id
                    else:
                        old_values[ticket.id][field] = field_value
        
        result = super(HelpdeskTicket, self).write(vals)
        
        # Auto-assign to ticket owner if ticket is rejected
        if stage_is_rejected:
            for ticket in self:
                # Store who rejected the ticket
                if not ticket.reject_by:
                    ticket.reject_by = self.env.user
                
                # Reassign to original ticket owner if currently assigned to someone else
                if ticket.ticket_owner_id and ticket.user_id != ticket.ticket_owner_id:
                    ticket.user_id = ticket.ticket_owner_id
        
        # Call update_form_state when stage changes
        if 'stage_id' in vals:
            for ticket in self:
                ticket.update_form_state()
        
        # Create audit log
        for ticket in self:
            for field, new_value in vals.items():
                if field in old_values.get(ticket.id, {}):
                    old_val = old_values[ticket.id][field]
                    if old_val != new_value:
                        ticket._log_audit_trail('write', f'Updated {field}', old_val, new_value)
        
        return result
    
    def update_form_state(self):
        """
        Called when stage changes to perform stage-specific actions
        This method can be extended to add custom logic for different stages
        """
        self.ensure_one()
        
        # Actions when moving to New stage
        if self.is_stage_new:
            self._log_audit_trail('stage_change', f'Ticket moved to New stage')
        
        # Actions when moving to Assigned stage
        elif self.is_stage_assigned:
            # Ensure department is set
            if not self.team_department_id:
                raise UserError(_('Department must be selected when moving to Assigned stage.'))
            
            # Log the assignment
            self._log_audit_trail('stage_change', f'Ticket assigned to department: {self.team_department_id.name}')
            
            # Set assignment date if not already set
            if not self.date_assigned:
                self.date_assigned = fields.Datetime.now()
        
        # Actions when moving to In Progress stage
        elif self.is_stage_in_progress:
            self._log_audit_trail('stage_change', f'Ticket moved to In Progress')
            
            # Update status if needed
            if self.status != 'in_progress':
                self.status = 'in_progress'
        
        # Actions when moving to Resolved stage
        elif self.stage_id.is_resolved:
            if not self.date_resolved:
                self.date_resolved = fields.Datetime.now()
            self._log_audit_trail('stage_change', f'Ticket resolved')
        
        # Actions when moving to Closed stage
        elif self.stage_id.is_closed:
            if not self.date_closed:
                self.date_closed = fields.Datetime.now()
            
            # Send satisfaction survey if not already sent
            if not self.survey_sent:
                self._send_survey()
            
            self._log_audit_trail('stage_change', f'Ticket closed')
    
    def _send_ticket_notification(self):
        """Send email notification when ticket is created"""
        self.ensure_one()
        template = self.env.ref('osool_helpdesk.mail_template_ticket_created', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=False)
    
    def _log_audit_trail(self, action, description, old_value=None, new_value=None):
        """Create audit trail record"""
        self.ensure_one()
        self.env['helpdesk.audit'].create({
            'ticket_id': self.id,
            'user_id': self.env.user.id,
            'action': action,
            'description': description,
            'old_value': str(old_value) if old_value else False,
            'new_value': str(new_value) if new_value else False,
            'timestamp': fields.Datetime.now(),
        })
    
    def action_escalate(self):
        """Open escalation wizard"""
        return {
            'name': _('Escalate Ticket'),
            'type': 'ir.actions.act_window',
            'res_model': 'ticket.escalation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_ticket_id': self.id},
        }
    
    def action_reopen(self):
        """Reopen closed ticket"""
        self.ensure_one()
        self.write({
            'status': 'in_progress',
        })
        self._log_audit_trail('reopen', 'Ticket reopened')
        return True
    
    def action_close(self):
        """Close ticket"""
        self.ensure_one()
        if self.status != 'resolved':
            raise UserError(_('Ticket must be resolved before closing.'))
        
        self.write({
            'status': 'closed',
            'date_closed': fields.Datetime.now(),
        })
        self._log_audit_trail('close', 'Ticket closed')
        
        # Send satisfaction survey
        if not self.survey_sent:
            self._send_survey()
        
        return True
    
    def action_start_work(self):
        """Start working on assigned ticket"""
        self.ensure_one()
        if not self.is_stage_assigned:
            raise UserError(_('This action is only available for assigned tickets.'))
        
        self.write({
            'status': 'in_progress',
        })
        self._log_audit_trail('start_work', 'Started working on ticket')
        return True
    
    def action_request_info(self):
        """Request more information from customer"""
        self.ensure_one()
        if not self.is_stage_assigned:
            raise UserError(_('This action is only available for assigned tickets.'))
        
        # This would typically open a composer to send an email
        return {
            'type': 'ir.actions.act_window',
            'name': _('Request Information'),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_model': 'helpdesk.ticket',
                'default_res_ids': self.ids,
                'default_template_id': self.env.ref('osool_helpdesk.mail_template_request_info', raise_if_not_found=False).id if self.env.ref('osool_helpdesk.mail_template_request_info', raise_if_not_found=False) else False,
            }
        }
    
    def action_send_team_department_notification(self):
        """Send email notification to all teams under the selected department"""
        self.ensure_one()
        
        if self.department_notified:
            raise UserError(_('Notification has already been sent for this ticket.'))
        
        if not self.team_department_id:
            raise UserError(_('No department assigned to this ticket.'))
        
        # Get all teams that belong to this department
        teams = self.env['helpdesk.team'].search([('team_department_id', '=', self.team_department_id.id)])
        
        if not teams:
            raise UserError(_('No teams found under department: %s') % self.team_department_id.name)
        
        # Collect notification emails from all teams in this department
        notification_emails = self.env['helpdesk.team.notified.email']
        for team in teams:
            notification_emails |= team.notified_email_ids.filtered(lambda e: e.active and e.email)
        
        if not notification_emails:
            raise UserError(_('No notification emails configured for teams under department: %s') % self.team_department_id.name)
        
        # Prepare email body
        body = _('''
            <div style="font-family: Arial, sans-serif; font-size: 14px;">
                <h3 style="color: #875A7B;">Ticket Assigned to: %s</h3>
                <table style="width: 100%%; border-collapse: collapse; margin-top: 20px;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold; width: 30%%;">Ticket Number:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Subject:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Priority:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Customer:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Department:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Ticket Owner:</td>
                        <td style="padding: 8px; border: 1px solid #ddd;">%s</td>
                    </tr>
                </table>
                <p style="margin-top: 20px;">
                    <a href="/web#id=%s&model=helpdesk.ticket&view_type=form" 
                       style="background-color: #875A7B; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                        View Ticket
                    </a>
                </p>
            </div>
        ''') % (
            self.team_department_id.name if self.team_department_id else 'N/A',
            self.display_name or str(self.id),
            self.name or 'N/A',
            dict(self._fields['priority'].selection).get(self.priority, 'N/A'),
            self.partner_id.name if self.partner_id else 'N/A',
            self.team_department_id.name if self.team_department_id else 'N/A',
            self.user_id.name if self.user_id else 'Unassigned',
            self.id
        )
        
        # Send email to each notification address
        mail_values_list = []
        for notif_email in notification_emails:
            mail_values = {
                'subject': _('Ticket %s - Assigned to %s') % (self.display_name or str(self.id), self.team_department_id.name if self.team_department_id else 'Department'),
                'body_html': body,
                'email_to': notif_email.email,
                'email_from': self.env.user.email or self.env.company.email or 'noreply@example.com',
                'auto_delete': False,
                'model': 'helpdesk.ticket',
                'res_id': self.id,
            }
            mail_values_list.append(mail_values)
        
        # Create and send emails
        if mail_values_list:
            mail_ids = self.env['mail.mail'].sudo().create(mail_values_list)
            mail_ids.send()
        
        # Mark as notified
        self.department_notified = True
        
        # Log audit trail
        email_list = ', '.join(notification_emails.mapped('email'))
        self._log_audit_trail('notification', 'Email notification sent to: %s' % email_list)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Notification Sent'),
                'message': _('Email notification sent to %s recipient(s).') % len(notification_emails),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _send_survey(self):
        """Send satisfaction survey to customer"""
        self.ensure_one()
        survey = self.env.ref('osool_helpdesk.ticket_satisfaction_survey', raise_if_not_found=False)
        if survey and self.partner_id:
            survey._create_answer(partner=self.partner_id)
            self.write({'survey_sent': True, 'survey_id': survey.id})

    def action_open_tenant_profile(self):
        """Open the full Tenant (res.partner) profile of the ticket's partner.
        If partner is a contact, open the parent company (tenant).
        This avoids relying on XMLID resolution during XML parsing time.
        """
        self.ensure_one()
        if not self.partner_id:
            raise UserError(_('No customer is linked to this ticket.'))

        # If partner is a contact (has parent), open the parent (tenant)
        # Otherwise, open the partner itself (which is the tenant/company)
        tenant_id = self.partner_id.parent_id.id if self.partner_id.parent_id else self.partner_id.id
        tenant_name = self.partner_id.parent_id.name if self.partner_id.parent_id else self.partner_id.name

        return {
            'type': 'ir.actions.act_window',
            'name': _('Tenant: %s') % tenant_name,
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': tenant_id,
            'target': 'current',
            'context': {
                'default_is_tenant': True,
            },
        }
    
    def action_open_genesys_conversation(self):
        """Open Genesys conversation details in browser"""
        self.ensure_one()
        if not self.conversation_id:
            raise UserError(_('No Genesys conversation ID available.'))
        
        # Get Genesys environment from system parameters
        genesys_env = self.env['ir.config_parameter'].sudo().get_param('helpdesk.genesys_environment', 'mypurecloud.com')
        
        # Build URL
        url = f'https://apps.{genesys_env}/directory/#/analytics/interactions/{self.conversation_id}'
        
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }
