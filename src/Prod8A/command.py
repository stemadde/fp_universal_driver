import datetime
from decimal import Decimal
from typing import List, Tuple

from src.Prod8A.category import Category
from src.Prod8A.header import Header
from src.Prod8A.iva import Iva
from src.Prod8A.pos import Pos
from src.command import AbstractClosing, AbstractReceipt, AbstractVp, AbstractInfo, AbstractIsReady, AbstractCommand


class Info(AbstractInfo):
    def get_cmd_byte_list(self):
        bytes_list = [b'a', b'0/2/', b'9/', b't/']  # Serial, closing, receipt no, datetime
        return bytes_list

    @staticmethod
    def parse_response(response_list: List[str]) -> Tuple[str, int, int, datetime.datetime]:
        serial = response_list[0]
        serial = serial.split("/")[0]
        closing = response_list[1]
        closing = int(closing.split("/")[0]) + 1
        receipt = response_list[2]
        receipt = int(receipt.split("/")[5])
        date = response_list[3]
        date = datetime.datetime.strptime(date, "%d%m%y/%H%M%S")
        return serial, closing, receipt, date


class Closing(AbstractClosing):
    def get_cmd_bytes(self) -> bytes:
        return b'x/7//////'


class IsReady(AbstractIsReady):

    def get_cmd_byte_list(self) -> List[bytes]:
        return [b'X']  # receipt state, if ok return 0

    @staticmethod
    def parse_response(response: str) -> bool:
        state = int(response.split("/")[0])
        if state == 0:
            return True
        return False

    @staticmethod
    def is_ready(response: str) -> bool:
        return IsReady.parse_response(response)


class Receipt(AbstractReceipt):
    SELL_ROW_CMD = '3/S'
    DEFAULT_QUANTITY = 0
    DEFAULT_REP_N = 1

    PAYMENT_ROW_CMD = '5'

    def get_cmd_byte_list(self) -> List[bytes]:
        command_list = []
        for product in self.product_list:
            qty = str(product.get('quantity', self.DEFAULT_QUANTITY)).zfill(4)
            qty = qty[:-3]+"."+qty[-3:]
            rep_n = str(product.get('rep_n', self.DEFAULT_REP_N))
            price = str(product['price']).zfill(3)
            price = price[:-2]+"."+price[-2:]
            description = product.get('description', '')
            command = f'{self.SELL_ROW_CMD}/{description}//{qty}/{price}/{rep_n}/////'
            command_list.append(bytes(command, 'ascii'))
        for payment in self.payment_list:
            payment_id = str(payment['payment_id'])
            amount_paid = str(payment['amount_paid']).zfill(3)
            amount_paid = amount_paid[:-2]+"."+amount_paid[-2:]
            command = f'{self.PAYMENT_ROW_CMD}/{payment_id}/{amount_paid}///////'
            command_list.append(bytes(command, 'ascii'))

        return command_list


class Vp(AbstractVp):

    def get_cmd_byte_list(self) -> List[bytes]:
        bytes_list = []
        if self.perform_first_closing:
            bytes_list.append(Closing().get_cmd())
            self.current_closing += 1

        if self.send_receipt_1:  # Counts as 4 commands
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 1',
                    'price': self.receipt_value_1,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 1,  # Contanti
                    'amount_paid': self.receipt_value_1,
                }],
            ).get_cmd())

        # Enable lottery
        bytes_list.append(f'I/{self.lottery_code}/0'.encode('ascii'))
        if self.send_receipt_2:  # Counts as 4 commands
            bytes_list.append(Receipt(
                product_list=[{
                    'rep_n': 1,
                    'description': 'VP 2',
                    'price': self.receipt_value_2,
                    'iva_id': 1,
                }],
                payment_list=[{
                    'payment_id': 3,  # Bonifico
                    'amount_paid': self.receipt_value_2,
                }],
            ).get_cmd())

        if self.send_receipt_1:  # Void first receipt
            bytes_list.append(f'+/1/{self.fp_datetime.strftime("%d%m%y")}/{self.current_closing}/1////'.encode('ascii'))
        if self.send_receipt_2:  # Void second receipt
            bytes_list.append(f'+/1/{self.fp_datetime.strftime("%d%m%y")}/{self.current_closing}/2////'.encode('ascii'))
        bytes_list.append(Closing().get_cmd())
        self.current_closing += 1
        #mpdr print
        bytes_list.append(f'k/{self.fp_datetime.strftime("%d%m%y")}/{self.fp_datetime.strftime("%d%m%y")}/0'.encode("ascii"))
        #print SD report
        bytes_list.append(f'@/2/{self.current_closing-1}/{self.current_closing-1}/1/4///1'.encode('ascii'))

        return bytes_list


