#!/bin/bash
# prolog script
# $Id: start-openmpi-d9.sh 2972 2020-07-23 09:15:48Z ltaulell $

function PeHostfile2MachineFile
{
    # machinefile is either written:
    # (hostname -s):ncpu (old OpenMPI)
    # or written:
    # (hostname -s) x ncpu/ligne (all OpenMPI)
    # start with UUOC
    #cat "$1" | while read LINE; do
    while read -r LINE < "$1" ; do
        if [ "${IB}" = "Yes" ] ; then
            HOST=$(echo "${LINE}" | cut -f1 -d" " | cut -f1 -d"." )-ib
        else
            HOST=$(echo "${LINE}" | cut -f1 -d" " | cut -f1 -d"." )
        fi

        NCPUS=$(echo "${LINE}" | cut -f2 -d" " )
        if [ "${SHARED}" = "Yes" ] ; then
            echo "${HOST}:${NCPUS}"
        else
            i=1
            while [ "${i}" -le "${NCPUS}" ]; do
                # add here code to map regular hostnames into ATM hostnames
                echo "${HOST}"
                #i=`expr $i + 1`
                i=$((i + 1))
            done
        fi
    done
}

MACHINES="${TMPDIR}/machines"

PeHostfile2MachineFile "$1" >> "${MACHINES}"

# nslots, ib, shared ?
#ln -s ${SGE_ROOT}/mpich/ssh ${TMPDIR}/ssh

exit 0
