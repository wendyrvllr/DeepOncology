#METHODE SPECIFIQUES A MA CLASSIFICATION
import os
import numpy as np 
import matplotlib.pyplot as plt 

"""
methods to decode predictions, truths and show true/false predictions 
"""

def decodage_predictions(inference):
    """[summary]

    Args:
        inference ([list]): [ [(array_predictions_head,size=(nombre_inference,2)), (array_predictions_legs,size=(nombre_inference,3)), (array_predictions_right_arm,size=(nombre_inference,2)), (array_predictions_left_arm,size=(nombre_inference,2))]]

    Returns:
        [type]: [description]
    """
    result = []
    for i in range(len(inference[0])):
        #i = number of inferences
        sub_result = []
        for j in range(0,4) : 
            #j = head,legs, right_arm, left_arm
            a = inference[j][i].tolist()
            maxi = np.max(a)
            index = a.index(maxi)
            if j == 0 : #head 
                if index == 0 : 
                    sub_result.append('Vertex')
                else : 
                    sub_result.append('Eye / Mouth')
            elif j == 1 : #leg 
                if index == 0 : 
                    sub_result.append('Hips')
                elif index == 1 : 
                    sub_result.append('Knee')
                else : 
                    sub_result.append('Foot')

            elif j == 2 : #right arm 
                if index == 0 : 
                    sub_result.append('down')
                else : 
                    sub_result.append('up')

            elif j == 3 : #left arm
                if index == 0 : 
                    sub_result.append('down')
                else : 
                    sub_result.append('up')
        result.append(sub_result)
    return result


def decodage_truth(array) : 
    """decode truth label array

    Args:
        array ([type]): [array of size (number_of_labelled_img, 4)]

    Returns:
        [type]: [description]
    """
    truth = []
    for i in range(array.shape[0]): 
        sub = []
        liste = array[i].tolist()
        #head
        if liste[0] == 0 : 
            sub.append('Vertex')
        else : 
            sub.append('Eye / Mouth')
        #leg 
        if liste[1] == 0 : 
            sub.append('Hips')
        if liste[1] == 1 : 
            sub.append('Knee')
        if liste[1] == 2 : 
            sub.append('Foot')
        #right arm 
        if liste[2] == 0 : 
            sub.append('down')
        if liste[2] == 1 : 
            sub.append('up')
        #left arm 
        if liste[3] == 0 : 
            sub.append('down')
        if liste[3] == 1 : 
            sub.append('up')

        truth.append(sub)

    return truth 
        

def affichage(liste_array, liste_pred_label, liste_true_label, directory):
    """generate image with true and predict labels, and save them in True or False folder.

    Args:
        liste_array ([list]): [description]
        liste_pred_label ([list]): [description]
        liste_true_label ([list]): [description]
        directory ([str]): [description]
    """

    true = directory+'/predictions/true'
    false = directory+'/predictions/false'
    os.makedirs(false)
    os.makedirs(true)
    for i in range(len(liste_array)):
        image = liste_array[i][:,:,0] #2D
        image = np.rot90(image, k=2)
        f = plt.figure(figsize=(10,16))
        axes = plt.gca()
        axes.set_axis_off()
        plt.imshow(image, cmap='gray')
        plt.title("pred : {}, truth : {}".format(liste_pred_label[i], liste_true_label[i]))
        #plt.show()

        if liste_pred_label[i] == liste_true_label[i] : 
            filename = true+'/'+str(i)+'.jpeg'
            f.savefig(filename, bbox_inches='tight', origin='lower') 
            plt.close()

        else : 
            filename = false+'/'+str(i)+'.jpeg'
            f.savefig(filename, bbox_inches='tight', origin='lower') 
            plt.close()


