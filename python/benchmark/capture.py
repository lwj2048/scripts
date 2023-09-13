#import torch
#from collections import OrderedDict
from functools import wraps
from custom_torch import fixed_dropout, fixed_droppath, fixed_randperm, fixed_distribution
import sys
import os
#from mmengine.registry import HOOKS
#from mmengine.hooks import Hook
#from mmengine.structures import BaseDataElement

import pickle as pkl
import numpy as np

fixed_dropout()
fixed_droppath()
fixed_randperm()
fixed_distribution()
get_input = False               # 截取输入

max_iters = int(os.environ.get('max_iters', 10))

def replace_input(func, runner):
    nn = [0]
    @wraps(func)
    def function(*args, **kwargs):
        if nn[0] >= max_iters:
            print('OOOOOOneIter: Run to Max Iter. Finish.')
            sys.exit()
        nn[0] += 1
        return func(*args, **kwargs)
    return function


def insert_capture(runner):
    runner.model.train_step = replace_input(
        runner.model.train_step, runner)

