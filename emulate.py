#!/usr/bin/env python
# node_type = 'Server'
node_type = 'client'
scenario = 'simple_ddos'
import argparse
import sys, os
# exec( 'import scenario.%s as scen'%(scenario) )
def load_module(scenario):
    __import__('scenario.%s'%(scenario))
    scen = sys.modules['scenario.%s'%(scenario)]
    return scen


def run_server(scen):
    node = scen.Node()
    cmd = scen.ServerCMD(scen.server_fsm)
    cmd.install(node)
    node.start()


def run_client(scen):
    node = scen.Node()
    ccmd = scen.ClientCMD(scen.client_fsm)
    ccmd.install(node)
    node.start()

def run_botmaster(scen):
    node = scen.Node()
    ccmd = scen.BotMaster(scen.botmaster_fsm)
    ccmd.install(node)
    node.start()

run_map = {
        'server':run_server,
        'client':run_client,
        'botmaster':run_botmaster,
        }

parser = argparse.ArgumentParser(description='imalse')
scenario_ops = [f_name for f_name in os.listdir('./scenario/') if not f_name.lower().endswith('py')]
parser.add_argument('-s', '--scenario', default='None',
        help='specify the scenario you want to execute. Scenearios availiable are: %s'%(scenario_ops )
        )

parser.add_argument('-r', '--role', default='None',
        help='specify the role you want to emulate, 1.[server], 2.[client], 3.[botmaster]'
        )
args = parser.parse_args()
if args.scenario not in scenario_ops:
    parser.print_help()
    exit()
scen = load_module(args.scenario)
run_map[args.role](scen)

