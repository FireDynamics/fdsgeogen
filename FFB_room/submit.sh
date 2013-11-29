for id in id*; do
    cd $id
    pwd
    msub fds.job
    cd -
done