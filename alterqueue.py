#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# $Id: alterqueue.py | Wed Sep 27 17:55:07 2017 +0200 | Loïs Taulelle  $
# SPDX-License-Identifier: CECILL-B OR BSD-2-Clause

"""
DOC:
    remplace le oneliner qalter par un équivalent python plus simple, traitement par lots
    for i in $(qstat -u "login" -s p | awk '{print $1}'); do qalter -q queue1,queue2,queue3 $i; done

REFS:
    https://docs.python.org/3/library/stdtypes.html

TODO:
    * faire un filtre sur user + queue ?
    * pouvoir changer le -pe, si nécessaire

FIXME:

DONE:
    See @END
"""

import sys
import argparse
import subprocess
import distutils.spawn
import distutils.util


def queryYesNo(question):
    """
    Ask a yes/no question via input() and return 1 if yes, 0 elsewhere.
    """
    print(question + " [y/n]?")
    while True:
        try:
            return distutils.util.strtobool(input().lower())
        except ValueError:
            print('Répondre par "y" ou "n".')


def verifExec(binaire):
    try:
        cmd_exist = distutils.spawn.find_executable(binaire)
        if cmd_exist is None:
            print("Command not found:", binaire, file=sys.stderr)
        else:
            if args.d:
                print("Command found:", cmd_exist, file=sys.stderr)
            return cmd_exist
    except OSError as error:
        print("Execution failed:", error, file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Altère les jobs en attente d'un utilisateur (modification des queues)")
    parser.add_argument("-d", action="store_true", help="Active le debug")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--mono", action="store_true",
                       help="Tous les jobs MONO-processeur")
    group.add_argument("-M", "--multi", action="store_true",
                       help="Tous les jobs MULTI-processeurs")
    group.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="TOUS les jobs (default).",
        default=True)
    parser.add_argument("login", type=str, help="SGE user login")
    parser.add_argument(
        "queues",
        type=str,
        help="SGE queues (virgule, sans espace)")
    args = parser.parse_args()

    # debug
    if args.d:
        print(args)
        print(args.login)
        print(type(args.login))
        print(args.queues)
        print(type(args.queues))

    qstat = str(verifExec("qstat"))
    qalter = str(verifExec("qalter"))

    # get joblist
    str_joblist = subprocess.check_output(
        qstat + " -u " + args.login + " -s p", shell=True)
    if args.d:
        print(type(str_joblist))
        print(str_joblist)

    # joblist est une str, transformer en liste de lignes
    lst_joblist = bytes.decode(str_joblist).splitlines()

    # nettoyage des premières entrées (entêtes SGE)
    if args.d:
        print(type(lst_joblist))
        print(lst_joblist[0])
        print(str(len(lst_joblist)) + " éléments")

    if "job-ID" in lst_joblist[0]:
        del lst_joblist[0]

    if args.d:
        print(lst_joblist[0])
        print(str(len(lst_joblist)) + " éléments")

    if "----" in lst_joblist[0]:
        del lst_joblist[0]

    if args.d:
        print(lst_joblist[0])
        print(str(len(lst_joblist)) + " éléments")

    joblist = []
    # ne garder que le premier item de chaque ligne
    # pour chaque ligne de lst_joblist, split au premier espace, garde SGE JobID (awk-like)
    # [u'2075577', u'0.05003', u'bl_pe_repe', u'jjust', u'qw', u'09/14/2017', u'21:55:37', u'1']
    for line in lst_joblist:
        if args.d:
            print(line.split())
        if args.mono:
            if int(line.split()[7]) == 1:
                joblist.append(line.split()[0])
        elif args.multi:
            if int(line.split()[7]) > 1:
                joblist.append(line.split()[0])
        else:  # elif args.all: kif-kif
            joblist.append(line.split()[0])

    if args.d:
        print(joblist[0])

    # verification
    print("\n\t" + str(len(joblist)) + " job(s) à modifier selon cette forme :")
    print("\n" + qalter + " -q " + args.queues + " " + str(joblist[0]) + "\n")
    gonogo = queryYesNo("Procéder ainsi ")
    if args.d:
        print(gonogo)

    if gonogo is 1:
        for jobid in joblist:
            result = subprocess.call(
                qalter +
                " -q " +
                args.queues +
                " " +
                str(jobid),
                shell=True)
    else:
        sys.exit("noGo, exiting...")

"""
Successfull TODO/FIXME->DONE documented:
    * traduire en python3
    * faire un filtre mono/multi/all

"""
