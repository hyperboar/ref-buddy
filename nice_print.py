from abc import ABC, abstractmethod

class PrinterInterface(ABC):
    @abstractmethod
    def step_up(self) -> None:
        print("Abstract step_up")
        return

    @abstractmethod
    def step_down(self) -> None:
        print("Abstract step_down")
        return

    @abstractmethod
    def line(self, msg:str, replace:bool=False, same_line:bool=False) -> None:
        print("Abstract line")
        return

    @abstractmethod
    def header(self, msg:str) -> None:
        print("Abstract header")
        return

class DefaultPrinter(PrinterInterface):
    def __init__(self):
        pass
    def step_up(self) -> None:
        pass

    def step_down(self) -> None:
        pass

    def line(self, msg:str, replace:bool=False, same_line:bool=False) -> None:
        if msg == '':
            print('')
            return
        print(("\r" if replace else "") + msg, end=('' if same_line or replace else '\n'), flush=True)

    def header(self, msg: str) -> None:
        print(msg, flush=True)

class NicePrinter(PrinterInterface):
    def __init__(self, logger):
        self.step = 0
        self.logger = logger

    def step_up(self) -> None:
        self.step = self.step + 1

    def step_down(self) -> None:
        self.step = max(0, self.step - 1)

    def line(self, msg:str, replace:bool=False, same_line:bool=False) -> None:
        if msg == '':
            print('')
            return

        console_msg = ("\r" if replace else "") + (' ' * self.step * 4) + msg
        print(console_msg + self.padding(len(console_msg)), end=('' if same_line or replace else '\n'), flush=True)

    def header(self, msg: str) -> None:
        print((' ' * self.step * 4) + msg, flush=True)

    def padding(self, actual_len:int, target_len:int = 80) -> str:
        return ' ' * max(0, target_len - actual_len)