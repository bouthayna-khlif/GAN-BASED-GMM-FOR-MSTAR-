# -*- coding: utf-8 -*-
"""GMM_PCA__GAN_MSTAR"""

import tensorflow as tf

from sklearn import datasets
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error
from sklearn.mixture import GaussianMixture as GMM

import tensorflow_datasets as tfds
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import tensorflow as tf

from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

from sklearn.metrics import classification_report, log_loss, accuracy_score
from sklearn.model_selection import train_test_split
import torch

# import splitfolders
import tensorflow as tf
print(tf.test.gpu_device_name())
print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))

from google.colab import drive
drive.mount('/content/drive')

train = r"/content/drive/MyDrive/PFE ENSTA BRETAGNE/mstar/TRAIN"
test = r"/content/drive/MyDrive/PFE ENSTA BRETAGNE/mstar/TEST"

cat_counts = {}
for cat in os.listdir(train):
    counts = len(os.listdir(os.path.join(train, cat)))
    cat_counts[cat] =counts
print(cat_counts)

cat_counts = {}
for cat in os.listdir(test):
    counts = len(os.listdir(os.path.join(test, cat)))
    cat_counts[cat] =counts
print(cat_counts)

PATH1=r'/content/drive/MyDrive/dataset.pt'
PATH2='/content/drive/MyDrive/datatest.pt'

import torch

dataset=torch.load(PATH1)
datatest=torch.load(PATH2)

x_train,y_train=zip(*dataset)
x_test, y_test=zip(*datatest)
y_train=to_categorical(y_train)
x_train=np.array(x_train)
y_test=to_categorical(y_test)
x_test=np.array(x_test)

x_test.shape

#### Normalize
#### Normalize
norm_train = np.float32(x_train)/255.00
norm_test = np.float32(x_test)/255.00
n_images = x_train.shape[0]
indexes = np.random.randint(0, norm_train.shape[0],size=n_images)
images = norm_train[indexes]

### Center datasets for PCA

images = np.float32(images)
mu = np.mean(images)
std = np.std(images)
images -= mu
images /= std
pca_input = np.reshape(images,(-1,n_images))

#### DO the PCA

n = 100
pca_ = PCA(n_components=n)
principalComponents = pca_.fit_transform(pca_input)
recon = pca_.inverse_transform(principalComponents)
mse = mean_squared_error(pca_input, recon,squared=True)
print(f"MSE: {mse} with {n} components")

principalComponents.shape

plt.figure()
plt.scatter(principalComponents[:, 0], principalComponents[:, 1],cmap="Paired")
plt.colorbar()

from sklearn.mixture import GaussianMixture
gmm = GaussianMixture(n_components=2, covariance_type='full')
gmm=gmm.fit(principalComponents )
labels = gmm.predict(principalComponents )

gmm = GMM(n_components=2, covariance_type='full', random_state=42)
plot_gmm(gmm,  principalComponents)

plt.scatter(principalComponents[:, 0], principalComponents[:, 1], c=labels, s=10, cmap='viridis');
plt.colorbar()

probs = gmm.predict_proba(principalComponents)
probs

size = 50 * probs.max(1) ** 2  # square emphasizes differences
plt.scatter(principalComponents[:, 0], principalComponents[:, 1], c=labels, cmap='viridis', s=size)

#POUR VERIFIER LE NUMBER DES CLUSTERS 
Sum_bic = []
Sum_aic = []

K = range(1,10)
for k in K:
    gmm = GaussianMixture(n_components=k)
    gmm = gmm.fit(principalComponents)
    Sum_bic.append(gmm.bic(principalComponents))
    Sum_aic.append(gmm.aic(principalComponents))

x1 = K
y1 = Sum_aic
plt.plot(x1, y1, label = "AIC")
x2 = K
y2 = Sum_bic
plt.plot(x2, y2, label = "BIC")

plt.title("AIC and BIC for dofferent numbers of k", fontsize=16, fontweight='bold')
plt.xlabel("k")
plt.ylabel("Information Criterion")
plt.legend(loc='upper right')
plt.show()

Z= gmm.sample(100)[1]

Z.size

