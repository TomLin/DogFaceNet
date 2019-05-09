"""
DogFaceNet
The main DogFaceNet implementation
This file contains:
 - Data loading
 - Model definition
 - Model training

Licensed under the MIT License (see LICENSE for details)
Written by Guillaume Mougeot
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

import os
# import pickle
import numpy as np
import skimage as sk
import matplotlib.pyplot as plt
import tensorflow.keras.backend as K
from triplets_processing import *
from online_training import *
from triplet_loss import *

PATH = '../data/dogfacenet/aligned/after_4_bis/'
PATH_SAVE = '../output/history/'
PATH_MODEL = '../output/model/'
SIZE = (224,224,3)
VALID_SPLIT = 0.1
TEST_SPLIT = 0.1

filenames = np.empty(0)
labels = np.empty(0)
idx = 0
for root,dirs,files in os.walk(PATH):
    if len(files)>1:
        for i in range(len(files)):
            files[i] = root + '/' + files[i]
        filenames = np.append(filenames,files)
        labels = np.append(labels,np.ones(len(files))*idx)
        idx += 1
    if len(files) == 1:
        #print(root)
        shutil.rmtree(root)
print(len(labels))

nbof_classes = len(np.unique(labels))
print(nbof_classes)

nbof_test = int(TEST_SPLIT*nbof_classes)

keep_test = np.less(labels,nbof_test)
keep_train = np.logical_not(keep_test)

filenames_test = filenames[keep_test]
labels_test = labels[keep_test]

filenames_train = filenames[keep_train]
labels_train = labels[keep_train]

print("Number of training data: " + str(len(filenames_train)))
print("Number of training classes: " + str(nbof_classes-nbof_test))
print("Number of testing data: " + str(len(filenames_test)))
print("Number of testing classes: " + str(nbof_test))

alpha = 0.3
def triplet(y_true,y_pred):
    
    a = y_pred[0::3]
    p = y_pred[1::3]
    n = y_pred[2::3]
    
    ap = K.sum(K.square(a-p),-1)
    an = K.sum(K.square(a-n),-1)

    return K.sum(tf.nn.relu(ap - an + alpha))

# def triplet(y_true,y_pred):
#     return batch_hard_triplet_loss(y_true,y_pred,alpha)

def triplet_acc(y_true,y_pred):
    a = y_pred[0::3]
    p = y_pred[1::3]
    n = y_pred[2::3]
    
    ap = K.sum(K.square(a-p),-1)
    an = K.sum(K.square(a-n),-1)
    
    return K.less(ap+alpha,an)

# start = 463
# model = tf.keras.models.load_model(PATH_MODEL + '2019.04.29.dogfacenet_v12.'+str(start)+'.h5', custom_objects={'triplet':triplet,'triplet_acc':triplet_acc})

# Model definition

"""
With the keras models... too big to load them into memory!
"""

# emb_size = 64
# from tensorflow.keras.layers import Dropout, Flatten, Dense, Lambda

# base = tf.keras.applications.MobileNet(alpha=0.5, input_shape=(224,224,3),include_top=False, weights=None, pooling='avg')

# x = Flatten()(base.output)
# x = Dropout(0.5)(x)
# x = Dense(emb_size, use_bias=False)(x)
# outputs = Lambda(lambda x: tf.nn.l2_normalize(x,axis=-1))(x)

# model = tf.keras.Model(base.input,outputs)

# model.compile(loss=triplet,
#               optimizer='adam',
#               metrics=[triplet_acc])


from tensorflow.keras import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Add, GlobalAveragePooling2D
from tensorflow.keras.layers import Activation, Dropout, Flatten, Dense, Lambda, BatchNormalization


"""
Model number 12: Modified ResNet without bottleneck layers
"""

# emb_size = 64

# inputs = Input(shape=SIZE)

# x = Conv2D(16, (7, 7), (2, 2), use_bias=False, activation='relu', padding='same')(inputs)
# x = BatchNormalization()(x)
# x = MaxPooling2D((3,3))(x)

# for layer in [16,32,64,128,512]:

#     x = Conv2D(layer, (3, 3), strides=(2,2), use_bias=False, activation='relu', padding='same')(x)
#     r = BatchNormalization()(x)
# #     r = Dropout(0.25)(r)
    
#     x = Conv2D(layer, (3, 3), use_bias=False, activation='relu', padding='same')(r)
#     x = BatchNormalization()(x)
#     r = Add()([r,x])
# #     r = Dropout(0.25)(r)
    
#     x = Conv2D(layer, (3, 3), use_bias=False, activation='relu', padding='same')(r)
#     x = BatchNormalization()(x)
#     x = Add()([r,x])
# #     x = Dropout(0.25)(x)
    

# x = GlobalAveragePooling2D()(x)
# x = Flatten()(x)
# x = Dropout(0.5)(x)
# x = Dense(emb_size, use_bias=False)(x)
# outputs = Lambda(lambda x: tf.nn.l2_normalize(x,axis=-1))(x)

# model = tf.keras.Model(inputs,outputs)

# model.compile(loss=triplet,
#               optimizer='adam',
#               metrics=[triplet_acc])


"""
Model 25: ResNet without bottleneck layers
"""

# emb_size = 64

# inputs = Input(shape=SIZE)

# x = Conv2D(16, (7, 7), strides=(2,2), use_bias=False, padding='same')(inputs)
# x = BatchNormalization()(x)
# x = Activation('relu')(x)
# x = MaxPooling2D((3,3),strides=(2,2))(x)

# for layer in [16,32,64,128,256]:

#     x = Conv2D(layer, (3, 3), strides=(2,2), use_bias=False, padding='same')(x)
#     r = BatchNormalization()(x)
#     r = Activation('relu')(r)
    
#     x = Conv2D(layer, (3, 3), use_bias=False, padding='same')(r)
#     x = BatchNormalization()(x)
#     x = Activation('relu')(x)
#     r = Add()([r,x])
    
#     x = Conv2D(layer, (3, 3), use_bias=False, padding='same')(r)
#     x = BatchNormalization()(x)
#     x = Activation('relu')(x)
#     x = Add()([r,x])

# x = GlobalAveragePooling2D()(x)
# x = Flatten()(x)
# x = Dropout(0.6)(x)
# x = Dense(emb_size, use_bias=False)(x)
# outputs = Lambda(lambda x: tf.nn.l2_normalize(x,axis=-1))(x)

# model = tf.keras.Model(inputs,outputs)

# model.compile(loss=triplet,
#               optimizer='adam',
#               metrics=[triplet_acc])


"""
Model number 27: ResNet-18 without the last layers
"""

emb_size = 128

layers = [64,128,256]

inputs = Input(shape=SIZE)

x = Conv2D(64, (7, 7), strides=(2,2), use_bias=False, padding='same')(inputs)
x = BatchNormalization()(x)
x = Activation('relu')(x)
r = MaxPooling2D((3,3),strides=(2,2))(x)

for i in range(len(layers)):

    for j in range(2):
        x = BatchNormalization()(r)
        x = Activation('relu')(x)
        x = Conv2D(layers[i], (3, 3), use_bias=False, padding='same')(x)

        x = BatchNormalization()(x)
        x = Activation('relu')(x)
        x = Conv2D(layers[i], (3, 3), use_bias=False, padding='same')(x)

        r = Add()([r,x])
    
    if i!=len(layers)-1:
        x = BatchNormalization()(r)
        x = Activation('relu')(x)
        r = Conv2D(layers[i+1], (3, 3), strides=(2,2), use_bias=False, padding='same')(x)

x = GlobalAveragePooling2D()(x)
x = Flatten()(x)
x = Dropout(0.6)(x)
x = Dense(emb_size, use_bias=False)(x)
outputs = Lambda(lambda x: tf.nn.l2_normalize(x,axis=-1))(x)

model = tf.keras.Model(inputs,outputs)

model.compile(loss=triplet,
              optimizer='adam',
              metrics=[triplet_acc])


print(model.summary())



histories = []


# model.compile(loss=triplet,
#               optimizer=tf.keras.optimizers.Adam(lr=0.0005),
#               metrics=[triplet_acc])

# Super hard training
"""
for epoch in range(1000):
    print("Epoch: "+str(epoch))
    predict_train = model.predict_generator(predict_generator(filenames_train, 32),
                                steps=np.ceil(len(filenames_train)/32))
    histories += [model.fit_generator(
        hard_image_generator(filenames_train,labels_train,predict_train,3*20,use_aug=False),
        steps_per_epoch=300,
        epochs=1,
        validation_data=image_generator(filenames_test,labels_test,3*20,use_aug=False),
        validation_steps=30
    )]
    if epoch%10==0:
        loss = np.empty(0)
        val_loss = np.empty(0)
        acc = np.empty(0)
        val_acc = np.empty(0)

        for history in histories:
            loss = np.append(loss,history.history['loss'])
            val_loss = np.append(val_loss,history.history['val_loss'])
            acc = np.append(acc,history.history['triplet_acc'])
            val_acc = np.append(val_acc,history.history['val_triplet_acc'])

        model.save(PATH_MODEL + '2019.04.30.dogfacenet_v12.'+str(epoch)+'.h5')
        history_ = np.array([loss,val_loss,acc,val_acc])
        np.save(PATH_SAVE+'2019.04.30.dogfacenet_v12.'+str(epoch)+'.h5',history_)
        np.savetxt(PATH_SAVE+'2019.04.30.dogfacenet_v12.'+str(epoch)+'.h5.txt',history_)
