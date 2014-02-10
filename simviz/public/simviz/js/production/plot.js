//var chart; // global
var receiver = 0;
var checked = 0;

$(document).ready(function() {
    $.ajaxSetup({cache: false});

    function PlotViewModel() {
        // Data
        var self = this;

        //View Model Variables
        self.chart = ko.observable();
        self.plot = ko.observable();
        self.mainSim = ko.observable();

        self.simItems = ko.observableArray([]);
        self.simTBItems = ko.observableArray([]);

        self.timeSeriesVar = ko.observable();
        self.variables = ko.observableArray([]);
        self.searchVariables = ko.observableArray();
        self.checkedVariables = ko.observableArray([]);
        self.varDownloadLink = ko.observable();
        self.paramDownloadLink = ko.observable();
        self.csvExportReady = ko.observable(false);
        self.graphItems = ko.observableArray([]);

        self.includeFilePath = "/simviz";

        self.initPlot = function(plotID) {
            var post_data = {
                plotID: plotID
            };

            $.post("/simviz_rest/getPlotInfoFromDB/" + plotID, {}, function(result) {
                //var json = $.parseJSON(result);
                self.plot(new Plot(result.settings));


                $.post("/simviz_rest/getSimulation/" + self.plot().simID(), {}, function(simResult) {
                    console.log(simResult.data);
                    self.simItems.push(new Simulation(simResult.data[0]));
                    self.mainSim(new Simulation(simResult.data[0]));

                    $.post("/simviz_rest/getSimsByPlotID/" + plotID, {}, function(result) {
                        //var json = $.parseJSON(result);
                        self.graphItems = ko.observableArray([]);
                        
                        $.each(result.sims, function(i, item) {
                            if (item.simID != self.mainSim().simID())
                            {
                                self.simItems.push(new Simulation(item));
                            }
                        });
                        //console.log(self.simItems());

                        self.simItems.subscribe(function() {
                            self.drawAllVariables();
                        });

                        self.getSimulationsByTBID(self.plot().testbenchID());

                        self.initializeD3Chart();
                        //self.initChartSettings();
                    });
                });
            });
        };

        self.initializeD3Chart = function() {
            nv.addGraph(function() {

                var chart = nv.models.lineChart();
                chart.xAxis
                        .axisLabel('Time (ms)')
                        .tickFormat(d3.format(',r'));

                chart.yAxis
                        .axisLabel('')
                        .tickFormat(d3.format('.02f'));

                d3.select('#chart svg')
                        .datum(self.graphItems())
                        .transition().duration(250)
                        .call(chart);

                nv.utils.windowResize(function() {
                    d3.select('#chart svg').call(chart);
                });

                self.chart(chart);

                return chart;
            });
            self.initTime();
        };
        self.initTime = function() {
            var plotID = self.plot().plotID();

            var post_data = {
                plotID: plotID
            };

            $.post("/simviz_rest/getTimeSeries/", post_data, function(result) {
                self.timeSeriesVar(new Variable(result.time));
                //console.log(self.timeSeriesVar().variable_id());
                self.initChartSettings();
            });
        };
        self.initChartSettings = function() {
            var settings = self.plot().plotSettings();
            console.log(settings.series);
            var mappedSettingsVars = $.map(settings.series, function(item) {
                return new Variable(item);
            });
            console.log(mappedSettingsVars);
            $.each(mappedSettingsVars, function(i, obj) {
                self.varBoxClick(obj);

                //TODO need if statement check here for if var needs to be checked
                if (obj.checked() == "true")
                {
                    self.clickYAxisVariableOnInit(obj);
                }
            });


            //        $("#plotSettings").html(settings);
            //        var setName = settings.series.name;
            //        var finName = setName.split(".").join("__");
            //        doChartYDraw('<?php echo base_url(); ?>include/'+settings.series.data_link, finName);
            //        $('#y'+finName).prop("checked", true);
            //        chart.redraw();
            //        $('#x'+finName).prop("checked", true);
            //        chart.showResetZoom();
        };
        self.varBoxClick = function(clckVar) {
            self.searchVariables.remove(clckVar);
            self.variables.push(clckVar);

            var found = false;

            // Check and make sure the variables are found in the plot settings. 
            // Otherwise, update the plot settings
            ko.utils.arrayForEach(self.plot().plotSettings().series, function(item) {
                //console.log(item);
                //console.log(item.variable_id + ' - ' + clckVar.variable_id());
                if (item.variable_id === clckVar.variable_id()) {
                    found = true;
                }
            });

            if (!found)
            {
                //Add variable to plot settings json
                var name = clckVar.name();
                var seriesShortName = clckVar.name();
                var id = clckVar.variable_id();

                var post_data = {
                    plotID: self.plot().plotID(),
                    name: name,
                    var_id: id,
                    data_link: clckVar.data_link(),
                    var_type: clckVar.type(),
                    checked: clckVar.checked()
                };

                $.post("/simviz_rest/updatePlotSettings/", post_data, function(result) {
//                    var json = $.parseJSON(result);
                    console.log(result);
                });
            }

            //        $(this).css('background-color', '#ccc');
            //        var newCheckBox = "";
            //        newCheckBox += '<li>';
            //        newCheckBox += '<input type="checkbox" name="elements[]" id="y'+id+'" seriesName="'+name+'" seriesShortName="'+shortname+'" value="'+datalink+'" class="yaxisvar" />';
            //        newCheckBox += '<label for="y'+id+'" class="eltLabel">'+shortname+'</label>';
            //        newCheckBox += '</li>';
            //        $("#yaxislist").append(newCheckBox);
        };
        self.clickYAxisVariableOnInit = function(yvar) {
            var settings = self.plot().plotSettings();
            var name = yvar.name;
            var seriesShortName = yvar.name;
            var id = yvar.variable_id();

            if ($("#y" + id).is(':checked'))
            {
                console.log('not checked');
                $("#y" + id).attr('checked', '');
                self.checkedVariables.remove(yvar);
                self.removeVar(yvar);
                //Remove variable from plot settings json
            }
            else
            {
                $("#y" + id).attr('checked', 'checked');
                self.checkedVariables.push(yvar);
                self.doD3ChartYDrawNew(yvar);
            }

            return true;
        };
        self.clickYAxisVariable = function(yvar) {
            var settings = self.plot().plotSettings();
            var name = yvar.name;
            var seriesShortName = yvar.name;
            var id = yvar.variable_id();

            if (!$("#y" + id).is(':checked'))
            {
                console.log('not checked');
                $("#y" + id).attr('checked', '');
                yvar.checked(false);
                self.checkedVariables.remove(yvar);
                self.removeVar(yvar);
                //Remove check from plot settings json
            }
            else
            {
                $("#y" + id).attr('checked', 'checked');
                yvar.checked(true);
                self.checkedVariables.push(yvar);
                self.doD3ChartYDrawNew(yvar);
            }
            
            self.updateVariableInPlotSettings(yvar);

            return true;
        };

        self.updateVariableInPlotSettings = function(clckVar) {
            //Add variable to plot settings json
            var name = clckVar.name();
            var seriesShortName = clckVar.name();
            var id = clckVar.variable_id();

            var post_data = {
                plotID: self.plot().plotID(),
                name: name,
                var_id: id,
                data_link: clckVar.data_link(),
                var_type: clckVar.type(),
                checked: clckVar.checked()
            };

            $.post("/simviz_rest/updateVariableInPlotSettings/", post_data, function(result) {
//                    var json = $.parseJSON(result);
                console.log(result);
            });
        };

        self.clickRemoveSimFromPlot = function(sim) {

            var id = sim.simID();

            self.simItems.remove(sim);
            self.simTBItems.push(sim);

            var post_data = {
                plotID: self.plot().plotID(),
                simID: sim.simID
            };

            $.post("/simviz_rest/removeSimFromPlot/", post_data, function(result) {
                console.log(result);
                //var json = $.parseJSON(result);
                return true;
            });
        };

        self.clickAddSimToPlot = function(sim) {

            var id = sim.simID();

            self.simTBItems.remove(sim);
            self.simItems.push(sim);

            var post_data = {
                plotID: self.plot().plotID(),
                simID: sim.simID
            };

            $.post("/simviz_rest/addSimToPlot/", post_data, function(result) {
                console.log(result);
                //var json = $.parseJSON(result);
                return true;
            });
        };


        self.initializeD3ScatterPlotChart = function() {
            nv.addGraph(function() {

                var chart = nv.models.scatterChart()
                        .showDistX(true)
                        .showDistY(true)
                        .color(d3.scale.category10().range());

                //              chart.xAxis
                //                      .axisLabel('Time (ms)')
                //                      .tickFormat(d3.format(',r'));
                //
                //              chart.yAxis
                //                      .axisLabel('')
                //                      .tickFormat(d3.format('.02f'));

                chart.xAxis.axisLabel('Time (ms)').tickFormat(d3.format('.02f'));
                chart.yAxis.tickFormat(d3.format('.02f'));

                d3.select('#chart svg')
                        .datum(self.graphItems())
                        .transition().duration(500)
                        .call(chart);

                nv.utils.windowResize(function() {
                    d3.select('#chart svg').call(chart);
                });

                self.chart(chart);

                return chart;
            });

            self.initTime();
        };
        self.initializeD3BarChart = function() {
            nv.addGraph(function() {


                var width = nv.utils.windowSize().width - 40,
                        height = nv.utils.windowSize().height - 40;

                var chart = nv.models.multiBar()
                        .width(width)
                        .height(height)
                        .stacked(true)

                d3.select('#chart svg')
                        .datum(testData())
                        .transition().duration(500)
                        .call(chart);

                nv.utils.windowResize(function() {
                    d3.select('#chart svg').call(chart);
                });

                self.chart(chart);

                return chart;
            });

            self.initTime();
        };
        self.doD3ChartYDraw = function(yvar) {
            var settings = self.plot().plotSettings();
            var name = yvar.name();
            var seriesShortName = yvar.name();
            var id = yvar.variable_id();

            var data_link = "";

            //get time
            var time_data_link = self.includeFilePath + settings.data_folder + "/" + self.timeSeriesVar().data_link();
            console.log(time_data_link);

            var time = new Array();

            $.getJSON(time_data_link, function(json) {
                $.each(json, function(i, obj) {

                    if (obj.name === "time")
                    {
                        data_link = self.includeFilePath + settings.data_folder + "/" + obj.data_link;
                        console.log(data_link);
                        $.getJSON(data_link, function(ts_json) {
                            $.each(ts_json[obj.index], function(j, obj2) {
                                time.push(obj2);
                            });
//                      console.log(time);

                            //Once we have time, do awesome things
                            if (yvar.data_link().indexOf("var") > -1)
                            {
                                //console.log("var");
                                var var_data_link = self.includeFilePath + settings.data_folder + "/" + yvar.data_link();
                                console.log(var_data_link);
                                $.getJSON(var_data_link, function(json) {
                                    //console.log(name);

                                    $.each(json, function(i, varObj) {
                                        if (varObj.name === name)
                                        {
                                            //console.log(varObj.name);
                                            data_link = self.includeFilePath + settings.data_folder + "/" + varObj.data_link;
                                            console.log(data_link);
                                            $.getJSON(data_link, function(json) {
                                                console.log(json);

                                                var line = [];

                                                $.each(json[varObj.index], function(j, obj2) {
                                                    line.push({x: time[j], y: obj2});
                                                });

                                                self.graphItems.push({
                                                    values: line,
                                                    key: name,
                                                    color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                                });

                                                d3.select('#chart svg')
                                                        .datum(self.graphItems())
                                                        .transition().duration(500)
                                                        .call(self.chart());
                                            })
                                                    .error(function(request, err) {
                                                console.log('error');
                                                console.log(err);
                                            });

                                            return false;
                                        }
                                    });
                                });
                            }
                            else if (yvar.data_link().indexOf("param") > -1)
                            {
                                //console.log(settings);
                                var var_data_link = self.includeFilePath + settings.data_folder + "/" + yvar.data_link();
                                console.log(var_data_link);
                                $.getJSON(var_data_link, function(json) {

                                    console.log(json);

                                    $.each(json, function(i, varObj) {
                                        if (varObj.name === name)
                                        {
                                            console.log(varObj.name);

                                            var line = [];
                                            var objValue = varObj.value;

                                            //Push each point onto the line
                                            $.each(time, function(j, obj2) {
                                                line.push({x: time[j], y: objValue});
                                            });

                                            self.graphItems.push({
                                                values: line,
                                                key: name,
                                                color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                            });

                                            d3.select('#chart svg')
                                                    .datum(self.graphItems())
                                                    .transition().duration(500)
                                                    .call(self.chart());

                                            return false;
                                        }
                                    });
                                });
                            }
                            return false;
                        });

                        return false;
                    }
                });
            });
        };


        self.doD3ChartYDrawNew = function(yvar) {
            var settings = self.plot().plotSettings();
            var name = yvar.name();
            var seriesShortName = yvar.name();
            var id = yvar.variable_id();

            var data_link = "";

            $.each(self.simItems(), function(k, simItem) {
                //get time
                var time_data_link = self.includeFilePath + simItem.simDataPath() + self.timeSeriesVar().data_link();
                console.log(ko.toJS(simItem));

                var time = new Array();

                $.getJSON(time_data_link, function(json) {
                    $.each(json, function(i, obj) {

                        if (obj.name === "time")
                        {
                            data_link = self.includeFilePath + simItem.simDataPath() + obj.data_link;
                            console.log(data_link);
                            $.getJSON(data_link, function(ts_json) {
                                $.each(ts_json[obj.index], function(j, obj2) {
                                    time.push(obj2);
                                });

                                //Once we have time, do awesome things
                                if (yvar.data_link().indexOf("var") > -1)
                                {
                                    //console.log("var");
                                    var var_data_link = self.includeFilePath + simItem.simDataPath() + yvar.data_link();
                                    console.log(var_data_link);
                                    $.getJSON(var_data_link, function(json) {
                                        //console.log(name);

                                        $.each(json, function(i, varObj) {
                                            if (varObj.name === name)
                                            {
                                                //console.log(varObj.name);
                                                data_link = self.includeFilePath + simItem.simDataPath() + varObj.data_link;
                                                //console.log(data_link);
                                                $.getJSON(data_link, function(json) {
                                                    //console.log(json);

                                                    var line = [];

                                                    $.each(json[varObj.index], function(j, obj2) {
                                                        line.push({x: time[j], y: obj2});
                                                    });

                                                    self.graphItems.push({
                                                        values: line,
                                                        key: name,
                                                        color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                                    });

                                                    d3.select('#chart svg')
                                                            .datum(self.graphItems())
                                                            .transition().duration(500)
                                                            .call(self.chart());
                                                })
                                                        .error(function(request, err) {
                                                    console.log('error');
                                                    console.log(err);
                                                });

                                                return false;
                                            }
                                        });
                                    });
                                }
                                else if (yvar.data_link().indexOf("param") > -1)
                                {
                                    //console.log(settings);
                                    var var_data_link = self.includeFilePath + simItem.simDataPath() + yvar.data_link();
                                    console.log(var_data_link);
                                    $.getJSON(var_data_link, function(json) {

                                        //console.log(json);

                                        $.each(json, function(i, varObj) {
                                            if (varObj.name === name)
                                            {
                                                console.log(varObj.name);

                                                var line = [];
                                                var objValue = varObj.value;

                                                //Push each point onto the line
                                                $.each(time, function(j, obj2) {
                                                    line.push({x: time[j], y: objValue});
                                                });

                                                self.graphItems.push({
                                                    values: line,
                                                    key: name,
                                                    color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                                });

                                                d3.select('#chart svg')
                                                        .datum(self.graphItems())
                                                        .transition().duration(500)
                                                        .call(self.chart());

                                                return false;
                                            }
                                        });
                                    });
                                }
                                return false;
                            });

                            return false;
                        }
                    });
                });


            });
        };

        self.loadChartData = function(yvar) {
            var settings = self.plot().plotSettings();
            var name = yvar.name();
            var seriesShortName = yvar.name();
            var id = yvar.variable_id();

            var data_link = "";

            //get time
            var time_data_link = self.includeFilePath + settings.data_folder + self.timeSeriesVar().data_link();
            //console.log(time_data_link);

            var time = new Array();

            $.getJSON(time_data_link, function(json) {
                $.each(json, function(i, obj) {

                    if (obj.name === "time")
                    {
                        data_link = self.includeFilePath + settings.data_folder + "/" + obj.data_link;
                        console.log(data_link);
                        $.getJSON(data_link, function(ts_json) {
                            $.each(ts_json[obj.index], function(j, obj2) {
                                time.push(obj2);
                            });
//                      console.log(time);

                            //Once we have time, do awesome things
                            if (yvar.data_link().indexOf("var") > -1)
                            {
                                console.log("var");
                                var var_data_link = self.includeFilePath + settings.data_folder + yvar.data_link();
                                console.log(var_data_link);
                                $.getJSON(var_data_link, function(json) {
                                    //console.log(name);

                                    $.each(json, function(i, varObj) {
                                        if (varObj.name === name)
                                        {
                                            //console.log(varObj.name);
                                            data_link = self.includeFilePath + settings.data_folder + varObj.data_link;

                                            $.getJSON(data_link, function(json) {
                                                console.log(json);

                                                var line = [];

                                                $.each(json[varObj.index], function(j, obj2) {
                                                    line.push({x: time[j], y: obj2});
                                                });

                                                self.graphItems.push({
                                                    values: line,
                                                    key: name,
                                                    color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                                });

                                                self.chart().update();

//                                                d3.select('#chart svg')
//                                                        .datum(self.graphItems())
//                                                        .call(self.chart());

                                            })
                                                    .error(function(request, err) {
                                                console.log('error');
                                                console.log(err);
                                            });

                                            return false;
                                        }
                                    });
                                });
                            }
                            else if (yvar.data_link().indexOf("param") > -1)
                            {
//                                console.log("param");
                                var var_data_link = self.includeFilePath + settings.data_folder + yvar.data_link();
                                console.log(var_data_link);
                                $.getJSON(var_data_link, function(json) {

                                    console.log(json);

                                    $.each(json, function(i, varObj) {
                                        if (varObj.name === name)
                                        {
                                            console.log(varObj.name);

                                            var line = [];
                                            var objValue = varObj.value;

                                            //Push each point onto the line
                                            $.each(time, function(j, obj2) {
                                                line.push({x: time[j], y: objValue});
                                            });

                                            self.graphItems.push({
                                                values: line,
                                                key: name,
                                                color: '#' + Math.floor(Math.random() * 16777215).toString(16)
                                            });

                                            self.chart().update();

//                                            d3.select('#chart svg')
//                                                    .datum(self.graphItems())
//                                                    .call(self.chart());

                                            return false;
                                        }
                                    });
                                });
                            }
                            return false;
                        });

                        return false;
                    }
                });
            });
        };



        self.doChartXDraw = function(jsonFilePath, name) {
            name = name.split("__").join(".");
            $.getJSON(jsonFilePath, function(json) {
                var categories = [];
                $.each(json.variables, function(i, obj) {
                    if (obj.name == name)
                    {
                        var series = {data: []}
                        var pCounter = 0;
                        $.each(obj.data, function(j, obj2) {
                            if (pCounter % 25 == 0)
                                categories.push(obj2);
                            pCounter++;
                        });
                        chart.xAxis[0].setCategories(categories);
                    }
                });
            });
        };
        self.findClick = function() {
            $("#barLoader").show();
            var search = $.trim($("#variableSerach").val());

            var post_data = {
                search: search
            };

            $.post('/simviz_rest/getSearchResults/' + self.plot().simID(), post_data, function(result) {

                //var json = $.parseJSON(result);
                var json = result;
                console.log(json);

                var mappedVars = $.map(json.vars, function(item) {
                    return new Variable(item);
                });
                self.searchVariables(mappedVars);

                //$("#searchResults").html(result);
                $("#barLoader").hide();
            });
        };


        self.initVariableDialog = function() {
            //Global Variables
            var plotSettings = {};
            $("#plotSettings").html('' + plotSettings);

            //Add variable / Variable Search Functions
            //            $('#AddVariableDialog').dialog({
            //              autoOpen: false,
            //              width: 1000,
            //              height: 600,
            //              buttons: {
            //                "Close": function() {
            //                  $(this).dialog("close");
            //                }
            //              }
            //            });

            //            $('#AddVariableDialog_open').live("click", function() {
            //              $('#AddVariableDialog').dialog('open');
            //              return false;
            //            });
            //
            //            $('#ClearVariable').live("click", function() {
            //              for (var i = 0; i < series.length; i++)
            //              {
            //                console.log("series name: " + series[i].name);
            //                chart.series[i].remove(true);
            //              }
            //            });
        };
        self.clickXAxisVariable = function(xvar) {
            var data_link = $(this).val();
            console.log(data_link);
            var name = $(this).attr("id");
            name = name.substring(1);
            console.log(name);
            if ($(this).is(':checked'))
            {
                var categories = [];
                chart.xAxis[0].setCategories(categories);
                doChartXDraw(data_link, name);
                chart.redraw();
            }
        };


        self.removeVar = function(yvar) {
            $.each(self.graphItems(), function(i, obj) {
                if (obj.key === yvar.name())
                {
                    //console.log("found!");
                    self.graphItems.splice(i, 1);
                    self.chart().update();
                    return false;
                }
            });

            if (self.graphItems().length === 0)
            {
                if (self.chart() !== undefined)
                {
                    self.chart().update();
                }
            }
        };
        self.drawAllVariables = function() {
            self.graphItems.removeAll();

            $.each(self.checkedVariables(), function(i, yvar) {
                console.log(yvar);
                self.doD3ChartYDrawNew(yvar);
            });

            if (self.checkedVariables().length === 0)
            {
                self.chart().update();
            }

        };

        self.getSimulationsByTBID = function(tbID) {

            var url = "/simviz_rest/getSimulationByTestBenchConfigIDs/" + tbID + "/0";
            console.log(url);

            $.post(url, {}, function(result) {
                //var json = $.parseJSON(result);
                self.simTBItems.removeAll();

                $.each(result.data, function(i, item) {
                   console.log(item[0]);

                    var found = 0;

                    //console.log(self.simItems());

                    $.each(self.simItems(), function(j, obj) {

                        //console.log(obj);

                        if (obj.simID() == item[0].simID)
                        {
                            found = 1;
                            return;
                        }
                    });

                    //If we get to this point
                    if (found == 0)
                    {
                        self.simTBItems.push(new Simulation(item[0]));
                    }
                });
                //console.log(self.simTBItems());
            });
        };

        //Init Calls
        self.initPlotID = ko.observable();

        var pID = $.QueryString("plotID");
        console.log(pID);
        if (pID !== "" && pID !== null)
        {
            self.initPlotID(pID);
        }

        self.initPlot(self.initPlotID());
        self.initVariableDialog();

    }

    var plotViewModel = new PlotViewModel();
    ko.applyBindings(plotViewModel);

});


