"""
A simulator for Nokia 1830-PSS for testing purposes
"""

import os
import re
import logging

import sshim

logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

fixture_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fixtures')
logger.info(fixture_path)

class NokiaPSS1830Sim(object):
    AVAIL_COMMANDS = (
        (re.compile(r'sh[\w]*[ ]+ve[\w ]*'), 'show_version'),
        (re.compile(r'pag[\w]*[ ]+st[\w]*[ ]+di[\w ]*'), 'pagin_status_disable'),
        (re.compile(r'^[ ]*$'), 'empty'),
        (re.compile(r'sh[\w]*[ ]+red[\w ]*'), 'show_redundancy'),
        (re.compile(r'sh[\w]*[ ]+so[\w]*[ ]+up[\w]*[ ]+st[\w ]*'), 'show_software_upgrade_status'),
        (re.compile(r'co[\w]*[ ]+so[\w]*[ ]+up[\w]*[ ]+st[\w ]*'), 'show_software_upgrade_status'),
        (re.compile(r'sh[\w]*[ ]+ge[\w]*[ ]+na[\w ]*'), 'show_general_name'),
        (re.compile(r'sh[\w]*[ ]+ge[\w]*[ ]+ca[\w]*[ ]+ec[ ]*'), 'show_general_capacity_ec'),
    )


    def __init__(self, fixture_path, prompt='Nokia_1830PSS_Sim# '):
        self.prompt = prompt
        self.fixture_path = fixture_path
        self.fixture_data = {}

    def load_fixture(self, name):
        path = os.path.join(self.fixture_path, name)

        if path in self.fixture_data:
            return self.fixture_data[path]

        with open(path) as f:
            data = f.read()

        data = data.replace('\n', '\r\n')
        self.fixture_data[path] = data
        return data

    def command_not_found(self, command, fixture):
        return 'Error: command not found: %s' % command

    def empty(self, command, fixture):
        return ''

    def show_version(self, command, fixture):
        return self.load_fixture(fixture)

    def pagin_status_disable(self, command, fixture):
        return ''

    def show_redundancy(self, command, fixture):
        return self.load_fixture(fixture)

    def show_software_upgrade_status(self, command, fixture):
        return self.load_fixture(fixture)

    def show_general_name(self, command, fixture):
        return self.load_fixture(fixture)

    def show_general_capacity_ec(self, command, fixture):
        return self.load_fixture(fixture)

    def execute_command(self, command):
        for match, func_name in self.AVAIL_COMMANDS:
            if match.match(command):
                resp = getattr(self, func_name)(command, func_name)
                return u'\r\n'.join([resp, self.prompt])
        return u'\r\n'.join([self.command_not_found(command, None), self.prompt])


def welcome(script):
    """Simulate 1830PSS welcome banner after cli session
    """
    if script.username != 'cli':
        #TODO: terminate the session
        pass

    script.write('''
Linux EC1830-81-1 2.6.10_mvlcge401-8555-cplab #8 Thu Jun 7 13:39:42 EDT 2018 ppc GNU/Linux\r

Welcome to MontaVista(R) Linux(R) Carrier Grade Edition 4.0 (0600995).\r

Last login: Mon Sep 23 20:58:26 2019 from 192.168.0.101\r
Linux EC1830-81-1 2.6.10_mvlcge401-8555-cplab #8 Thu Jun 7 13:39:42 EDT 2018 ppc GNU/Linux\r

Welcome to MontaVista(R) Linux(R) Carrier Grade Edition 4.0 (0600995).\r
    ''')

    script.write('\r\nUsername: ')

    groups = script.expect(re.compile('(?P<username>.*)'), True).groupdict()
    username = groups['username']
    logger.info('Username %s provided' % username)

    script.write('Password: ')
    groups = script.expect(re.compile('(?P<password>.*)'), False).groupdict()
    password = groups['password']
    logger.info('Password %s provided', password)

    script.write('''
Last Login: Mon Sep 23 20:58:32 2019 from ssh_192.168.0.101:53238\r

Security compliance warning - Please check password status!\r

Nokia 1830 PSS, WAVELENGTH TRACKER\r
(c) 2018 Nokia.  All rights reserved.\r

   Legal Notices  applicable to  any  software   distributed  alone or in\r
   connection with the product to which this text pertains, are available\r
   at  NOS (Nokia Online Services)  with "1830  Photonic  Service  Switch\r
   (PSS) Software Legal Notice Details".\r

   This  system   is  restricted  solely to  Nokia  authorized  users for\r
   legitimate    business  purposes   only.    The actual   or  attempted\r
   unauthorized  access, use, or modification of this system  is strictly\r
   prohibited  by  Nokia.  Unauthorized  users  are  subject  to  Company\r
   disciplinary   proceedings and/or  criminal and  civil penalties under\r
   state, federal, or other applicable domestic and foreign laws.  Use of\r
   this  system may  be monitored  and  recorded for  administrative  and\r
   security reasons.  Anyone accessing this system expressly  consents to\r
   such  monitoring and is advised  that if  monitoring  reveals possible\r
   evidence of criminal activity, Nokia may provide  the evidence of such\r
   activity to law  enforcement  officials.   All  users must comply with\r
   Nokia   Corporate  Instructions  regarding  the  protection  of  Nokia\r
   information assets.\r
        ''')
    script.write('\r\nDo you acknowledge? (Y/N)? ')
    groups = script.expect(re.compile('(?P<answer>[YyNn])'), True).groupdict()
    answer = groups['answer']
    logger.info('got answer %s (%s)' % (answer, answer.upper() == 'Y'))
    script.writeline('Alarm Status:  Critical-9   Major-3   Minor-2 Warning-0\n')
    script.write('Nokia_1830PSS_Sim# ')


def main(script):
    pss = NokiaPSS1830Sim(fixture_path)
    welcome(script)
    logger.info('running main script')
    while True:
        groups = script.expect(re.compile('(?P<command>.*)'), True).groupdict()
        command = groups['command']
        logger.info('got command %s' % command)
        if command == 'logout':
            script.writeline('Logging out....')
            break
        else:
            script.write(pss.execute_command(command))

server = sshim.Server(main, port=0)

def run_forever(server):
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()

if __name__ == "__main__":
    run_forever(server)
