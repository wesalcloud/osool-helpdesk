# -*- coding: utf-8 -*-
"""
Pre-migration script to handle duplicate subcategory codes
This runs before module upgrade to clean up any duplicates
"""

def migrate(cr, version):
    """Remove duplicate subcategory codes before upgrade"""
    
    # Find duplicates (keeping the oldest record with each code+category combination)
    cr.execute("""
        DELETE FROM helpdesk_subcategory
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM helpdesk_subcategory
            GROUP BY code, category_id
        )
        AND code IS NOT NULL
    """)
    
    duplicates_removed = cr.rowcount
    if duplicates_removed > 0:
        print(f"Removed {duplicates_removed} duplicate subcategory records")
