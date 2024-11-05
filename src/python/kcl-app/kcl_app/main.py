#### #!/usr/bin/env python
import datetime
import logging
import multiprocessing
import os
import sys
import threading
import time
from logging.handlers import QueueListener

import uvicorn
from amazon_kclpy import kcl
from amazon_kclpy.v3 import processor
from fastapi import FastAPI
from interface import healthcheck
from kcl_app.log.formetter import JsonFormatter
from kcl_app.service.event import EventType
from kcl_app.service.multiprocess_consumer import MultiProcessConsumer

# from multiprocessing import Process


class RecordProcessor(processor.RecordProcessorBase):
    def __init__(
        self,
        logger: logging.Logger,
        log_queue: multiprocessing.Queue,
        event_queue: multiprocessing.Queue,
    ):
        self._SLEEP_SECONDS = 5
        self._CHECKPOINT_RETRIES = 5
        self._CHECKPOINT_FREQ_SECONDS = 60
        self._largest_seq = (None, None)
        self._largest_sub_seq = None
        self._last_checkpoint_time = None
        self._logger = logger
        # self._consumer = Consumer(logger=self._logger, worker_size=5)
        self._consumer = MultiProcessConsumer(
            logger=logger,
            num_process=1,
            num_threads=10,
            log_queue=log_queue,
            event_queue=event_queue,
        )

    def log(self, message):
        sys.stderr.write(message)

    def initialize(self, initialiation_input):
        # self.log('initialize')
        self._logger.warning("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDddddata")
        self._logger.warning(f"{log_level}")

        self._largest_seq = (None, None)
        self._last_checkpoint_time = time.time()

    def checkpoint(self, checkpointer, sequence_number=None, sub_sequence_number=None):
        self.log("checkpoint")
        """
        Checkpoints with retries on retryable exceptions.

        :param amazon_kclpy.kcl.Checkpointer checkpointer: the checkpointer provided to either process_records
            or shutdown
        :param str or None sequence_number: the sequence number to checkpoint at.
        :param int or None sub_sequence_number: the sub sequence number to checkpoint at.
        """
        for n in range(0, self._CHECKPOINT_RETRIES):
            try:
                checkpointer.checkpoint(sequence_number, sub_sequence_number)
                return
            except kcl.CheckpointError as e:
                if "ShutdownException" == e.value:
                    #
                    # A ShutdownException indicates that this record processor should be shutdown. This is due to
                    # some failover event, e.g. another MultiLangDaemon has taken the lease for this shard.
                    #
                    print("Encountered shutdown exception, skipping checkpoint")
                    return
                elif "ThrottlingException" == e.value:
                    #
                    # A ThrottlingException indicates that one of our dependencies is is over burdened, e.g. too many
                    # dynamo writes. We will sleep temporarily to let it recover.
                    #
                    if self._CHECKPOINT_RETRIES - 1 == n:
                        sys.stderr.write(
                            "Failed to checkpoint after {n} attempts, giving up.\n".format(n=n)
                        )
                        return
                    else:
                        print(
                            "Was throttled while checkpointing, will attempt again in {s} seconds".format(
                                s=self._SLEEP_SECONDS
                            )
                        )
                elif "InvalidStateException" == e.value:
                    sys.stderr.write(
                        "MultiLangDaemon reported an invalid state while checkpointing.\n"
                    )
                else:  # Some other error
                    sys.stderr.write(
                        "Encountered an error while checkpointing, error was {e}.\n".format(e=e)
                    )
            time.sleep(self._SLEEP_SECONDS)

    def process_record(
        self, data: bytes, partition_key: str, sequence_number: int, sub_sequence_number: int
    ):
        """Called for each record that is passed to process_records.

        :param str data: The blob of data that was contained in the record.
        :param str partition_key: The key associated with this record.
        :param int sequence_number: The sequence number associated with this record.
        :param int sub_sequence_number: the sub sequence number associated with this record.
        """
        # logging.warn(f"data: {type(data)}")
        # logging.warn(f"partition_key: {type(partition_key)}")
        # logging.warn(f"sequence_number: {type(sequence_number)}")
        # logging.warn(f"sub_sequence_number: {type(sub_sequence_number)}")
        # logging.warning('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxeeeeeeeeeeeeeeeeeeeee')

        # data_type = type(data)
        # self._logger.warning(f"data_type = {data_type}")
        # self._logger.warning(
        #     "Record (Partition Key: {pk}, Sequence Number: {seq}, Subsequence Number: {sseq}, Data Size: {ds}, Data: {data})".format(
        #         pk=partition_key,
        #         seq=sequence_number,
        #         sseq=sub_sequence_number,
        #         ds=len(data),
        #         data=data,
        #     )
        # )
        ####################################
        # Insert your processing logic here
        ####################################
        # self._logger.warning(f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {threading.get_ident()}")
        self._consumer.process_record(data, sequence_number, sub_sequence_number)
        # self._logger.warning(f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< {threading.get_ident()}")
        # self.log("Record (Partition Key: {pk}, Sequence Number: {seq}, Subsequence Number: {sseq}, Data Size: {ds}"
        #          .format(pk=partition_key, seq=sequence_number, sseq=sub_sequence_number, ds=len(data)))

    def should_update_sequence(self, sequence_number, sub_sequence_number):
        """Determines whether a new larger sequence number is available.

        :param int sequence_number: the sequence number from the current record
        :param int sub_sequence_number: the sub sequence number from the current record
        :return boolean: true if the largest sequence should be updated, false otherwise
        """
        return (
            self._largest_seq == (None, None)
            or sequence_number > self._largest_seq[0]
            or (
                sequence_number == self._largest_seq[0]
                and sub_sequence_number > self._largest_seq[1]
            )
        )

    def process_records(self, process_records_input):
        """Called by a KCLProcess with a list of records to be processed and a
        checkpointer which accepts sequence numbers from the records to
        indicate where in the stream to checkpoint.

        :param amazon_kclpy.messages.ProcessRecordsInput process_records_input: the records, and metadata about the
            records.
        """
        try:
            for record in process_records_input.records:
                data = record.binary_data
                seq = int(record.sequence_number)
                sub_seq = record.sub_sequence_number
                key = record.partition_key
                self.process_record(data, key, seq, sub_seq)
                if self.should_update_sequence(seq, sub_seq):
                    self._largest_seq = (seq, sub_seq)

            #
            # Checkpoints every self._CHECKPOINT_FREQ_SECONDS seconds
            #
            if time.time() - self._last_checkpoint_time > self._CHECKPOINT_FREQ_SECONDS:
                self.checkpoint(
                    process_records_input.checkpointer,
                    str(self._largest_seq[0]),
                    self._largest_seq[1],
                )
                self._last_checkpoint_time = time.time()

        except Exception as e:
            self.log(
                "Encountered an exception while processing records. Exception was {e}\n".format(e=e)
            )

    def lease_lost(self, lease_lost_input):
        self.log("lease_lost")
        pass

    def shard_ended(self, shard_ended_input):
        self.log("shard_ended")
        pass

    def shutdown_requested(self, shutdown_requested_input):
        logging.warning("SHUTDOWN")
        time.sleep(5)
        self.log("shutdown_requested")
        pass


