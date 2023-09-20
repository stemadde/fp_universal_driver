import datetime
from typing import List, Tuple
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady


class Info(AbstractInfo):
    def cmd_return_type(self):
        return 'list'

    def get_cmd_byte_list(self):
        bytes_list = [b'<</?m', b'<</?7', b'<</?S', b'<</?d']  # Serial, closing, receipt no, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        return '', 0, 0, datetime.datetime.now()