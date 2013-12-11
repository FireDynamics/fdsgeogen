for id in id*; do
    cd $id
    pwd
    sh ./chain.sh
    cd -
done
