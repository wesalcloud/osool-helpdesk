# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.addons.website.controllers.main import Website


class HelpdeskController(http.Controller):
    """
    Custom Helpdesk Controller
    Note: Ticket creation routes are handled in controllers/portal.py
    This controller is reserved for future custom endpoints.
    """
    pass



