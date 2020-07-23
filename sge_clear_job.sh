#!/bin/bash
#
# PSMN: $Id: sge_clear_job.sh 2970 2020-07-23 08:58:00Z ltaulell $
#

if [ $# -ne "1" ];
then
  echo "Clear 'Eqw' status of login's jobs"
  echo "Usage: $0 <login>(,<login>,...)"
  exit 1
else
  LOGIN=$1
fi



for i in $(qstat -u "${LOGIN}" -s p | grep "Eqw" | awk '{print $1}')
do 
  qmod -cj "${i}"
done

exit 0
