import csv
import json
import os
import sys
import uuid

import jinja2
import pika
import redis

# get rabbitmq env vars
rabbitmq_host = os.environ.get('RABBITMQ_SERVICE_HOST', 'localhost')
rabbitmq_port = os.environ.get('RABBITMQ_SERVICE_PORT', '6672')
rabbitmq_vhost = os.environ.get('RABBITMQ_VHOST', '/')
rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE', 'Case.CaseDelivery')
rabbitmq_exchange = os.environ.get('RABBITMQ_EXCHANGE', '')
rabbitmq_user = os.environ.get('RABBITMQ_USER', 'guest')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD', 'guest')

# rabbit global vars
rabbitmq_credentials = None
rabbitmq_connection = None
rabbitmq_channel = None

# get redis env vars
redis_host = os.environ.get('REDIS_SERVICE_HOST', 'localhost')
redis_port = os.environ.get('REDIS_SERVICE_PORT', '7379')
redis_db = os.environ.get('REDIS_DB', '0')

# globally load sampleunit message template
env = jinja2.Environment(loader=jinja2.FileSystemLoader(["./"]))
jinja_template = env.get_template("./utilities/sample_loader/message_template.xml")


def load_sample_file(context):
    init_rabbit()
    with open(context.sample_file_name) as f_obj:
        return sample_reader(f_obj, context.collection_exercise_id, context.action_plan_id, context.classifier_id)


def sample_reader(file_obj, ce_uuid, ap_uuid, ci_uuid):
    sampleunits = {}
    reader = csv.DictReader(file_obj, delimiter=',')
    count = 0
    for sampleunit in reader:
        sample_id = uuid.uuid4()
        sampleunits.update({"sampleunit:" + str(sample_id): create_json(sample_id, sampleunit)})
        publish_sampleunit(
            jinja_template.render(sample=sampleunit, uuid=sample_id, ce_uuid=ce_uuid, ap_uuid=ap_uuid, ci_uuid=ci_uuid))
        count += 1
        if count % 5000 == 0:
            sys.stdout.write("\r" + str(count) + " samples loaded")
            sys.stdout.flush()

    print('\nAll Sample Units have been added to the queue ' + rabbitmq_queue)
    rabbitmq_connection.close()
    write_sampleunits_to_redis(sampleunits)

    return sampleunits


def create_json(sample_id, sampleunit):
    sampleunit = {"id": str(sample_id), "attributes": sampleunit}

    return json.dumps(sampleunit)


def publish_sampleunit(message):
    rabbitmq_channel.basic_publish(exchange=rabbitmq_exchange,
                                   routing_key=rabbitmq_queue,
                                   body=str(message),
                                   properties=pika.BasicProperties(content_type='text/xml'))


def init_rabbit():
    global rabbitmq_credentials, rabbitmq_connection, rabbitmq_channel
    rabbitmq_credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    rabbitmq_connection = pika.BlockingConnection(
        pika.ConnectionParameters(rabbitmq_host,
                                  rabbitmq_port,
                                  rabbitmq_vhost,
                                  rabbitmq_credentials))
    rabbitmq_channel = rabbitmq_connection.channel()

    if rabbitmq_queue == 'localtest':
        rabbitmq_channel.queue_declare(queue=rabbitmq_queue)


def write_sampleunits_to_redis(sampleunits):
    redis_connection = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)

    print("Writing sampleunits to Redis")
    count = 0
    redis_pipeline = redis_connection.pipeline()
    for key, attributes in sampleunits.items():
        redis_connection.set(key, attributes)
        count += 1
        if count % 5000 == 0:
            sys.stdout.write("\r" + str(count) + " samples loaded")
            sys.stdout.flush()

    redis_pipeline.execute()
    print("Sample Units written to Redis")
