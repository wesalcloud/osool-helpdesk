# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Helpdesk Ticket Category'
    _order = 'sequence, name'
    
    name = fields.Char(string='Category Name', required=True, translate=True)
    code = fields.Char(string='Category Code', required=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Form Type mapping
    form_type = fields.Selection([
        ('complaint', 'Complaint'),
        ('marketing', 'Marketing'),
        ('security', 'Security'),
        ('vvip_lift', 'VVIP Lift Booking'),
        ('regular_lift', 'Regular Lift Booking'),
        ('procurement', 'Procurement'),
        ('hr', 'Human Resources'),
        ('announcement', 'Announcement'),
        ('maximo', 'Maximo'),
    ], string='Related Form Type', help='Form type that will be automatically set when this category is selected')
    
    # Default Team assignment
    team_id = fields.Many2one('helpdesk.team', string='Default Team')
    
    # Department assignment
    team_department_id = fields.Many2one('helpdesk.team.department', string='Department', help='Department that will be automatically assigned when this category is selected')
    
    # Default Ticket Owner
    ticket_owner_id = fields.Many2one('res.users', string='Default Ticket Owner', help='Default owner for tickets in this category')
    
    # Subcategories
    subcategory_ids = fields.One2many('helpdesk.subcategory', 'category_id', string='Subcategories')
    
    # Statistics
    ticket_count = fields.Integer(string='Ticket Count', compute='_compute_ticket_count')
    
    def _compute_ticket_count(self):
        for category in self:
            category.ticket_count = self.env['helpdesk.ticket'].search_count([
                ('request_category_id', '=', category.id)
            ])
