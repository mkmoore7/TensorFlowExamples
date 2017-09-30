# Inspired by the TF Tutorial: https://www.tensorflow.org/get_started/mnist/pros

import tensorflow as tf
# Mnist Data
from tensorflow.examples.tutorials.mnist import input_data as mnist_data

# Define variable functions
def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape=shape)
    return tf.Variable(initial)


# Define conv and pool functions
def conv2d(x, W):
      return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# Get Data
mnist = mnist_data.read_data_sets("MNIST_data/", one_hot=True)

SIZE_X = 28
SIZE_Y = 28
NUM_CLASSES = 10 
LEARN_RATE = 1e-4
BATCH_SIZE = 512 
MAX_TRAIN_STEPS = 1000 
output_steps = 20

# Placeholders for data and labels
x = tf.placeholder(tf.float32, shape=[None, SIZE_X*SIZE_Y])
y_true = tf.placeholder(tf.float32, shape=[None, NUM_CLASSES])
# Dropout Placeholder (probability of dropping)
keep_prob = tf.placeholder(tf.float32)

# Reshape X to make it into a 2D image
x_image = tf.reshape(x, [-1, SIZE_X, SIZE_Y, 1])

# Weights 
W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])

W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])

W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])

W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

# Convolve and Maxpool layer 1
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

# Convolve and Maxpool layer 2
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

# FC Layer 1
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

# Dropout Layer
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# FC Layer 2 - Output Layer
y_pred = tf.matmul(h_fc1_drop, W_fc2) + b_fc2


# Objective Function
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y_true, logits=y_pred))

# Define the training step
train_step = tf.train.AdamOptimizer(LEARN_RATE).minimize(cross_entropy)


# Create the session
sess = tf.Session()

# Create Summary Writer for TB
writer = tf.summary.FileWriter('/tmp/logdir/1')
writer.add_graph(sess.graph) 

# Init all weights
sess.run(tf.global_variables_initializer())

# Define test metrics
correct_prediction = tf.equal(tf.argmax(y_pred,1), tf.argmax(y_true,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

# Train 
with sess.as_default():
    for i in range(MAX_TRAIN_STEPS):
        batch = mnist.train.next_batch(BATCH_SIZE)
        if i % output_steps == 0:
            train_accuracy = accuracy.eval(feed_dict={x: batch[0], y_true: batch[1], keep_prob: 1.0})
            print('step ' + str(i) + '\ttraining accuracy ' + str(round(100*train_accuracy, 2)) + '%')
        train_step.run(feed_dict={x: batch[0], y_true: batch[1], keep_prob: 0.5})

    print('test accuracy %g' % accuracy.eval(feed_dict={
        x: mnist.test.images, y_true: mnist.test.labels, keep_prob: 1.0}))
