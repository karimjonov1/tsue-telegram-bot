from aiogram.fsm.state import State, StatesGroup


class AdminBroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirm_code = State()
