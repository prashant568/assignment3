# import frappe
# from frappe.model.document import Document
# from frappe import _

# class StockTransaction(Document):

#     def validate(self):
      

#         if not self.item or not self.quantity:
#             frappe.throw(_("Item and Quantity are required."))

#         if self.quantity <= 0:
#             frappe.throw(_("Quantity must be greater than zero."))

        

#     def on_submit(self):
       
#         self.update_inventory_stock()

#     def update_inventory_stock(self):
#         try:
           
#             item = frappe.get_doc("Inventory items", self.item)

#             current_stock = item.current_stock or 0
#             frappe.msgprint(f"📦 Current stock of {item.item}: {current_stock}")
#             frappe.msgprint(f"📥 Transaction Type: {self.type} | Quantity: {self.quantity}")

#             if self.type == "In":
#                 item.current_stock = current_stock + self.quantity
#                 frappe.msgprint(f"➕ Adding stock: New stock = {item.current_stock}")
#             elif self.type == "Out":
#                 if self.quantity > current_stock:
#                     frappe.throw(_("❌ Not enough stock. Available: {0}, Required: {1}")
#                                  .format(current_stock, self.quantity))
#                 item.current_stock = current_stock - self.quantity
#                 frappe.msgprint(f"➖ Removing stock: New stock = {item.current_stock}")
#             else:
#                 frappe.throw(_("⚠️ Transaction type must be 'In' or 'Out'."))

#             item.save()
#             frappe.msgprint(_("✅ Stock updated for Item: {0}. Final Stock: {1}")
#                             .format(item.item, item.current_stock))

#             # 🔔 Check for Reorder Level
#             if item.reorder_level and item.current_stock <= item.reorder_level:
#                 frappe.msgprint(f"⚠️ Stock for {item.item} has reached reorder level ({item.current_stock} ≤ {item.reorder_level}). Creating purchase request...")
#                 self.create_purchase_request(item)

#         except Exception as e:
#             import traceback
#             frappe.throw(_("🔥 Error in updating stock: {0}\n{1}")
#                          .format(str(e), traceback.format_exc()))
            
#     frappe.msgprint("🚨 create_purchase_request() was called")
#     def create_purchase_request(self, item):
#         existing = frappe.get_all("Purchase Request", filters={
#             "item": item.item,
#             "status": "Pending"
#         })

#         if existing:
#             frappe.msgprint("📌 Purchase Request already exists for this item.")
#             return

#         reorder_qty = item.reorder_level * 2  # Example logic: 2x reorder level

#         purchase_request = frappe.new_doc("Purchase Request")
#         purchase_request.item = item.item
#         purchase_request.purchase_quantity = reorder_qty
#         purchase_request.request_date = frappe.utils.nowdate()
#         purchase_request.status = "Draft"
        
#         purchase_request.remarks = f"Auto-created from Stock Transaction {self.name}"
#         purchase_request.farm = self.farm 
#         purchase_request.save(ignore_permissions=True)
#         frappe.msgprint(f"📝 Purchase Request {purchase_request.name} created for item {item.item} (Qty: {reorder_qty})")
#         try:
#             from agrstock_app.agrstock_app.doctype.purchase_request.purchase_request import fulfill_purchase_request
#             fulfill_purchase_request(purchase_request.name)
#         except Exception as e:
#              frappe.log_error(f"❌ Error calling fulfill_purchase_request: {e}", "Auto-Fulfill Error")
#              frappe.msgprint("❌ Something went wrong during auto-fulfillment.")
import frappe
from frappe.model.document import Document


