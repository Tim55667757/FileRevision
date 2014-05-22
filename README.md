FileRevision
============

This module realize work with revisions file.

Revisions looks like dictionary with key funcName and value is the tuple: hash + source:

   {"funcName1": (funcName1_hash, funcName1_source),
   
    "funcName2": (funcName2_hash, funcName2_source), ...}
    
File for revision contains list:

   [revision's last date-n-time, {revisions}]
   
Empty revision-file looks like this: [None, {}]
