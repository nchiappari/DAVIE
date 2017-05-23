from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client

AUTH_URL = "http://10.107.0.2:5000/v3"
USERNAME = "nchiappari"
PASSWORD = ""
PROJECT_ID = "69f48877162b4b94a99c1ffa67f5691c"
VERSION = "2"

loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url=AUTH_URL,
                                username=USERNAME,
                                password=PASSWORD,
                                user_domain_name="users")
sess = session.Session(auth=auth)
nova = client.Client(VERSION, session=sess)

nova.servers.list()