app = FastAPI()
app.include_router(healthcheck.router)


def run_http_server() -> None:
    uvicorn.run("kcl_app.main:app", host="0.0.0.0", port=8080)


def event_handler() -> None:
    started_at = datetime.datetime.now()
    results = 0
    timeout_waiting_for_available_worker = 0
    timeout_waiting_for_data = 0

    logger.warning("RESULT_LOG")
    while True:
        event = event_queue.get()
        if event.event_type == EventType.FINISHED_STREAM_DATA:
            results = results + event.extra["results"]
            seconds = (datetime.datetime.now() - started_at).total_seconds()
            logger.warning(f"FINISHED_STREAM_DATA: {results / seconds}")
            # logger.warning(f"event: {event}")
        elif event.event_type == EventType.TIMEOUT_WAITING_FOR_AVAILABLE_WORKER:
            timeout_waiting_for_available_worker += 1
            logger.warning(
                f"TIMEOUT_WAITING_FOR_AVAILABLE_WORKER: {timeout_waiting_for_available_worker/seconds}"
            )
        elif event.event_type == EventType.TIMEOUT_WAITING_FOR_DATA:
            timeout_waiting_for_data += 1
            logger.warning(f"TIMEOUT_WAITING_FOR_DATA: {timeout_waiting_for_data/seconds}")


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "INFO")
    # sys.stderr.write('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEe')

    formatter = JsonFormatter("%(asctime)s")
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)

    log_queue = multiprocessing.Queue()
    listener = QueueListener(log_queue, log_handler)  # queueを見るようにする
    listener.start()

    event_queue = multiprocessing.Queue()

    logging.basicConfig(handlers=[log_handler], level=log_level)
    logging.warning("WARN")

    logger = logging.getLogger(__name__)
    logger.warning("WARNING")
    logger.info("INFO")
    x = logging.LoggerAdapter(logger, {"key": "value"})
    x.warning("WARNINGWARNINGWARNINGWARNINGWARNING", extra={"F": "G"})

    # t1 = threading.Thread(target=run_http_server)
    # t1.start()
    t2 = threading.Thread(target=event_handler)
    t2.start()

    kclprocess = kcl.KCLProcess(
        RecordProcessor(logger=logger, log_queue=log_queue, event_queue=event_queue)
    )
    kclprocess.run()

    t2.join()
