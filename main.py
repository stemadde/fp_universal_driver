import configparser
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def main():
    config = configparser.ConfigParser()
    config.read(os.path.join(BASE_PATH, 'config.ini'))
    producer = config['DEFAULT']['FP_PRODUCER']
    if producer == '96':
        from src.Prod96.fp import FP
        fp = FP(
            ip=config['DEFAULT']['FP_IP'],
            port=int(config['DEFAULT']['FP_PORT']),
            categories=[],
            plus=[],
            ivas=[],
            payments=[],
            headers=[],
            poses=[],
            protocol='tcp',
            serial=config['DEFAULT']['FP_SERIAL'],
        )
        fp.send_vp()
    else:
        print("Producer not supported")


if __name__ == '__main__':
    main()
    quit(0)
