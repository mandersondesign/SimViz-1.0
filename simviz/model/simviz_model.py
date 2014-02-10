# -*- coding: utf-8 -*-
"""
SimViz* related model.

This is where the models used by the SimViz stack are defined.

It's perfectly fine to re-use this definition in the simviz application,
though.

"""
import os, sys
from datetime import datetime
from hashlib import sha256
__all__ = ['PlotRow', 'Variable', 'Configuration', 'Simulation', 'TestBench', 'LinkSimPlot']

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import *
from sqlalchemy.orm import relation, synonym

from simviz.model import DeclarativeBase, metadata, DBSession

# class Plot(DeclarativeBase):
#     """
#     Group definition

#     Only the ``group_name`` column is required.

#     """

#     __tablename__ = 'vw_plot'

#     PlotID = Column(Integer, autoincrement=True, primary_key=True)
#     PlotSimID = Column(Integer)
#     PlotSimName = Column(String)
#     PlotConfigurationID = Column(Integer)
#     PlotConfigurationName = Column(String)
#     PlotConfigurationFolderName = Column(String)
#     PlotTestBenchName = Column(String)
#     PlotTestBenchID = Column(Integer)
#     PlotTestBenchDescription = Column(String)
#     PlotTestBenchFolderName = Column(String)
#     PlotVersion = Column(Integer)
#     PlotJSON = Column(Text)
#     PlotSettings = Column(Text)
#     PlotTreeLocation = Column(Text)
#     PlotDataStoreLocation = Column(Text)
#     PlotCreateDate = Column(Date)
#     PlotLastUpdateDate = Column(Date)

#     def __repr__(self):
#         return ('<Group: name=%s>' % self.PlotVersion).encode('utf-8')

#     def __unicode__(self):
#         return self.PlotVersion

class PlotRow(DeclarativeBase):
    """
    Group definition

    Only the ``group_name`` column is required.

    """

    __tablename__ = 'plot'

    plotID = Column(Integer, autoincrement=True, primary_key=True)
    plotSimID = Column(Integer)
    plotVersion = Column(Integer)
    plotJSON = Column(Text)
    plotCreateDate = Column(Date)
    plotRemoveDate = Column(Date)
    plotLastUpdateDate = Column(Date)
    plotSettings = Column(Text)

    def __repr__(self):
        return ('<Group: name=%s>' % self.plotVersion).encode('utf-8')

    def __unicode__(self):
        return self.plotVersion

class Variable(DeclarativeBase):
    """
    Variable definition

    Only the ``varID`` column is required.

    """

    __tablename__ = 'variable'

    varID = Column(Integer, autoincrement=True, primary_key=True)
    varShortName = Column(String, index=True)
    varName = Column(String, index=True)
    varPlotID = Column(Integer)
    varSimID = Column(Integer)
    varType = Column(String)
    varDataLink = Column(String)
    

    def __repr__(self):
        return ('<Variable: name=%s>' % self.varName).encode('utf-8')

    def __unicode__(self):
        return self.varName

class Configuration(DeclarativeBase):
    """
    Configuration definition

    Only the ``confID`` column is required.

    """

    __tablename__ = 'configuration'

    confID = Column(Integer, autoincrement=True, primary_key=True)
    confName = Column(String)
    confCreateDate = Column(Date)
    confFolderName = Column(String)

    def __repr__(self):
        return ('<Configuration: name=%s>' % self.confName).encode('utf-8')

    def __unicode__(self):
        return self.varName

class Simulation(DeclarativeBase):
    """
    Simulation definition

    Only the ``varID`` column is required.

    """

    __tablename__ = 'simulation'

    simID = Column(Integer, autoincrement=True, primary_key=True)
    simTestBenchID = Column(Integer)
    simConfigID = Column(Integer)
    simName = Column(String)
    simIsActive = Column(Boolean)
    simIndexedFlag = Column(Boolean)
    simCreateDate = Column(Date)
    simRemoveDate = Column(Date)
    simLastUpdateDate = Column(Date)
    simDataPath = Column(String)

    def __repr__(self):
        return ('<Simulation: name=%s>' % self.simName).encode('utf-8')

    def __unicode__(self):
        return self.varName

# class SimulationView(DeclarativeBase):
#     """
#     SimulationView definition

#     Only the ``SimID`` column is required.

#     """

#     __tablename__ = 'vw_simulation'

#     SimID = Column(Integer, autoincrement=True, primary_key=True)
#     SimTestBenchID = Column(Integer)
#     SimTestBenchName = Column(String)
#     SimTestBenchFolderName = Column(String)
#     SimTestBenchDescription = Column(String)
#     SimConfigID = Column(Integer)
#     SimConfigName = Column(String)
#     SimConfigFolderName = Column(String)
#     SimName = Column(String)
#     SimIsActive = Column(Boolean)
#     SimIndexedFlag = Column(Boolean)
#     SimCreateDate = Column(Date)
#     SimRemoveDate = Column(Date)
#     SimLastUpdateDate = Column(Date)
#     SimDataPath = Column(String)

#     def __repr__(self):
#         return ('<Simulation: name=%s>' % self.SimName).encode('utf-8')

#     def __unicode__(self):
#         return self.SimName

class TestBench(DeclarativeBase):
    """
    Variable definition

    Only the ``varID`` column is required.

    """

    __tablename__ = 'test_bench'

    tbID = Column(Integer, autoincrement=True, primary_key=True)
    tbProjectID = Column(Integer)
    tbName = Column(String)
    tbDesc = Column(String)
    tbFoldername = Column(String)
    tbCreateDate = Column(Date)
    

    def __repr__(self):
        return ('<Test Bench: name=%s>' % self.tbName).encode('utf-8')

    def __unicode__(self):
        return self.tbName

class LinkSimPlot(DeclarativeBase):
    """
    Configuration definition

    Only the ``confID`` column is required.

    """

    __tablename__ = 'link_sim_plot'

    lspSimID = Column(Integer, primary_key=True)
    lspPlotID = Column(Integer, primary_key=True)

    def __repr__(self):
        return ('<Plot ID: id=%s>' % self.lspPlotID).encode('utf-8')

    def __unicode__(self):
        return self.lspPlotID