class StockTransaction(Document):
    def on_submit(self):
        frappe.msgprint("🚀 on_submit triggered")
        from agrstock_app.utils import check_reorder  # make sure path is correct
        check_reorder()
        delta = self.quantity
        uom = self.uom_name
        price_per_unit = self.price_per_unit
        item = self.item

        if self.transaction_type == "In":
            frappe.msgprint(f"📦 Transaction: In | Qty: {delta} | Item: {item}")

            # ➕ Update FARM (Target)
            if self.target_type == "Farm":
                frappe.msgprint(f"🧭 Updating FARM TARGET: {self.target_name}")
                update_farm_stock(self.target_name, item, delta, uom, price_per_unit)

            # ➖ Update SUPPLIER (Source)
            if self.source_type == "Supplier":
                frappe.msgprint(f"🔄 Updating SUPPLIER SOURCE: {self.source_name}")
                update_supplier_stock(self.source_name, item, -delta, uom, price_per_unit)

        elif self.transaction_type == "Out":
            frappe.msgprint(f"📦 Transaction: Out | Qty: {delta} | Item: {item}")

            # ➖ Update FARM (Source)
            if self.source_type == "Farm":
                frappe.msgprint(f"🌾 Updating FARM SOURCE: {self.source_name}")
                update_farm_stock(self.source_name, item, -delta, uom, price_per_unit)

            # ➕ Update SUPPLIER (Target)
            if self.target_type == "Supplier":
                frappe.msgprint(f"🏪 Updating SUPPLIER TARGET: {self.target_name}")
                update_supplier_stock(self.target_name, item, delta, uom, price_per_unit)


def update_farm_stock(farm_name, item_name, delta, uom, price_per_unit):
    farm_doc = frappe.get_doc("Farm", farm_name)
    farm_doc.flags.ignore_permissions = True
    farm_doc.flags.ignore_validate_update_after_submit = True
    farm_doc.flags.ignore_submit = True

    # ✅ Ensure price_per_unit is not None or 0
    if not price_per_unit:
        price_per_unit = frappe.db.get_value(
            "Items Supplied", {"item": item_name}, "price_per_unit"
        ) or 0

    estimated_price = price_per_unit * delta
    found = False

    for row in farm_doc.farm_products:
        if row.item == item_name:
            old_qty = row.quantity or 0
            new_qty = old_qty + delta

            if new_qty < 0:
                frappe.throw(f"❌ Not enough stock in farm '{farm_name}' for item '{item_name}'")

            row.quantity = new_qty
            row.uom_item = uom
            row.price = new_qty * price_per_unit  # ✅ Ensure not 0
            frappe.msgprint(f"✅ Updated FARM: {item_name} from {old_qty} ➡️ {new_qty}")
            found = True
            break

    if not found:
        if delta < 0:
            frappe.throw(f"❌ Cannot reduce, item '{item_name}' not found in farm '{farm_name}'")

        farm_doc.append("farm_products", {
            "item": item_name,
            "quantity": delta,
            "uom_item": uom,
            "price": estimated_price
        })
        frappe.msgprint(f"🆕 Added to FARM: {item_name} = {delta} {uom}, ₹{estimated_price}")

    try:
        farm_doc.save(ignore_permissions=True)
        frappe.msgprint(f"💾 Farm '{farm_name}' updated successfully.")
    except Exception as e:
        frappe.throw(f"💥 Error saving Farm: {e}")



def update_supplier_stock(supplier_name, item_name, delta, uom, price_per_unit=None):
    supplier_doc = frappe.get_doc("Supplier", supplier_name)
    supplier_doc.flags.ignore_permissions = True
    supplier_doc.flags.ignore_validate_update_after_submit = True
    supplier_doc.flags.ignore_submit = True

    found = False

    for row in supplier_doc.supplier_items:
        if row.item == item_name:
            old_qty = row.available_stock or 0
            new_qty = old_qty + delta

            if new_qty < 0:
                frappe.throw(f"❌ Not enough stock in supplier '{supplier_name}' for '{item_name}'")

            row.available_stock = new_qty
            row.uom_name = uom or row.uom_name

            # ✅ Only update price if passed and not 0
            if price_per_unit and price_per_unit > 0:
                row.price_per_unit = price_per_unit

            frappe.msgprint(f"✅ Updated SUPPLIER: {item_name} from {old_qty} ➡️ {new_qty}")
            found = True
            break

    if not found:
        if delta < 0:
            frappe.throw(f"❌ Cannot reduce, item '{item_name}' not found in supplier '{supplier_name}'")

        supplier_doc.append("supplier_items", {
            "item": item_name,
            "uom_name": uom,
            "price_per_unit": price_per_unit or 0,
            "available_stock": delta
        })

        frappe.msgprint(f"🆕 Added to SUPPLIER: {item_name} = {delta} {uom}")

    try:
        supplier_doc.save(ignore_permissions=True)
        frappe.msgprint(f"💾 Supplier '{supplier_name}' updated successfully.")
    except Exception as e:
        frappe.throw(f"💥 Error saving Supplier: {e}")
