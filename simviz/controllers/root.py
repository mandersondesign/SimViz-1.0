# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, lurl, request, redirect, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from simviz import model
from simviz.controllers.secure import SecureController
from simviz.model import DBSession, metadata, PlotRow, Variable, Configuration, Simulation, TestBench, LinkSimPlot
from tgext.admin.tgadminconfig import TGAdminConfig
from tgext.admin.controller import AdminController

from simviz.lib.base import BaseController
from simviz.controllers.error import ErrorController

from sqlalchemy import desc, Date, cast, and_, sql
from datetime import date

import json
import cgi, os
import subprocess
import sys
import cgitb; cgitb.enable()
import zipfile
import shutil

#from sqlalchemy import *
#import MySQLdb as mdb
import mat_conversion_v2

__all__ = ['RootController','SimVizController']


class SimVizController(BaseController):
    @expose('json')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('json')
    def data(self):
        """Handle the front-page."""
        result = {}
        result['id'] = 10
        result['name'] = 'Zsolt'
        
        return dict(page='data', result=result)

    @expose('json')
    def data2(self, name):
        """Handle the front-page."""
        result = {}
        result['id'] = 10
        result['name'] = name
        
        return dict(page='data', result=result)

    @expose('json')
    def data3(self, name, **kwargs):
        """Handle the front-page."""
        result = {}
        result['id'] = 10
        result['name'] = name
        result['args'] = kwargs
        
        return dict(page='data', result=result)

    @expose('json')
    def jsondata(self, cfgID):
        """Handle the front-page."""
        cur_dir = os.path.dirname(__file__)
        json_dir = os.path.abspath(os.path.join(cur_dir, "..", "public", "simviz", "data", cfgID))
        
        with open(os.path.join(json_dir, 'tree.json')) as json_data:
            result = json.load(json_data)
        
        return dict(page='data', result=result)

    def traverseForList(self, jsonObj):
        
        tempList = []
        
        if jsonObj != None:
            for item in jsonObj:
                if 'data_link' in item:
                    tempList.append(item)
                elif 'children' in item:
                    tempList.extend(self.traverseForList(item['children']))

        return tempList

    @expose('json')
    def loadVariables(self, simID):
        """Handle the front-page."""

        simDetails = DBSession.query(Simulation).filter_by(simID=simID).first()

        dataPath = simDetails.simDataPath.replace("/", "\\");

        cur_dir = os.path.dirname(__file__)
        json_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "simviz"))
        
        json_dir += dataPath
        #return dict(page='data', vars=json_dir)
        
        with open(os.path.join(json_dir, 'tree.json')) as json_data:
            result = json.load(json_data)
        
        finalList = []

        for r in result:
            if 'children' in r:
                toPass = r['children']
                finalList.extend(self.traverseForList(toPass))
            else:
                if 'data_link' in r:
                    finalList.append(r)

        for v in finalList:
            var = Variable()
            var.varSimID = simID
            var.varName = v['full_name']
            var.varShortName = v['name']
            var.varDataLink = v['data_link']

            varType = "var"
            if "param" in v['data_link']:
                varType="param"

            var.varType = varType
            DBSession.add(var)
            DBSession.flush()

        DBSession.query(Simulation).filter_by(simID=simID).update({Simulation.simIndexedFlag: 1}, synchronize_session=False)
        DBSession.flush()

        return dict(page='loadVariables', status=1, message="Variables have been indexed")

    @expose('json')
    def simList(self, cfgID):
        """Handle the front-page."""
        cur_dir = os.path.dirname(__file__)
        json_dir = os.path.abspath(os.path.join(cur_dir, "..", "public", "simviz", "data", cfgID))
        
        with open(os.path.join(json_dir, 'tree.json')) as json_data:
            result = json.load(json_data)
        
        finalList = []

        for r in result:
            if 'children' in r:
                toPass = r['children']
                finalList.extend(self.traverseForList(toPass))
            else:
                if 'data_link' in r:
                    finalList.append(r)


        return dict(page='data', vars=finalList)
    
    @expose('json')
    def getPlotJson(self):
        """Generate a dummy plot settings for demo"""
        
        plotSettings = {}

        plotSettings['Name'] = "Plot 1"
        plotSettings['xaxis'] = "Time"
        plotSettings['series'] = []

        # seriesEntry = {}
        # seriesEntry['name'] = "m_MaxTorque.MetricValue"
        # seriesEntry["short_name"] = "m_MaxTorque.MetricValue"
        # seriesEntry["variable_id"] = "50891"
        # seriesEntry["data_link"] = "var_0.json"
        # seriesEntry["type"] = "var"
        # seriesEntry["plot_id"] = "35"

        # plotSettings['series'].append(seriesEntry)


        plotSettings['TestBenchID'] = 31
        plotSettings['data_folder'] = "data/msd/"        

        plotInfo = {}
        plotInfo['plot_id'] = 20
        plotInfo['sim_id'] = 20
        plotInfo['config_id'] = 20
        plotInfo['testbench_id'] = 20
        plotInfo['plot_json'] = {}
        plotInfo['plot_settings'] = plotSettings
        plotInfo['plot_tree_location'] = 'data/msd/tree.json'
        plotInfo['plot_data_store_location'] = 'data/msd/'

        return dict(page='data', settings=plotInfo)

    @expose('json')
    def getTimeSeries(self, plotID):
        """Generate a dummy plot settings for demo"""
        
        seriesEntry = {}
        seriesEntry['name'] = "time"
        seriesEntry["short_name"] = "time"
        seriesEntry["variable_id"] = "25243"
        seriesEntry["data_link"] = "var_0.json"
        seriesEntry["type"] = "var"
        seriesEntry["plot_id"] = plotID

        return dict(page='data', time=seriesEntry)

    @expose('json')
    def getPlotInfoFromDB(self, plotID):
        """Generate a dummy plot settings for demo"""
        

        plotDetails = DBSession.query(PlotRow,Simulation,Configuration,TestBench).\
            join(Simulation,PlotRow.plotSimID == Simulation.simID).\
            join(Configuration,Simulation.simConfigID == Configuration.confID).\
            join(TestBench, Simulation.simTestBenchID == TestBench.tbID).\
            filter(PlotRow.plotID==plotID).first()

        # plotDetails = DBSession.query(Plot).filter_by(PlotID=plotID).first()

        plotSettings = json.loads(plotDetails[0].plotSettings)
        

        # seriesEntry = {}
        # seriesEntry['name'] = "m_MaxTorque.MetricValue"
        # seriesEntry["short_name"] = "m_MaxTorque.MetricValue"
        # seriesEntry["variable_id"] = "50891"
        # seriesEntry["data_link"] = "var_0.json"
        # seriesEntry["type"] = "var"
        # seriesEntry["plot_id"] = "35"

        #plotSettings['series'].append(seriesEntry)


        #plotSettings['TestBenchID'] = 31
        #plotSettings['data_folder'] = "data/msd/"        

        plotInfo = {}
        plotInfo['plot_id'] = plotDetails[0].plotID
        plotInfo['sim_id'] = plotDetails[1].simID
        plotInfo['sim_name'] = plotDetails[1].simName
        plotInfo['config_id'] = plotDetails[2].confID
        plotInfo['config_name'] = plotDetails[2].confName
        plotInfo['config_folder_name'] = plotDetails[2].confFolderName
        plotInfo['testbench_id'] = plotDetails[3].tbID
        plotInfo['testbench_name'] = plotDetails[3].tbName
        plotInfo['testbench_folder_name'] = plotDetails[3].tbFoldername
        plotInfo['create_date'] = plotDetails[0].plotCreateDate
        plotInfo['last_update_date'] = plotDetails[0].plotLastUpdateDate
        plotInfo['plot_json'] = plotDetails[0].plotJSON
        plotInfo['plot_settings'] = plotSettings
        plotInfo['plot_tree_location'] = plotDetails[1].simDataPath + 'tree.json'
        plotInfo['plot_data_store_location'] = plotDetails[1].simDataPath + ''

        return dict(page='data', settings=plotInfo, plot_details=plotDetails)

    @expose('json')
    def getConfiguration(self, confID):
        """Generate a dummy plot settings for demo"""
        
        confDetails = DBSession.query(Configuration).filter_by(confID=confID).first()

        return dict(page='data', data=confDetails)

    @expose('json')
    def getSimulation(self, simID):
        """Generate a dummy plot settings for demo"""
        
        simDetails = DBSession.query(Simulation,Configuration,TestBench).filter(and_(Simulation.simTestBenchID==TestBench.tbID, Simulation.simConfigID==Configuration.confID, Simulation.simID==simID, Simulation.simIsActive==1)).first()
        # simDetails = DBSession.query(Simulation).filter_by(simID=simID).first()

        return dict(page='data', data=simDetails)

    @expose('json')
    def getTestBench(self, tbID):
        """Generate a dummy plot settings for demo"""
        
        tbDetails = DBSession.query(TestBench).filter_by(tbID=tbID).first()

        return dict(page='data', data=tbDetails)

    @expose('json')
    def getConfigurations(self):
        """Generate a dummy plot settings for demo"""
        
        confRes = DBSession.query(Configuration)

        confDetails = []

        for r in confRes:
            confDetails.append(r)

        return dict(page='data', data=confDetails)

    @expose('json')
    def getSimulations(self):
        """Generate a dummy plot settings for demo"""
        
        simRes = DBSession.query(Simulation,Configuration,TestBench).filter_by(simTestBenchID=TestBench.tbID, simConfigID=Configuration.confID, simIsActive=1).all()

        simDetails = []

        for r in simRes:
            simDetails.append(r)

        return dict(page='data', data=simDetails)

    @expose('json')
    def getSimulationByTestBenchConfigIDs(self, tbID, confID):
        """Generate a dummy plot settings for demo"""
        
        if (tbID != "0" and confID != "0"):
            simRes = DBSession.query(Simulation,Configuration,TestBench).\
            filter(and_(Simulation.simTestBenchID==TestBench.tbID,Simulation.simTestBenchID==tbID,Simulation.simConfigID==Configuration.confID,Simulation.simConfigID==confID,Simulation.simIsActive==1))

        elif(tbID != "0"):
            simRes = DBSession.query(Simulation,TestBench).\
            filter(and_(Simulation.simTestBenchID==TestBench.tbID,Simulation.simTestBenchID==tbID,Simulation.simIsActive==1))
        elif(confID != "0"):
            simRes = DBSession.query(Simulation,Configuration).\
            filter((Simulation.simConfigID==Configuration.confID,Simulation.simConfigID==confID,Simulation.simIsActive==1))

        #simRes = DBSession.query(Simulation)

        simDetails = []

        for r in simRes:
            simDetails.append(r)

        return dict(page='data', data=simDetails, confID=confID, tbID=tbID)

    @expose('json')
    def getPlotsBySimID(self, passedSimID):
        """Get plot by simID"""
        
        if(passedSimID != "0"):
            plotRes = DBSession.query(PlotRow,Simulation,Configuration,TestBench).\
            filter(and_(PlotRow.plotSimID == Simulation.simID,Simulation.simConfigID == Configuration.confID,Simulation.simTestBenchID == TestBench.tbID,PlotRow.plotSimID == passedSimID))

            # plotRes = DBSession.query(Plot).filter_by(PlotSimID=simID)

        plotDetails = []

        if plotRes:
            for r in plotRes:

                plotSettings = json.loads(r[0].plotSettings)

                plotInfo = {}
                plotInfo['plot_id'] = r[0].plotID
                plotInfo['sim_id'] = r[1].simID
                plotInfo['sim_name'] = r[1].simName
                plotInfo['config_id'] = r[2].confID
                plotInfo['config_name'] = r[2].confName
                plotInfo['config_folder_name'] = r[2].confFolderName
                plotInfo['testbench_id'] = r[3].tbID
                plotInfo['testbench_name'] = r[3].tbName
                plotInfo['testbench_folder_name'] = r[3].tbFoldername
                plotInfo['create_date'] = r[0].plotCreateDate
                plotInfo['last_update_date'] = r[0].plotLastUpdateDate
                plotInfo['plot_json'] = r[0].plotJSON
                plotInfo['plot_settings'] = plotSettings
                plotInfo['plot_tree_location'] = r[1].simDataPath + 'tree.json'
                plotInfo['plot_data_store_location'] = r[1].simDataPath + ''

                plotDetails.append(plotInfo)


        # plotInfo = {}
        # plotInfo['plot_id'] = plotDetails[0].plotID
        # plotInfo['sim_id'] = plotDetails[1].simID
        # plotInfo['config_id'] = plotDetails[2].confID
        # plotInfo['testbench_id'] = plotDetails[3].tbID
        # plotInfo['plot_json'] = plotDetails[0].plotJSON
        # plotInfo['plot_settings'] = plotSettings
        # plotInfo['plot_tree_location'] = plotDetails[1].simDataPath + '/tree.json'
        # plotInfo['plot_data_store_location'] = plotDetails[1].simDataPath + '/'


        return dict(page='data', data=plotDetails, passedSimID=passedSimID)

    @expose('json')
    def getSimsByPlotID(self, plotID):
        """Get sims by plotID"""
        
        if(plotID != "0"):
            plotLinks = DBSession.query(LinkSimPlot).filter_by(lspPlotID=plotID)

        sims = []

        for r in plotLinks:
            sims.append(DBSession.query(Simulation).filter_by(simID=r.lspSimID).first())

        return dict(page='getSimsByPlotID', sims=sims, plotID=plotID)

    @expose('json')
    def getRecentPlots(self):
        """Get plot by simID"""
        
        plotRes = DBSession.query(PlotRow,Simulation,Configuration,TestBench).filter(PlotRow.plotSimID == Simulation.simID).\
            filter(Simulation.simConfigID == Configuration.confID).\
            filter(Simulation.simTestBenchID == TestBench.tbID).order_by(desc(PlotRow.plotLastUpdateDate)).limit(10).all()

        # plotRes = DBSession.query(Plot).order_by(desc(Plot.PlotLastUpdateDate)).limit(10).all()
        plotDetails = []

        for r in plotRes:
            plotSettings = json.loads(r[0].plotSettings)

            plotInfo = {}
            plotInfo['plot_id'] = r[0].plotID
            plotInfo['sim_id'] = r[1].simID
            plotInfo['sim_name'] = r[1].simName
            plotInfo['config_id'] = r[2].confID
            plotInfo['config_name'] = r[2].confName
            plotInfo['config_folder_name'] = r[2].confFolderName
            plotInfo['testbench_id'] = r[3].tbID
            plotInfo['testbench_name'] = r[3].tbName
            plotInfo['testbench_folder_name'] = r[3].tbFoldername
            plotInfo['create_date'] = r[0].plotCreateDate
            plotInfo['last_update_date'] = r[0].plotLastUpdateDate
            plotInfo['plot_json'] = r[0].plotJSON
            plotInfo['plot_settings'] = plotSettings
            plotInfo['plot_tree_location'] = r[1].simDataPath + 'tree.json'
            plotInfo['plot_data_store_location'] = r[1].simDataPath + ''

            plotDetails.append(plotInfo)

        return dict(page='data', data=plotDetails)

    @expose('json')
    def getTestBenches(self):
        """Generate a dummy plot settings for demo"""
        
        tbRes = DBSession.query(TestBench)

        tbDetails = []

        for r in tbRes:
            tbDetails.append(r)


        return dict(page='data', data=tbDetails)

    @expose('json')
    def getSearchResults(self, simID, search):
        """Generate a dummy plot settings for demo"""
        

        # search ="accel"
        plotVars = DBSession.query(Variable).filter(and_(Variable.varSimID==simID, sql.func.lower(Variable.varName).like("%%"+search.lower()+"%%")))

        #plotSettings = json.loads(plotDetails.PlotSettings)
        
        variableList = []

        for pvr in plotVars:
            if search.lower() in pvr.varName.lower():
                seriesEntry = {}
                seriesEntry['variable_id'] = pvr.varID
                seriesEntry["name"] = pvr.varName
                seriesEntry["short_name"] = pvr.varShortName
                seriesEntry["data_link"] = pvr.varDataLink
                seriesEntry["type"] = pvr.varType
                seriesEntry["plot_id"] = pvr.varPlotID
                seriesEntry["sim_id"] = pvr.varSimID
                variableList.append(seriesEntry)
                
        return dict(page='searchResults', search=search, vars=variableList)

    @expose('json')
    def createPlot(self, **kw):

        message = ""
        simID = kw['simID']
        plotVersion = 1
        plotName = kw['plotName']

        simDetails = DBSession.query(Simulation).filter_by(simID=simID).first()

        plotSettings = {}
        plotSettings['series'] = []
        plotSettings["name"] = plotName
        plotSettings["testbenchid"] = simDetails.simTestBenchID
        plotSettings["extremelow"] = 0
        plotSettings["extremehigh"] = 0
        plotSettings["xaxis"] = "time"
        plotSettings["data_folder"] = simDetails.simDataPath


        plot = PlotRow()
        plot.plotSimID = simID
        plot.plotVersion = plotVersion
        plot.plotJSON = json.dumps({})
        plot.plotSettings = json.dumps(plotSettings)
        plot.plotCreateDate = date.today()
        DBSession.add(plot)
        DBSession.flush()

        message += "Plot Added"
        status = 1

        #self.redirect("/simviz/plot.html?plotID="+plot.plotID)

        return dict(page='data', plot=plot, message=message, status=status)

    @expose('json')
    def createTestBench(self, **kw):

        message = ""
        testbenchName = kw['testBenchName']

        tb = TestBench()
        tb.tbName = testbenchName
        tb.tbCreateDate = date.today()
        DBSession.add(tb)
        DBSession.flush()

        message += "TestBench " + testbenchName + " successfully Added"
        status = 1

        return dict(page='createTestBench', tb=tb, message=message, status=status)

    @expose('json')
    def addSimToPlot(self, **kw):

        message = ""
        simID = kw['simID']
        plotID = kw['plotID']

        lsp = DBSession.query(LinkSimPlot).filter_by(lspPlotID=plotID, lspSimID=simID).first()

        if lsp is None:

            lsp = LinkSimPlot()
            lsp.lspSimID = simID
            lsp.lspPlotID = plotID
            DBSession.add(lsp)
            DBSession.flush()

            message += "Simulation Successfully Added"

        else:
            message += "Sim already linked"

        status = 1

        return dict(page='addSimToPlot', lsp=lsp, message=message, status=status)

    @expose('json')
    def removeSimFromPlot(self, **kw):

        message = ""
        simID = kw['simID']
        plotID = kw['plotID']

        lsp = DBSession.query(LinkSimPlot).filter_by(lspPlotID=plotID, lspSimID=simID).first()
        DBSession.delete(lsp)
        DBSession.flush()

        message += "Simulation Successfully Removed"
        status = 1

        return dict(page='removeSimFromPlot', lsp=lsp, message=message, status=status)
    
    @expose('json')
    def createConfiguration(self, **kw):

        message = ""
        configName = kw['configName']

        config = Configuration()
        config.confName = configName
        config.confCreateDate = date.today()
        DBSession.add(config)
        DBSession.flush()

        message += "Configuration " + configName + " successfully added."
        status = 1

        return dict(page='data', config=config, message=message, status=status)

    @expose('json')
    def updatePlotSettings(self, **kw):
        plotDetails = DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).first()
        plotSettings = json.loads(plotDetails.plotSettings)

        seriesEntry = {}
        seriesEntry['name'] = kw['name']
        seriesEntry["short_name"] = kw['name']
        seriesEntry["variable_id"] = kw['var_id']
        seriesEntry["data_link"] = kw['data_link']
        seriesEntry["type"] = kw['var_type']
        seriesEntry["checked"] = kw['checked']
        seriesEntry["plot_id"] = kw['plotID']

        plotSettings['series'].append(seriesEntry)
        
        plotDetails.plotSettings = json.dumps(plotSettings)

        DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).update({"plotSettings":json.dumps(plotSettings)}, synchronize_session=False)
        DBSession.flush()

        message = "Success"

        return dict(page='updatePlotSettings', settings=plotSettings, plot_details=plotDetails, message=message, status=1)

    @expose('json')
    def updateVariableInPlotSettings(self, **kw):
        plotDetails = DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).first()
        plotSettings = json.loads(plotDetails.plotSettings)

        for s in plotSettings['series']:
            if s['variable_id'] == kw['var_id']:
                s['checked'] = kw['checked']



        # seriesEntry = {}
        # seriesEntry['name'] = kw['name']
        # seriesEntry["short_name"] = kw['name']
        # seriesEntry["variable_id"] = kw['var_id']
        # seriesEntry["data_link"] = kw['data_link']
        # seriesEntry["type"] = kw['var_type']
        # seriesEntry["checked"] = kw['checked']
        # seriesEntry["plot_id"] = kw['plotID']

        # plotSettings['series'].append(seriesEntry)
        
        plotDetails.plotSettings = json.dumps(plotSettings)

        DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).update({"plotSettings":json.dumps(plotSettings)}, synchronize_session=False)
        DBSession.flush()

        message = "Success"

        return dict(page='updateVariableInPlotSettings', settings=plotSettings, plot_details=plotDetails, message=message, status=1)

    @expose('json')
    def clearPlotSeries(self, **kw):
        plotDetails = DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).first()
        plotSettings = json.loads(plotDetails.plotSettings)

        plotSettings['series'] = []
        
        plotDetails.plotSettings = json.dumps(plotSettings)

        DBSession.query(PlotRow).filter_by(plotID=kw['plotID']).update({"plotSettings":json.dumps(plotSettings)}, synchronize_session=False)
        DBSession.flush()

        message = "Variables Cleared"

        return dict(page='data', settings=plotSettings, plot_details=plotDetails, message=message, status=1)

    @expose('json')
    def uploadMatFile(self, **kw):

        message = ""
        
        simname=kw['new_simulation']



        # A nested FieldStorage instance holds the file
        fileitem = kw['upfile']

        # Test if the file was uploaded
        if fileitem.filename:
            
            if fileitem.filename.endswith(".zip"):

                #Upload zip to temp loaction
                directory = os.getcwd() +"\simviz\public\simviz\data\\temp_unzip"

                finalpath = directory+fileitem.filename
                basefolder = os.path.splitext(os.path.basename(fileitem.filename))[0]

                if not os.path.exists(directory):
                    os.makedirs(directory)

                f = file(finalpath, "wb")
                f.write(kw['upfile'].value)
                f.close()

                names = []

                zfile = zipfile.ZipFile(finalpath)
                for name in zfile.namelist():

                    #names.append(name)

                    (dirname, filename) = os.path.split(name)

                    dirname = directory+"\\"+dirname

                    message += "Decompressing " + filename + " on " +dirname +"\n"
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                        os.chmod(dirname, 0777)

                    if not name.endswith('/') and not name.endswith('\\'):
                        fd = open(dirname +"\\"+ filename,"wb")
                        fd.write(zfile.read(name))
                        fd.close()


                #Now Select TB name and Config name from json file
                summaryFileLocation = directory+"\\"+basefolder+"\\"+"summary.testresults.json"
                
                
                with open(summaryFileLocation, 'r') as json_file:
                    message = "File Opened"
                    summaryResults = json.load(json_file)


                tbDetails = DBSession.query(TestBench).filter_by(tbName=summaryResults['TestBench']).first()
                confDetails = DBSession.query(Configuration).filter_by(confName=summaryResults['DesignName']).first()

                #Create TB and Config if they don't exist
                if not tbDetails:
                    message += "Need to create TestBench"
                    tbDetails = self.createTestBenchInternal(summaryResults['TestBench'])

                if not confDetails:
                    message += "Need to create Config"
                    confDetails = self.createConfigurationInternal(summaryResults['DesignName'])

                # strip leading path from file name to avoid directory traversal attacks
                matFileOriginalLocation = directory+"\\"+basefolder+"\\design_v."+summaryResults['DesignName']+".mat"
                finaldirectory = os.getcwd() +"\simviz\public\simviz\data\\" +tbDetails.tbName +"\\"+confDetails.confName +"\\"+simname +"\\"
                finalmatpath = finaldirectory+"design_v."+summaryResults['DesignName']+".mat"

                if not os.path.exists(finaldirectory):
                    os.makedirs(finaldirectory)

                shutil.copy(matFileOriginalLocation, finaldirectory)

                
                message += 'The file "' + finalmatpath + '" was copied successfully.'
                
                # status = self.convertMatFileFromUpload(finalpath, directory)
                pyexe = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "bin", "Python27", "Scripts", "Python.exe"))
                #pyexe = os.getcwd()+"..\\..\\..\\bin\\Python27\\Scripts\\Python.exe"
                cwd = os.getcwd()+"\simviz\public\simviz\scripts\\"
                command = pyexe+" "+cwd+"mat_conversion_v2.py "+finalmatpath+" "+finaldirectory


                #result = 0
                result = subprocess.call(command)
                conv = dict( pyexe=pyexe, cwd=cwd, command=command, result=result)

                sim = Simulation()
                sim.simTestBenchID = tbDetails.tbID
                sim.simConfigID = confDetails.confID
                sim.simName = simname
                sim.simIsActive = 1
                sim.simCreateDate = date.today()
                sim.simDataPath = "/data/" +tbDetails.tbName +"/"+confDetails.confName +"/"+simname +"/"
                DBSession.add(sim)
                DBSession.flush()

                message += ' Sim has been added to the DB.'

                status = 1
                redirect('/simviz/dashboard.html?page=simHome&simID='+str(sim.simID)+'')
                return dict(page='data', message=message, tb=tbDetails, conf=confDetails, sim=sim, results=tbDetails, conversion=conv)

            elif fileitem.filename.endswith(".mat"):

                tbID=kw['select_tb']
                confID=kw['select_config']
                tbDetails = DBSession.query(TestBench).filter_by(tbID=tbID).first()
                confDetails = DBSession.query(Configuration).filter_by(confID=confID).first()

                # strip leading path from file name to avoid directory traversal attacks
                json_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "public", "simviz"))
                directory = json_dir+"\data\\" +tbDetails.tbName +"\\"+confDetails.confName +"\\"+simname +"\\"
                finalpath = directory+fileitem.filename

                if not os.path.exists(directory):
                    os.makedirs(directory)

                f = file(finalpath, "wb")
                f.write(kw['upfile'].value)
                f.close()
                message = 'The file "' + fileitem.filename + '" was uploaded successfully.'
                
                status = self.convertMatFileFromUpload(finalpath, directory)

                sim = Simulation()
                sim.simTestBenchID = tbID
                sim.simConfigID = confID
                sim.simName = simname
                sim.simIsActive = 1
                sim.simCreateDate = date.today()
                sim.simDataPath = "/data/" +tbDetails.tbName +"/"+confDetails.confName +"/"+simname +"/"
                DBSession.add(sim)
                DBSession.flush()

                message += ' Sim has been added to the DB.'
                redirect('/simviz/dashboard.html?page=simHome&simID='+str(sim.simID)+'')
                return dict(page='data', message=message, tb=tbDetails, conf=confDetails, simname=simname, conversion=status)


            else:
                message = 'File was an unsupported extension'
                return dict(page='uploadMatFile', message=message)
           
        else:
            message = 'No file was uploaded'
            return dict(page='uploadMatFile', message=message)

    @expose('json')
    def convertMatFile(self):

        #pyexe = os.__file__
        pyexe = "C:\Python27\Python.exe"
        cwd = os.getcwd()+"\simviz\public\simviz\scripts\\"
        finalpath = os.getcwd()+"\simviz\public\simviz\data\\test\\"
        path = os.getcwd()+"\simviz\public\simviz\data\\"
        filepath = path+"MassSpringDamper_cfg1_res.mat"

        command = pyexe+" "+cwd+"mat_conversion_v2.py "+filepath+" "+finalpath

        result = subprocess.call(command)

        return dict(page='data', pyexe=pyexe, cwd=cwd, command=command, result=result)

    @expose('json')
    def convertMatFileFromUpload(self, matfilepath, directory):

        #pyexe = os.__file__
        mat_conversion_v2.main(matfilepath, directory)
        #pyexe = os.path.abspath(os.path.join(os.getcwd(), "..", "..", "..", "bin", "Python27", "Scripts", "Python.exe"))
        #cwd = os.getcwd()+"\simviz\public\simviz\scripts\\"

        #command = pyexe+" "+cwd+"mat_conversion_v2.py "+matfilepath+" "+directory

        #result = subprocess.call(command)
        #result = "this"
        pyexe = 'none'
        cwd = 'someDir'
        command = 'command'
        result = 0
        return dict(page='convertMatFileFromUpload', pyexe=pyexe, cwd=cwd, command=command, result=result)

    def createTestBenchInternal(self, testbenchName):

        message = ""

        tb = TestBench()
        tb.tbName = testbenchName
        tb.tbCreateDate = date.today()
        DBSession.add(tb)
        DBSession.flush()

        message += "TestBench " + testbenchName + " successfully Added"
        status = 1

        return tb
    
    def createConfigurationInternal(self, configName):

        message = ""

        config = Configuration()
        config.confName = configName
        config.confCreateDate = date.today()
        DBSession.add(config)
        DBSession.flush()

        message += "Configuration " + configName + " successfully added."
        status = 1

        return config

class RootController(BaseController):
    """
    The root controller for the simviz application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    simviz_rest = SimVizController()
    
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "simviz"

    @expose('simviz.templates.index')
    def index(self):
        """Handle the front-page."""
        redirect('/simviz/dashboard.html')

    @expose('simviz.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('simviz.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(page='environ', environment=request.environ)

    @expose('simviz.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(page='data', params=kw)
    @expose('simviz.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('simviz.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('simviz.templates.login')
    def login(self, came_from=lurl('/')):
        """Start the user login."""
        login_counter = request.environ.get('repoze.who.logins', 0)
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                params=dict(came_from=came_from, __logins=login_counter))
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
