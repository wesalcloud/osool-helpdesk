# -*- coding: utf-8 -*-
{
    'name': 'Osool Helpdesk',
    'version': '19.0.1.0.3',
    'category': 'Services/Helpdesk',
    'summary': 'Custom Enterprise Helpdesk Extension for Case Management',
    'description': """
        Osool Helpdesk - Custom Enterprise Helpdesk Extension
        ======================================================
        
        Extends Odoo Enterprise Helpdesk module with:
        - Multiple Case Management Forms (Complaint, Marketing, Procurement, HR, Security, Announcement, Maximo, VVIP & Regular Lift Booking)
        - Category-based routing rules with auto-assignment
        - SLA management with response and resolution times
        - Self-service portal for tenants, employees, and customers
        - Caller source tracking (Voice, Email, WhatsApp, Chat, Walk-in, Self-service)
        - Custom ticket statuses (New, Assigned, In Progress, Resolved, Rejected, Pending Internal, Pending Customer, Closed, Cancelled)
        - Automated notifications via email and WhatsApp
        - Feedback surveys after ticket resolution
        - Full audit trail for ticket changes
        - Work instructions for each category
    """,
    'author': 'Osool',
    'website': 'https://www.osool.com',
    'license': 'LGPL-3',
    'depends': [
        'helpdesk',
        'mail',
        'portal',
        'website',
        'survey',
        'base_automation',
        'hr',
    ],
    'data': [
        # Security
        'security/osool_helpdesk_security.xml',
        'security/ir.model.access.csv',
        
        # Data
        # 'data/helpdesk_stage_data.xml',
        'data/helpdesk_site_data.xml',
        'data/helpdesk_category_data.xml',
        'data/helpdesk_team_data.xml',
        'data/helpdesk_subcategory_data.xml',
        'data/website_page_security.xml',
        
        # 'data/helpdesk_sla_data.xml',  # TODO: Fix SLA data
        # 'data/mail_template_data.xml',  # TODO: Fix template data
        # 'data/survey_data.xml',  # TODO: Fix survey data
        # 'data/automation_data.xml',  # TODO: Fix automation data
        
        # Views
        'views/res_partner_tenant_views.xml',
        'views/helpdesk_site_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_category_views.xml',
        'views/helpdesk_subcategory_views.xml',
        'views/helpdesk_team_department_views.xml',
        'views/helpdesk_department_dashboard_views.xml',
        'views/helpdesk_team_views.xml',
        # 'views/helpdesk_sla_views.xml',  # TODO: Fix view inheritance
        'views/helpdesk_audit_views.xml',
        'views/helpdesk_dashboard_views.xml',
        'views/helpdesk_menu.xml',
        'views/res_config_settings_views.xml',
        
        # Portal
        'views/portal_templates.xml',
        'views/portal_helpdesk_ticket.xml',
        
        # Wizard
        # 'wizard/ticket_escalation_wizard_views.xml',  # TODO: Fix wizard views
    ],
    'assets': {
        'web.assets_backend': [
            'osool_helpdesk/static/src/js/helpdesk_dashboard.js',
            'osool_helpdesk/static/src/js/ticket_form_tabs.js',
        ],
        'web.assets_frontend': [
        ],
    },
 
    'installable': True,
    'application': True,
    'auto_install': False,
}
