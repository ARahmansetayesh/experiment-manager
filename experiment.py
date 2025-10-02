from abc import ABC, abstractmethod

import pickle
import numpy as np

import os
import logging
import traceback

from datetime import datetime






class Experiment_abst(ABC):
    required_attributes = ["experiment_title" , "experiment_unique_id", "experiment_description"]
    
    @abstractmethod
    def __init__(self , hyper_parameters: dict):
        self.save_result_path = "experiment_data"
        self.save_log_path = "experiment_log"

        self.hyper_parameters = hyper_parameters
        self.experiment_done = False


    
    @abstractmethod    
    def run(self):
        """Run the experiment.
        This method should be implemented by subclasses to define the specific steps of the experiment.
        this method should fill self.final_experiment_log self.final_experiment_quality self.final_experiment_data with the results of the experiment.
        
        """
        raise NotImplementedError()
    
        self.final_experiment_quality = 0
        self.final_experiment_data = {}
        self.final_experiment_log = ""

        return


    def get_final_experiment_quality(self) :
        return self.final_experiment_quality
    


    def get_final_experiment_log(self) -> str:
        return self.final_experiment_log


    def get_final_experiment_data(self) -> dict:
        return self.final_experiment_data



        

    def __init_subclass__(cls):
        for attr in cls.required_attributes:
            if not hasattr(cls, attr):
                raise TypeError(f"Missing required attribute: {attr}")
        super().__init_subclass__()


    
    def get_experiment_parameter_specification(self) -> str:
        parameter_specification = ""
        for key in self.hyper_parameters:

            if key[0] != "_": # ignore keys starting with "_" . this option is for the hyperparameters that dont have effect on the experiment results (fo example a parameter that just impact model in evaluation mode and doesn effect the model we save)
                if isinstance(self.hyper_parameters[key], str):
                    parameter_specification += key + "_" + self.hyper_parameters[key] + "_" 
                if isinstance(self.hyper_parameters[key], int):
                    parameter_specification += key + "_" + str(self.hyper_parameters[key]) + "_" 
                if isinstance(self.hyper_parameters[key], float):
                    parameter_specification += key + "_" + str(self.hyper_parameters[key]).replace(".", "d")  + "_"
                if isinstance(self.hyper_parameters[key], bool):
                    parameter_specification += key + "_" + str(self.hyper_parameters[key])  + "_"
                if self.hyper_parameters[key] is None:
                    parameter_specification += key + "_" + "None"  + "_"
                if isinstance(self.hyper_parameters[key], list):
                    if all(isinstance(x, int) or isinstance(x, float) or isinstance(x, str) for x in self.hyper_parameters[key]):
                        str0 = "_".join(str(x).replace(".", "d") for x in self.hyper_parameters[key])
                        parameter_specification += key + "_" + str0 + "_"
        

        return parameter_specification[:-1]

    
    def run_and_save_log(self , repeat_if_log_is_saved = False , save_log = True , save_result = True , save_result_quality_threshold = 1):
        
        """
         if the experiment log is already saved, the experiment will not run again if repeat_if_log_is_saved is set to False
         if the experiment log is already saved, the experiment will run again if repeat_if_log_is_saved is set to True
         if save_log is set to True, the experiment log will be saved
         if save_result is set to True, the experiment result will be saved if the final_experiment_quality is greater than or equal to save_result_quality_threshold, but the experiment log will be saved
         if save_result is set to False, the experiment result will not be saved regardless of the final_experiment_quality

        """

        try:
   



            if repeat_if_log_is_saved == False :
                if self.is_experiment_log_saved() == False:
                    print("\nThe experiment:\n" + self.experiment_title + ": " + self.get_experiment_parameter_specification()  + "\nis running.")
                    self.run()
                    self.experiment_done = True
                    

                    if save_log==True:
                        self.save_experiment_log()

                    if save_result==True:
                        if save_result_quality_threshold <= self.get_final_experiment_quality():
                            self.save_experiment_result()  

                    print("The experiment execution has ended.")
                    return self.get_final_experiment_data()

                else:
                    print("\nThe experiment:\n\n" + self.experiment_title + ": " + self.get_experiment_parameter_specification()  + "\n\ndid not run because the log has already been saved.\n")

                    self.results = self.load_experiment_result()

                    return self.results

            else:
                print("\nThe experiment:\n" + self.experiment_title + ": " + self.get_experiment_parameter_specification()  + "\nis running.")
                self.run()
                self.experiment_done = True
                


                if save_log==True:
                    self.save_experiment_log()

                if save_result==True:
                    if save_result_quality_threshold <= self.get_final_experiment_quality():
                        self.save_experiment_result()  

                print("The experiment execution ended.")
                return self.get_final_experiment_data()
        



        except Exception as e:

            tb_str = traceback.format_exc()

            print(tb_str)

            self.log_error("")
   
    
    def is_experiment_done(self) -> bool:
        return self.experiment_done
    


    
    def is_experiment_log_saved(self) -> bool:

        if not os.path.isdir(self.save_log_path):
            return False

        save_path = self.save_log_path + "/" + self.experiment_title     

        if not os.path.isdir(save_path):
            return False

        for log_file_name in os.listdir(save_path):

            if "experiments_log_quality" in log_file_name :

                experiment_title =  self.experiment_title 
                unique_id =  self.experiment_unique_id  
                parameters_specification = self.get_experiment_parameter_specification() 
                # text_to_write += "\nid: " + self.experiment_unique_id + "\n"
                # text_to_write += "Parameters specification: " + self.experiment_title + "\n\n"

                n = 0
                with open(save_path + "/" + log_file_name, 'r') as file:
                    for line in file:


                        if experiment_title in line:
                            n+=1

                        elif unique_id in line:
                            n+=1
                        elif parameters_specification in line:
                            n+=1

                        else:
                            n=0

                        if n==3 :
                            return True

        return False
            



    
    def is_experiment_result_saved(self) -> bool:
        if  os.path.isdir(self.save_result_path):
            path_experiment = self.save_result_path + "/" + self.experiment_title
            if  os.path.isdir(path_experiment):
                file_path_name = path_experiment + "/" + self.get_experiment_parameter_specification()     
                if os.path.exists(file_path_name):
                    return True
        return False

    def save_experiment_result(self) -> bool:
        
        if self.experiment_done == False :
            return
        
        experiment_result = self.get_final_experiment_data() 
        assert isinstance(experiment_result, dict), 'Argument of wrong type!'

        now = datetime.now()

        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        experiment_result["timestamp"] = formatted_datetime
        
        if not os.path.isdir(self.save_result_path):
            os.mkdir(self.save_result_path)
        path_experiment = self.save_result_path + "/" + self.experiment_title     
        if not os.path.isdir(path_experiment):
            os.mkdir(path_experiment)
        file_path_name = path_experiment + "/" + self.get_experiment_parameter_specification()     
        with open( file_path_name  , "wb") as fp:   #Pickling
            pickle.dump( experiment_result  , fp)  


    def load_experiment_result(self) -> bool:
        experiment_result = {}
        if  os.path.isdir(self.save_result_path):
            path_experiment = self.save_result_path + "/" + self.experiment_title     
            if  os.path.isdir(path_experiment):
                file_path_name = path_experiment + "/" + self.get_experiment_parameter_specification()     
                if os.path.exists(file_path_name):
                    with open( file_path_name , "rb") as fp:   #Pickling
                        experiment_result = pickle.load(fp) 

        return experiment_result



    
    def save_experiment_log(self) :
        
        if self.experiment_done == False :
            return
        
        if not os.path.isdir(self.save_log_path):
            os.mkdir(self.save_log_path)

        save_path = self.save_log_path + "/" + self.experiment_title               
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        quality = self.get_final_experiment_quality()
        assert isinstance(quality, int), 'Argument of wrong type!'
        assert quality>=0, 'Quality should be a non-negative integer!'
        log_file_name = "/experiments_log_quality_" +  str(quality) + ".txt"

        now = datetime.now()

        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")

        text_to_write = "\r\n\r\n--------------------------------\r\n" + formatted_datetime + "\r\nExperiment title: " + self.experiment_title + "  \r\n"
        text_to_write += "id: " + self.experiment_unique_id + "  \r\n"
        text_to_write += "Parameters specification: " + self.get_experiment_parameter_specification() + "  \r\n\r\n"
        text_to_write += self.get_final_experiment_log() + "\r\n---------\r\n"
        with open(save_path +  log_file_name, "a") as file:
            file.write(text_to_write)


    def log_error(self , str_error_log) -> bool:

        if not os.path.isdir(self.save_log_path):
            os.mkdir(self.save_log_path)
        save_path = self.save_log_path + "/" + self.experiment_title  
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
                

        log_file_name = "/experiments_error_log.txt"

        logging.basicConfig(filename = save_path +  log_file_name , level=logging.ERROR, 
                    format='\r\n\r\n--------------------------------------\r\n%(asctime)s - %(levelname)s - %(message)s ' , force=True)
        
        # logger = logging.getLogger()
        # fhandler = logging.FileHandler(filename= self.save_log_path +  log_file_name  , mode='a' )
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # fhandler.setFormatter(formatter)
        # logger.addHandler(fhandler)
        # logger.setLevel(logging.DEBUG)


        text_to_write = "Experiment title: " + self.experiment_title + "  \r\n"
        text_to_write += "id: " + self.experiment_unique_id + "  \r\n"
        text_to_write += "Parameters specification: " + self.get_experiment_parameter_specification() 


        # Log the exception with full traceback
        logging.error("An error occurred \r\n" + text_to_write + "\r\n" + str_error_log + "\r\n", exc_info=True)

        logging.shutdown()





    
    def set_save_path(self , save_result_path:str ):
        assert isinstance(save_result_path, str), 'Argument of wrong type!'
        self.save_result_path = save_result_path

    def set_log_folder_name(self , save_log_path:str ):
        assert isinstance(save_log_path, str), 'Argument of wrong type!'
        self.save_log_path = save_log_path


    

def truncate_lists_to_min_length(list_of_lists):
    min_len = min(len(lst) for lst in list_of_lists)
    return [lst[:min_len] for lst in list_of_lists]