#!/usr/bin/env python
"""
_AvailableFiles_

MySQL implementation of Subscription.GetAvailableFiles

Return a list of files that are available for processing.
Available means not acquired, complete or failed and takes into account site 
black/white lists.

CREATE TABLE wmbs_file_location (
             file     INT(11),
             location INT(11),
             UNIQUE(file, location),
             FOREIGN KEY(file)     REFERENCES wmbs_file_details(id)
               ON DELETE CASCADE,
             FOREIGN KEY(location) REFERENCES wmbs_location(id)
               ON DELETE CASCADE)

CREATE TABLE wmbs_subscription_location (
             subscription     INT(11)      NOT NULL,
             location         INT(11)      NOT NULL,
             valid            BOOLEAN      NOT NULL DEFAULT TRUE,
             FOREIGN KEY(subscription)  REFERENCES wmbs_subscription(id)
               ON DELETE CASCADE,
             FOREIGN KEY(location)     REFERENCES wmbs_location(id)
               ON DELETE CASCADE)
"""

__all__ = []
__revision__ = "$Id: GetAvailableFiles.py,v 1.16 2010/06/23 20:49:04 mnorman Exp $"
__version__ = "$Revision: 1.16 $"

from WMCore.Database.DBFormatter import DBFormatter

class GetAvailableFiles(DBFormatter):
    def getSQLAndBinds(self, subscription, conn = None, transaction = None):
        sql = ""
        binds = {'subscription': subscription}
        
        sql = '''select count(valid), valid from wmbs_subscription_location
        where subscription = :subscription group by valid'''
        result = self.dbi.processData(sql, binds, 
                                      conn = conn, transaction = transaction)
        result = self.format(result)
        
        whitelist = False
        blacklist = False
        
        for i in result:
            # i is a tuple with count and valid, 0 = False
            if i[0] > 0 and i[1] == 0:
                blacklist = True
            elif i[0] > 0 and i[1] == 1:
                whitelist = True
        
       
        
        sql = """SELECT wff.file, wl.se_name FROM wmbs_fileset_files wff 
                  INNER JOIN wmbs_subscription ws ON ws.fileset = wff.fileset 
                  INNER JOIN wmbs_file_location wfl ON wfl.file = wff.file
                  INNER JOIN wmbs_location wl ON wl.id = wfl.location 
                  LEFT OUTER JOIN  wmbs_sub_files_acquired wa ON ( wa.file = wff.file AND wa.subscription = ws.id )
                  LEFT OUTER JOIN  wmbs_sub_files_failed wf ON ( wf.file = wff.file AND wf.subscription = ws.id )
                  LEFT OUTER JOIN  wmbs_sub_files_complete wc ON ( wc.file = wff.file AND wc.subscription = ws.id )
                  WHERE ws.id=:subscription AND wa.file is NULL 
                        AND wf.file is NULL AND wc.file is NULL 
              """


        if whitelist:
            sql += """ AND wfl.location IN (select location from wmbs_subscription_location where
                        subscription=:subscription AND valid = 1)"""
        elif blacklist:
            sql += """ AND wfl.location NOT IN (select location from wmbs_subscription_location where
                        subscription=:subscription AND valid = 0)"""

        #sql += " FOR UPDATE"
        return sql, binds

    def formatDict(self, results):
        """
        _formatDict_

        Cast the file column to an integer as the DBFormatter's formatDict()
        method turns everything into strings.  Also, fixup the results of the
        Oracle query by renaming 'fileid' to file.
        """
        formattedResults = DBFormatter.formatDict(self, results)

        for formattedResult in formattedResults:
            if "file" in formattedResult.keys():
                formattedResult["file"] = int(formattedResult["file"])
            else:
                formattedResult["file"] = int(formattedResult["fileid"])

        #Now the tricky part
        tempResults = {}
        for formattedResult in formattedResults:
            if formattedResult["file"] not in tempResults.keys():
                tempResults[formattedResult["file"]] = []
            if "se_name" in formattedResult.keys():
                tempResults[formattedResult["file"]].append(formattedResult["se_name"])

        finalResults = []
        for key in tempResults.keys():
            tmpDict = {"file": key}
            if not tempResults[key] == []:
                tmpDict['locations'] = tempResults[key]
            finalResults.append(tmpDict)

        return finalResults
           
    def execute(self, subscription = None, conn = None, transaction = False):

        sql, binds = self.getSQLAndBinds(subscription, conn = conn,
                                         transaction = transaction)

        results = self.dbi.processData(sql, binds, conn = conn,
                                      transaction = transaction)
        return self.formatDict(results)
