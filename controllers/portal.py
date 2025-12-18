# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class HelpdeskPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # Always compute the user's ticket count so the tile shows reliably
        try:
            domain = [('partner_id', '=', request.env.user.partner_id.id)]
            values['ticket_count'] = request.env['helpdesk.ticket'].sudo().search_count(domain)
        except Exception:
            # Fallback to zero if any issue (e.g., during install)
            values['ticket_count'] = 0
        return values
    
    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        # Check if user is Public user (not logged in)
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/my/tickets')
        
        values = self._prepare_portal_layout_values()
        Ticket = request.env['helpdesk.ticket']
        
        # Only show tickets for the logged-in user's partner
        domain = [('partner_id', '=', request.env.user.partner_id.id)]
        
        searchbar_sortings = {
            'date': {'label': 'Newest', 'order': 'create_date desc'},
            'name': {'label': 'Subject', 'order': 'name'},
            'status': {'label': 'Status', 'order': 'status'},
        }
        
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        
        ticket_count = Ticket.search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=ticket_count,
            page=page,
            step=self._items_per_page
        )
        
        tickets = Ticket.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'date': date_begin,
            'tickets': tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("osool_helpdesk.portal_my_tickets", values)
    
    # Create ticket (GET)
    @http.route(['/helpdesk/ticket/create'], type='http', auth="user", website=True)
    def portal_ticket_create(self, **kw):
        # Force login if public
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/helpdesk/ticket/create')

        categories = request.env['helpdesk.category'].sudo().search([('active', '=', True)], order='sequence, name')
        values = {
            'categories': categories,
            'user': request.env.user,
            'errors': [],
            'post': {},
        }
        return request.render("osool_helpdesk.portal_create_ticket", values)

    # Create ticket (POST)
    @http.route(['/helpdesk/ticket/submit'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_ticket_submit(self, **post):
        # Validate login
        if request.env.user._is_public():
            return request.redirect('/web/login?redirect=/helpdesk/ticket/create')

        subject = (post.get('subject') or '').strip()
        description = (post.get('description') or '').strip()
        category_id = post.get('category_id')

        # Minimal validation
        errors = []
        if not subject:
            errors.append('Subject is required')
        if not description:
            errors.append('Description is required')

        # Re-render with errors
        if errors:
            categories = request.env['helpdesk.category'].sudo().search([('active', '=', True)], order='sequence, name')
            values = {
                'categories': categories,
                'user': request.env.user,
                'errors': errors,
                'post': post,
            }
            return request.render("osool_helpdesk.portal_create_ticket", values)

        vals = {
            'name': subject,
            'description': description,
            'partner_id': request.env.user.partner_id.id,
            'caller_source': 'selfservice',
        }

        # Optional category
        try:
            if category_id:
                cat_id = int(category_id)
                vals['request_category_id'] = cat_id
                # Persist the correct form_type based on the selected category
                cat = request.env['helpdesk.category'].sudo().browse(cat_id)
                if cat.exists() and cat.form_type:
                    vals['form_type'] = cat.form_type
        except Exception:
            # ignore invalid category id
            pass

        # Create the ticket with sudo to bypass portal create ACLs safely
        try:
            ticket = request.env['helpdesk.ticket'].sudo().create(vals)
        except Exception as e:
            # On error, show it to the user
            categories = request.env['helpdesk.category'].sudo().search([('active', '=', True)], order='sequence, name')
            values = {
                'categories': categories,
                'user': request.env.user,
                'errors': [str(e)],
                'post': post,
            }
            return request.render("osool_helpdesk.portal_create_ticket", values)

        # Redirect to the ticket detail in portal
        return request.redirect(f"/my/ticket/{ticket.id}")

    @http.route(['/helpdesk/help', '/my/helpdesk/help'], type='http', auth="public", website=True)
    def portal_help_page(self, **kw):
        """Public help page that explains how to submit and track tickets from the portal."""
        try:
            values = self._prepare_portal_layout_values()
        except Exception:
            values = self._prepare_home_portal_values({})
        return request.render("osool_helpdesk.portal_help_page", values)

    # Override the default helpdesk ticket detail route to use custom template
    @http.route([
        "/helpdesk/ticket/<int:ticket_id>",
        "/helpdesk/ticket/<int:ticket_id>/<access_token>",
        '/my/ticket/<int:ticket_id>',
        '/my/ticket/<int:ticket_id>/<access_token>'
    ], type='http', auth="public", website=True)
    def tickets_followup(self, ticket_id=None, access_token=None, **kw):
        # Use parent method to get ticket and check access
        try:
            ticket_sudo = self._document_check_access('helpdesk.ticket', ticket_id, access_token=access_token)
        except Exception:
            return request.redirect('/my')
        
        values = {
            'ticket': ticket_sudo,
            'page_name': 'ticket',
        }
        # Render custom template instead of default helpdesk.tickets_followup
        return request.render("osool_helpdesk.portal_ticket_detail", values)
