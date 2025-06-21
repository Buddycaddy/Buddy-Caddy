from PyQt5.QtCore import QEvent

class QCustomEvent(QEvent):
    def __init__(self, callback, arg=None):
        super().__init__(QEvent.User)
        self.callback = callback
        self.arg = arg

    def execute(self,arg):
        if arg is not None:
            self.callback(arg)
        else:
            self.callback()