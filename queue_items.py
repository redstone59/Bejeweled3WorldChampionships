class QueueItem:
    def __init__(self, function: str, *arguments):
        self.function = function
        if type(arguments) not in [tuple, list]:
            try:
                self.arguments = tuple(self.arguments,)
            except:
                self.arguments = (self.arguments,)
        else:
            self.arguments = arguments