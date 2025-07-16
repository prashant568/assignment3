# Copyright (c) 2025, prashant and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe.model.document import Document
from agrstock_app.agrstock_app.doctype.purchase_request.purchase_request import create_purchase_request

class FarmConsumptionLog(Document):
    def on_submit(self):
        farm_doc = frappe.get_doc("Farm", self.farm)
        found = False

        for row in farm_doc.farm_products:
            if row.item == self.item:
                if row.usage_type != "Use":
                    frappe.throw(f"❌ Item '{self.item}' is not marked as 'Use' type in the farm.")

                if row.quantity < self.quantity_used:
                    frappe.throw(f"❌ Not enough '{self.item}' stock to consume.")

                old_qty = row.quantity
                row.quantity -= self.quantity_used
                frappe.msgprint(f"📉 {self.quantity_used} {row.uom_item} of '{self.item}' used. Remaining: {row.quantity}")
                found = True

                # 🔁 Check for Reorder
                if row.reorder_level and row.quantity < row.reorder_level:
                    qty_needed = row.reorder_level - row.quantity
                    create_purchase_request(farm_doc.name, self.item, qty_needed)

                break

        if not found:
            frappe.throw(f"❌ Item '{self.item}' not found in farm '{self.farm}'.")

        farm_doc.save()
