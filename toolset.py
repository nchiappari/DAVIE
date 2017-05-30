import sys
import os_client_config
import yaml, json
from terminaltables import AsciiTable

# map id to name
flavor_id_to_name = {}
project_id_to_name= {}

# collects aggregate data on flavors used by project
# {project_id:{flavor_id:flavor_occurrance_count_within_that_project}}
aggregate_data = {}

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

print_all_info()
