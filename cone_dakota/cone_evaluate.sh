echo "running dakota shell script"

echo "input file content:"
cat $1

BASE_DIR=$PWD/..
RUN_BASE=runs

SETUP_DIR=foam_simple

FLUX_FILE=fluxes.dat
XML_FILE=cone.xml
CREATEFDS=~/fdsgeogen/createfds.py

ID=`cat $RUN_BASE/count`
let ID=ID+1

echo $ID > $RUN_BASE/count

EVAL_DIR=$PWD/$RUN_BASE/id$ID
mkdir $EVAL_DIR

echo "INFO: evalutaion ID: $ID"

#### execute various radiation simulations

echo "#ignition time in simulation [s]; trust of simulation []" > $EVAL_DIR/ignition_times.dat

FLUX_ID=0
FLUX_ID_MAX=`tail -n +2 $FLUX_FILE | wc -l`
while [ $FLUX_ID -lt $FLUX_ID_MAX ]; do

    RUN_DIR=$EVAL_DIR/flux_$FLUX_ID
    mkdir $RUN_DIR

    echo "INFO: prepare input for flux_id: $FLUX_ID (out of $FLUX_ID_MAX)"

    python $BASE_DIR/extract_replace_dakota_values.py $1 $XML_FILE > $RUN_DIR/cone_rad_template.xml
    python $BASE_DIR/extract_replace_flux.py $FLUX_FILE $FLUX_ID $RUN_DIR/cone_rad_template.xml > $RUN_DIR/$XML_FILE

    cd $RUN_DIR

    python $CREATEFDS $XML_FILE &> createfds.out

    echo "INFO: running FDS"
    ~/soft/bin/fds_intel_linux_64 cone_test.fds &> fds_stdout.out

    python $BASE_DIR/compute_ignition.py cone_test_hrr.csv >> $EVAL_DIR/ignition_times.dat

    cd -

    let FLUX_ID=FLUX_ID+1

done

pr -m -t -s\  $FLUX_FILE $EVAL_DIR/ignition_times.dat > $EVAL_DIR/result_table.dat

python $BASE_DIR/compute_errorfunction.py $EVAL_DIR/result_table.dat > $2