Z.shape

batch_size=100
nz = 100

def get_noise(batch_size, noise_code):
  if noise_code == "normal":

    return torch.randn( (batch_size, nz, 1, 1), dtype = torch.float )

  elif noise_code == "normal_naive_pca":

    out = np.random.normal(noise_mean, noise_std, size = (batch_size,nz))
    return torch.tensor(out, dtype=torch.float).view(batch_size,nz,1,1)

  elif noise_code == "normal_multivar_pca":

    out = np.random.multivariate_normal(noise_mean, noise_cov, size = (batch_size))
    return torch.tensor(out, dtype=torch.float).view(batch_size,nz,1,1)

  elif noise_code =="gm_pca":
      return torch.tensor(gmm.sample(batch_size)[0], dtype=torch.float).view(batch_size,nz,1,1)
  else:
    return None

z=np.array(Z)

from sklearn.model_selection import train_test_split
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.2, random_state=1)

train_images= x_train

train_images.shape

BUFFER_SIZE = 60000
 BATCH_SIZE = 32

# Batch and shuffle the data
train_dataset = tf.data.Dataset.from_tensor_slices(train_images).shuffle(BUFFER_SIZE).batch(BATCH_SIZE)
print(type(train_dataset))

import glob
import imageio
import matplotlib.pyplot as plt
import numpy as np
import os
import PIL
from tensorflow.keras import layers
import time

from IPython import display
from keras.layers import Input, Reshape, Dropout, Dense, Flatten, BatchNormalization, Activation, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D
from keras.models import Sequential, Model, load_model
from tensorflow.keras.optimizers import Adam
import numpy as np
from PIL import Image
import os

def make_generator_model():
    model = tf.keras.Sequential()
    model.add(layers.Dense(8*8*256, use_bias=False, input_shape=Z.shape))
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Reshape((8, 8, 256)))
    assert model.output_shape == (None, 8, 8, 256) # Note: None is the batch size

    model.add(layers.Conv2DTranspose(128, (5, 5), strides=(1, 1), padding='same', use_bias=False))
    assert model.output_shape == (None, 8, 8, 128)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())



    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False))
    assert model.output_shape == (None, 16, 16, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(64, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    assert model.output_shape == (None, 32, 32, 64)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(32, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    assert model.output_shape == (None, 64, 64, 32)
    model.add(layers.BatchNormalization())
    model.add(layers.LeakyReLU())

    model.add(layers.Conv2DTranspose(1, (5, 5), strides=(2, 2), padding='same', use_bias=False, activation='tanh'))
    #assert model.output_shape == (None, 128, 128)
  
    return model

generator = make_generator_model()

noise = gmm.sample(100)[0]
generated_image = generator(noise, training=False)
print(generated_image[0, :, :, 0])
plt.imshow(generated_image[0, :, :, 0], cmap='gray')

generator.summary()

def make_discriminator_model():
    model = tf.keras.Sequential()
    model.add(layers.Conv2D(64, (5, 5), strides=(1, 1), padding='same',
                                      input_shape=(128, 128,1)))
                            
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Conv2D(128, (5, 5), strides=(2, 2), padding='same'))
    model.add(layers.LeakyReLU())
    model.add(layers.Dropout(0.3))

    model.add(layers.Flatten())
    model.add(layers.Dense(1))

    return model

discriminator = make_discriminator_model()
decision = discriminator(generated_image)
print (decision)

discriminator.summary()

# This method returns a helper function to compute cross entropy loss
cross_entropy = tf.keras.losses.BinaryCrossentropy(from_logits=True)

def discriminator_loss(real_output, fake_output):
    real_loss = cross_entropy(tf.ones_like(real_output), real_output)
    fake_loss = cross_entropy(tf.zeros_like(fake_output), fake_output)
    total_loss = real_loss + fake_loss
    return total_loss

def generator_loss(fake_output):
    return cross_entropy(tf.ones_like(fake_output), fake_output)

generator_optimizer = tf.keras.optimizers.Adam(1e-4)
discriminator_optimizer = tf.keras.optimizers.Adam(1e-4)

import os

checkpoint_dir = './training_checkpoints'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 discriminator_optimizer=discriminator_optimizer,
                                 generator=generator,
                                 discriminator=discriminator)

EPOCHS = 500
# We will reuse this seed overtime (so it's easier)
# to visualize progress in the animated GIF)
num_examples_to_generate = 16
noise_dim = 100
seed = tf.random.normal([num_examples_to_generate, noise_dim])

noise = gmm.sample(100)[0]

# tf.function annotation causes the function 
# to be "compiled" as part of the training
@tf.function
def train_step(images):
  
    # 1 - Create a random noise to feed it into the model
    # for the image generation
    noise = tf.random.normal([BATCH_SIZE, noise_dim])
    
    # 2 - Generate images and calculate loss values
    # GradientTape method records operations for automatic differentiation.
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
      generated_images = generator(noise, training=True)

      real_output = discriminator(images, training=True)
      fake_output = discriminator(generated_images, training=True)

      gen_loss = generator_loss(fake_output)
      disc_loss = discriminator_loss(real_output, fake_output)

    # 3 - Calculate gradients using loss values and model variables
    # "gradient" method computes the gradient using 
    # operations recorded in context of this tape (gen_tape and disc_tape).
    
    # It accepts a target (e.g., gen_loss) variable and 
    # a source variable (e.g.,generator.trainable_variables)
    # target --> a list or nested structure of Tensors or Variables to be differentiated.
    # source --> a list or nested structure of Tensors or Variables.
    # target will be differentiated against elements in sources.

    # "gradient" method returns a list or nested structure of Tensors  
    # (or IndexedSlices, or None), one for each element in sources. 
    # Returned structure is the same as the structure of sources.
    gradients_of_generator = gen_tape.gradient(gen_loss, 
                                               generator.trainable_variables)
    gradients_of_discriminator = disc_tape.gradient(disc_loss, 
                                                discriminator.trainable_variables)
    
    # 4 - Process  Gradients and Run the Optimizer
    # "apply_gradients" method processes aggregated gradients. 
    # ex: optimizer.apply_gradients(zip(grads, vars))
    """
    Example use of apply_gradients:
    grads = tape.gradient(loss, vars)
    grads = tf.distribute.get_replica_context().all_reduce('sum', grads)
    # Processing aggregated gradients.
    optimizer.apply_gradients(zip(grads, vars), experimental_aggregate_gradients=False)
    """
    generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, discriminator.trainable_variables))

