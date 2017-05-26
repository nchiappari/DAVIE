import sys
import os_client_config
import yaml, json
from terminaltables import AsciiTable

#retrieves the names of all of the clouds specified in clouds.yaml
with open("clouds.yaml", 'r') as config_file:
    clouds = yaml.load(config_file)['clouds'].keys()


def print_instance_breakdown(cloud):
    instances = sdk.compute.servers()

    table_data = [
        ['Name', 'Project', 'Flavor', 'Created']
    ]
    for instance in instances:
        row = []
        row.append(instance.name)
        row.append(instance.project_id)
        row.append(instance.flavor['id'])
        row.append(instance.created_at)
        table_data.append(row)

    table = AsciiTable(table_data)
    print(table.table)


def method_to_be_named_later():
    for cloud in clouds:
        row_of_pluses = "+"*((100 - len(cloud)) / 2)
        #print cloud name
        print("\n{} CLOUD: {} {}\n".format(row_of_pluses, cloud, row_of_pluses))

        sdk = os_client_config.make_sdk(cloud=cloud)

        for pt in conn.cluster.profile_types():
            print(pt.to_dict())

    projects = print_instance_breakdown(cloud)
