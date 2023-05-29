from abc import ABCMeta


class Closing(metaclass=ABCMeta):
    def __init__(self):
        pass

    def run(self):
        raise NotImplementedError('run() not implemented')
