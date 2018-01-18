# run in NeuralNetworks env
# useage: 
# $ CUDA_VISIBLE_DEVICES=6,7 python TF_test.py
import tensorflow as tf
import time
sess = tf.Session()
while True:
    time.sleep(60)