import time
from IPython import display # A command shell for interactive computing in Python.

def train(dataset, epochs):
  # A. For each epoch, do the following:
  for epoch in range(epochs):
    start = time.time()
    # 1 - For each batch of the epoch, 
    for image_batch in dataset:
      # 1.a - run the custom "train_step" function
      # we just declared above
      train_step(image_batch)

    # 2 - Produce images for the GIF as we go
    display.clear_output(wait=True)
    generate_and_save_images(generator,
                             epoch + 1,
                             seed)

    # 3 - Save the model every 5 epochs as 
    # a checkpoint, which we will use later
    if (epoch + 1) % 5 == 0:
      checkpoint.save(file_prefix = checkpoint_prefix)

    # 4 - Print out the completed epoch no. and the time spent
    print ('Time for epoch {} is {} sec'.format(epoch + 1, time.time()-start))

  # B. Generate a final image after the training is completed
  display.clear_output(wait=True)
  generate_and_save_images(generator,
                           epochs,
                           seed)

def generate_and_save_images(model, epoch, test_input):
  # Notice `training` is set to False.
  # This is so all layers run in inference mode (batchnorm).
  # 1 - Generate images
  predictions = model(test_input, training=False)
  # 2 - Plot the generated images
  fig = plt.figure(figsize=(4,4))
  for i in range(predictions.shape[0]):
      plt.subplot(4, 4, i+1)
      plt.imshow(predictions[i, :, :, 0] * 127.5 + 127.5, cmap='gray')
      plt.axis('off')
  # 3 - Save the generated images
  plt.savefig('image_at_epoch_{:04d}.png'.format(epoch))
  plt.show()

train(train_dataset, EPOCHS)
