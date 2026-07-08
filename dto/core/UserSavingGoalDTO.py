class UserSavingGoalDTO:

    def __init__(
        self,
        user_id,
        saving_mode=None,
        target_percent=None,
        target_amount=None
    ):
        self.user_id = user_id
        self.saving_mode = saving_mode
        self.target_percent = target_percent
        self.target_amount = target_amount