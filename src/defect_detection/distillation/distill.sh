# GRU 50MB: 256 384 4 14000
# GRU 20MB: 256 256 3 8000
# GRU 3MB: 128 256 1 2000
# TODO: LSTM and CNN
declare -a alphas=(1.0 0.95 0.9 0.85 0.8 0.75 0.7 0.65 0.6 0.55 0.5 0.45 0.4 0.35 0.3 0.25 0.2 0.15 0.1 0.05 0.0)

for loss in "ce" "mse"
do
  for alpha in ${alphas[@]}
  do
    MODEL_DIR=./checkpoint/$loss/3/$alpha
    mkdir -p $MODEL_DIR
    CUDA_VISIBLE_DEVICES=0 python distill.py \
        --do_train \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/valid.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --loss_func $loss \
        --alpha $alpha \
        --input_dim 128 \
        --hidden_dim 256 \
        --n_layers 1 \
        --vocab_size 2000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --epochs 25 \
        --seed 123456 2>&1| tee $MODEL_DIR/train.log

    CUDA_VISIBLE_DEVICES=0 python distill.py \
        --do_eval \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/test.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --input_dim 128 \
        --hidden_dim 256 \
        --n_layers 1 \
        --vocab_size 2000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --choice best \
        --seed 123456 2>&1| tee $MODEL_DIR/eval.log
  done &
done

declare -a alphas=(1.0 0.95 0.9 0.85 0.8 0.75 0.7 0.65 0.6 0.55 0.5 0.45 0.4 0.35 0.3 0.25 0.2 0.15 0.1 0.05 0.0)

for loss in "ce" "mse"
do
  for alpha in ${alphas[@]}
  do
    MODEL_DIR=./checkpoint/$loss/20/$alpha
    mkdir -p $MODEL_DIR
    CUDA_VISIBLE_DEVICES=1 python distill.py \
        --do_train \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/valid.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --loss_func $loss \
        --alpha $alpha \
        --input_dim 256 \
        --hidden_dim 256 \
        --n_layers 3 \
        --vocab_size 8000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --epochs 25 \
        --seed 123456 2>&1| tee $MODEL_DIR/train.log

    CUDA_VISIBLE_DEVICES=1 python distill.py \
        --do_eval \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/test.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --input_dim 256 \
        --hidden_dim 256 \
        --n_layers 3 \
        --vocab_size 8000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --choice best \
        --seed 123456 2>&1| tee $MODEL_DIR/eval.log
  done &
done

declare -a alphas=(1.0 0.95 0.9 0.85 0.8 0.75 0.7 0.65 0.6 0.55 0.5 0.45 0.4 0.35 0.3 0.25 0.2 0.15 0.1 0.05 0.0)

for loss in "ce" "mse"
do
  for alpha in ${alphas[@]}
  do
    MODEL_DIR=./checkpoint/$loss/50/$alpha
    mkdir -p $MODEL_DIR
    CUDA_VISIBLE_DEVICES=3 python distill.py \
        --do_train \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/valid.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --loss_func $loss \
        --alpha $alpha \
        --input_dim 256 \
        --hidden_dim 384 \
        --n_layers 4 \
        --vocab_size 14000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --epochs 25 \
        --seed 123456 2>&1| tee $MODEL_DIR/train.log

    CUDA_VISIBLE_DEVICES=3 python distill.py \
        --do_eval \
        --train_data_file=../../../data/defect_detection/train.jsonl \
        --eval_data_file=../../../data/defect_detection/test.jsonl \
        --model_dir $MODEL_DIR \
        --std_model biGRU \
        --input_dim 256 \
        --hidden_dim 384 \
        --n_layers 4 \
        --vocab_size 14000 \
        --block_size 400 \
        --train_batch_size 16 \
        --eval_batch_size 64 \
        --choice best \
        --seed 123456 2>&1| tee $MODEL_DIR/eval.log
  done &
done