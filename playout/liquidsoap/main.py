""" Runs Airtime liquidsoap
"""
import argparse
import logging
import os
import subprocess

from pypo import pure

from . import generate_liquidsoap_cfg

PYPO_HOME = "/var/tmp/airtime/pypo/"


def run():
    """Entry-point for this application"""
    print("Airtime Liquidsoap")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="run in debug mode", action="store_true")
    args = parser.parse_args()

    os.environ["HOME"] = PYPO_HOME

    if args.debug:
        logging.basicConfig(level=getattr(logging, "DEBUG", None))

    generate_liquidsoap_cfg.run()
    """ check liquidsoap version so we can run a scripts matching the liquidsoap minor version """
    liquidsoap_version = subprocess.check_output(
        "liquidsoap 'print(liquidsoap.version) shutdown()'",
        shell=True,
        universal_newlines=True,
    )[0:3]
    script_path = os.path.join(
        os.path.dirname(__file__), liquidsoap_version, "ls_script.liq"
    )
    exec_args = [
        "/usr/bin/liquidsoap",
        "libretime-liquidsoap",
        "--verbose",
        script_path,
    ]
    if args.debug:
        print(f"Liquidsoap {liquidsoap_version} using script: {script_path}")
        exec_args.append("--debug")
    os.execl(*exec_args)
