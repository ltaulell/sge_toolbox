#!/usr/bin/env python3
# coding: utf-8
#
# PSMN: $Id: qconf_addexec3.py 971 2019-03-07 11:14:50Z gruiick $
#

"""
    add one or multiple hostnames to SGE Hosts list, need ClusterShell
    API (for NodeSet).

    for -Aconf/-as, temporary file MUST match hostname

TODO:

FIXME:

DOC/DONE:
    * fichier temporaire -> tempfile.gettempdir() ?
    https://docs.python.org/dev/library/tempfile.html
    https://docs.python.org/2/library/tempfile.html
"""

import sys
import os
import argparse
import distutils.spawn

import execo
from ClusterShell.NodeSet import NodeSet


OPTIONS = {'-Ae': False, '-Aconf': False, '-as': False}


def query_yes_no(question, default='no'):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {'yes': 'yes', 'y': 'yes', 'ye': 'yes',
             'no': 'no', 'n': 'no',
             'ya': 'yes2all'
             }
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: {}'.format(default))

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid.keys():
            return valid[choice]
        else:
            print("Please answer 'yes' or 'no' (or 'y' or 'n').")


def verif_exec(binaire):
    """ 'which-like' function

    return the complete path of 'binaire', if in $PATH
    """
    try:
        cmd_exist = distutils.spawn.find_executable(binaire)
        if cmd_exist is None:
            execo.log.logger.info('Command not found: ' + binaire)

        else:
            execo.log.logger.debug('found:')
            execo.log.logger.debug(str(cmd_exist))

            return cmd_exist

    except OSError as error:
        execo.log.logger.critical('Execution failed:')
        execo.log.logger.critical(str(error))


def get_args():
    """ get arguments from CLI """
    parser = argparse.ArgumentParser(description='Add host(s) to SGE')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='toggle debug on AND dryrun')
    group = parser.add_mutually_exclusive_group(required=True)
    # only one at a time : simple conf OR exec host OR submit host
    group.add_argument('-c', action='store_true',
                       help='Add host(s) configuration',
                       default=False)
    group.add_argument('-e', action='store_true',
                       help='Add exec host(s) configuration',
                       default=False)
    group.add_argument('-s', action='store_true',
                       help='Add submit host(s) configuration',
                       default=False)
    parser.add_argument('host', type=str, help='host(s), nodeset syntax')
    return parser.parse_args()


def startup():
    """ set running options """
    largs = get_args()
    if largs.debug:
        execo.log.logger.setLevel('DEBUG')

    # toggle the one whose True
    OPTIONS['-Aconf'] = largs.c
    OPTIONS['-Ae'] = largs.e
    OPTIONS['-as'] = largs.s

    execo.log.logger.debug(largs)

    return largs


if __name__ == '__main__':
    args = startup()

    execo.log.logger.debug(args.host)
    execo.log.logger.debug(OPTIONS)

    qconf = str(verif_exec("qconf"))

    nodes = NodeSet(args.host)

    gonogo = 'no'

    for node in nodes:
        filename = str(node) + '.psmn.ens-lyon.fr'
        execo.log.logger.debug('file :' + filename)
        # should be with:/try: ?
        ftemp = open(filename, 'w')
        # with open(filename, 'w') as ftemp:
        ftemp.write('hostname              ' +
                    str(node) + '.psmn.ens-lyon.fr\n')
        ftemp.write('load_scaling          NONE\n')
        ftemp.write('complex_values        NONE\n')
        ftemp.write('user_lists            NONE\n')
        ftemp.write('xuser_lists           NONE\n')
        ftemp.write('projects              NONE\n')
        ftemp.write('xprojects             NONE\n')
        ftemp.write('usage_scaling         NONE\n')
        ftemp.write('report_variables      NONE\n')

        if args.debug:
            ftemp = open(filename, "r")
            ftemp.seek(0)
            execo.log.logger.debug(ftemp.name)
            print(ftemp.read())

        if gonogo not in ['yes2all']:
            gonogo = query_yes_no('Add ' + node + '?', gonogo)
            if any(gonogo in w for w in ['yes', 'yes2all']):
                ftemp.seek(0)  # ?
                qconf_result = 0
                option = ' '.join([key for key, value in OPTIONS.items() if value is True])
                cmd = ' '.join([qconf, option, ftemp.name])

                if not args.debug:
                    try:
                        process = execo.process.Process(cmd, shell=True).run()

                    except execo.exception.ProcessesFailed:
                        execo.log.logger.exception('Process error')
                        sys.exit(1)

                    if process.exit_code != 0:
                        execo.log.logger.critical('process:\n%s', process)
                        execo.log.logger.warning('process stdout:\n%s', process.stdout)
                        execo.log.logger.warning('process stderr:\n%s', process.stderr)
                        sys.exit(1)

                    execo.log.logger.info(node + ' done')

                else:
                    execo.log.logger.debug(cmd)

            elif gonogo is "no":
                ftemp.close()
                # on sort au premier 'no'
                sys.exit("noGo, exiting...")

        ftemp.close()
        os.unlink(ftemp.name)

    print("done.")
