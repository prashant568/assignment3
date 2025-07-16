// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Stock Transaction", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Purchase Request', {
    refresh(frm) {
        console.log("🔍 JS loaded for Purchase Request");

        if (frm.doc.docstatus === 1 && frm.doc.status === "Pending") {
            console.log("🟡 Showing Fulfill Button");

            frm.add_custom_button('Mark as Fulfilled', () => {
                console.log("🟢 Fulfill button clicked");

                frappe.call({
                    method: 'agrstock_app.agrstock_app.doctype.purchase_request.purchase_request.fulfill_purchase_request',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function (r) {
                        console.log("🔁 Backend call complete", r);
                        if (!r.exc) {
                            frappe.msgprint('✅ Request fulfilled and stock updated.');
                            frm.reload_doc();
                        } else {
                            frappe.msgprint('❌ Something went wrong.');
                        }
                    }
                });
            }, 'Actions');
        }
    }
});
