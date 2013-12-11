echo "running dakota shell script"

echo "input file content:"
cat $1

FLUX_FILE=fluxes.dat
XML_FILE=cone.xml
FDS_FILE=cone_test.fds
RUN_BASE=run_1

ID=`cat $RUN_BASE/id`
let ID=ID+1

echo $ID > $RUN_BASE/id

EVAL_DIR=run_1/id_$ID
mkdir $EVAL_DIR

echo "ASIM: evalutaion ID: $ID"

#### execute various radiation simulations

echo "#ignition time in simulation [s]; trust of simulation []" > $EVAL_DIR/ignition_times.dat

FLUX_ID=0
FLUX_ID_MAX=`tail -n +2 $FLUX_FILE | wc -l`
while [ $FLUX_ID -lt $FLUX_ID_MAX ]; do

    RUN_DIR=$EVAL_DIR/flux_$FLUX_ID
    mkdir $RUN_DIR

    echo "ASIM: prepare input for flux_id: $FLUX_ID (out of $FLUX_ID_MAX)"

    python extract_replace_dakota_values.py $1 $XML_FILE > $RUN_DIR/cone_rad_template.xml
    python extract_replace_flux.py $FLUX_FILE $FLUX_ID $RUN_DIR/cone_rad_template.xml > $RUN_DIR/$XML_FILE
    cp cone.input $RUN_DIR

    cd $RUN_DIR

    python ~/fdsgeogen/createfds.py $XML_FILE > createfds.out

    echo "ASIM: running FDS"
    ~/soft/bin/fds_intel_linux_64 cone_test.fds &> fds_stdout.out

    python ../../../compute_ignition.py cone_test_hrr.csv >> ../ignition_times.dat

    cd -

    let FLUX_ID=FLUX_ID+1

done

pr -m -t -s\  $FLUX_FILE $EVAL_DIR/ignition_times.dat > $EVAL_DIR/result_table.dat

python compute_errorfunction.py $EVAL_DIR/result_table.dat > $2
