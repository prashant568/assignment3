// Copyright (c) 2025, prashant and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Purchase Request", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Purchase Request', {
    farm: function(frm) {
        frm.set_query('item', function() {
            if (frm.doc.farm) {
                return {
                    filters: {
                        farm: frm.doc.farm  // sirf wahi item dikhao jiska farm match kare
                    }
                };
            }
        });
    }
});
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



