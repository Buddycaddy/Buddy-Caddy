from PyQt5.QtCore import QEvent

class QCustomEvent(QEvent):
    def __init__(self, callback , frame=None):
        super().__init__(QEvent.User)
        self.callback = callback
        self.frame = frame

    def execute(self):
        self.callback()