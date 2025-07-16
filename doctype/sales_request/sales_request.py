# Copyright (c) 2025, prashant and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SalesRequest(Document):
    pass

import frappe

@frappe.whitelist()
def notify_supplier_low_stock(supplier_name=None):
    low_stock_items = []

    filters = {"name": supplier_name} if supplier_name else {}
    suppliers = frappe.get_all("Supplier", filters=filters)

    for sup in suppliers:
        sup_doc = frappe.get_doc("Supplier", sup.name)

        # ✅ Correct child table fieldname
        for row in sup_doc.supplier_items:
            stock = row.available_stock or 0
            if stock < 500:
                low_stock_items.append({
                    "item": row.item,
                    "available_stock": stock,
                    "uom": row.uom_name,
                    "supplier": sup.name
                })

                # ✅ Avoid duplicate Purchase Request
                existing = frappe.db.exists("Purchase Request", {
                    "supplier": sup.name,
                    "item": row.item,
                    "status": ["!=", "Fulfilled"]
                })
                if existing:
                    continue

                # ✅ Create Purchase Request
                req = frappe.new_doc("Purchase Request")
                req.supplier = sup.name
                req.item = row.item
                req.quantity = 1000
                req.uom_name = row.uom_name
                req.rate_per_unit = row.price_per_unit or 0
                req.status = "Pending"
                req.farm = getattr(sup_doc, "default_farm", "Main Farm")
                req.insert(ignore_permissions=True)
                req.submit()

                frappe.msgprint(f"📦 Created Purchase Request for '{row.item}' (Qty: 1000)")

    return low_stock_items
