# -*- coding: utf-8 -*-
from odoo import models, api


class WebsitePage(models.Model):
    _inherit = 'website.page'

    @api.model
    def _fix_page_security_osool(self, page_slug):
        """
        Restrict customer care page to logged-in users only
        Called from data/website_page_security.xml
        """
        # Search for the page by URL
        page = self.search([('url', '=', f'/helpdesk/{page_slug}')], limit=1)
        
        if page:
            # Set groups to require portal or internal user login
            portal_group = self.env.ref('base.group_portal')
            user_group = self.env.ref('base.group_user')
            
            page.write({
                'groups_id': [(6, 0, [portal_group.id, user_group.id])]
            })
            
            self.env.cr.commit()
            return True
        return False
