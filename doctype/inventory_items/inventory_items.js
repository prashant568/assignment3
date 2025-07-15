// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Inventory items", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Inventory items', {
    refresh: function(frm) {
        if (frm.doc.current_stock !== undefined && frm.doc.reorder_level !== undefined) {
            if (frm.doc.current_stock < frm.doc.reorder_level) {
                frappe.msgprint({
                    title: "⚠️ Low Stock Alert",
                    message: `📦 Current stock (${frm.doc.current_stock}) is below reorder level (${frm.doc.reorder_level})`,
                    indicator: 'red'
                });
            }
        }
    }
});
