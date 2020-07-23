#!/bin/bash
# epilog script
# $Id: stop-openmpi-d9.sh 2971 2020-07-23 09:00:58Z ltaulell $

HOSTFILE="${TMPDIR}"/machines

if [[ -e "${HOSTFILE}" ]];
then
    for i in $(uniq "${HOSTFILE}" | xargs)
    do
        # cleanup shm usage from lch and al.
        ssh "${i}" rm -fr /dev/shm/"${USER}"/"${JOB_ID}"
        ssh "${i}" echo 1 > /proc/sys/vm/drop_caches
    done
fi
rm -f "${HOSTFILE}"

exit 0
