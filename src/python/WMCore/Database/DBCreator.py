#!/usr/bin/python

"""
_DBCreator_

Base class for formatters that create tables.

"""

__revision__ = "$Id: DBCreator.py,v 1.5 2008/10/13 12:43:46 metson Exp $"
__version__ = "$Revision: 1.5 $"
__author__ = "fvlingen@caltech.edu"



from WMCore.Database.DBFormatter import DBFormatter
from WMCore.WMException import WMException
from WMCore.WMExceptions import WMEXCEPTION


class DBCreator(DBFormatter):
    
    """
    _DBCreator_
    
    Generic class for creating database tables.
    
    """
    
    def __init__(self, logger, dbinterface):
        """
        _init_
        
        Call the constructor of the parent class and create empty dictionaries
        to hold table create statements, constraint statements and insert
        statements.
        """
        DBFormatter.__init__(self, logger, dbinterface)
        self.create = {}
        self.constraints = {}
        self.inserts = {}
        self.indexes = {}
            
    def execute(self, conn = None, transaction = False):     
        """
        _execute_
        
        Generic method to create tables and constraints by execute
        sql statements in the create, and constraints dictionaries.
        
        Before execution the keys assigned to the tables in the self.create
        dictionary are sorted, to offer the possibilitiy of executing 
        table creation in a certain order.
        """
        # get the keys for the table mapping:
        tableKeys = self.create.keys()
        tableKeys.sort()
        
        for i in tableKeys:
            self.logger.debug( i )
            try:
                self.dbi.processData(self.create[i], 
                                     conn = conn, 
                                     transaction = transaction)
            except Exception, e:
                
                msg = WMEXCEPTION['WMCore-2'] + '\n\n' +\
                                  str(self.create[i]) +'\n\n' +str(e)
                self.logger.debug( msg )
                raise WMException(msg,'WMCore-2')
            
            keys = self.constraints.keys()
            self.logger.debug( keys )

        for i in self.constraints.keys():
            self.logger.debug( i )
            try:
                self.dbi.processData(self.constraints[i], 
                                 conn = conn, 
                                 transaction = transaction)
            except Exception, e:
                self.logger.debug( e )
                
        for i in self.indexes.keys():
            self.logger.debug( i )
            try:
                self.dbi.processData(self.indexes[i], 
                                     conn = conn, 
                                     transaction = transaction)
            except Exception, e:
                self.logger.debug( e ) 

        for i in self.inserts.keys():
            self.logger.debug( i )
            try:
                self.dbi.processData(self.inserts[i], 
                                     conn = conn, 
                                     transaction = transaction)
            except Exception, e:
                self.logger.debug( e )                

        return True
   
    def __str__(self):
        """
        _str_
        
        Return a well formatted text representation of the schema held in the
        self.create, self.constraints, self.inserts, self.indexes dictionaries.
        """
        string = ''
        for i in self.create, self.constraints, self.inserts, self.indexes:
            for j in i.keys():
                string = string + i[j].lstrip() + '\n'
        return string
        