#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#


from unittest import TestCase, main
import time
from pulsar import Client, \
            CompressionType, ConsumerType

from _pulsar import ProducerConfiguration, ConsumerConfiguration


class PulsarTest(TestCase):
    def test_producer_config(self):
        conf = ProducerConfiguration()
        conf.send_timeout_millis(12)
        self.assertEqual(conf.send_timeout_millis(), 12)

        self.assertEqual(conf.compression_type(), CompressionType.None)
        conf.compression_type(CompressionType.LZ4)
        self.assertEqual(conf.compression_type(), CompressionType.LZ4)

        conf.max_pending_messages(120)
        self.assertEqual(conf.max_pending_messages(), 120)

    def test_consumer_config(self):
        conf = ConsumerConfiguration()
        self.assertEqual(conf.consumer_type(), ConsumerType.Exclusive)
        conf.consumer_type(ConsumerType.Shared)
        self.assertEqual(conf.consumer_type(), ConsumerType.Shared)

        self.assertEqual(conf.consumer_name(), '')
        conf.consumer_name("my-name")
        self.assertEqual(conf.consumer_name(), "my-name")

    def test_simple_producer(self):
        client = Client('pulsar://localhost:6650/')
        producer = client.create_producer('persistent://sample/standalone/ns/my-python-topic')
        producer.send('hello')
        producer.close()
        client.close()

    def test_producer_send_async(self):
        client = Client('pulsar://localhost:6650/')
        producer = client.create_producer('persistent://sample/standalone/ns/my-python-topic')

        sent_messages = []

        def send_callback(producer, msg):
            sent_messages.append(msg)

        producer.send_async('hello', send_callback)
        producer.send_async('hello', send_callback)
        producer.send_async('hello', send_callback)

        time.sleep(0.1)
        self.assertEqual(len(sent_messages), 3)
        client.close()

    def test_producer_consumer(self):
        client = Client('pulsar://localhost:6650/')
        consumer = client.subscribe('persistent://sample/standalone/ns/my-python-topic-producer-consumer',
                                    'my-sub',
                                    consumer_type=ConsumerType.Shared)
        producer = client.create_producer('persistent://sample/standalone/ns/my-python-topic-producer-consumer')
        producer.send('hello')

        msg = consumer.receive(1000)
        self.assertTrue(msg)
        self.assertEqual(msg.data(), 'hello')

        try:
            msg = consumer.receive(100)
            self.assertTrue(False)  # Should not reach this point
        except:
            pass  # Exception is expected

        client.close()

    def test_message_listener(self):
        client = Client('pulsar://localhost:6650/')

        received_messages = []

        def listener(consumer, msg):
            print "Got message", msg
            received_messages.append(msg)
            consumer.acknowledge(msg)

        client.subscribe('persistent://sample/standalone/ns/my-python-topic-listener',
                         'my-sub',
                         consumer_type=ConsumerType.Exclusive,
                         message_listener=listener)
        producer = client.create_producer('persistent://sample/standalone/ns/my-python-topic-listener')
        producer.send('hello-1')
        producer.send('hello-2')
        producer.send('hello-3')

        time.sleep(0.1)
        self.assertEqual(len(received_messages), 3)
        self.assertEqual(received_messages[0].data(), "hello-1")
        self.assertEqual(received_messages[1].data(), "hello-2")
        self.assertEqual(received_messages[2].data(), "hello-3")
        client.close()


if __name__ == '__main__':
    main()
