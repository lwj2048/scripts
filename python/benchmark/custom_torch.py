from functools import wraps

import torch
import torch.nn as nn


def replace_dropout(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        a = args[0]
        out = func(*args, **kwargs)
        a.p = 0
        return out
    return wrapper

def replace_dropout_fun(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        out = args[0]
        return out
    return wrapper


def replace_uniform(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        a = args[0]
        out = func(a, 0, 0)
        return out
    return wrapper


def replace_torch_rand(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        out = func(*args, **kwargs)
        out.fill_(0.5)
        return out
    return wrapper


def replace_multi_att(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        a = args[0]
        out = func(*args, **kwargs)
        a.dropout = 0.0
        return out
    return wrapper


def replace_torch_randn(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        out = func(*args, **kwargs)
        out.fill_(0.1)
        return out
    return wrapper


def fixed_dropout():
    nn.Dropout.__init__ = replace_dropout(nn.Dropout.__init__)
    nn.Dropout1d.__init__ = replace_dropout(nn.Dropout1d.__init__)
    nn.Dropout2d.__init__ = replace_dropout(nn.Dropout2d.__init__)
    nn.Dropout3d.__init__ = replace_dropout(nn.Dropout3d.__init__)
    nn.functional.dropout = replace_dropout_fun(nn.functional.dropout)
    nn.functional.dropout1d = replace_dropout_fun(nn.functional.dropout1d)
    nn.functional.dropout2d = replace_dropout_fun(nn.functional.dropout2d)
    nn.functional.dropout3d = replace_dropout_fun(nn.functional.dropout3d)
    torch.nn.MultiheadAttention.__init__ = replace_multi_att(torch.nn.MultiheadAttention.__init__)  # noqa:E501


def replace_droppath(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        a = args[0]
        out = func(*args, **kwargs)
        a.drop_prob = 0
        return out
    return wrapper


def fixed_droppath():
    from mmcv.cnn.bricks import DropPath
    DropPath.__init__ = replace_droppath(DropPath.__init__)


def replace_randperm(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        n = args[0]
        out = func(*args, **kwargs)
        out = torch.arange(0, n)
        return out
    return wrapper


def fixed_randperm():
    torch.rand = replace_torch_rand(torch.rand)
    torch.randn = replace_torch_randn(torch.randn)
    torch.randperm = replace_randperm(torch.randperm)

def replace_normal(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        out = args[0]
        return out
    return wrapper


def fixed_distribution():
    torch.Tensor.normal_ = replace_normal(torch.Tensor.normal_)
    torch.Tensor.uniform_ = replace_uniform(torch.Tensor.uniform_)


def modif_config_out(func, one_flag=False):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cfg = func(*args, **kwargs)
        if one_flag:
            cfg.data.samples_per_gpu = 1
        return cfg
    return wrapper


def modif_config(one_flag=False):
    from mmcv import Config
    Config.fromfile = modif_config_out(Config.fromfile, one_flag)


def replace_dataset(func):
    class Dataset(object):
        def __init__(self):
            self.CLASSES = None

        def __getitem__(self, index):
            return [32, 2]

        def __len__(self):
            return 1

    dataset = Dataset()

    @wraps(func)
    def wrapper(*args, **kwargs):
        args = list(args)
        args[1] = dataset
        args = tuple(args)
        kwargs['num_workers'] = 0
        kwargs['sampler'] = torch.utils.data.SequentialSampler(dataset)
        out = func(*args, **kwargs)
        return out
    return wrapper


def dummy_dataloader():
    func = torch.utils.data.dataloader.DataLoader.__init__
    torch.utils.data.dataloader.DataLoader.__init__ = replace_dataset(func)

