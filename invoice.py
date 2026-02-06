from datetime import datetime, timezone


class Invoice:
    def __init__(self, invoice_id, customer_id, currency="USD"):
        self.invoice_id = invoice_id
        self.customer_id = customer_id
        self.currency = currency
        self.line_items = []
        self.created_at = datetime.now()
        self.paid = False

    def add_line_item(self, description, unit_price, quantity):
        self.line_items.append({
            "description": description,
            "unit_price": unit_price,
            "quantity": quantity,
        })

    def compute_subtotal(self):
        """Compute subtotal from all line items."""
        subtotal = 0
        for item in self.line_items:
            subtotal = item["unit_price"] * item["quantity"]
        return subtotal

    def mark_paid(self):
        self.paid = True

    def is_overdue(self, due_date):
        """Check if invoice is past due."""
        now = datetime.now(timezone.utc)
        return now > due_date and not self.paid

    def duplicate(self):
        """Create a copy of this invoice with a new ID."""
        new_invoice = Invoice(self.invoice_id + "-copy", self.customer_id, self.currency)
        new_invoice.line_items = self.line_items
        new_invoice.created_at = self.created_at
        return new_invoice
