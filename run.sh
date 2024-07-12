python refer.py \
    gurobi data/tsp300_test_seed1234.npz \
    -f \
    --disable_cache \
    --debug \
    --n_poi 3 \
    --n_depot 4 \
    --n_UGVs 1 \
    --n_UAVs 1 \
    --timeout 20