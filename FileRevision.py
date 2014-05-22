# -*- coding: utf-8 -*-
#
# Author: Timur Gilmullin
# (c) Positive Technologies, 2013


# This module realize work with revisions file.
# Revisions looks like dictionary with key funcName and value is the tuple: hash + source:
#     {"funcName1": (funcName1_hash, funcName1_source),
#      "funcName2": (funcName2_hash, funcName2_source), ...}
# File for revision contains list:
#     [revision's last date-n-time, {revisions}]
# Empty revision-file looks like this: [None, {}]


import os
import inspect
from datetime import datetime
import traceback


# text messages:
MSG_CHECK = "Checking revision for function:"
MSG_NOT_MODIFIED = "Given function not modified from last revision."
MSG_MODIFIED = "Given function was modified since last revision!"
MSG_UPDATE = "Starting update function:"
MSG_UPDATED = "Given function was update successful."
MSG_UPDATE_ERROR = "It was an error during update given function!"
MSG_DELETE = "Starting file-revision's clean process..."
MSG_DELETED = "All function revisions delete successful."
MSG_DELETE_ERROR = "It was an error during delete revision!"


class Revision():
    """
    Main class for realize work with revisions
    """

    def __init__(self, fileRevision='revision.txt'):
        self.fileRevision = fileRevision
        self.mainRevision = self._ReadFromFile(self.fileRevision)  # get main revision first

    def _ReadFromFile(self, file=None):
        """
        Helper function that parse and return revision from file.
        """
        revision = [None, {}]
        if file == None:
            file = self.fileRevision
        try:
            if os.path.exists(file) and os.path.isfile(file):
                with open(file) as fH:
                    revision = eval(fH.read())
        except:
            traceback.print_exc()
        finally:
            return revision

    def _WriteToFile(self, revision=[None, {}], file=None):
        """
        Helper procedure than trying to write given revision to file.
        """
        status = False
        if file == None:
            file = self.fileRevision
        try:
            with open(file, "w") as fH:
                fH.write(str(revision))
            status = True
        except:
            traceback.print_exc()
        finally:
            return status

    def _GetOld(self, func=None):
        """
        Get old revision for given function and return tuple: (old_hash, old_source).
        """
        funcHashOld = None  # old code is None if function not exist in previous revision
        funcSourceOld = None  # old hash is None if function not exist in previous revision
        try:
            if func.__name__ in self.mainRevision[1]:
                funcHashOld = self.mainRevision[1][func.__name__][0]  # field with old hash of function
                funcSourceOld = self.mainRevision[1][func.__name__][1]  # field with old code of function
        except:
            traceback.print_exc()
        finally:
            return (funcHashOld, funcSourceOld)

    def _GetNew(self, func=None):
        """
        Get new revision for given function and return tuple: (new_hash, new_source).
        """
        funcSourceNew = None  # if function doesn't exist, its also doesn't have code
        funcHashNew = None  # hash is None if function not exist
        try:
            funcSourceNew = inspect.getsource(func)  # get function's source
            funcHashNew = hash(funcSourceNew)  # new hash of function
        except:
            traceback.print_exc()
        finally:
            return (funcHashNew, funcSourceNew)

    def _Similar(self, hashOld, sourceOld, hashNew, sourceNew):
        """
        Checks if given params for modified then return tuple with revision's diff:
        (old_revision, new_revision), otherwise return None.
        """
        similar = True  # old and new functions are similar, by default
        if hashNew != hashOld:
            if sourceOld != sourceNew:
                similar = False # modified if hashes are not similar and functions not contains similar code
        return similar

    def Update(self, func=None):
        """
        Set new revision for function.
        revision = [revision date-n-time,
                    {"funcName1": (funcName1_hash, funcName1_source),
                    {"funcName2": (funcName2_hash, funcName2_source), ...}]
        """
        status = False
        if func:
            try:
                funcSourceNew = inspect.getsource(func)  # get function's source
                funcHashNew = hash(funcSourceNew)  # new hash of function
                revisionDateNew = datetime.now().strftime('%d.%m.%Y %H:%M:%S')  # revision's date
                funcRevisionNew = {func.__name__: [funcHashNew, funcSourceNew]}  # form for function's revision
                self.mainRevision[0] = revisionDateNew  # set new date for main revision
                self.mainRevision[1].update(funcRevisionNew)  # add function's revision to main revision
                if self._WriteToFile(self.mainRevision):  # write main revision to file
                    status = True
            except:
                traceback.print_exc()
            finally:
                return status

    def DeleteAll(self):
        """
        Helper function that parse and return revision from file.
        """
        status = False
        try:
            self.mainRevision = [None, {}]  # clean revision
            if self._WriteToFile(self.mainRevision):  # write main revision to file
                status = True
        except:
            traceback.print_exc()
        finally:
            return status

    def ShowOld(self, func=None):
        """
        Function return old revision for given function.
        """
        funcHashOld, funcSourceOld = self._GetOld(func)  # get old revision for given function
        dateStr = "Last revision: " + str(self.mainRevision[0])
        hashStr = "\nOld function's hash: " + str(funcHashOld)
        codeStr = "\nOld function's code:\n" + "- " * 30 + "\n" + str(funcSourceOld) + "\n" + "- " * 30
        oldRevision = dateStr + hashStr + codeStr
        return oldRevision

    def ShowNew(self, func=None):
        """
        Function return old revision for given function.
        """
        funcHashNew, funcSourceNew = self._GetNew(func)  # get old revision for given function
        hashStr = "New function's hash: " + str(funcHashNew)
        codeStr = "\nNew function's code:\n" + "- " * 30 + "\n" + str(funcSourceNew) + "\n" + "- " * 30
        newRevision = hashStr + codeStr
        return newRevision

    def Diff(self, func=None):
        """
        Checks if given function modified then return tuple with revision's diff:
        (old_revision, new_revision), otherwise return None.
        """
        funcHashOld, funcSourceOld = self._GetOld(func)  # get old revision for given function
        funcHashNew, funcSourceNew = self._GetNew(func)  # get new revision for given function
        # check old and new revisions:
        if self._Similar(funcHashOld, funcSourceOld, funcHashNew, funcSourceNew):
            diff = None  # not difference
        else:
            diff = ("Last revision: " + str(self.mainRevision[0]) +
                    "\nOld function's hash: " + str(funcHashOld) +
                    "\nOld function's code:\n" + "- " * 30 + "\n" +
                    str(funcSourceOld) + "\n" + "- " * 30,
                    "\nNew function's hash: " + str(funcHashNew) +
                    "\nNew function's code:\n" + "- " * 30 + "\n" +
                    str(funcSourceNew)  + "\n" + "- " * 30)  # if new function not similar old function
        return diff


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def _testFunction(a=None):
    """
    This is fake test function for module.
    """
    # this is comment
    if a:
        return True
    else:
        return False


