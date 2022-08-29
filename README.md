# nso6_to_hdf5
Converts nso type 6 data headers, data, linelist, and response functions to hdf5 format

File: nso6_to_hdf5.py is python file to do the conversion
      Usage: python nso6_to_hdf5.py <Filename> (without extension)
File: Cr110600.001_r.hdr: example header file (created from xgremlin)
      Cr110600.001_r.dat: example data file (created from xgremlin)
      Cr110600.001_r.lin: example binary lines file (created from xgremlin)
      Cr110600.001_r.resposne: example response function (created from xgremlin)
Output file is Cr110600.001_r.hdf5, and can be read with hdf5view.
