#!/bin/bash

# getting data from nvidia-smi
echo -n "Retrieving GPU Data:..."
nvidia-smi -q > ~/.smi &
proc=$!

# fancy loading animation
loading() {
  while true
  do
    sleep 0.4
    echo -ne '\b\b\b*..'
    sleep 0.15
    echo -ne '\b\b\b.*.'
    sleep 0.15
    echo -ne '\b\b\b..*'
    sleep 0.15
    echo -ne '\b\b\b...'
  done
}
loading &
load=$!
disown $load
wait $proc
kill $load
echo -e '\b\b\b Done'

# getting relevant data from saved smi output
cat ~/.smi | grep -e "Minor Number" -e "Processes" -e \
  "Process ID" -e 'Gpu\|Memory''.*%' | \
  sed 's/^.*None$/\tID\t\t: -/' > ~/.temp
rm ~/.smi

# turning data into table form and adding column headers
paste <(grep "Minor" ~/.temp | cut -d ':' -f2) \
      <(grep "ID" ~/.temp | cut -d ':' -f2) \
      <(grep "Gpu" ~/.temp | cut -d ':' -f2) \
      <(grep "Mem" ~/.temp | cut -d ':' -f2) | \
  sed 's/%//g' | tr -d ' ' > ~/.GPU-log
sed -i '1iGPU\tPID\tGPU\tMEM' ~/.GPU-log
sed -i '2iid\t#\t%\t%' ~/.GPU-log
rm ~/.temp

# loop over PIDs running on GPUs
for pid in $(cat .GPU-log | awk '{print $2}' | tail -n +3)
do
  if [ $pid = "-" ] # GPU has no runnning task
  then
    echo $'-\t-\t\t-\t-\t\t-'  >> ~/.info
    continue
  fi
  
  # otherwise there IS an active task:
  # get command
  cat /proc/$pid/comm | tr -d '\n' >> ~/.info
  # get username
  usr=$(id -nu `cat /proc/$pid/loginuid` | tr -d '\n')
  echo -ne $'\t'$usr$'\t' >> ~/.info
  # look for user in list of logged in users
  who | grep -q "$usr"
  if [ $? -eq 0 ]
  # if user is logged in:
  then
    echo -ne $'online\t' >> ~/.info
  else
    # get month and day of last logout
    seen=$(last -F $usr -n 1 | \
           head -1 | cut -d '-' -f2 | \
           cut -d ' ' -f3,4,5 | tr -d '\n')
    if [ "$seen" = "" ]
	# if no login is logged
    then
      echo -ne $'???\t' >> ~/.info
    else
      echo -ne $seen$'\t' >> ~/.info
    fi
  fi
  # get ps time and elapsed time (whatever that means)
  ps -ho "%x  %t" $pid >> ~/.info
done

# add headers
sed -i '1iPROGRAM\tUSER\t\tLOGIN\tTIME\t\tTIME' ~/.info
sed -i '2icmd\tname\t\tlast\tcpu\t\trun' ~/.info
# fuse GPU info and process info files
paste  ~/.GPU-log ~/.info > ~/.GPU-log-temp
cat ~/.GPU-log-temp > ~/.GPU-log
cat ~/.GPU-log
# remove temp files
rm ~/.info
rm ~/.GPU-log-temp

