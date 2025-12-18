# -*- coding: utf-8 -*-
from odoo import models, fields


class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'
    
    # Extended stage properties
    is_new = fields.Boolean(string='Is New Stage', default=False)
    is_closed = fields.Boolean(string='Is Closed Stage', default=False)
    is_resolved = fields.Boolean(string='Is Resolved Stage', default=False)
    is_rejected = fields.Boolean(string='Is Rejected Stage', default=False)
    is_assigned = fields.Boolean(string='Is Assigned Stage', default=False)
    is_in_progress = fields.Boolean(string='Is In Progress Stage', default=False)
    requires_approval = fields.Boolean(string='Requires Approval', default=False)
    approval_user_ids = fields.Many2many('res.users', string='Approvers')
