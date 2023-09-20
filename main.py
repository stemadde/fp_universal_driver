import configparser
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_fp_instance(fp_class: type, config: configparser.ConfigParser):
    fp = fp_class(
        ip=config['DEFAULT']['FP_IP'],
        port=int(config['DEFAULT']['FP_PORT']),
        categories=[],
        plus=[],
        ivas=[],
        payments=[],
        headers=[],
        poses=[],
        protocol=config['DEFAULT']['FP_PROTOCOL'],
        serial=config['DEFAULT']['FP_SERIAL'],
    )
    return fp


def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(BASE_PATH, 'config.ini'))
    producer = config['DEFAULT']['FP_PRODUCER']
    vp_args = {
        "value1": int(config['DEFAULT']['RECEIPT_VALUE_1']),
        "value2": int(config['DEFAULT']['RECEIPT_VALUE_2']),
        "lottery_code": config['DEFAULT']['LOTTERY_CODE'],
    }

    if producer == '96':
        from src.Prod96.fp import FP
        fp = get_fp_instance(FP, config)
        fp.send_vp(**vp_args)
    elif producer == '8A':
        from src.Prod8A.fp import FP
        fp = get_fp_instance(FP, config)
        fp.send_vp(**vp_args)

    else:
        print("Producer not supported")


if __name__ == '__main__':
    main()
    quit(0)
