#!/usr/bin/env python

from tables import *
import h5py
import numpy as np
import sys

#
# This class is used to match the structure in the original Fortran linelists generated by Xgremlin.
#

class linespec(IsDescription):
    sig = Float64Col()
    xint = Float32Col()
    width = Float32Col()
    dmping = Float32Col()
    itn = Int16Col()
    ihold = Int16Col()
    tags = StringCol(4)
    epstot = Float32Col()
    epsevn = Float32Col()
    epsodd = Float32Col()
    epsran = Float32Col()
    spare = Float32Col()
    ident = StringCol(32)  
    
def read_linelist(sp,flin):
    #
    # This function reads in the linelist and saves it as a pytable in the hdf5 file.
    # There is room for more than one linelist in the group, but this function currently only imports one.
    #

    from struct import unpack
    tags=[4]

    #
    # Read the header information in the .lin file
    #
    
    nlin=unpack("i",flin.read(4))[0]          # No. of lines in the file
    print(nlin, "lines in file")
    linlen = unpack("i",flin.read(4))[0]      # Total number of valid data in file
    
    # Next line is to make up total of 320 bytes that is the prefix in the file
    tmp = flin.read(312)
    
    #
    # Now read in all the lines and add to the pytable
    #
    for i in range(nlin) :
        sp['sig'],sp['xint'],sp['width'],sp['dmping'],sp['itn'],sp['ihold'] = unpack("dfffhh",flin.read(24))
        sp['tags'] = flin.read(4)
        sp['epstot'],sp['epsevn'],sp['epsodd'],sp['epsran'],sp['spare']=unpack("fffff",flin.read(20))
        sp['ident']=flin.read(32)
    
        sp.append()
    print(i+1,"lines converted")
    linel.flush()
    return()
#
# Main program
#

if len(sys.argv) != 2:
    print("Usage: 'python nos6_to_hdf5.py <filename>', with no extension to the filename")
    sys.exit()
else:
    specfile = sys.argv[1]

header = {}
linel=[]

#
# Open the header and use it to create the metadata
#
try:
	hdr = open(specfile + ".hdr")
except:
	print("No header file found")
	exit()
	
for line in hdr:
    if line[0] == "/" or line[0:3] == "END":
        continue
    if line[0:8] == "continue" :
        val = val + line[9:32]
    else:
        key = line[0:8].rstrip()
        val = line[9:32]
    if line[0:2] == "id":
        val = line[9:80]
    header[key]=val
    header[key+"_comment"] = line[34:80]

#
# Now read the data
#
    
with open(specfile + ".dat","rb") as f:
    spec = np.fromfile(f,np.float32)

#
#  TO DO:
#  Include something here to read complex files and split into two datasets - real and imaginary
#  Base it on the value of 'data_is'
#

if len(spec)-int(header["npo"]) !=0:
    print("No. of points does not match npo: npo = ", header["npo"], " length = ", len(spec))
else :
    print (len(spec), "points read")
    
#
# Create the hdf5 file, create spectrum group and write the data to a dataset in the spectrum group
#
    
hdf_file = open_file(specfile + '.hdf5','w', title="Cr spectrum")
spectrum_group = hdf_file.create_group("/","spectrum")
dataset = hdf_file.create_array(spectrum_group,"spectrum",spec,"original spectrum")

#
# Write the metadata to the dataset in the spectrum group
#

for key,value in header.items():
    dataset.attrs[key] = value

#
# Create a group for the linelists. Should be able to add more than one linelist with different dates, creators, etc.
# Create a linelist table using pytables within the group
#

try:
    flin = open(specfile+".lin","rb")
    linelist_group = hdf_file.create_group("/","linelists")   
    linel = hdf_file.create_table(linelist_group, "linelist1", linespec,"Original linelist")

    #
    # Now write the linelists to the tables
    #

    sp = linel.row
    read_linelist(sp,flin)

except:
	print("No linelist found")

#
# Create a group for the response function. Again, may have more than one with various versions.
# Create a dataset within it
#

response = np.empty((0,2),float)


try:
    fresp = open(specfile+".response","r")
    response_group = hdf_file.create_group("/","responses")
    for line in fresp:
       if line[0] == "!" :
           continue
       else:
           line = line.split()    
           response = np.append(response, np.array([[float(line[0]),float(line[1])]]), axis=0)
    
    resp_dset=hdf_file.create_array(response_group,"Response",response,"Original response")
    
            
except:
 	print("No response function found: trying file", specfile + ".response")
	

#
# Close file to save all the data
#

hdf_file.close()
