#!/usr/bin/env python3
"""
Script to load Arabic translations for osool_helpdesk module
"""
import sys
import os

# Add Odoo to path
sys.path.insert(0, '/opt/odoo19')
os.chdir('/opt/odoo19')

from odoo import api, SUPERUSER_ID
from odoo.tools import config
from odoo.modules.registry import Registry

# Initialize Odoo config
config.parse_config(['--config=/etc/odoo19.conf'])

DB_NAME = 'osool'

try:
    # Get registry
    registry = Registry.new(DB_NAME)
    
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        print("Loading Arabic translations for osool_helpdesk...")
        
        # Import translation file
        from odoo.tools.translate import trans_load
        
        po_file = '/opt/odoo19/custom-addons/osool_helpdesk/i18n/ar.po'
        
        if os.path.exists(po_file):
            print(f"Found translation file: {po_file}")
            
            # Load the translations
            trans_load(cr, po_file, 'ar_001', module_name='osool_helpdesk', verbose=True)
            cr.commit()
            
            print("✅ Successfully loaded Arabic translations!")
            
            # Verify loaded translations
            translation_count = env['ir.translation'].search_count([
                ('module', '=', 'osool_helpdesk'),
                ('lang', '=', 'ar_001')
            ])
            
            print(f"📊 Total translations in database: {translation_count}")
            
            # Show some sample translations
            print("\n📝 Sample translations:")
            samples = env['ir.translation'].search([
                ('module', '=', 'osool_helpdesk'),
                ('lang', '=', 'ar_001'),
                ('type', '=', 'model')
            ], limit=5)
            
            for trans in samples:
                print(f"  {trans.name}: {trans.source} → {trans.value}")
        else:
            print(f"❌ Translation file not found: {po_file}")
            sys.exit(1)
            
except Exception as e:
    print(f"❌ Error loading translations: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ Translation loading completed successfully!")
print("👉 Now go to Settings → Translations → Languages")
print("   and make sure Arabic (ar_001) is active.")
print("👉 Then change your user preferences to Arabic language.")
