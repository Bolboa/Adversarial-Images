import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_float('learning_rate', 1e-3, 'Initial learning rate.')
flags.DEFINE_integer('training_epochs', 20, 'Number of times training vectors are used once to update weights.')
flags.DEFINE_integer('batch_size', 1, 'Batch size. Must divide evenly into the data set sizes.')

def use_model():
    
    mnist = input_data.read_data_sets("/tmp/data/", one_hot=True)

    # tf Graph Input
    x = tf.placeholder(tf.float32, shape=[None, 784])
    #x = tf.get_variable("input_image", shape=[100,784], dtype=tf.float32)
    y = tf.placeholder(shape=[None,10], name='input_label', dtype=tf.float32)  # 0-9 digits recognition => 10 classes

    # set model weights
    W = tf.get_variable("weights", shape=[784, 10], dtype=tf.float32, initializer=tf.random_normal_initializer())
    b = tf.get_variable("biases", shape=[1, 10], dtype=tf.float32, initializer=tf.zeros_initializer())

    # construct model
    logits = tf.matmul(x, W) + b
    pred = tf.nn.softmax(logits)  # Softmax

    # minimize error using cross entropy
    cost = tf.reduce_mean(-tf.reduce_sum(y * tf.log(pred), reduction_indices=1))
    
    # Gradient Descent
    optimizer = tf.train.GradientDescentOptimizer(FLAGS.learning_rate).minimize(cost)

    # initializing the variables    
    init = tf.global_variables_initializer()

    saver = tf.train.Saver()

    with tf.Session() as sess:
        # reload model
        saver.restore(sess, "/tmp/model.ckpt")

        # initialize array that will store images of number 2
        labels_of_2 = []
        
        # get number 2 from mnist dataset
        while mnist.test.next_batch(FLAGS.batch_size):
            # get next batch
            sample_image, sample_label = mnist.test.next_batch(FLAGS.batch_size)
            # returns index of label
            itemindex = np.where(sample_label == 1)

            # if image label is a number 2 store the image
            if itemindex[1][0] == 2:
                labels_of_2.append(sample_image)
            else:
                continue

            # if there are 10 images stored then end the loop
            if len(labels_of_2) == 100:
                break

        
        # convert into a numpy array of shape [10, 784]
        labels_of_2 = np.concatenate(labels_of_2, axis=0)


        epsilons = np.array([-0.2, -0.4, -0.25, -0.25, 
                     -0.3, -0.515, -0.15, -0.7, 
                     -1.0, -0.20]).reshape((10, 1))
        
        # placeholder for target label
        fake_label = tf.placeholder(tf.int32, shape=[100])
        # setup the fake loss
        fake_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,labels=fake_label)

        gradients = tf.gradients(fake_loss, x)

        #sess.run(pred, feed_dict={x:labels_of_2})
        
        gradient_value = sess.run(gradients, feed_dict={x:labels_of_2, fake_label:np.array([6]*100)})

        sign = np.sign(gradient_value[0][0])

        noise = epsilons * sign

        #print(sign)

        for j in range(len(labels_of_2)):
            labels_of_2[j] = labels_of_2[j] + noise[0]

        
        

        plt.subplot(2,2,1)
        plt.imshow(sess.run(x[0], feed_dict={x:labels_of_2}).reshape(28,28),cmap='gray')

        
        plt.show()

        classification = sess.run(tf.argmax(pred, 1), feed_dict={x:labels_of_2})
        print(classification)
        
use_model()