class HeadersCmd(AbstractCommand):

    def get_cmd_bytes(self) -> bytes:
        return b'O/'

    def send_cmd_bytes(self, header_list: List[Header]) -> bytes:
        return_string = "L"
        for header in header_list:
            return_string += f'/{header.get_formatting_flag()}/{header.description}/{header.get_alignment_flag()}'
        return return_string.encode("ascii")

    @staticmethod
    def parse_response(response: str) -> List[Header]:
        return_list = []
        split = response.split("/")

        for i in range(int(len(split)/2)):
            j = i*2
            descrizione = split[j]
            stripped_descrizione = descrizione.lstrip()
            formattazione = split[j+1]

            header = Header(
                header_id=i+1,
                description=descrizione.strip(),
                is_centered=len(descrizione) != len(stripped_descrizione),
                is_double_height=formattazione in ["1", "3"],
                is_double_width=formattazione in ["2", "3"],
                is_bold=formattazione == '4',
                is_italic=False,
                is_underlined=False
            )
            return_list.append(header)
            if i > 6:
                break
        return return_list

class IvasCmd(AbstractCommand):

    def get_cmd_bytes(self) -> bytes:
        return b'e/'

    @staticmethod
    def parse_response(response: str) -> List[Iva]:
        return_list = []
        split = response.split("/")

        for i in range(int(len(split)/3)):
            valore_iva = Decimal(split[i])
            natura = split[i+12]
            codice_ateco = int(split[i+24])
            codice_natura = 0
            if valore_iva:
                iva_type = "aliquota"
            else:
                codice_natura = int(natura)
                if codice_natura == 6:
                    iva_type = "ventilazione"
                else:
                    iva_type = "natura"

            iva = Iva(
                iva_id=i+1,
                iva_type=iva_type,
                aliquota_value=valore_iva,
                natura_code=codice_natura,
                ateco_code=codice_ateco
            )
            return_list.append(iva)
        return return_list

    @staticmethod
    def send_cmd_bytes(iva_list: List[Iva]) -> bytes:
        return_string = "b"
        for i in range(3):
            for iva in iva_list:
                if i == 0:
                    return_string += f'/{iva.aliquota_value}'
                elif i == 1:
                    return_string += f'/{iva.natura_code}'
                else:
                    return_string += f'/{iva.ateco_code}'
        return return_string.encode("ascii")


class CategoryCmd(AbstractCommand):

    def get_cmd_byte_list(self, max_categories_length: int) -> List[bytes]:
        list_category = []
        for i in range(max_categories_length):
            list_category.append(f":/{i+1}/".encode("ascii"))
        return list_category

    @staticmethod
    def parse_response(response_list: List[str]) ->List[Category]:
        return_list = []
        for i, category in enumerate(response_list):
            split = category.split("/")
            description = split[0]
            iva = split[1]
            category_id = i+1
            default_price = Decimal(split[3])
            max_price = Decimal(split[4])
            flags = split[6]
            is_active = bool(int(flags[0]))
            free_price = bool(int(flags[1]))
            category_type = "beni" if flags[7] == "0" else "servizi"

            category = Category(
                category_id=category_id,
                description=description,
                default_price=default_price,
                iva_id=iva,
                max_price=max_price,
                is_active=is_active,
                free_price=free_price,
                category_type=category_type,
            )
            return_list.append(category)
        return return_list

    @staticmethod
    def send_cmd_byte_list(category_list: List[Category]) -> List[bytes]:
        return_list = []
        for category in category_list:
            return_string = "N"
            return_string += f'/{category.id}'
            return_string += f'/{category.description}'
            return_string += f'/{category.iva_id}'
            return_string += f'/1'
            return_string += f'/{category.default_price}'
            return_string += f'/{category.max_price}'
            return_string += f'/0.00'
            return_string += f'/{category.get_flags()}'
            return_string += '//'
            return_list.append(return_string.encode("ascii"))
        return return_list

class PosCmd(AbstractCommand):

    def get_cmd_byte_list(self, max_poses_length: int) -> List[bytes]:
        list_poses = []
        for i in range(max_poses_length):
            list_poses.append(f'p/{i+1}'.encode("ascii"))
        return list_poses

    @staticmethod
    def parse_response(response_list: List[str]) -> List[Pos]:
        return_list = []
        for i, pos in enumerate(response_list):
            split = pos.split("/")
            description = split[0]
            indirizzo_ip = split[1]
            pos_id = i+1
            porta_tcp = int(split[2])
            id_terminale = split[3]
            id_cassa = split[4]

            pos = Pos(
                pos_id=pos_id,
                description=description,
                ip=indirizzo_ip,
                port=porta_tcp,
                terminal_id=id_terminale,
                rt_id=id_cassa
            )
            return_list.append(pos)
        return return_list

    @staticmethod
    def send_cmd_byte_list(pos_list: List[Pos]) -> List[bytes]:
        return_list = []
        for pos in pos_list:
            return_string = "P"
            return_string += f'/{pos.id}'
            return_string += f'/{pos.description}'
            return_string += f'/{pos.ip}'
            return_string += f'/{pos.port}'
            return_string += f'/{pos.terminal_id}'
            return_string += f'/{pos.rt_id}'
            return_string += f'/20'
            return_list.append(return_string.encode("ascii"))
        return return_list
