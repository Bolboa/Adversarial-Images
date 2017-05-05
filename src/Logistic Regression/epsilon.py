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
    x = tf.placeholder(tf.float32, [None, 784]) # mnist data image of shape 28*28=784
    y = tf.placeholder(tf.float32, [None, 10]) # 0-9 digits recognition => 10 classes

    # set model weights
    W = tf.Variable(tf.zeros([784, 10]))
    b = tf.Variable(tf.zeros([10]))

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
            if len(labels_of_2) == 10:
                break

        
        # convert into a numpy array of shape [10, 784]
        labels_of_2 = np.concatenate(labels_of_2, axis=0)

        # generate 101 different epsilon values to test with
        epsilon_res = 101
        eps = np.linspace(-1.0, 1.0, epsilon_res).reshape((epsilon_res, 1))

        # labels for each image (used for graphing)
        labels = [str(i) for i in range(10)]

        # set different colors for every Softmax hypothesis
        num_colors = 10
        cmap = plt.get_cmap('hsv')
        colors = [cmap(i) for i in np.linspace(0, 1, num_colors)]
        
        # Create an empty array for our scores
        scores = np.zeros((len(eps), 10))

        # placeholder for target label
        fake_label = tf.placeholder(tf.int32, shape=[10])

        # setup the fake loss
        fake_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits,labels=fake_label)

        # calculate gradient
        gradients = tf.gradients(fake_loss, x)

        # compute gradient value using the same Softmax model used to train the orginal model,
        # the gradient generates the values necessary to change the predictions of the number 2 to a number 6
        # with minimal cost
        gradient_value = sess.run(gradients, feed_dict={x:labels_of_2, fake_label:np.array([6]*10)})

        for j in range(len(labels_of_2)):

            # extract the sign of the gradient value for each image
            sign = np.sign(gradient_value[0][j])

            # apply every epsilon value along with the sign of the gradient to the image
            for i in range(len(eps)):
                x_fool = labels_of_2[j].reshape((1, 784)) + eps[i] * sign

                # the scores are re-evaluated using the model and each 10 hypotheses are saved
                scores[i, :] = logits.eval({x:x_fool})

            # create a figure
            plt.figure(figsize=(10, 8))
            plt.title("Image {}".format(j))

            # loop through transpose of the scores to plot the effect of epsilon of every hypothesis
            for k in range(len(scores.T)):
                plt.plot(eps, scores[:, k], 
                     color=colors[k], 
                     marker='.', 
                     label=labels[k])
 
        plt.legend(prop={'size':8})
        plt.xlabel('Epsilon')
        plt.ylabel('Class Score')
        plt.grid('on')
        plt.show()  
        
use_model()
