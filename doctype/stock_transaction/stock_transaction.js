// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Stock Transaction", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Stock Transaction', {
    item: function(frm) {
        // Always disable quantity until item and uom are confirmed
        frm.set_df_property('quantity', 'read_only', 1);
        frm.set_value('uom_name', null);

        if (frm.doc.item) {
            frappe.db.get_value('Inventory items', frm.doc.item, 'uom_name', function(r) {
                if (r && r.uom_name) {
                    frm.set_value('uom_name', r.uom_name);

                    // ✅ Only enable and set quantity if it is empty or zero
                    frm.set_df_property('quantity', 'read_only', 0);
                    if (!frm.doc.quantity || frm.doc.quantity === 0) {
                        frm.set_value('quantity', 1);
                    }
                } else {
                    frappe.msgprint("❌ Could not fetch UOM for selected item.");
                }
            });
        } else {
            frm.set_df_property('quantity', 'read_only', 1);
            frm.set_value('quantity', null);
        }
    }
});

