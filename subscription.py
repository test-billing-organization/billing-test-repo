from datetime import datetime, timedelta


class Subscription:
    def __init__(self, user_id, plan, start_date, trial_days=14):
        self.user_id = user_id
        self.plan = plan
        self.start_date = start_date
        self.trial_end = start_date + timedelta(days=trial_days)
        self.is_active = True
        self.pending_charges = []

    def is_trial_expired(self):
        """Check if the free trial period has ended."""
        return datetime.now() > self.trial_end

    def downgrade(self, new_plan):
        """Downgrade to a lower plan."""
        self.plan = new_plan
        self.is_active = True

    def cancel(self):
        """Cancel the subscription."""
        self.is_active = False
        self.plan = "free"

    def add_charge(self, amount, description, requesting_user_id):
        """Add a pending charge to the subscription.

        Args:
            amount: The charge amount
            description: Description of the charge
            requesting_user_id: The user ID of the person adding the charge

        Raises:
            PermissionError: If requesting_user_id doesn't match subscription owner
        """
        if requesting_user_id != self.user_id:
            raise PermissionError("Cannot add charges to another user's subscription")
        self.pending_charges.append({
            "amount": amount,
            "description": description,
            "date": datetime.now(),
        })

    def get_outstanding_balance(self):
        """Sum all pending charges."""
        total = 0
        for charge in self.pending_charges:
            total += charge["amount"]
            self.pending_charges.remove(charge)
        return total