"""

# Training: Lowest level implementation

date='2019.05.08.'
network_name='dogfacenet_resnet-18.'
start_epoch = 1

max_epoch = 1000 + start_epoch

max_step = 300
max_step_test = 30
batch_size = 3*10


tot_loss_test = 0
mean_loss_test = 0

tot_acc_test = 0
mean_acc_test = 0

# Save
loss = []
val_loss = []
acc = []
val_acc = []

for epoch in range(start_epoch,max_epoch):
    
    step = 1
    
    tot_loss = 0
    mean_loss = 0

    tot_acc = 0
    mean_acc = 0
    
    # Training
    for images_batch,labels_batch in online_adaptive_hard_image_generator(
        filenames_train,
        labels_train,
        model,
        mean_acc,
        batch_size,
        nbof_subclasses=10
        ):


        h = model.train_on_batch(images_batch,labels_batch)
        tot_loss += h[0]
        mean_loss = tot_loss/step
        tot_acc += h[1]
        mean_acc = tot_acc/step
        #clear_output()

        # hard_triplet_ratio = np.exp(-mean_loss * 10 / batch_size)
        hard_triplet_ratio = max(0,1.2/(1+np.exp(-10*mean_acc+5.3))-0.19)

        print(
            "Epoch: " + str(epoch) + "/" + str(max_epoch) +
            ", step: " + str(step) + "/" + str(max_step) + 
            ", loss: " + str(mean_loss) + 
            ", acc: " + str(mean_acc) +
            ", hard_ratio: " + str(hard_triplet_ratio)
        )
        print(
            "Test loss: " + str(mean_loss_test) + 
            ", test acc: " + str(mean_acc_test)
        )

        if step == max_step:
            break
        step+=1
    
    loss += [mean_loss]
    acc += [mean_acc]
    
    # Testing
    step = 1
    
    tot_loss_test = 0
    mean_loss_test = 0

    tot_acc_test = 0
    mean_acc_test = 0
    
    for images_batch,labels_batch in image_generator(filenames_test,labels_test,batch_size,use_aug=False):
        h = model.test_on_batch(images_batch,labels_batch)

        tot_loss_test += h[0]
        mean_loss_test = tot_loss_test/step
        tot_acc_test += h[1]
        mean_acc_test = tot_acc_test/step

        if step == max_step_test:
            break
        step+=1
    
    val_loss += [mean_loss_test]
    val_acc += [mean_acc_test]
    
    # Save
    model.save(PATH_MODEL + date + network_name + str(epoch) + '.h5')
    history_ = np.array([loss,val_loss,acc,val_acc])
    np.save(PATH_SAVE + date + network_name + str(epoch) + '.npy',history_)
    # np.savetxt(PATH_SAVE+'2019.04.29.dogfacenet_v12.'+str(epoch)+'.h5.txt',history_)