import json
import os
import sys

import numpy as np
from scipy.io import loadmat
from scipy.io.matlab.mio4 import VarReader4

VARIABLE_INDICES = set()
VARIABLES = {}
## helper functions
def load_info_from_mat(data_file, 
                       filter=[],
                       gather_desc=False):
    
    """
    Loads data such as name, sign, position of timeseries 
    from the mat_file, the time series are not gathered at this stage. 

    The information is returned in;

    parameter_info - {"name": (data_pos, data_sign, unit, description),..}
    variable_info. -                        --  || --

    """

    VARIABLE_INDICES.clear()

    # return dictionaries
    parameter_info = {}
    variable_info = {}

    to_collect = ['name', 'dataInfo']
    if gather_desc:
        to_collect.append('description')

    data = loadmat(data_file, 
                   matlab_compatible=True, 
                   variable_names = to_collect)
    
    # name of parameter or variable
    names = data['name'].transpose()

    # if 1 -> parameter, if 2 -> variable
    data_type = data['dataInfo'][0]
         
    # position in respective dataset        
    data_pos = np.abs(data['dataInfo'][1])-1
     
    # sign of data
    data_sign = np.sign(data['dataInfo'][1])
    
    # description of parameter of variable
    if gather_desc:
        desc = data['description'].transpose()

    # build up search tree if filter is given
    if filter :
        root_node = TreeNode("root_node")
        root_node.populate_tree(filter)

    for i in xrange(names.shape[0]):
        # Most time is spent here...
        name = ''.join([str(e) for e in names[i]]).rstrip()
        
        success = True
        if filter:
            success = root_node.search_tree(name)       

        if name == 'Time':
            name = 'time'
        elif not success:
            continue
        #print "success finding : " + name 

        # Use dymola name convention for der-operator, 
        # e.g. name = der(brake.phi) then becomes brake.der(phi)
        while(name.startswith('der(')):
            j = name.rfind('.')
            if j != -1 :
                name = name[4:j+1] + 'der(' + name[j+1:]
            else :
                break
        description = ""
        unit = ""
        if gather_desc:
            description = ''.join([str(e) for e in desc[i]]).rstrip()
            unit_ind1 = description.rfind('[')
            unit_ind2 = description.rfind(']')
            if unit_ind1 > 0 and unit_ind2 > 0:
                unit = description[unit_ind1 + 1:unit_ind2]
                description = description[:unit_ind1]

        if data_type[i] == 1:
            parameter_info[name] = (data_pos[i], data_sign[i], unit, description)
        else:
            variable_info[name] = (data_pos[i], data_sign[i], unit, description)
            VARIABLE_INDICES.add(data_pos[i])

    return parameter_info, variable_info
# end of load_INFO_from_mat

def load_variables_from_mat(data_file):
    """
    Loads the time_series data from the mat file, 
    uses variable indices from global the global set.

    """ 

    # Saves the default and overrides the inner standard loadmat function.  
    default_read_sub_array = VarReader4.read_sub_array 
    VarReader4.read_sub_array = VARIABLE_read_sub_array

    loadmat(data_file, matlab_compatible=True, variable_names = ['data_2'])

    # Sets the loadmat function back to default.
    VarReader4.read_sub_array = default_read_sub_array

# end of load_VARIABLES

def VARIABLE_read_sub_array(self, hdr, copy=False):
    """
    Modification of the scipy function read_sub_array,
    that is called from loadmat.

    The modification only collects the variables with indices
    given in VARIABLE_INDICES.

    (The read_sub_array is nested in scipy and inorder to
     avoid argument modifications of all involved functions,
     VARIABLES and VARIABLE_INDICES are defined globally)
    """
    dt = hdr.dtype
    dims = hdr.dims

    vars = dims[0]
    time_points = dims[1]*1
    num_bytes = dt.itemsize*vars

    index_ar = np.zeros((vars*1, 1))
    cnt = 0
    for key_index in VARIABLE_INDICES:
        cnt += 1
        index_ar[key_index] = cnt
    index_array_bool = index_ar > 0
    arr = np.zeros((cnt, time_points))

    for delta_t in range(0, time_points):
        arr[:, delta_t] = np.ndarray(shape=(vars, np.array(1)),
            dtype=dt,
            buffer=self.mat_stream.read(int(num_bytes)),
            order='F')[index_array_bool]

    sorted_variable_indices = list(VARIABLE_INDICES)
    sorted_variable_indices.sort()
    cnt = 0
    for key_index in sorted_variable_indices:
        VARIABLES[key_index] = arr[cnt, :]
        cnt += 1

