from classification.dataset import DataManager
import numpy as np 
import SimpleITK as sitk 
from dicom_to_cnn.model.reader.Nifti import Nifti 
from dicom_to_cnn.model.post_processing.mip.MIP_Generator import MIP_Generator 

def get_data(csv_path):

    DM = DataManager(csv_path)
    train, val, test = DM.get_train_val_test()
    dataset = dict()
    dataset['train'], dataset['val'], dataset['test'] = train, val, test 
    return dataset 

def encoding_instance(dictionnary):
    """encoding label 

    Args:
        dictionnary ([dict]): ['right arm': value, 'left_arm':value, 'head':value, 'leg':value]

    Returns:
        [list]: [return a list with encoded labels ]
    """
    label = []
    
        #upper Limit 
    if dictionnary['head'] == 'Vertex' : 
        label.append(0)
    if dictionnary['head'] == 'Eye'  or dictionnary['head'] == 'Mouth' : 
        label.append(1)

        #lower Limit
    if dictionnary['leg'] == 'Hips' : 
        label.append(0)
    if dictionnary['leg'] == 'Knee': 
        label.append(1)
    if dictionnary['leg'] == 'Foot':
        label.append(2)

        #right Arm 
    if dictionnary['right_arm'] == 'down' : 
        label.append(0)
    if dictionnary['right_arm'] == 'up' : 
        label.append(1)

        #left Arm 
    if dictionnary['left_arm'] == 'down' : 
        label.append(0)
    if dictionnary['left_arm'] == 'up' : 
        label.append(1)

    return label

class DataGeneratorFromDict(tf.keras.utils.Sequence):
    """A class to create a DataGenerator object for model.fit()
    
    """

    def __init__(self,
                 images_paths,
                 batch_size=1,
                 shuffle=True,
                 x_key='input',
                 y_key='output'):
        """
        :param images_paths: list[dict] or dict[dict]
        :param batch_size: batch size
        :param shuffle: bool. If set to true, indexes will be suffled at each end of epoch.
        :param x_key: key corresponding to input of neural network
        :param y_key: key correspond to output of neural network
        """

        self.images_paths = images_paths
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.on_epoch_end()
        self.x_key = x_key
        self.y_key = y_key

    def __len__(self):
        """
        :return: int, the number of batches per epoch
        """
        return int(np.floor(len(self.images_paths) / self.batch_size))

    def on_epoch_end(self):
        """Updates indexes after each epoch"""
        self.indexes = np.array(list(self.images_paths.keys())) if isinstance(self.images_paths, dict) else np.arange(len(self.images_paths))
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __getitem__(self, index):
        """
        Generate one batch of data
        :param index: int, position of the batch in the Sequence
        :return: tuple of numpy array, (X_batch, Y_batch) of shape (batch_size, ...)
        """

        # select indices of data for next batch
        indexes = self.indexes[index * self.batch_size: (index + 1) * self.batch_size]
        #print('PREPARE THE BATCH')
        #start_time = time.time()
        # prepare the batch
        X_batch = []
        Y_batch = []
        for idx in indexes:
            img_dict = self.images_paths[idx]

            #prepare transform 
            resampled_array = Nifti(img_dict['ct_img']).resampled(shape_matrix=(256, 256, 1024), shape_physic=(700, 700, 2000))
            resampled_array[np.where(resampled_array < 500)] = 0 #500 UH
            normalize = resampled_array[:,:,:,]/np.max(resampled_array)
            mip_generator = MIP_Generator(normalize)
            mip = mip_generator.project(angle=0)

            label = encoding_instance(img_dict)

            # add it to the batch
            X_batch.append(mip)
            Y_batch.append(label)

        X_batch = np.array(X_batch)
        Y_batch = np.array(Y_batch)
        #print("END BATCH --- %s seconds ---" % (time.time() - start_time))
        return X_batch, Y_batch
