import frappe
from frappe.model.document import Document

class SalesTransaction_(Document):
    def on_submit(self):
        # Debug: confirm method is triggered
        frappe.msgprint(f"Submitting Sales Transaction for item: {self.item}")

        # Ensure required fields are present
        if not self.item or not self.quantity or not self.type:
            frappe.throw("Item, Quantity, and Type are required.")

        try:
            # Fetch linked Inventory Item
            inventory_item = frappe.get_doc("Inventory ITEMS_", self.item)
            current_stock = inventory_item.current_stock or 0

            # Update stock based on type
            if self.type == "In":
                inventory_item.current_stock = current_stock + self.quantity
                frappe.msgprint(f"Added {self.quantity}. New stock: {inventory_item.current_stock}")
            elif self.type == "Out":
                if current_stock < self.quantity:
                    frappe.throw("Not enough stock to perform this transaction.")
                inventory_item.current_stock = current_stock - self.quantity
                frappe.msgprint(f"Removed {self.quantity}. New stock: {inventory_item.current_stock}")
            else:
                frappe.throw("Type must be either 'In' or 'Out'.")

            inventory_item.save()
            frappe.msgprint("Inventory updated successfully.")

        except Exception as e:
            frappe.throw(f"Error updating inventory: {e}")
