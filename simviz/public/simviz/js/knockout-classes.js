
function SettingsItem(json) {
    var self = this;

    self.ps_id = ko.observable(json.ps_id);
    self.user_id = ko.observable(json.user_id);
    self.user_name = ko.observable(json.user_name);
    self.user_picture = ko.observable(json.user_picture);

    //Comments
    self.shouldShowCommentsLoading = ko.observable(true);
    self.shouldShowCommentsContainer = ko.observable(false);

    self.shouldShowCommentLoader = ko.observable(false);

    var mappedComments = $.map(json.content.comments, function(item) {
        return new Comment(item)
    });
    self.comments = ko.observable(mappedComments);

    self.commentReply = ko.observable();
    self.activeComment = ko.observable();

    //Votes
    self.votes = ko.observable(json.content.votes);
    self.reports = ko.observable(json.content.reports);

    self.shouldShowCommentsLoading(false);
    self.shouldShowCommentsContainer(true);

    //      self.formattedVotes = ko.computed(function() {
    //        return self.up_votes() +'/'+self.down_votes()+' ('+self.votes_ratio()*100+'%)';
    //      });
}

function Plot(json) {
    var self = this;
console.log("this");
    self.plotID = ko.observable(json.plot_id);
    self.simID = ko.observable(json.sim_id);
    self.simName = ko.observable(json.sim_name);
    self.configID = ko.observable(json.config_id);
    self.configName = ko.observable(json.config_name);
    self.configFolderName = ko.observable(json.config_folder_name);
    self.testbenchID = ko.observable(json.testbench_id);
    self.testbenchName = ko.observable(json.testbench_name);
    self.testbenchFolderName = ko.observable(json.testbench_folder_name);
    self.testbenchDesc = ko.observable(json.testbench_desc);

    self.plotVersion = ko.observable(json.plot_version);
    self.plotJSON = ko.observable(json.plot_json);
    self.plotSettings = ko.observable(json.plot_settings);
    self.plotCreateDate = ko.observable(json.create_date);

    self.plotLastUpdateDate = ko.observable(json.last_update_date);
    self.plotTreeLocation = ko.observable(json.plot_tree_location);
    self.plotDataStoreLocation = ko.observable(json.plot_data_store_location);

    //Booleans
    self.shouldShowCommentsLoading = ko.observable(true);
    self.shouldShowCommentsContainer = ko.observable(false);
    self.shouldShowCommentLoader = ko.observable(false);

self.formattedDate = ko.computed(function() {
        if (self.plotCreateDate() != null)
        {
            return self.plotCreateDate();
            //return Date.parse(self.PlotCreateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.plotCreateDate();
        }
        //return Date.parse(self.PlotCreateDate().toString()).toString('hh:mm tt - M/dd/yy');
    });
    self.formattedLastUpdateDate = ko.computed(function() {
        if (self.plotLastUpdateDate() != null)
        {
            return self.plotLastUpdateDate();
            //return Date.parse(self.PlotLastUpdateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.plotLastUpdateDate();
        }
        //return Date.parse(self.PlotLastUpdateDate().toString()).toString('hh:mm tt - M/dd/yy');
    });


    console.log(json);
    //Computables


    //      self.formattedDate = ko.computed(function() {
    //        return Date.parse(self.create_date().toString()).toString('hh:mm tt - M/dd/yy');
    //      });

}



function PlotItem(json) {
    var self = this;

    self.PlotID = ko.observable(json.PlotID);
    self.PlotSimID = ko.observable(json.PlotSimID);
    self.PlotSimName = ko.observable(json.PlotSimName);
    self.PlotConfigurationID = ko.observable(json.PlotConfigurationID);
    self.PlotConfigurationName = ko.observable(json.PlotConfigurationName);
    self.PlotConfigurationFolderName = ko.observable(json.PlotConfigurationFolderName);
    self.PlotTestBenchID = ko.observable(json.PlotTestBenchID);
    self.PlotTestBenchName = ko.observable(json.PlotTestBenchName);
    self.PlotTestBenchFolderName = ko.observable(json.PlotTestBenchFolderName);
    self.PlotTestBenchDescription = ko.observable(json.PlotTestBenchDescription);

    self.PlotVersion = ko.observable(json.PlotVersion);
    self.PlotJSON = ko.observable(json.PlotJSON);
    self.PlotSettings = ko.observable($.parseJSON(json.PlotSettings));
    self.PlotCreateDate = ko.observable(json.PlotCreateDate);
    self.PlotLastUpdateDate = ko.observable(json.PlotLastUpdateDate);
    self.create_date = ko.observable(json.create_date);

    self.last_update_date = ko.observable(json.last_update_date);
    self.PlotTreeLocation = ko.observable(json.PlotTreeLocation);
    self.PlotDataStoreLocation = ko.observable(json.PlotDataStoreLocation);

    //Booleans
    self.shouldShowCommentsLoading = ko.observable(true);
    self.shouldShowCommentsContainer = ko.observable(false);
    self.shouldShowCommentLoader = ko.observable(false);


    console.log(json);
    //Computables


    self.formattedDate = ko.computed(function() {
        if (self.PlotCreateDate() != null)
        {
            return self.PlotCreateDate();
            //return Date.parse(self.PlotCreateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.PlotCreateDate();
        }
        //return Date.parse(self.PlotCreateDate().toString()).toString('hh:mm tt - M/dd/yy');
    });
    self.formattedLastUpdateDate = ko.computed(function() {
        if (self.PlotLastUpdateDate() != null)
        {
            return self.PlotLastUpdateDate();
            //return Date.parse(self.PlotLastUpdateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.PlotLastUpdateDate();
        }
        //return Date.parse(self.PlotLastUpdateDate().toString()).toString('hh:mm tt - M/dd/yy');
    });

}

