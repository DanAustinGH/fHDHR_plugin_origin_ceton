import base64
import re
import socket
import time
import xmltodict

from random import randint


class Plugin_OBJ():

    def __init__(self, plugin_utils, stream_args, tuner):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils
        self.stream_args = stream_args
        self.tuner = tuner

        self.bytes_per_read = int(self.plugin_utils.config.dict["streaming"]["bytes_per_read"])

    def open_socket(self, port):
        self.plugin_utils.logger.info('Opening socket on UDP port %s' % port)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("", port))
            sock.settimeout(5)
        except socket.error as e:
            self.plugin_utils.logger.info('Failed to open socket, will retry...')
            time.sleep(5)
            return self.open_socket(port)

    def direct_stream(self, instance, port):
        self.plugin_utils.logger.info('Attempting to direct stream...')
        sock = self.open_socket(port)


        def generate():
            chunk_counter = 1
            try:
                while self.tuner.tuner_lock.locked():
                    chunk = bytearray(b" " * self.bytes_per_read)
                    size = sock.recv_into(chunk)
                    buf = chunk[:size]

                    header_size = 12 + 4 * (buf[0] & 16)

                    chunk = buf[header_size:]
                    chunk_size = int(sys.getsizeof(chunk))
                    self.plugin_utils.logger.info("Passing Through Chunk #%s with size %s" % (chunk_counter, chunk_size))

                    yield chunk
                    self.tuner.add_downloaded_size(chunk_size)

                    chunk_counter += 1

                self.plugin_utils.logger.info("Connection Closed: Tuner Lock Removed")

            except GeneratorExit:
                self.plugin_utils.logger.info("Connection Closed.")
            except Exception as e:
                self.plugin_utils.logger.info("Connection Closed: %s" % e)
            finally:
                self.plugin_utils.logger.info("Connection Closed: Tuner Lock Removed")
                self.close_stream(instance, "")
                # raise TunerError("806 - Tune Failed")

        return generate()












