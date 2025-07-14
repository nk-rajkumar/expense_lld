"""
Unique id generator using Twitter snowflake algorithm.
id structure:
    epoch timestamp in millisecond - 41 bits
    node id - 10 bits --> 1024 nodes
    process id - 5 bits --> 32 process ids
    sequence no - 5 bits --> 32 request per millisecond (5k TPS)
"""

import os
import uuid
from datetime import datetime, timezone
from time import sleep

# Wednesday, 1 January 2020 00:00:00 GMT
startepoch = 1577836800000
mult = 1000
node_id_bits = 10
process_id_bits = 5
sequence_bits = 5
process_id_mask = -1 ^ (-1 << process_id_bits)
node_id_mask = -1 ^ (-1 << node_id_bits)
process_id_shift = sequence_bits
node_id_shift = sequence_bits + process_id_bits
timestamp_left_shift = sequence_bits + process_id_bits + node_id_bits
sequence_mask = -1 ^ (-1 << sequence_bits)
snowflake_generator = None


def get_snowflake_generator():
    global snowflake_generator
    if not snowflake_generator:
        snowflake_generator = snowflake_id_gen()
    return snowflake_generator


def snowflake_id_gen(node_id=None, process_id=None):
    """
    initializer method which constructs and returns a snowflake id generator object

    Usage::
        # Node id and process id are optional, default values are mac address for node id and os.pid for process id
        >> id_gen = snowflake_id_gen(Node_id, process_id)
        >> next(id_gen)

    :param node_id:
    :type node_id:
    :param process_id:
    :type process_id:
    :return:
    :rtype:
    """
    worker_id = create_worker_id(node_id, process_id)
    id_gen = generator(worker_id)
    return id_gen


def create_worker_id(node_id=None, process_id=None):
    """
    Helper function to generate a 15 bit worker id.
    Worker id structure:
        node id - 10 bits --> 1024 nodes
        process id - 5 bits --> 32 process ids
    node_id and process_id defaults to mac_address and os.pid respectively
    :param node_id:
    :type node_id:
    :param process_id:
    :type process_id:
    :return:
    :rtype:
    """
    node_id = node_id or uuid.getnode()
    process_id = process_id or os.getpid()
    node_id = node_id & node_id_mask
    process_id = process_id & process_id_mask
    worker_id = (node_id << node_id_shift) | (process_id << process_id_shift)
    return worker_id


def generator(worker_id):
    """
    Core generator function which uses the worker_id to generate a 64-bit unique id which is sortable.
    id structure:
            epoch timestamp in millisecond - 41 bits
            worker id - 15 bits --> 32767 unique worker ids
            sequence no - 5 bits --> 32 request per millisecond (5k TPS)
    pseudocode:
            compute utc time in milliseconds
            initialise sequence number to 0
            construct unique snowflake id using the above structure.
                Use left shift to move the timestamp bits to accommodate the worker id and sequence no
                Use left shift to move the worker id to accommodate the sequence no
                Use bitwise OR operator to merge all three entities --> timestamp | worker_id | sequence id
    :param worker_id:
    :type worker_id:
    :return:
    :rtype:
    """
    last_timestamp = -1
    sequence = 0

    while True:
        timestamp = int(datetime.now(timezone.utc).timestamp() * mult)
        if last_timestamp == timestamp:
            sequence = (sequence + 1) & sequence_mask
            if sequence == 0:
                sequence = -1 & sequence_mask
                # sleep for 1 millisecond if Sequence number becomes 0 to ensure
                # that next iteration succeeds with the next set of sequence numbers
                sleep(1 / mult)
                continue
        else:
            sequence = 0

        last_timestamp = timestamp

        yield (
            ((timestamp - startepoch) << timestamp_left_shift) | worker_id | sequence
        )


def snowflake_id_gen_for_timestamp(timestamp):
    """
    node id can be max of 1024 and process id can be max of 32
    timestamp inc can be maximum of 32768 events per second if it crosses it there might be duplicate id after that
    @param timestamp:
    @return:
    """
    node_id = timestamp.inc
    process_id = (node_id // node_id_mask) + 1
    node_id = (node_id % node_id_mask) + 1
    worker_id = create_worker_id(node_id=node_id, process_id=process_id)
    return (
        ((timestamp.time * mult - startepoch) << timestamp_left_shift) | worker_id | 1
    )
