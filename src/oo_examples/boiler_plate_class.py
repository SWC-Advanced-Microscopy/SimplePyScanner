import numpy as np


class boiler_plate_class():
    '''
        boiler_plate_class

        Purpose
        This is a minimal example class that doesn't do anything very interesting but
        captures the basic behaviors of what a class is for.

        Usage
        You may call this class from the system command line. If so, an instance of the class
        is created then destroyed. e.g. run:
        $ python boiler_plate_class.py

        More usefully, however, call this from within Python to intercact with an instance
        of the class. For instance:

        >>> import boiler_plate_class as b
        >>> myBPC = b.boiler_plate_class()
        Constructing object of class "boiler_plate_class"
        boiler_plate_class.someProperty has a value of 0
        boiler_plate_class.someProperty has a value of 99

        >>> myBPC.set_someProperty_to_random_number()
        >>> myBPC.someProperty
        11
        >>> myBPC.set_someProperty_to_random_number()
        >>> myBPC.someProperty
        90
        >>> myBPC.print_value_of_someProperty()
        boiler_plate_class.someProperty has a value of 90
        >>> myBPC.someProperty=1234
        >>> myBPC.print_value_of_someProperty()
        boiler_plate_class.someProperty has a value of 1234
        >>> 
    '''


    # Properties of the class go here. A "property" is just a 
    # variable that is part of a class. 
    someProperty = 0 # Create a property called "someProperty" and assign it the value zero



    def __init__(self):
        # This method is the "constructor". It runs once when an instance of the class is instantiated.
        # "Instantiating" a class means to create an object of its type.
        # The "self" variable is created automatically and is an internal reference to the 
        # class itself. e.g. see how we access "someProperty" in the constructor. 

        print('Constructing object of class "boiler_plate_class"')

        self.print_value_of_someProperty()
        self.someProperty = 99
        self.print_value_of_someProperty()
    #close constructor


    def __del__(self):
        # This method is the "destructor". It runs once when the object is deleted.
        self.someProperty = 0 #Reset someProperty to zero for no good reason
        print('In destructor')
    #close destructor


    def set_someProperty_to_random_number(self):
        self.someProperty = round(np.random.rand() * 100);
    #close set_someProperty_to_random_number


    def print_value_of_someProperty(self):
        print("boiler_plate_class.someProperty has a value of %d" % self.someProperty)
    #close print_value_of_someProperty

#close boiler_plate_class



# If this file is called from the system command line, the following if statement 
# is True and the code there runs. 
if __name__ == '__main__':
    # Instantiates the class. Does nothing. Then kills it. 
    myInstance = boiler_plate_class()
    input('press return')
