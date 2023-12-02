import json
from function.main import get_fp_instance, get_fp_class
from function.models import Fp
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)
patch_all()


def lambda_handler(event, context):
    logger.warning('STARTING SCRIPT INFO...')
    try:
        body = json.loads(event["body"])
        fp = Fp(**body)
        fp_instance = get_fp_instance(get_fp_class(fp.producer), fp)

        if fp_instance is None:
            raise NotImplementedError(f"Producer {fp.producer} not supported")
        result = fp_instance.serialize()
        return {
            "statusCode": 201,
            "body": json.dumps({result})
        }
    except NotImplementedError as err:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": err
            })
        }

    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": "Something went wrong. Unable to parse data !"
            })
        }
