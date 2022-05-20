for log in log_ali_*.log ; do
  for model in mono trideltas trisat ; do
    grep ^dataset -B2 -A3 $log | grep tdnn_$model -A5 > ${log%.log}.$model
  done
done
