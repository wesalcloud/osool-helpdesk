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
