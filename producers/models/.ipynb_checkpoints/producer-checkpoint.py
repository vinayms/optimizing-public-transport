"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)
BROKER_URL = "PLAINTEXT://localhost:9092,PLAINTEXT://localhost:9093,PLAINTEXT://localhost:9094"
SCHEMA_REGISTRY_URL="PLAINTEXT://localhost:8081"

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        #
        # TODO: Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        #
        #
        self.broker_properties = {
            "bootstrap.servers":BROKER_URL,
            #"client.id":"cta_1",
            #"linger.ms":10000,
            #"compression.type":"lz4",
            "schema.registry.url": "http://localhost:8081"
            #"queue.buffering.mx.messages":100000
        }
        self.admin_client = AdminClient({"bootstrap.servers":BROKER_URL})

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # TODO: Configure the AvroProducer
        #schema_registry = CachedSchemaRegistryClient(SCHEMA_REGISTRY_URL)
        self.producer = AvroProducer(config=self.broker_properties,
                                    #schema_registry=schema_registry,
                                    default_key_schema=self.key_schema,
                                    default_value_schema=self.value_schema
                                    )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        #
        #
        # TODO: Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.
        #
        #
        if self.topic_exists(self.topic_name):
            return
        logger.info(f"Creating new topic :{self.topic_name}")
        topic_meta = self.admin_client.list_topics()
        if topic_meta.topics.get(self.topic_name) is None:
            fs = self.admin_client.create_topics(
            [NewTopic(topic=self.topic_name,
                      num_partitions=self.num_partitions,
                      replication_factor=self.num_replicas)])
            for topic, f in fs.items():
                try:
                    f.result()
                    print("Topic {} created".format(topic))
                except Exception as e:
                    print("Failed to create topic {} with error {} ".format(topic,e))
        
    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        logger.info("closing producer")
        self.producer.flush(timeout=5)

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
    
    def topic_exists(self, topic_name):
        """Checks if the given topic exists"""
        topic_metadata = self.admin_client.list_topics(timeout=5)
        return topic_name in set(t.topic for t in iter(topic_metadata.topics.values()))
