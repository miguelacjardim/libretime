import traceback

"""
Python part of radio playout (pypo)

This function acts as a gateway between liquidsoap and the server API.
Mainly used to tell the platform what pypo/liquidsoap does.

Main case:
 - whenever LS starts playing a new track, its on_metadata callback calls
   a function in ls (notify(m)) which then calls the python script here
   with the currently starting filename as parameter
 - this python script takes this parameter, tries to extract the actual
   media id from it, and then calls back to the API to tell about it about it.

"""

import json
import logging.config
import sys
from optparse import OptionParser

# custom imports
# from util import *
from api_clients import version1 as api_client

# additional modules (should be checked)
from configobj import ConfigObj

LOG_LEVEL = logging.INFO
LOG_PATH = "/var/log/airtime/pypo/notify.log"

# help screeen / info
usage = "%prog [options]" + " - notification gateway"
parser = OptionParser(usage=usage)

# Options
parser.add_option(
    "-d",
    "--data",
    help="Pass JSON data from Liquidsoap into this script.",
    metavar="data",
)
parser.add_option(
    "-m",
    "--media-id",
    help="ID of the file that is currently playing.",
    metavar="media_id",
)
parser.add_option(
    "-e",
    "--error",
    action="store",
    dest="error",
    type="string",
    help="Liquidsoap error msg.",
    metavar="error_msg",
)
parser.add_option("-s", "--stream-id", help="ID stream", metavar="stream_id")
parser.add_option(
    "-c",
    "--connect",
    help="Liquidsoap connected",
    action="store_true",
    metavar="connect",
)
parser.add_option(
    "-t",
    "--time",
    help="Liquidsoap boot up time",
    action="store",
    dest="time",
    metavar="time",
    type="string",
)
parser.add_option(
    "-x", "--source-name", help="source connection name", metavar="source_name"
)
parser.add_option(
    "-y", "--source-status", help="source connection status", metavar="source_status"
)
parser.add_option(
    "-w",
    "--webstream",
    help="JSON metadata associated with webstream",
    metavar="json_data",
)
parser.add_option(
    "-n",
    "--liquidsoap-started",
    help="notify liquidsoap started",
    metavar="json_data",
    action="store_true",
    default=False,
)


# parse options
(options, args) = parser.parse_args()

# Set up logging
logging.captureWarnings(True)
logFormatter = logging.Formatter(
    "%(asctime)s [%(module)s] [%(levelname)-5.5s]  %(message)s"
)
rootLogger = logging.getLogger()
rootLogger.setLevel(LOG_LEVEL)

fileHandler = logging.handlers.RotatingFileHandler(
    filename=LOG_PATH, maxBytes=1024 * 1024 * 30, backupCount=8
)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)
logger = rootLogger

# need to wait for Python 2.7 for this..
# logging.captureWarnings(True)

# loading config file
try:
    config = ConfigObj("/etc/airtime/airtime.conf")

except Exception as e:
    logger.error("Error loading config file: %s", e)
    sys.exit()


class Notify:
    def __init__(self):
        self.api_client = api_client.AirtimeApiClient(logger=logger)

    def notify_liquidsoap_started(self):
        logger.debug("Notifying server that Liquidsoap has started")
        self.api_client.notify_liquidsoap_started()

    def notify_media_start_playing(self, media_id):
        logger.debug("#################################################")
        logger.debug("# Calling server to update about what's playing #")
        logger.debug("#################################################")
        response = self.api_client.notify_media_item_start_playing(media_id)
        logger.debug("Response: " + json.dumps(response))

    # @pram time: time that LS started
    def notify_liquidsoap_status(self, msg, stream_id, time):
        logger.info("#################################################")
        logger.info("# Calling server to update liquidsoap status    #")
        logger.info("#################################################")
        logger.info("msg = " + str(msg))
        response = self.api_client.notify_liquidsoap_status(msg, stream_id, time)
        logger.info("Response: " + json.dumps(response))

    def notify_source_status(self, source_name, status):
        logger.debug("#################################################")
        logger.debug("# Calling server to update source status        #")
        logger.debug("#################################################")
        logger.debug("msg = " + str(source_name) + " : " + str(status))
        response = self.api_client.notify_source_status(source_name, status)
        logger.debug("Response: " + json.dumps(response))

    def notify_webstream_data(self, data, media_id):
        logger.debug("#################################################")
        logger.debug("# Calling server to update webstream data       #")
        logger.debug("#################################################")
        response = self.api_client.notify_webstream_data(data, media_id)
        logger.debug("Response: " + json.dumps(response))

    def run_with_options(self, options):
        if options.error and options.stream_id:
            self.notify_liquidsoap_status(
                options.error, options.stream_id, options.time
            )
        elif options.connect and options.stream_id:
            self.notify_liquidsoap_status("OK", options.stream_id, options.time)
        elif options.source_name and options.source_status:
            self.notify_source_status(options.source_name, options.source_status)
        elif options.webstream:
            self.notify_webstream_data(options.webstream, options.media_id)
        elif options.media_id:
            self.notify_media_start_playing(options.media_id)
        elif options.liquidsoap_started:
            self.notify_liquidsoap_started()
        else:
            logger.debug(
                "Unrecognized option in options({}). Doing nothing".format(options)
            )


def run():
    print()
    print("#########################################")
    print("#           *** pypo  ***               #")
    print("#     pypo notification gateway         #")
    print("#########################################")

    # initialize
    try:
        n = Notify()
        n.run_with_options(options)
    except Exception as e:
        print(traceback.format_exc())
