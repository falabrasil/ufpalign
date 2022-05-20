for log in log_ali_*.log ; do
  for model in mono tri1 tri2b tri3b ; do
    grep ^dataset -B2 -A3 $log | grep -w ${model}_ali -A5 >> log.$model
  done
done
