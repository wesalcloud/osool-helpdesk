#!/usr/bin/env python3
"""
Generate demo tickets for Osool Helpdesk module
Run with: python3 /opt/odoo19/custom-addons/osool_helpdesk/scripts/generate_demo_tickets.py
"""

import sys
import os

# Add Odoo to path
sys.path.append('/opt/odoo19')

import odoo
from odoo import api, SUPERUSER_ID

# Database connection
DB_NAME = 'osool'

def generate_tickets():
    odoo.tools.config.parse_config(['-d', DB_NAME, '-c', '/etc/odoo19.conf'])
    
    from odoo.modules.registry import Registry
    registry = Registry.new(DB_NAME)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # Get categories and teams
        cat_complaint = env.ref('osool_helpdesk.category_complaint')
        cat_marketing = env.ref('osool_helpdesk.category_marketing')
        cat_security = env.ref('osool_helpdesk.category_security')
        cat_lift = env.ref('osool_helpdesk.category_lift_booking')
        cat_procurement = env.ref('osool_helpdesk.category_procurement')
        cat_hr = env.ref('osool_helpdesk.category_hr')
        cat_announcement = env.ref('osool_helpdesk.category_announcement')
        cat_maximo = env.ref('osool_helpdesk.category_maximo')
        
        team_technical = env.ref('osool_helpdesk.team_technical')
        team_customer = env.ref('osool_helpdesk.team_customer_service')
        team_hr = env.ref('osool_helpdesk.team_hr')
        
        Ticket = env['helpdesk.ticket']
        
        print("Creating demo tickets...")
        
        # Complaint Tickets (10)
        complaints = [
            {'name': 'AC not working in apartment 3A', 'desc': 'Air conditioning unit stopped working', 'type': 'service', 'severity': 'major', 'priority': '2'},
            {'name': 'Noise complaint from neighbors', 'desc': 'Excessive noise from apartment 5B late hours', 'type': 'other', 'severity': 'moderate', 'priority': '1'},
            {'name': 'Incorrect billing amount', 'desc': 'Charged for 2 parking spots but only have 1', 'type': 'billing', 'severity': 'moderate', 'priority': '1'},
            {'name': 'Rude behavior from security staff', 'desc': 'Security guard unprofessional at main entrance', 'type': 'staff', 'severity': 'major', 'priority': '2'},
            {'name': 'Water leakage from ceiling', 'desc': 'Water leaking from bathroom ceiling', 'type': 'service', 'severity': 'critical', 'priority': '3'},
            {'name': 'Parking spot occupied', 'desc': 'Assigned parking spot occupied by unknown vehicle', 'type': 'other', 'severity': 'moderate', 'priority': '1'},
            {'name': 'Elevator breaks down frequently', 'desc': 'Building A elevator breaks twice a week', 'type': 'service', 'severity': 'major', 'priority': '2'},
            {'name': 'Gym equipment not maintained', 'desc': 'Treadmill broken for over a month', 'type': 'service', 'severity': 'minor', 'priority': '0'},
            {'name': 'Late maintenance delivery', 'desc': 'Scheduled maintenance no show', 'type': 'service', 'severity': 'moderate', 'priority': '1'},
            {'name': 'Overcharged for utilities', 'desc': 'Electricity bill 3x higher than usual', 'type': 'billing', 'severity': 'major', 'priority': '2'},
        ]
        
        for c in complaints:
            Ticket.create({
                'name': c['name'],
                'description': c['desc'],
                'request_category_id': cat_complaint.id,
                'complaint_type': c['type'],
                'complaint_severity': c['severity'],
                'priority': c['priority'],
                'team_id': team_technical.id,
            })
        print(f"✓ Created {len(complaints)} complaint tickets")
        
        # Marketing Tickets (5)
        marketing = [
            {'name': 'Summer Festival 2025', 'campaign': 'Summer Festival 2025', 'budget': 15000},
            {'name': 'Social Media - New Amenities', 'campaign': 'Amenities Renovation', 'budget': 8500},
            {'name': 'Referral Program Launch', 'campaign': 'Referral Program Q3', 'budget': 5000},
            {'name': 'Email Newsletter November', 'campaign': 'Monthly Newsletter', 'budget': 1200},
            {'name': 'Year-End Appreciation', 'campaign': 'Year End Appreciation', 'budget': 12000},
        ]
        
        for m in marketing:
            Ticket.create({
                'name': m['name'],
                'description': f"Marketing campaign: {m['campaign']}",
                'request_category_id': cat_marketing.id,
                'marketing_campaign': m['campaign'],
                'marketing_budget': m['budget'],
                'team_id': team_customer.id,
            })
        print(f"✓ Created {len(marketing)} marketing tickets")
        
        # Security Tickets (5)
        security = [
            {'name': 'Suspicious person in parking', 'type': 'threat', 'location': 'Basement Parking B2'},
            {'name': 'Vandalism in lobby', 'type': 'vandalism', 'location': 'Main Lobby Building A'},
            {'name': 'Unauthorized roof access', 'type': 'access', 'location': 'Roof Access Building B'},
            {'name': 'Bicycle theft from storage', 'type': 'theft', 'location': 'Bicycle Storage B1'},
            {'name': 'CCTV camera not working', 'type': 'other', 'location': 'East Entrance'},
        ]
        
        for s in security:
            Ticket.create({
                'name': s['name'],
                'description': f"Security incident at {s['location']}",
                'request_category_id': cat_security.id,
                'security_incident_type': s['type'],
                'security_location': s['location'],
                'priority': '2',
                'team_id': team_technical.id,
            })
        print(f"✓ Created {len(security)} security tickets")
        
        # Lift Booking (4)
        lifts = [
            {'name': 'Moving furniture to 12th floor', 'size': 'large', 'from': 'Ground', 'to': '12th'},
            {'name': 'Delivery of appliances', 'size': 'large', 'from': 'Loading Dock', 'to': '8th'},
            {'name': 'Office relocation boxes', 'size': 'medium', 'from': '5th', 'to': '9th'},
            {'name': 'Move out complete apartment', 'size': 'large', 'from': '15th', 'to': 'Ground'},
        ]
        
        for l in lifts:
            Ticket.create({
                'name': l['name'],
                'description': f"Lift booking: {l['from']} to {l['to']} floor",
                'request_category_id': cat_lift.id,
                'lift_size': l['size'],
                'lift_floor_from': l['from'],
                'lift_floor_to': l['to'],
                'team_id': team_technical.id,
            })
        print(f"✓ Created {len(lifts)} lift booking tickets")
        
        # Procurement (3)
        procurement = [
            {'name': 'Purchase cleaning equipment', 'item': 'Vacuum Cleaners', 'qty': 5, 'budget': 8500},
            {'name': 'Office supplies bulk order', 'item': 'Office Supplies', 'qty': 1, 'budget': 3500},
            {'name': 'Replace HVAC filters', 'item': 'HVAC Filters', 'qty': 120, 'budget': 12000},
        ]
        
        for p in procurement:
            Ticket.create({
                'name': p['name'],
                'description': f"Procurement request for {p['item']}",
                'request_category_id': cat_procurement.id,
                'procurement_item': p['item'],
                'procurement_quantity': p['qty'],
                'procurement_budget': p['budget'],
                'team_id': team_technical.id,
            })
        print(f"✓ Created {len(procurement)} procurement tickets")
        
        # HR (3)
        hr_tickets = [
            {'name': 'Request annual leave', 'type': 'leave', 'dept': 'Facilities'},
            {'name': 'New employee recruitment', 'type': 'recruitment', 'dept': 'IT'},
            {'name': 'Training request - Safety', 'type': 'training', 'dept': 'Facilities'},
        ]
        
        for h in hr_tickets:
            Ticket.create({
                'name': h['name'],
                'description': f"HR request: {h['type']}",
                'request_category_id': cat_hr.id,
                'hr_request_type': h['type'],
                'hr_department': h['dept'],
                'team_id': team_hr.id,
            })
        print(f"✓ Created {len(hr_tickets)} HR tickets")
        
        # Announcements (3)
        announcements = [
            {'name': 'Pool closure', 'title': 'Swimming Pool Maintenance', 'audience': 'all'},
            {'name': 'Fire drill scheduled', 'title': 'Mandatory Fire Drill', 'audience': 'all'},
            {'name': 'New parking policy', 'title': 'Updated Parking Policy', 'audience': 'tenants'},
        ]
        
        for a in announcements:
            Ticket.create({
                'name': a['name'],
                'description': f"Announcement: {a['title']}",
                'request_category_id': cat_announcement.id,
                'announcement_title': a['title'],
                'announcement_target_audience': a['audience'],
                'team_id': team_customer.id,
            })
        print(f"✓ Created {len(announcements)} announcement tickets")
        
        # Maximo (2)
        maximo = [
            {'name': 'Chiller maintenance', 'wo': 'WO-2025-1045', 'asset': 'CHILLER-A-01'},
            {'name': 'Generator inspection', 'wo': 'WO-2025-1067', 'asset': 'GEN-B-02'},
        ]
        
        for mx in maximo:
            Ticket.create({
                'name': mx['name'],
                'description': f"Maximo work order {mx['wo']}",
                'request_category_id': cat_maximo.id,
                'maximo_work_order': mx['wo'],
                'maximo_asset_id': mx['asset'],
                'maximo_priority': 'high',
                'team_id': team_technical.id,
            })
        print(f"✓ Created {len(maximo)} Maximo tickets")
        
        cr.commit()
        
        total = len(complaints) + len(marketing) + len(security) + len(lifts) + len(procurement) + len(hr_tickets) + len(announcements) + len(maximo)
        print(f"\n✅ Successfully created {total} demo tickets!")
        print("Go to Helpdesk → Tickets → All Tickets to see them")

if __name__ == '__main__':
    generate_tickets()
