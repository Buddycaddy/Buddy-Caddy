from PyQt5.QtCore import QEvent

class QCustomEvent(QEvent):
    def __init__(self, callback):
        super().__init__(QEvent.User)
        self.callback = callback

    def execute(self):
        self.callback()