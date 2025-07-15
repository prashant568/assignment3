import frappe
from frappe.model.document import Document
from frappe import _

class StockTransaction(Document):

    def validate(self):
        frappe.msgprint("🔍 Validating Stock Transaction...")

        if not self.item or not self.quantity:
            frappe.throw(_("Item and Quantity are required."))

        if self.quantity <= 0:
            frappe.throw(_("Quantity must be greater than zero."))

        frappe.msgprint("✅ Validation passed.")

    def on_submit(self):
        frappe.msgprint("🚀 Submitting Stock Transaction...")
        self.update_inventory_stock()

    def update_inventory_stock(self):
        try:
            frappe.msgprint(f"🔄 Fetching Inventory Item: {self.item}")
            item = frappe.get_doc("Inventory items", self.item)

            current_stock = item.current_stock or 0
            frappe.msgprint(f"📦 Current stock of {item.item}: {current_stock}")
            frappe.msgprint(f"📥 Transaction Type: {self.type} | Quantity: {self.quantity}")

            if self.type == "In":
                item.current_stock = current_stock + self.quantity
                frappe.msgprint(f"➕ Adding stock: New stock = {item.current_stock}")
            elif self.type == "Out":
                if self.quantity > current_stock:
                    frappe.throw(_("❌ Not enough stock. Available: {0}, Required: {1}")
                                 .format(current_stock, self.quantity))
                item.current_stock = current_stock - self.quantity
                frappe.msgprint(f"➖ Removing stock: New stock = {item.current_stock}")
            else:
                frappe.throw(_("⚠️ Transaction type must be 'In' or 'Out'."))

            item.save()
            frappe.msgprint(_("✅ Stock updated for Item: {0}. Final Stock: {1}")
                            .format(item.item, item.current_stock))

            # 🔔 Check for Reorder Level
            if item.reorder_level and item.current_stock <= item.reorder_level:
                frappe.msgprint(f"⚠️ Stock for {item.item} has reached reorder level ({item.current_stock} ≤ {item.reorder_level}). Creating purchase request...")
                self.create_purchase_request(item)

        except Exception as e:
            import traceback
            frappe.throw(_("🔥 Error in updating stock: {0}\n{1}")
                         .format(str(e), traceback.format_exc()))

    def create_purchase_request(self, item):
        existing = frappe.get_all("Purchase Request", filters={
            "item": item.item,
            "status": "Pending"
        })

        if existing:
            frappe.msgprint("📌 Purchase Request already exists for this item.")
            return

        reorder_qty = item.reorder_level * 2  # Example logic: 2x reorder level

        purchase_request = frappe.new_doc("Purchase Request")
        purchase_request.item = item.item
        purchase_request.purchase_quantity = reorder_qty
        purchase_request.request_date = frappe.utils.nowdate()
        purchase_request.status = "Draft"
        purchase_request.remarks = f"Auto-created from Stock Transaction {self.name}"
        purchase_request.farm = self.farm 
        purchase_request.save(ignore_permissions=True)
        frappe.msgprint(f"📝 Purchase Request {purchase_request.name} created for item {item.item} (Qty: {reorder_qty})")
