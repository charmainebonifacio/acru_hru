############################################################################################
# TITLE        : RCM_Summary
# CREATED BY   : Charmaine Bonifacio
# DATE CREATED : April 29, 2014
# EDITED BY    : Charmaine Bonifacio
# DATE EDITED  : May 13, 2014
#------------------------------------------------------------------------------------------
# DESCRIPTION  : This python script will run further downscaling analysis on the RCM data-
#                set using the Daily 10KM Grid Data.
#------------------------------------------------------------------------------------------
# TOOL SETUP FOR INPUT PARAMETERS:
#                Display Name:         Data Type:          Direction:      Type:
#                Watershed Boundary    Raster              Input           Required
#                AB Grid               Raster              Input           Required
#                Elevation             Raster              Input           Required
#                Land Cover            Raster              Input           Required
#                Rasiation             Raster              Input           Required
#                Output Directory      Directory           Input           Required
#                HRU Name              Text                Input           Required
#------------------------------------------------------------------------------------------
# INPUT        : > The Daily 10KM Grid Data
#                > RCM Grid Data
#                > Monthly Raster File per variable (ie Tmin, Tmax or Precip)
# OUTPUT       : The shapefile that contains AB10 and RCM. It should contain additional
#                fields.
############################################################################################

# Import system modules
import os
import sys
import arcpy
import arcpy.sa as sa
from arcpy import env
from arcpy.sa import *
import time
import math

# Set overwrite option
arcpy.env.overwriteOutput = True

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# GLOBAL VARIABLES
# Function Parameters for RASTER CONVERSION
global simplify
global raster_field
simplify = "NO_SIMPLIFY"
raster_field = "Value"

# Function Parameters for DISSOLVE
global in_features
global out_feature_class
global dissolve_field
global statistics_fields
global multi_part
global unsplit_lines
dissolve_field = "GRIDCODE"
statistics_fields = ""
multi_part = "MULTI_PART"
unsplit_lines = "DISSOLVE_LINES"

# Function Parameters for TABLE
global field_name
global field_type 
global field_precision 
global field_scale 
global field_length 
global field_alias 
global field_is_nullable 
global field_is_required 
global field_domain
global expression
global expression_type
global code_block
field_name = "AREAKM2"
field_type = "DOUBLE"
field_precision = ""
field_scale = ""
field_length = ""
field_alias = ""
field_is_nullable = "NULLABLE"
field_is_required = "NON_REQUIRED"
field_domain = ""
expression = "!SHAPE.AREA@SQUAREKILOMETERS!"
expression_type = "PYTHON_9.3"
code_block = "#"

# Miscellaneous variables:
global underScore
global output
underScore = "_"
output = "Results"

# File Variables
global fileType
global dbfExt
global shpExt
dbfExt = '.dbf'
shpExt = '.shp'

############################################################################################                      
# HELPER FUNCTIONS
#-------------------------------------------------------------------------------------------
# FUNCTION: checkFolderStatus
# This function will check the status of the directory.
def checkFolderStatus( directoryPath ):
    print "Checking directory status on: "
    print "* %s " % directoryPath
    if os.path.exists(directoryPath) == True:
        print "Valid directory."
        return True
    else:
        print "Invalid directory. Try again."
        return False
#-------------------------------------------------------------------------------------------
# FUNCTION: createOutputFolder
# This function creates a directory if it does not exists.
def createOutputFolder( directoryPath ):
    if not os.path.exists(directoryPath):
        os.makedirs(directoryPath)
        print "Created output %s. " % directoryPath
    else: print "%s already exists. " % directoryPath
#-------------------------------------------------------------------------------------------
# FUNCTION: checkFileStatus
# This function checks the status of the file.
def checkFileStatus( fileName ):
    print "Checking file status on: "
    print "* %s " % fileName
    if os.path.isfile(fileName) == True:
        print "Valid input. File exists."
        return True
    else:
        print "Invalid input. File does not exist."
        return False
#-------------------------------------------------------------------------------------------
# FUNCTION: concatenateStringNames
# This function renames the field names by concatenating two strings and a link.
def renameStrings( name1, name2, link ):
    return name1 + link + name2
#-------------------------------------------------------------------------------------------
# FUNCTION: quitProgram
# User is required to enter "O" to quit the program
def quitProgram():
    global quitText
    quitText = input("\nEnter 0 to quit program: ")
    if quitText == 0:
        return True
    else: quitProgram();
    
