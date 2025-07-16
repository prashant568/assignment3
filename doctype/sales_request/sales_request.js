// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Sales Request", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Supplier', {
    refresh: function(frm) {
        console.log("✅ Supplier form refreshed");
        frm.add_custom_button("🔁 Check Low Stock", () => {
            console.log("🔁 Button clicked");
            frappe.call({
                method: "agrstock_app.agrstock_app.doctype.sales_request.sales_request.notify_supplier_low_stock",
                args: {
                    supplier_name: frm.doc.name
                },
                callback: function(r) {
                    console.log("📦 Callback received", r.message);
                    if (r.message && r.message.length > 0) {
                        let html = `<ul>`;
                        r.message.forEach(item => {
                            html += `<li>📦 <b>${item.item}</b>: ${item.available_stock} ${item.uom}</li>`;
                        });
                        html += `</ul>`;
                        frappe.msgprint({
                            title: "Low Stock Items",
                            message: html,
                            indicator: "orange"
                        });
                    } else {
                        frappe.msgprint("✅ No low stock items found.");
                    }
                }
            });
        });
    }
});