function Variable(data) {
    var self = this;

    self.variable_id = ko.observable(data.variable_id);
    self.name = ko.observable(data.name);
    self.short_name = ko.observable(data.short_name);
    self.data_link = ko.observable(data.data_link);
    self.plot_id = ko.observable(data.plot_id);
    self.type = ko.observable(data.type);

    self.checked = ko.observable(false);
    if (data.checked !== undefined)
    {
        self.checked(data.checked);
    }
}

function Configuration(data) {
    var self = this;

    self.confID = ko.observable(data.confID);
    self.confName = ko.observable(data.confName);
    self.confFolderName = ko.observable(data.confFolderName);
    self.confCreateDate = ko.observable(data.confCreateDate);
}

function TestBench(data) {
    var self = this;

    self.tbProjectID = ko.observable(data.tbProjectID);
    self.tbName = ko.observable(data.tbName);
    self.tbDesc = ko.observable(data.tbDesc);
    self.tbCreateDate = ko.observable(data.tbCreateDate);
    self.tbID = ko.observable(data.tbID);
    self.tbFoldername = ko.observable(data.tbFoldername);
}

function Simulation(data) {
    var self = this;

    self.simID = ko.observable(data.simID);
    self.simName = ko.observable(data.simName);
    self.simIsActive = ko.observable(data.simIsActive);
    self.simRemoveDate = ko.observable(data.simRemoveDate);
    self.simTestBenchID = ko.observable(data.simTestBenchID);
    self.simConfigID = ko.observable(data.simConfigID);
    self.simCreateDate = ko.observable(data.simCreateDate);
    self.simLastUpdateDate = ko.observable(data.simLastUpdateDate);
    self.simDataPath = ko.observable(data.simDataPath);
    self.simIndexedFlag = ko.observable(data.simIndexedFlag);

    self.formattedDate = ko.computed(function() {
        if (self.simCreateDate() != null)
        {
            return self.simCreateDate();
            //return Date.parse(self.simCreateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.simCreateDate();
        }
    });
}

function SimulationView(data) {
    var self = this;

    self.SimID = ko.observable(data.SimID);
    self.SimName = ko.observable(data.SimName);
    self.SimIsActive = ko.observable(data.SimIsActive);
    self.SimRemoveDate = ko.observable(data.SimRemoveDate);
    self.SimTestBenchID = ko.observable(data.SimTestBenchID);
    self.SimTestBenchName = ko.observable(data.SimTestBenchName);
    self.SimTestBenchDescription = ko.observable(data.SimTestBenchDescription);
    self.SimTestBenchFolderName = ko.observable(data.SimTestBenchFolderName);
    self.SimConfigID = ko.observable(data.SimConfigID);
    self.SimConfigName = ko.observable(data.SimConfigName);
    self.SimConfigFolderName = ko.observable(data.SimConfigFolderName);
    self.SimCreateDate = ko.observable(data.SimCreateDate);
    self.SimLastUpdateDate = ko.observable(data.SimLastUpdateDate);
    self.SimDataPath = ko.observable(data.SimDataPath);
    self.SimIndexedFlag = ko.observable(data.SimIndexedFlag);

    self.formattedDate = ko.computed(function() {
        if (self.SimCreateDate() != null)
        {
            return self.SimCreateDate();
            //return Date.parse(self.simCreateDate().toString()).toString('M/dd/yy');
        }
        else
        {
            return self.SimCreateDate();
        }
    });
}