############################################################################################
# GEOPROCESSING FUNCTIONS
#-------------------------------------------------------------------------------------------
# FUNCTION: rasterCalculator
#   RasterCalculator (expression, output_raster)
def rasterCalculator( raster_expression, output_raster ):
    env.workspace = workspace
    arcpy.gp.RasterCalculator_sa(raster_expression,
                                 output_raster)

#-------------------------------------------------------------------------------------------    
# FUNCTION: rasterConversion
#   RasterToPolygon_conversion (in_raster, out_polygon_features, {simplify}, {raster_field})
def rasterConversion( workspace, in_raster, out_polygon_features ):
    env.workspace = workspace
    arcpy.RasterToPolygon_conversion(in_raster,
                                     out_polygon_features,
                                     simplify,
                                     raster_field)

#-------------------------------------------------------------------------------------------
# FUNCTION: rasterConversion
#   Dissolve_management (in_features, out_feature_class, {dissolve_field},
#                        {statistics_fields}, {multi_part}, {unsplit_lines})
def dissolveManagement( workspace, in_features, out_feature_class ):
    env.workspace = workspace
    Dissolve_management(in_features,
                        out_feature_class,
                        dissolve_field,
                        statistics_fields,
                        multi_part,
                        unsplit_lines)
        
#-------------------------------------------------------------------------------------------
# FUNCTION: addcalculate_FieldManagement
#
#   USES THE FOLLOWING ARCPY FUNCTIONS:
#       AddField_management (in_table, field_name, field_type,
#                            {field_precision}, {field_scale}, {field_length},
#                            {field_alias}, {field_is_nullable},
#                            {field_is_required}, {field_domain})
#       CalculateField_management (in_table, field_name, expression,
#                                  {expression_type}, {code_block})
def addcalculate_FieldManagement( workspace, in_table  ):
    env.workspace = workspace
    arcpy.AddField_management(in_table,
                              field_name,
                              field_type,
                              field_precision,
                              field_scale,
                              field_length,
                              field_alias,
                              field_is_nullable,
                              field_is_required,
                              field_domain)
    arcpy.CalculateField_management(in_table,
                                    field_name,
                                    expression,
                                    expression_type)

############################################################################################
# MAIN FUNCTION
#-------------------------------------------------------------------------------------------
def main():
    # Obtain Input From User
    ws_file = arcpy.GetParameterAsText(0) # INPUT Raster
    ab_file = arcpy.GetParameterAsText(1) # INPUT Raster
    elev_file = arcpy.GetParameterAsText(2) # INPUT Raster
    lc_file = arcpy.GetParameterAsText(3) # INPUT Raster
    rad_file = arcpy.GetParameterAsText(4) # INPUT Raster 
    workSpace = arcpy.GetParameterAsText(5) # OUTPUT Directory
    HRUName = arcpy.GetParameterAsText(6) # Input HRU
    #
    # Monitor Time Elapsed
    # ===================================
    beginTime = time.clock()
    arcpy.AddMessage("\nChecking files and directories")

    # Create output folder
    outWorkSpace = os.path.join ( workSpace + os.sep, output )
    if checkFolderStatus( outWorkSpace ) == False:
        createOutputFolder( outWorkSpace );
    HRUEXP = ( ws_file * 100000000) + ( ab_file * 100000) + ( elev_file * 1000) + ( lc_file * 10) + rad_file
    arcpy.AddMessage("\nExpression".format(HRUEXP))
    HRU = os.path.join ( outWorkSpace + os.sep, HRUName )
    arcpy.AddMessage("\nHRU file".format(HRU))
    HRUEXP.save(HRU)

    # Process: Raster to Polygon
    SHPName = renameStrings( HRUName, shpExt, underScore )
    SHP = os.path.join ( outWorkSpace + os.sep, SHPName )
    rasterConversion( outWorkSpace, HRU, SHP )

    # Process: Dissolve
    SHPDisName = renameStrings( SHPName.rstrip(".shp"), "dis" + shpExt, underScore )
    SHPDis = os.path.join ( outWorkSpace + os.sep, SHPDisName )
    dissolveManagement( outWorkSpace, SHP, SHPDis )

    # Process: Add Field + Calculate Field
    addcalculate_FieldManagement( outWorkSpace, SHPDis )

    endTime = time.clock()
    time.sleep(2.0)
    return True # For MAIN function
        
#############################################################################################
# RUN MAIN PYTHON SCRIPT
#--------------------------------------------------------------------------------------------
try:
    if main() == False: sys.exit(0);

except:
    arcpy.AddMessage(arcpy.GetMessages())
