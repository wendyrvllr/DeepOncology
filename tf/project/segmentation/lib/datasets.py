import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


class DataManager(object):
    """A class to read the CSV file with CT/PET/MASK path, and prepare train, val and test set

    Args:
        object ([type]): [description]
    """

    def __init__(self, csv_path=None):
        self.csv_path = csv_path
        self.seed = 42  # random state
        self.test_size = 0.15
        self.val_size = 0.15


    def get_train_val_test(self, wrap_with_dict=False, subset = None):
        """[summary]

        Args:
            wrap_with_dict (bool, optional): Wrap dataset in list of dict. Defaults to False.

        Returns:
            []: [description]
        """
        
        df = pd.read_csv(self.csv_path)
            #df = df[df['PET'] == 'pet0']  # select only pet 0 exam
            
        if 'subset' not in df.columns:
            key_split = 'PATIENT_ID'  # unique id
            idx = np.arange(df[key_split].nunique()) #0 to number of PET0
            split = np.empty(df[key_split].nunique(), dtype="<U6")

            idx_train, idx_test = train_test_split(idx, test_size=self.test_size, random_state=self.seed) #index 

            size = self.val_size / (1 - self.test_size)
            idx_train, idx_val = train_test_split(idx_train, test_size=size, random_state=self.seed) #index 

            split[idx_train] = 'train'
            split[idx_val] = 'val'
            split[idx_test] = 'test' #put at avery index train, test, val
            #split = array avec train val test aux index correspondant

            df_patient = pd.DataFrame(data={key_split: df[key_split].unique(),
                                                'subset': split})
            df = df.merge(df_patient, on=key_split, how='left')
            #add column subset on the DataFrame/CSV

            df_train = df[df['subset'] == 'train']
            df_val = df[df['subset'] == 'val']
            df_test = df[df['subset'] == 'test']
            #a la fin du csv avec pandas, rajoute train, val ou test 
            if subset is not None : 
                return self.wrap_in_list_of_dict(df[df['subset'] == subset])

            if wrap_with_dict:
                #wrap in list of dict train, test and val set
                return self.wrap_in_list_of_dict(df_train), self.wrap_in_list_of_dict(df_val), self.wrap_in_list_of_dict(df_test)
            else:
                X_train, y_train = list(zip(df_train['NIFTI_PET'].values, df_train['NIFTI_CT'].values)), df_train['NIFTI_MASK'].values
                X_val, y_val = list(zip(df_val['NIFTI_PET'].values, df_val['NIFTI_CT'].values)), df_val['NIFTI_MASK'].values
                X_test, y_test = list(zip(df_test['NIFTI_PET'].values, df_test['NIFTI_CT'].values)), df_test['NIFTI_MASK'].values

                return X_train, X_val, X_test, y_train, y_val, y_test

   

    @staticmethod
    def wrap_in_dict(df):
        """
        :return: {'pet_img': [pet_img0, pet_img1, ...],
                  'ct_img': [ct_img0, ct_img1, ..],
                  'mask_img': [mask_img0, mask_img1, ...]}
        """

        return {'pet_img': df['NIFTI_PET'].values,
                'ct_img': df['NIFTI_CT'].values,
                'mask_img': df['NIFTI_MASK'].values}

    @staticmethod
    def wrap_in_list_of_dict(df):
        """
        :return: [ {'pet_img': pet_img0_path, 'ct_img': ct_img0_path, 'mask_img': mask_img0_path}
                    {'pet_img': pet_img1_path, 'ct_img': ct_img1_path, 'mask_img': mask_img1_path}
                    {'pet_img': pet_img2_path, 'ct_img': ct_img2_path, 'mask_img': mask_img2_path} ...]
        """

        mapper = {'NIFTI_PET': 'pet_img', 'NIFTI_CT': 'ct_img', 'NIFTI_MASK': 'mask_img'}
        return df[['NIFTI_PET', 'NIFTI_CT', 'NIFTI_MASK']].rename(columns=mapper).to_dict('records')



