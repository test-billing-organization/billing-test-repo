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

    def add_charge(self, amount, description):
        """Add a pending charge to the subscription."""
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
