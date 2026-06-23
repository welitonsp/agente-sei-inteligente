from app.sei.sei_action_guard import validate_action

class SeiGuardian:
    def check(self, action: str):
        return validate_action(action)
