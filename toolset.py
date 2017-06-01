import sys
import os_client_config
import yaml, json
from terminaltables import AsciiTable
import requests

# map id to name
flavor_id_to_name = {}
project_id_to_name = {}

# collects aggregate data on flavors used by project
# {project_id:{flavor_id:flavor_occurrance_count_within_that_project}}
aggregate_data = {}

# maps cloud names to tokens
cloud_to_token = {}

URL_COMPUTE = "http://10.107.0.2:8774/v2.1"

#retrieves the names of all of the clouds specified in clouds.yaml
with open("clouds.yaml", 'r') as config_file:
    clouds = yaml.load(config_file)['clouds'].keys()

# generates and prints ascii table
def print_table_from_list_of_dict(data_set, list_of_keys, header=None):
    if header:
        table_data = [header]
    else:
        table_data = [list_of_keys]

    for item in data_set:
        row = []

        for key in list_of_keys:
            if key in item:
                row.append(item[key])
            else:
                row.append("")

        table_data.append(row)

    table = AsciiTable(table_data)
    print(table.table)


# uses OpenStack SDK to gather data
def build_data_set():
    formatted_instances = []
    flavor_breakdown = []

    for cloud in clouds:
        sdk = os_client_config.make_sdk(cloud=cloud)

        instances = sdk.compute.servers()

        for instance in instances:
            new_dict = {}

            new_dict['name'] = instance.name
            new_dict['status'] = instance.status

            project_id = instance.project_id
            if project_id not in project_id_to_name:
                project_id_to_name[project_id] = sdk.identity.get_project(project_id).name
            new_dict['project_id'] = project_id
            new_dict['project_name'] = project_id_to_name[project_id]

            flavor_id = instance.flavor['id']
            if flavor_id not in flavor_id_to_name:
                flavor_id_to_name[flavor_id] = sdk.compute.get_flavor(flavor_id).name
            new_dict['flavor_id'] = flavor_id
            new_dict['flavor_name'] = flavor_id_to_name[flavor_id]

            # {project_id:{flavor_id:flavor_occurrance_count_within_that_project}}
            if project_id not in aggregate_data:
                aggregate_data[project_id] = {}
            if flavor_id not in aggregate_data[project_id]:
                aggregate_data[project_id][flavor_id] = 0
            aggregate_data[project_id][flavor_id] += 1

            new_dict['created_at'] = instance.created_at
            new_dict['cloud'] = cloud

            formatted_instances.append(new_dict)

    return sorted(formatted_instances, key=lambda k: k['created_at'], reverse=True)



def print_separator(title):
    row_of_pluses = "+"*((80 - len(title)) / 2)
    #print cloud name
    print("\n{} {} {}\n".format(row_of_pluses, title, row_of_pluses))


def get_flavor_metadata(flavor_id, token):
    r = requests.get("{}/flavors/{}/os-extra_specs".format(URL_COMPUTE, flavor_id), headers={'X-Auth-Token': token})
    return r.json()['extra_specs']

def print_GPU_breakdown():
    breakdown = build_GPU_breakdown()

    for key in breakdown:
        print("{}:".format(key))
        print_table_from_list_of_dict(breakdown[key], ['name', 'count'], header=["Flavor", "PCI Passthrough Device Count"])

# returns only GPU flavors and their PCI passthrough device count
def build_GPU_breakdown():
    result = {}
    for cloud in clouds:
        sdk = os_client_config.make_sdk(cloud=cloud)

        cloud_to_token[cloud] = sdk.authorize()

        flavors = sdk.compute.flavors()

        gpu_flavors = []

        for flavor in flavors:
            meta_data = get_flavor_metadata(flavor.id, cloud_to_token[cloud])
            if 'aggregate_instance_extra_specs:gpu' in meta_data and meta_data['aggregate_instance_extra_specs:gpu']:
                count = meta_data['pci_passthrough:alias'].split(":")[1]
                gpu_flavors.append({"name":flavor.name, "count":count})

        result[cloud] = gpu_flavors

    return result

def print_all_info():
    data_set = build_data_set()

    print_separator("VM Breakdown")

    key_list = ['name', 'project_name', 'flavor_name', 'status', 'created_at']
    header = ['Name', 'Project', 'Flavor', 'Status', 'Created']
    print_table_from_list_of_dict(data_set, key_list, header=header)

    print_separator("Aggregate Data By Project")

    for project_id in aggregate_data:
        print("{}:".format(project_id_to_name[project_id]))

        row = []

        for flavor_id in aggregate_data[project_id]:
            row.append({"Flavor":flavor_id_to_name[flavor_id], "Count":aggregate_data[project_id][flavor_id]})

        print_table_from_list_of_dict(row, ['Flavor', 'Count'])

    print_separator("GPU Breakdown")
    print_GPU_breakdown()



# TODO instead of printing all, add command interface/move specific functionality into separate files
print_all_info()
