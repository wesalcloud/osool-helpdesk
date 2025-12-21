# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    """
    Migrate notification emails from teams to departments
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check if old table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'helpdesk_team_notified_email'
        )
    """)
    old_table_exists = cr.fetchone()[0]
    
    if not old_table_exists:
        return
    
    # Find all notification emails linked to teams
    cr.execute("""
        SELECT id, team_id, name, email, active, sequence
        FROM helpdesk_team_notified_email
        WHERE team_id IS NOT NULL
    """)
    
    team_emails = cr.fetchall()
    
    for email_id, team_id, name, email, active, sequence in team_emails:
        # Get the department for this team
        cr.execute("""
            SELECT team_department_id
            FROM helpdesk_team
            WHERE id = %s
        """, (team_id,))
        
        result = cr.fetchone()
        if result and result[0]:
            department_id = result[0]
            
            # Update the email to point to department instead of team
            cr.execute("""
                UPDATE helpdesk_team_notified_email
                SET department_id = %s, team_id = NULL
                WHERE id = %s
            """, (department_id, email_id))
    
    # Drop team_id column since it's no longer used
    cr.execute("""
        ALTER TABLE helpdesk_team_notified_email
        DROP COLUMN IF EXISTS team_id
    """)
    
    # Rename table to new name
    cr.execute("""
        ALTER TABLE helpdesk_team_notified_email
        RENAME TO helpdesk_department_notified_email
    """)
