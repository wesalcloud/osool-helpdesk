# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    genesys_environment = fields.Char(
        string='Genesys Environment',
        config_parameter='helpdesk.genesys_environment',
        default='mypurecloud.com',
        help='Genesys Cloud environment domain (e.g., mypurecloud.com, mypurecloud.ie, mypurecloud.de)'
    )
    
    # Microsoft Graph API Configuration
    ms_graph_tenant_id = fields.Char(
        string='Microsoft Tenant ID',
        config_parameter='helpdesk.ms_graph_tenant_id',
        help='Azure AD Tenant ID for Microsoft Graph API authentication'
    )
    
    ms_graph_client_id = fields.Char(
        string='Microsoft Client ID',
        config_parameter='helpdesk.ms_graph_client_id',
        help='Application (client) ID from Azure AD app registration'
    )
    
    ms_graph_client_secret = fields.Char(
        string='Microsoft Client Secret',
        config_parameter='helpdesk.ms_graph_client_secret',
        help='Client secret value from Azure AD app registration'
    )
    
    ms_graph_calendar_email = fields.Char(
        string='Calendar Email',
        config_parameter='helpdesk.ms_graph_calendar_email',
        default='osoolcare@osoolre.com',
        help='Email address of the calendar where lift booking events will be created'
    )
