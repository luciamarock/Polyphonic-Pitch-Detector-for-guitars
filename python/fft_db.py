import numpy as np
import os

# Function to extract the numeric part of a filename
def get_numeric_part(filename):
    return int(filename.split('.')[0])
    
    
def walkdir(fft_files_dir):
    file_list = os.listdir(fft_files_dir)
    file_list.sort(key=get_numeric_part)
    list_of_files = []
    for filename in file_list:
        # Full path to the file
        file_path = os.path.join(fft_files_dir, filename)    
        list_of_files.append(file_path)
    return list_of_files
        
def arbitrary_depth_walk(root_directory):
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(root_directory):
        for filename in files:
            # Get the full path to the current file
            file_path = os.path.join(root, filename)            
            print("Processing {}".format(file_path))

def compose_db(list_of_fft_files):    
    average_ffts = []
    for fft_file in list_of_fft_files:
        fft_data = np.genfromtxt(fft_file)
        average_fft = np.mean(fft_data, axis=0)
        """ Norm Peak """
        #itsMax = np.max(average_fft)
        #scaled_fft = abs(average_fft / itsMax)
        """ Norm Energy """
        sum_of_elements = np.sum(average_fft)
        scaled_fft = abs(average_fft / sum_of_elements)
        average_ffts.append(scaled_fft)
    return average_ffts

def concatenate_and_compose(list_ibanez, list_prs):
    average_ffts = []
    for i in range(len(list_ibanez)):
        fft_data1 = np.genfromtxt(list_ibanez[i])
        if i < len(list_prs):
            fft_data2 = np.genfromtxt(list_prs[i])
            fft_data_combined = np.vstack((fft_data1, fft_data2))
        else:
            fft_data_combined = fft_data1
        average_fft_combined = np.mean(fft_data_combined, axis=0)
        """ Norm Energy """
        sum_of_elements = np.sum(average_fft_combined)
        scaled_fft = abs(average_fft_combined / sum_of_elements)
        average_ffts.append(scaled_fft)
    return average_ffts