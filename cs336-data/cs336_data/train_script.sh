#!/bin/bash
TRAIN_PATH="/home/sasha/classes/cs336/spring2024-assignment1-basics/project_data/data/TinyStoriesV2-GPT4-train-10000/cleaned_text-encoded.bin"
OUT_PATH="/home/sasha/classes/cs336/spring2024-assignment4-data/out_model"
SCRIPT_PATH="/home/sasha/classes/cs336/spring2024-assignment4-data/cs336-basics/scripts/train.py"
torchrun $SCRIPT_PATH \
--train-path $TRAIN_PATH \
--dev-path $TRAIN_PATH \
--output-dir $OUT_PATH \
--vocab-size 10000 \
--context-length 64 \
--d-model 128 \
--num-layers 4 \
--num-heads 4 \
--d-ff 512 \
--attn-pdrop 0.05 \
--residual-pdrop 0.05 \
--batch-size 16 \
--train-steps 20000 \
--eval-iters 1000 \
--eval-interval 2000 \
--learning-rate 1e-3 \
--lr-scheduler cosine \
--weight-decay 0.1 \
--warmup-ratio 0.01 \
--grad-clip 1.0 \
--device cpu
