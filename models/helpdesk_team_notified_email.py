# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HelpdeskTeamNotifiedEmail(models.Model):
    _name = 'helpdesk.team.notified.email'
    _description = 'Helpdesk Team Notified Email'
    _order = 'sequence, id'
    
    sequence = fields.Integer(string='Sequence', default=10)
    team_id = fields.Many2one('helpdesk.team', string='Team', required=True, ondelete='cascade')
    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email', required=True)
    active = fields.Boolean(string='Active', default=True)
