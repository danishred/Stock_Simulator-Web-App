# __all__=["user_controller", "product_controller"]
import os
import glob

# Adding all control files to the variable all as a string after removing .py from the end
__all__=[os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py" )]

# for f in glob.glob(os.path.dirname(__file__) + "/*.py" ):
#     __all__.append(os.path.basename(f)[:-3])