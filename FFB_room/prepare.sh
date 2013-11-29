python ~/judge_home/soft/fdsgeogen/createfds.py ../ffb.xml
for file in `ls *.fds`; do
    echo "create directory for $file"
    id=`echo $file | cut -f 3 --delimiter=_ | cut -f 1 --delimiter=.`
    echo "id: $id"
    mkdir id$id
    cp ../chain.sh ../fds.job $file id$id
done