# end of VARIABLE_read_sub_array


def load_parameters_from_mat(data_file,
                             parameter_info):
    """
    Loads the values of the parameters.
    """
    parameters = {}

    data = loadmat(data_file, 
                   matlab_compatible=True, 
                   variable_names=['data_1'])['data_1']

    for parameter in parameter_info:
        index = parameter_info[parameter][0]
        sign = parameter_info[parameter][1]
        value_0 = data[index][0]*sign
        #value_1 = data[index][1]*sign
        parameters[index] = value_0 

    return parameters
# end of load_PARAMETERS_from_mat

def getNode(tree_structure, name, full_name, data_link):
    node = {}
    
    pos = name.find('.')
    if (pos == -1):
        node['data_link'] = data_link # same for now
        node['name'] = name
        node['full_name'] = full_name
        tree_structure.append(node)
    else:
        node['name'] = name[:pos]
        
        needToAppend = True

        for node_item in tree_structure:
            if (node_item['name'] == node['name']):
                node = node_item
                needToAppend = False
                
        if not node.has_key('children'):
            node['children'] = []
            
        if needToAppend:
            tree_structure.append(node)

        getNode(node['children'], name[pos+1:], full_name, data_link)
     
class TreeNode():
    name = ''
    children = None
    """
    Class making up the filter
    
    """
    def __init__(self, name):
        self.name = name
        self.children = []
    # end of __init__

    def nbr_of_children(self):
        if self.children:
            return len(self.children)
        else:
            return 0
    # end of nbr_of_children

    def add_child(self, new_node, i=0):
        self.children.insert(i, new_node)
    # end of add_child

    def populate_tree(self, node_list):
        """
        Called on the root_node 
        """
        for node in node_list:
            self.place_in_tree(node.split('.'))
    # end of populate_tree
   
    def place_in_tree(self, name_pieces):
        i = 0
        nbr_children = self.nbr_of_children()
        if nbr_children != 0:
            while name_pieces[0] >= self.children[i].name:
                if name_pieces[0] == self.children[i].name:
                    self.children[i].place_in_tree(name_pieces[1:])
                    return
                else:
                    i += 1
                    if i == nbr_children:
                        break
                
        new_node = TreeNode(name_pieces[0])
        self.add_child(new_node, i)
        node = new_node
        for name in name_pieces[1:]:
            new_node = TreeNode(name)
            node.add_child(new_node)
            node = new_node
    # end of place_in_tree

    def search_tree(self, search_name):
        """
        Called on root_node when search begins.

        """  
        name_pieces = search_name.split('.')
        for child in self.children:
            if name_pieces[0] < child.name:
                return False
            elif child.name == name_pieces[0]:
                if len(name_pieces) == 1:
                    return True
                else: 
                    return child.search_tree_rec(name_pieces[1:])
        return False
    # end of search_tree

    def search_tree_rec(self, name_pieces):
        nbr_children = self.nbr_of_children()
        if nbr_children == 0:
            if name_pieces:
                return name_pieces[0] == self.name
            else:
                return False
        else :
            if self.children[0].name == '':
                return True
            elif self.children[0].name == '*' and len(name_pieces) == 1:
                return True
            for child in self.children:
                if name_pieces[0] < child.name :
                    return False
                elif child.name == name_pieces[0]:
                    if len(name_pieces) == 1:
                        return True
                    else:
                        return child.search_tree_rec(name_pieces[1:])

            return False
        # end of search_tree_rec
# end of tree_node

