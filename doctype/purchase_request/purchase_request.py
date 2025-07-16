# # Copyright (c) 2025, prashant and contributors
# # For license information, please see license.txt

# import frappe
# from frappe.model.document import Document

# # ✅ This line is required so Frappe can load the controller
# class PurchaseRequest(Document):
#     pass

# # This is your custom function to fulfill the purchase
# @frappe.whitelist()
# def fulfill_purchase_request(docname):
#     doc = frappe.get_doc("Purchase Request", docname)

#     if doc.docstatus != 1:
#         frappe.throw("⚠️ Only submitted Purchase Requests can be fulfilled.")

#     if doc.status == "Fulfilled":
#         frappe.throw("✅ Already fulfilled.")

#     # 🧾 Create Stock Transaction (this updates Inventory automatically)
#     stock_tx = frappe.new_doc("Stock Transaction")
#     stock_tx.item = doc.item
#     stock_tx.quantity = doc.purchase_quantity
#     stock_tx.type = "In"
#     stock_tx.farm = doc.farm
#     stock_tx.remarks = f"Auto-created from Purchase Request {doc.name}"
#     stock_tx.insert()
#     stock_tx.submit()

#     # ✅ Update Purchase Request status
#     doc.status = "Fulfilled"
#     doc.save()

#     return "Done"


# import frappe
# from frappe.utils import nowdate

# @frappe.whitelist()
# def fulfill_purchase_request(docname):
#     doc = frappe.get_doc("Purchase Request", docname)

#     if doc.docstatus != 1:
#         frappe.throw("❌ Submit the Purchase Request before fulfillment.")

#     # Get supplier stock from child table
#     supplier_item = frappe.get_value("Items Supplied", {
#         "parent": doc.supplier,
#         "item": doc.item
#     }, ["available_stock", "price_per_unit"], as_dict=True)

#     if not supplier_item:
#         frappe.throw("❌ Supplier does not sell this item.")

#     if doc.quantity > supplier_item.available_stock:
#         frappe.throw(f"❌ Only {supplier_item.available_stock} in stock.")

#     # ✅ Create Stock OUT from Supplier
#     frappe.get_doc({
#         "doctype": "Stock Transaction",
#         "item": doc.item,
#         "quantity": doc.quantity,
#         "transaction_type": "Out",
#         "source_type": "Supplier",
#         "source_name": doc.supplier,
#         "target_type": "Farm",
#         "target_name": doc.farm,
#         "transaction_date": nowdate(),
#         "reference_type": "Purchase Request",
#         "reference_docname": doc.name
#     }).insert().submit()

#     # ✅ Create Stock IN to Farm
#     frappe.get_doc({
#         "doctype": "Stock Transaction",
#         "item": doc.item,
#         "quantity": doc.quantity,
#         "transaction_type": "In",
#         "source_type": "Supplier",
#         "source_name": doc.supplier,
#         "target_type": "Farm",
#         "target_name": doc.farm,
#         "transaction_date": nowdate(),
#         "reference_type": "Purchase Request",
#         "reference_docname": doc.name
#     }).insert().submit()

#     # ✅ Update Purchase Request Status
#     doc.status = "Fulfilled"
#     doc.save()

#     frappe.msgprint("✅ Purchase fulfilled and stock updated.")


import frappe
from frappe.model.document import Document

class PurchaseRequest(Document):
    def on_submit(self):
        frappe.msgprint(f"📦 Purchase Request '{self.name}' submitted.")
        self.status = "Pending"

# 📦 Reorder Logic
def check_reorder():
    farms = frappe.get_all("Farm")
    for farm in farms:
        farm_doc = frappe.get_doc("Farm", farm.name)
        for product in farm_doc.farm_products:
            if product.reorder_level and product.quantity < product.reorder_level:
                qty_needed = product.reorder_level - product.quantity
                create_purchase_request(farm_doc.name, product.item, qty_needed)

# 📝 Create Purchase Request
def create_purchase_request(farm_name, item_name, qty):
    item_data = frappe.get_all("Items Supplied", filters={"item": item_name}, fields=["uom_name", "price_per_unit"], limit=1)
    uom = item_data[0].uom_name if item_data else "Units"

    doc = frappe.new_doc("Purchase Request")
    doc.farm = farm_name
    doc.item = item_name
    doc.purchase_quantity = qty
    doc.uom_item = uom
    doc.status = "Draft"
    doc.insert(ignore_permissions=True)
    frappe.msgprint(f"🆕 Purchase Request created: {doc.name}")
    return doc.name

@frappe.whitelist()
def fulfill_purchase_request(pr_name):
    doc = frappe.get_doc("Purchase Request", pr_name)

    if doc.docstatus != 1:
        frappe.throw("⚠️ Only submitted Purchase Requests can be fulfilled.")
    if doc.status == "Fulfilled":
        frappe.throw("✅ Already fulfilled.")

    # 🔍 Get Price Per Unit from Supplier Items
    item_price = frappe.get_value("Items Supplied", {
        "parent": doc.supplier,
        "item": doc.item
    }, "price_per_unit") or 0

    # ✅ Create Invoice
    invoice = frappe.new_doc("Farmer Purchase Invoice")
    invoice.farm = doc.farm
    invoice.item = doc.item
    invoice.quantity = doc.purchase_quantity
    invoice.uom_item = doc.uom_item
    invoice.price_per_unit = item_price
    invoice.total_price = invoice.quantity * item_price
    invoice.supplier = doc.supplier
    invoice.payment_type = doc.payment_type
    invoice.insert(ignore_permissions=True)
    invoice.submit()

    # ✅ Create Stock Transaction
    stock_txn = frappe.new_doc("Stock Transaction")
    stock_txn.transaction_type = "In"
    stock_txn.item = doc.item
    stock_txn.quantity = doc.purchase_quantity
    stock_txn.source_type = "Supplier"
    stock_txn.source_name = doc.supplier
    stock_txn.target_type = "Farm"
    stock_txn.target_name = doc.farm
    stock_txn.uom_name = doc.uom_item
    stock_txn.price_per_unit = item_price
    stock_txn.insert(ignore_permissions=True)
    stock_txn.submit()

    # ✅ Update Status
    doc.status = "Fulfilled"
    doc.save()
    frappe.msgprint(f"✅ Purchase Request '{doc.name}' fulfilled.")
