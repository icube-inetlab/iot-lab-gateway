#! /usr/bin/python
# -*- coding:utf-8 -*-


"""
Simple expect implementation

Author: Gaëtan Harter gaetan.harter@inria.fr
"""

import re
import time
import datetime
import sys
import serial


class SerialExpect(object):
    """ Simple Expect implementation for serial """

    def __init__(self, tty, baudrate, verbose=False):
        self.serial_fd = serial.Serial(tty, baudrate, timeout=0.1)
        self.serial_fd.flushInput()
        self.verb = verbose

    def __del__(self):
        self.serial_fd.close()

    def send(self, data):
        """ Write given data to serial with newline"""
        self.serial_fd.write(data + '\n')

    def expect_list(self, pattern_list, timeout=float('+inf')):
        """ expect multiple patterns """
        # concatenate in a single pattern
        pattern = '(' + ')|('.join(pattern_list) + ')'
        return self.expect(pattern, timeout)

    def expect(self, pattern, timeout=float('+inf')):
        """ expect pattern
        return matching string on match
        return '' on timeout
        It cannot match multiline pattern correctly """

        if '\n' in pattern:
            raise ValueError("Does not handle multiline patterns with '\\n'")

        end_time = time.time() + timeout

        buff = ''
        regexp = re.compile(pattern)
        while True:
            # get new data
            read_bytes = self.serial_fd.read(size=16)  # timeout 0.1

            if end_time <= time.time():
                # last read_bytes may not be printed but don't care
                return ''  # timeout

            # no data, continue
            if not read_bytes:
                continue

            # add new bytes to remaining of last line
            # no multiline patterns
            buff = buff.split('\n')[-1] + read_bytes

            # print each line with timestamp on front
            if self.verb:
                timestamp = datetime.datetime.now().time()
                line = read_bytes.replace('\n', '\n%s: ' % timestamp)
                sys.stdout.write(line)
                sys.stdout.flush()

            match = regexp.search(buff)
            if match:
                return match.group(0)

            # continue
