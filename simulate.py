#!/usr/bin/env python
"""
This is the main file of the
Integrated MALware Simulator & Emulator
imalse
prou: `I'm sir`
"""
# Create a Experiment
import sys
import os
sys.path.append(os.getcwd())
import argparse
# import optparse

try:
    import experiments
    # from experiments import *
except ImportError:
    print 'You should use ns3 waf shell to run this code'
    sys.exit()

from util import *

exper_options = get_experiment_option()
parser = argparse.ArgumentParser(description='imalse')
# parser.add_argument('-e', '--experiment', default='ImalseExperiment',
parser.add_argument('-e', '--experiment', default='ImalseSimExperiment',
# parser.add_argument('-e', '--experiment', default='ImalseTopoSimExperiment',
# parser.add_argument('-e', '--experiment', default='ImalsePingCsmaExperiment',
        help='specify the experiment. Avaliable experiments are [%s]'%(" |").join(exper_options)
        )
args, exper_args = parser.parse_known_args()
# print 'args, ', args
# print 'exper_args, ', exper_args
exec('x = experiments.%s()'%(args.experiment))

# Print Help when there is not argument
if len(sys.argv) == 1:
    print '---------Experment Selction Arguments-----------'
    parser.print_help()
    print '---------Exeriment Options-----------------------'
    x.print_help()
    sys.exit(1)

x.main(exper_args)
