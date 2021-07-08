import os 
import csv 
import json 
from datetime import datetime
from classification.dataset import DataManager
from classification.preprocessing import * 
from dicom_to_cnn.tools.cleaning_dicom.folders import *
from networks.classification import classification
import tensorflow as tf
import numpy as np
#training paramaters
epochs = 12
batch_size = 256
shuffle = True 


csv_path = '/media/oncopole/d508267f-cc7d-45e2-ae24-9456e005a01f/CLASSIFICATION/classification_dataset_NIFTI_V3.csv'
training_model_folder_name = '/media/oncopole/d508267f-cc7d-45e2-ae24-9456e005a01f/CLASSIFICATION/training/train_2'
def main() : 
    
    now = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    training_model_folder = os.path.join(training_model_folder_name, now)  # '/path/to/folder'
    if not os.path.exists(training_model_folder):
        os.makedirs(training_model_folder)
            
    logdir = os.path.join(training_model_folder, 'logs')
    if not os.path.exists(logdir):
        os.makedirs(logdir)

       # multi gpu training strategy
    strategy = tf.distribute.MirroredStrategy()

    dataset = get_data(csv_path)
    train_idx, val_idx, test_idx = dataset['train'], dataset['val'], dataset['test']
    print("TRAIN :", len(train_idx))
    print('VAL :', len(val_idx))
    print('TEST :', len(test_idx))
    write_json_file(training_model_folder, 'test_dataset', test_idx)

    #NEED CSV : [STUDY ID, MIP IMAGE 2D PATH, LABEL1, LABEL2, LABEL3, LABEL4] with encoded label 
    #X_train = []
    #y_train = []
    #for img_dict in train_idx : 
        #X_train.append(sitk.getArrayFromImage(sitk.ReadImage(img_dict['ct_img'])))
        #sub = []
        #sub.append(img_dict['label1])
        #sub.append(img_dict['label2])
        #sub.append(img_dict['label3])
        #sub.append(img_dict['label4])
        #y_train.append(sub)

    #X_val = []
    #y_val = []
    #for img_dict in val_idx : 
        #X_val.append(sitk.getArrayFromImage(sitk.ReadImage(img_dict['ct_img'])))
        #sub = []
        #sub.append(img_dict['label1])
        #sub.append(img_dict['label2])
        #sub.append(img_dict['label3])
        #sub.append(img_dict['label4])
        #y_val.append(sub)


    #X_train, y_train, X_val, y_val = np.asarray(X_train), np.asarray(y_train), np.asarray(X_val), np.asarray(y_val)
    #print(X_train.shape)
    #print(y_train.shape)
    #print(X_val.shape)
    #print(y_val.shape)

    #PREPARE THE TRAIN VAL TEST DATASET 


    callbacks = []
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=logdir, update_freq='epoch', write_graph=True, write_images=True)
    callbacks.append(tensorboard_callback)
    with strategy.scope(): 
        model = classification(input_shape=(1024, 256, 1))
    model.summary()
    
    with strategy.scope():
        optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3) #param
        model.compile(optimizer = optimizer, 
                loss={'left_arm' : 'sparse_categorical_crossentropy', 
                    'right_arm' : 'sparse_categorical_crossentropy', 
                    'head' : 'sparse_categorical_crossentropy', 
                    'legs' : 'sparse_categorical_crossentropy'}, 
                loss_weights ={'left_arm': 0.25, 'right_arm' : 0.25, 
                                'head' : 0.25, 
                                'legs': 0.25}, 
                metrics = {'left_arm': ['accuracy'], #'SparseCategoricalCrossentropy'
                            'right_arm' : ['accuracy'], 
                            'head' : ['accuracy'], 
                            'legs':['accuracy']}) #a voir pour loss

    print(model.summary())


    history = model.fit(X_train, {'head': y_train[:,0], 
                                    'legs': y_train[:,1],
                                    'right_arm' : y_train[:,2],
                                    'left_arm' : y_train[:,3], }, 
                            validation_data = (X_val, {'head': y_val[:,0], 
                                    'legs': y_val[:,1],
                                    'right_arm' : y_val[:,2],
                                    'left_arm' : y_val[:,3] ,
                                    }),
                            epochs=epochs,
                            callbacks=callbacks,  # initial_epoch=0,
                            verbose=1
                            )
    model.save(os.path.join(training_model_folder, 'trained_model_{}.h5'.format(now)))
    model.save(os.path.join(training_model_folder, 'trained_model_{}'.format(now)))
    
    
if __name__ == "__main__":
    main()