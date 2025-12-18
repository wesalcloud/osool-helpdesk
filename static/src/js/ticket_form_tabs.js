/**
 * Auto-open the category tab on ticket form based on form_type
 * Switches tab immediately when category changes (before save)
 */
odoo.define('osool_helpdesk.ticket_form_tabs', function (require) {
    'use strict';

    const FormController = require('web.FormController');
    const { whenReady } = require('web.dom_ready');

    function getFormType(root) {
        // Try to find the readonly selection value of form_type
        const container = root.querySelector('.o_form_view [name="form_type"], .o_form_view div[name="form_type"], .o_form_view span[name="form_type"]');
        if (!container) return null;
        // Get text content (readonly field displays text)
        const txt = container.textContent ? container.textContent.trim() : '';
        return txt ? txt.toLowerCase() : null;
    }

    function labelForFormType(formType) {
        switch (formType) {
            case 'complaint': return 'Complaint Details';
            case 'marketing': return 'Marketing Details';
            case 'security': return 'Security Details';
            case 'vvip_lift':
            case 'regular_lift': return 'Lift Booking Details';
            case 'procurement': return 'Procurement Details';
            case 'hr': return 'HR Details';
            case 'announcement': return 'Announcement Details';
            case 'maximo': return 'Maximo Details';
            default: return null;
        }
    }

    function activateTabByLabel(root, label) {
        if (!label) return false;
        const tabs = root.querySelectorAll('.o_form_view .o_notebook .nav-tabs .nav-link');
        for (const tab of tabs) {
            const text = (tab.textContent || '').trim();
            if (text === label) {
                tab.click();
                return true;
            }
        }
        return false;
    }

    const rpc = require('web.rpc');

    function tryActivate(root) {
        // Prefer resolving by request_category_id (more reliable)
        const catEl = document.querySelector('.o_form_view [name="request_category_id"]');
        if (catEl) {
            // Many2one widget stores the id in data-id or data-value attribute
            let catId = catEl.getAttribute('data-id') || catEl.getAttribute('data-value') || catEl.value;
            if (catId) {
                try {
                    catId = parseInt(catId, 10);
                } catch (e) {
                    catId = null;
                }
            }
            if (catId) {
                rpc.query({
                    model: 'helpdesk.category',
                    method: 'read',
                    args: [[catId], ['form_type']],
                }).then(function (res) {
                    if (res && res[0] && res[0].form_type) {
                        const label = labelForFormType(res[0].form_type);
                        if (label) {
                            // Retry activation until tabs mount
                            let attempts = 0;
                            const timer = setInterval(() => {
                                attempts += 1;
                                if (activateTabByLabel(root, label) || attempts >= 10) {
                                    clearInterval(timer);
                                }
                            }, 80);
                        }
                        return;
                    }
                    // Fallback to reading the displayed form_type
                    activateByDisplayedFormType(root);
                }).catch(function () {
                    activateByDisplayedFormType(root);
                });
                return;
            }
        }
        // No category id available, fallback to displayed form_type
        activateByDisplayedFormType(root);
    }

    function activateByDisplayedFormType(root) {
        const type = getFormType(root);
        const label = labelForFormType(type);
        if (label) {
            // Retry a few times if tabs are not yet mounted
            let attempts = 0;
            const timer = setInterval(() => {
                attempts += 1;
                if (activateTabByLabel(root, label) || attempts >= 10) {
                    clearInterval(timer);
                }
            }, 80);
        }
    }

    function setupObserver() {
        const root = document.body;
        // Observe form rendering changes and try activating when a ticket form appears
        const observer = new MutationObserver((mutations) => {
            for (const m of mutations) {
                for (const node of m.addedNodes) {
                    if (!(node instanceof HTMLElement)) continue;
                    if (node.querySelector && (node.matches('.o_form_view') || node.querySelector('.o_form_view'))) {
                        // Slight delay to ensure fields are mounted
                        setTimeout(() => tryActivate(node), 50);
                    }
                }
            }
        });
        observer.observe(root, { childList: true, subtree: true });

        // Also try once on DOM ready (in case the form is already present)
        setTimeout(() => tryActivate(document), 200);

        // Additionally, watch changes to the form_type field content and re-activate
        const ftObserver = new MutationObserver(() => tryActivate(document));
        const attachFieldObserver = () => {
            const ft = document.querySelector('.o_form_view [name="form_type"], .o_form_view div[name="form_type"], .o_form_view span[name="form_type"]');
            if (ft) {
                ftObserver.observe(ft, { childList: true, characterData: true, subtree: true });
            }
        };
        setTimeout(attachFieldObserver, 300);
    }

    // Hook into FormController to detect field changes
    FormController.include({
        _onFieldChanged: function (ev) {
            this._super.apply(this, arguments);
            
            // If request_category_id or form_type changed, re-activate the appropriate tab
            if (ev.data && (ev.data.changes.request_category_id || ev.data.changes.form_type)) {
                // Small delay to let the onchange propagate
                setTimeout(() => {
                    tryActivate(document);
                }, 150);
            }
        }
    });

    whenReady(setupObserver);
});