if __name__ == '__main__':

    func = _testFunction  # set function for review in revision
    revision = Revision('revision.txt')  # init revision class for using with revision.txt

    # how to use this module for review revision of function:
    print(MSG_CHECK, func.__name__)
    funcModified = revision.Diff(func)  # get function's diff as tuple (old_revision, new_revision)
    if funcModified:
        print(MSG_MODIFIED)
        print(funcModified[0])  # old revision
        print(funcModified[1])  # new revision
    else:
        print(MSG_NOT_MODIFIED)

    # how to use this module for update revision:
    action = input("Update function's revision? [y/n]: ")
    if action == 'y':
        print(MSG_UPDATE, func.__name__)
        if revision.Update(func):
            print(MSG_UPDATED)
        else:
            print(MSG_UPDATE_ERROR)

    # how to use this module for clean file-revision:
    action = input("Clean file-revision now? [y/n]: ")
    if action == 'y':
        print(MSG_DELETE)
        if revision.DeleteAll():
            print(MSG_DELETED)
        else:
            print(MSG_DELETE_ERROR)

    # how to use this module for show old review:
    action = input('Show old revision for function? [y/n]: ')
    if action == 'y':
        print(revision.ShowOld(func))

    # how to use this module for show new review:
    action = input('Show new revision for function? [y/n]: ')
    if action == 'y':
        print(revision.ShowNew(func))