def main(input_mat_file, output_dir):
    # TODO: logging
    if True:
        if not os.path.exists(input_mat_file):
            print 'Given result file does not exist: {0}'.format(input_mat_file)
            os.exit(0)
        
        # .mat file
        mat_file_name = input_mat_file
        np.set_printoptions(precision=4)

        # sizes of files
        num_of_var_in_a_chunk = 5000
        num_of_time_points_in_chunk = 75000

        # file names
        base_name = os.path.splitext(os.path.basename(input_mat_file))[0]
        newdir = os.path.join(os.path.dirname(os.path.abspath(input_mat_file)), base_name)
        
        if (len(sys.argv) > 2):            
            if os.path.exists(output_dir):
                newdir = os.path.abspath(output_dir)
            else:
                print 'Given output dir. does not exist:{0}'.format(output_dir)
        
        print 'Output directory: {0}'.format(newdir)

        if not os.path.exists(newdir):
            os.mkdir(newdir)
        os.chdir(newdir)     
        tree_file_name = 'tree.json'
        
        # Gather info files
        param_info, var_info = load_info_from_mat(
                                        mat_file_name, 
                                        gather_desc = True)
        tree_structure = []
        
        ## Parameters ## 

        # Load values from .mat file
        param_values = load_parameters_from_mat(mat_file_name, param_info)
        
        # Write out parameters in param_XX.json (unit, value, desc)
        # and place them to the tree_structure
        cnt_param = 0
        cnt_chunks = 0
        n = len(param_info)
        json_param = {}
        param_file_name = 'param_0.json'

        for i in range(0,n):
            cnt_param += 1
            param = param_info.popitem()
            name = param[0]
            index = param[1][0]
            sign = param[1][1]

            this_param = {}
            this_param["unit"] = param[1][2]
            this_param["desc"] = param[1][3]
            val_float = sign*param_values[index]
            value = "%.3e" %val_float
            this_param["value"] = float(value)
            this_param["name"] = name
            json_param[name] = this_param

            getNode(tree_structure, name, name, param_file_name)

            if cnt_param == num_of_var_in_a_chunk or i == n-1:
                with open(param_file_name,'wb') as file_out:
                    json.dump(json_param, file_out)
                cnt_chunks += 1
                param_file_name = 'param_' + str(cnt_chunks) + '.json'
                cnt_param = 0
                json_param = {}

        ## Variables ##
        
        # Load the time series into the global VARIABLES

        load_variables_from_mat(mat_file_name)

        # Print out the time_series and variables
        cnt_var = 0
        cnt_var_chunks = 0
        cnt_ts = 0
        cnt_ts_chunks = 0
        json_var = {}
        json_ts = []
        n = len(var_info)
        added_ts = {}
        var_file_name = 'var_0.json'
        ts_file_name =  'ts_0.json'
        peek_index = VARIABLE_INDICES.pop()
        nbr_intervals = len(VARIABLES[peek_index])
        num_ts_in_a_chunk = num_of_time_points_in_chunk/nbr_intervals

        VARIABLE_INDICES.add(peek_index)

        for i in range(0,n):
            cnt_var += 1
            var = var_info.popitem()
            name = var[0]
            index = var[1][0]
            sign = var[1][1]
            
            if not added_ts.has_key(sign*index):
                json_ts.append(["%.3e" %(val*sign) for val in VARIABLES[index]])
                ts_info = {}
                ts_info["data_link"] = ts_file_name
                ts_info["index"] = cnt_ts
                added_ts[index*sign] = ts_info
                cnt_ts += 1


            this_var = {}
            this_var["data_link"] = added_ts[sign*index]["data_link"]
            this_var["index"] = added_ts[sign*index]["index"]
            this_var["unit"] = var[1][2]
            this_var["desc"] = var[1][3]
            this_var["name"] = name
            json_var[name] = this_var

            getNode(tree_structure, name, name, var_file_name)

            if cnt_var == num_of_var_in_a_chunk:
                with open(var_file_name,'wb') as file_out:
                    json.dump(json_var, file_out)
                cnt_var_chunks += 1
                var_file_name = 'var_' + str(cnt_var_chunks) + '.json'
                cnt_var = 0
                json_var = {}
            
            if cnt_ts == num_ts_in_a_chunk:
                with open(ts_file_name, 'wb') as file_out:
                    file_out.write(str(json_ts).replace("'",''))
                cnt_ts_chunks += 1
                ts_file_name = 'ts_' + str(cnt_ts_chunks) + '.json'
                cnt_ts = 0
                json_ts = []

            # Last iteration dump all to json
            if i == n-1:
                with open(var_file_name,'wb') as file_out:
                    json.dump(json_var, file_out)
                with open(ts_file_name, 'wb') as file_out:
                    file_out.write(str(json_ts).replace("'",""))

        #print tree_structure
        with open(tree_file_name,'wb') as file_out:
            file_out.write(str(tree_structure).replace("'",'"'))
    else:
        print 'First argument must be a .mat result file.'