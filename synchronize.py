import os
import shutil
import time


#SubClass to write logs to both a file and the console
class log():
    COPYED_STR = "Copyed"
    REMOVED_STR = "Removed"
    CREATED_STR = "Created"

    #Constructor: Create instance variables
    def __init__(self, log_path):
        self.log_path = os.path.join(log_path,"log.txt")

    #Base function that can be utilized by other classes
    def write(self, operation, path):
        self.write_file(operation, path)
        self.write_console(operation, path)

    #Write the log into a file
    def _write_file(self, operation, path):
        with open(self.log_path, "a") as file:
            file.write("Path:{} has been {} \n".format(path, operation))

    #Write the log to display in the console
    def _write_console(self, operation, path):
        print("Path:{} has been {} \n".format(path, operation))


#Main class for synchronization
class synchronization():

    #Constant variable
    CHECK_STR = "check"
    DELETE_STR = "delete"

    #Constructor: Create instance variables
    def __init__(self, source_path, replica_path, log_path, interval_time):
        self.source_path = source_path
        self.replica_path = replica_path
        self.log_path = log_path
        self.interval_time = interval_time
        self.log_instance = log(self.log_path)
    
    #Base Function
    def synchronize(self):
        self.walk_path(self.source_path, self.replica_path, self.CHECK_STR)
        self.walk_path(self.replica_path, self.source_path, self.DELETE_STR)


    #Path Navigation: Verify directories and files, or delete them if needed
    def walk_path(self, path1, path2, operator):
        for root, dirs, files in os.walk(path1):
            rel_path = os.path.relpath(root, path1)
            dis_path = os.path.join(path2, rel_path)

            for dir in dirs:
                base_path = os.path.join(root, dir)
                dir_path = os.path.join(dis_path,dir)
                expersion = self.make_expersion(operator, dir_path, base_path)
                eval(expersion)

            for file in files:
                file_path = os.path.join(root,file)
                rep_path = os.path.join(path2,file)
                expersion = self.make_expersion(operator, rep_path, file_path, self.DELETE_STR)
                eval(expersion)


    #Create an expression to call functions
    def make_expersion(self, operator, path1, path2, type= None):
        #If the condictions evaluates to true, this section will be executed
        if operator == self.CHECK_STR and type == None:
            expersion_value = "self.{}_dir(r'{}')".format(operator, path1)
        #If the conditiona is true, this section will be executed to delete the directory
        elif operator == self.DELETE_STR and type == None:
            expersion_value = "self.{}_dir(r'{}',r'{}')".format(operator, path1, path2)
        #Else operator is for Delete files
        else:
            expersion_value = "self.{}_file(r'{}',r'{}')".format(operator, path1, path2)
        return expersion_value

    #It will check the directory path, and if it does not exist in the replica, it will create it
    def check_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            self.log_instance.write(self.log_instance.CREATED_STR, dir_path)


    #It will check the file, and if it does not exist in the replica, it will create it
    def check_file(self, des_path, source_path):
        if not os.path.exists(des_path) or (
            os.path.exists(des_path) and 
            (os.path.getmtime(des_path) < os.path.getmtime(source_path))
            ):
            shutil.copy2(source_path, des_path)
            self.log_instance.write(self.log_instance.COPYED_STR, des_path)

    #It will check the directory path, and if it does not exist in the source, it will be deleted
    def delete_dir(self, file_path, base_path):
        if not os.path.exists(file_path):
            shutil.rmtree(base_path)
            self.log_instance.write(self.log_instance.REMOVED_STR, base_path)
            
    #It will check the file, and if it does not exist in the source, it will be deleted
    def delete_file(self, des_path, source_path):
        if not os.path.exists(source_path):
            os.remove(des_path)
            self.log_instance.write(self.log_instance.REMOVED_STR, des_path)
        


if __name__ == "__main__" :
    #I could receive all the arguments as a single input, but it might be difficult for the user to provide them that way, so I decided to split them
    print("Enter your source path:")
    source_path = input()
    print("Enter your replica path:")
    replica_path = input()
    print("Enter your log path:")
    log_path = input()
    print("Enter your desired time for periodic review (min):")
    interval_time = int(input())
    

    #Instantiate a synchronization class by providing the necessary parameters to its constructor
    sync_files = synchronization(source_path, replica_path, log_path, interval_time)

    #Invoke the base function of the synchronization class to initiate the check process
    sync_files.synchronize()


    # This section will repeatedly call the function at regular intervals specified by the user
    while True:
        time.sleep(interval_time)
        sync_files.synchronize()