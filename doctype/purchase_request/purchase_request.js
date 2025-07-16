// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Purchase Request", {
// 	refresh(frm) {

// 	},
// });
// frappe.ui.form.on('Purchase Request', {
//     farm: function(frm) {
//         frm.set_query('item', function() {
//             if (frm.doc.farm) {
//                 return {
//                     filters: {
//                         farm: frm.doc.farm  // sirf wahi item dikhao jiska farm match kare
//                     }
//                 };
//             }
//         });
//     }
// });
// frappe.ui.form.on('Purchase Request', {
//     farm: function(frm) {
//         if (frm.doc.farm) {
//             frappe.db.get_value('Farm', { name: frm.doc.farm }, 'farm_owner')
//                 .then(r => {
//                     if (r.message && r.message.farm_owner) {
//                         frm.set_value('farm_manager', r.message.farm_owner);
//                     }
//                 });
//         } else {
//             frm.set_value('farm_manager', null);
//         }
//     }
// });



// frappe.ui.form.on('Purchase Request', {
//     refresh(frm) {
//         // Agar document submit ho chuka hai aur status "Pending" hai, tab hi button dikhao
//         if (frm.doc.docstatus === 1 && frm.doc.status === "Pending") {
//             frm.add_custom_button('Mark as Fulfilled', () => {
//                 frappe.call({
//                     method: 'agrstock_app.agrstock_app.doctype.purchase_request.purchase_request.fulfill_purchase_request',
//                     args: {
//                         docname: frm.doc.name
//                     },
//                     callback: function (r) {
//                         if (!r.exc) {
//                             frappe.msgprint('✅ Request fulfilled and stock updated.');
//                             frm.reload_doc(); // Form ko refresh karo
//                         }
//                     }
//                 });
//             }, 'Actions');
//         }
//     }
// });
// frappe.ui.form.on('Purchase Request', {
//     refresh: function(frm) {
//         if (frm.doc.docstatus === 1 && frm.doc.status !== "Fulfilled") {
//             frm.add_custom_button('Fulfill Request', () => {
//                 frappe.call({
//                     method: "agrstock_app.agrstock_app.doctype.purchase_request.purchase_request.fulfill_purchase_request",
//                     args: { docname: frm.doc.name },
//                     callback: () => frm.reload()
//                 });
//             });
//         }
//     }
// });


// frappe.ui.form.on("Purchase Request", {
//     supplier(frm) {
//         frm.set_query("item", () => {
//             return {
//                 query: "agrstock_app.api.get_supplier_items",
//                 filters: { supplier: frm.doc.supplier }
//             };
//         });
//     }
// });

frappe.ui.form.on('Purchase Request', {
    refresh(frm) {
        if (frm.doc.docstatus === 1 && frm.doc.status === 'Pending') {
            frm.add_custom_button('Fulfill Request', () => {
               frappe.call({
method: "agrstock_app.agrstock_app.doctype.purchase_request.purchase_request.fulfill_purchase_request"
,
    args: {
        pr_name: frm.doc.name
    },
    callback: function(r) {
        if (!r.exc) {
            frappe.msgprint("✅ Purchase Request Fulfilled");
            frm.reload_doc();
        }
    }
});
            });
        }
    }
});
