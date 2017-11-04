from loggers.logger import Logger


class TextLogger(Logger):
    def __init__(self, filename):
        self.filename = filename
        self.opened_file = None

    def open(self):
        self.opened_file = open(self.filename, 'wb')

    def close(self):
        self.opened_file.close()

    def write(self, log):
        self.opened_file.write('{}\n'.format(log))
