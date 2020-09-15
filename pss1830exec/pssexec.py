#!/usr/bin/env python

from __future__ import print_function
import sys
import time
import re
import argparse
import logging
import warnings
from datetime import datetime

warnings.filterwarnings("ignore")

from pss1830ssh.pss1830cli import PSS1830Cli
from pss1830ssh.pss1830root import PSS1830Root

from __version__ import VERSION

RET_LOGIN_FAIL = 1
RET_COMMAND_FAIL = 2
RET_SHELF_LOGIN_FAIL = 3
RET_UNKNOWN_ERROR = 4
RET_WRONG_ARGS = -1

def err(msg):
    pass

def out(msg):
    print(msg, end='')

def get_parser():
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Execute CLI/root commands on a 1830-PSS NE")
    parser.add_argument('-m', '--mode', type=str, choices=['root', 'cli'], required=True,
                        help="Mode for commands: can be either as root or cli")
    parser.add_argument('--host', type=str, help="IP address of PSS node", required=True)
    parser.add_argument('--port', help="Port (default: 22)", default=22, type=int)
    parser.add_argument('-u', '--user', required=True, help="Username", type=str)
    parser.add_argument('-p', '--pass', metavar="p", required=True, help="Password", type=str)
    parser.add_argument('-l', '--slot', type=str, 
                        help="Run command in a card at shelf/slot (e.g. 2/1). Applicable for root mode only")
    parser.add_argument('-c', '--command', required=True, nargs="+", 
                        help="Command(s). Can be repeated", action="append", type=str)
    parser.add_argument('-w', '--timeout',
                        help="Timeout (s) for sending/waiting for commands/results", type=int)
    parser.add_argument('-V', '--verbose', type=str, choices=['info', 'debug'], help="Enable debug mode")
    parser.add_argument('-v', '--version', action="version", version=VERSION)

    return parser

def get_config(args):
    config = {}
    config['mode'] = args.mode
    config['host'] = args.host
    config["port"] = args.port
    config["commands"] = [cmd for group in args.command for cmd in group]
    config["username"] = args.user
    config["password"] = vars(args)['pass']
    config["slot"] = args.slot
    config['timeout'] = args.timeout
    return config

def exit(msg, retcode=0):
    out('\n%s\n' % msg)
    out('\nFinished: %s\n' % datetime.now())
    sys.exit(retcode)

def run_cmds(pss, commands):
    for command in commands:
        try:
            out('\n%s %s\n' % (pss.prompt, command))
            for data in pss.execute(command):
                out(data)
        except Exception as e:
            pss.close()
            exit('Error during executing command (%s): %s\n' % (command, e), RET_COMMAND_FAIL)
        time.sleep(0.0)

def run(config):
    out('Start execution: %s\n' % datetime.now())
    if config['mode'] == 'root':
        PSS = PSS1830Root
        if config['slot']:
            try:
                shelf, slot = config['slot'].split('/')
                config['slot'] = (shelf, slot)
            except:
                exit('Wrong argument format provided: %s' % config['slot'], RET_WRONG_ARGS)
    else:
        PSS = PSS1830Cli
        if config['slot']:
            exit('Shelf option is not supported in CLI mode', RET_WRONG_ARGS)

    pss = PSS(config['host'], config['port'], config['username'], config['password'])
    if config['timeout']:
        pss.TIMEOUT = config['timeout']
    try:
        pss.open()
        assert pss.connected and pss.prompt
    except:
        exit('Failed to login to the node', 1)
    
    if config["slot"]:
        try:
            shelf, slot = config['slot']
            pss.login_to_slot(shelf, slot)
            run_cmds(pss, config['commands'])
            pss.logout_from_slot()
        except:
            pss.close()
            exit('Failed to login to shelf: %s' % config['slot'], RET_SHELF_LOGIN_FAIL)
    else:
        run_cmds(pss, config['commands'])

    pss.close()
    out('\nFinished: %s\n' % datetime.now())

def main():
    parser = get_parser()
    args = parser.parse_args()
    config = get_config(args)
    if args.verbose:
        logging.basicConfig(level=args.verbose.upper())
    try:
        run(config)
    except Exception as exc:
        exit('Exited with error: %s' % exc, RET_UNKNOWN_ERROR)

if __name__ == '__main__':
    main()
