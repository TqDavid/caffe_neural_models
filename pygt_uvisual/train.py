from __future__ import print_function
import h5py
import numpy as np
from numpy import float32, int32, uint8, dtype
import sys

# Relative path to where PyGreentea resides
pygt_path = '../../PyGreentea'


import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), pygt_path))

# Other python modules
import math

# Load PyGreentea
import PyGreentea as pygt

# Load the datasets
hdf5_raw_file = '../dataset_06/fibsem_medulla_7col/tstvol-520-1-h5/img_normalized.h5'
hdf5_gt_file = '../dataset_06/fibsem_medulla_7col/tstvol-520-1-h5/groundtruth_seg.h5'
hdf5_aff_file = '../dataset_06/fibsem_medulla_7col/tstvol-520-1-h5/groundtruth_aff.h5'

hdf5_raw = h5py.File(hdf5_raw_file, 'r')
hdf5_gt = h5py.File(hdf5_gt_file, 'r')
hdf5_aff = h5py.File(hdf5_aff_file, 'r')

hdf5_raw_ds = pygt.normalize(np.asarray(hdf5_raw[hdf5_raw.keys()[0]]).astype(float32), -1, 1)
hdf5_gt_ds = np.asarray(hdf5_gt[hdf5_gt.keys()[0]]).astype(float32)
hdf5_aff_ds = np.asarray(hdf5_aff[hdf5_aff.keys()[0]]).astype(float32)

datasets = []
for i in range(0,hdf5_raw_ds.shape[1]):
    dataset = {}
    dataset['data'] = hdf5_raw_ds[None, i, :]
    dataset['components'] = hdf5_gt_ds[None, i, :]
    dataset['label'] = hdf5_aff_ds[0:3, i, :]
    dataset['nhood'] = pygt.malis.mknhood2d()
    datasets += [dataset]

#test_dataset = {}
#test_dataset['data'] = hdf5_raw_ds
#test_dataset['label'] = hdf5_aff_ds


# Set train options
class TrainOptions:
    loss_function = "euclid"
    loss_output_file = "log/loss.log"
    test_output_file = "log/test.log"
    test_interval = 4000
    scale_error = True
    training_method = "affinity"
    recompute_affinity = True
    train_device = 0
    test_device = 0
    test_net=None #'net_test.prototxt'


options = TrainOptions()

# Set solver options
solver_config = pygt.caffe.SolverParameter()
solver_config.train_net = 'net_train_euclid.prototxt'
solver_config.base_lr = 0.0001
solver_config.momentum = 0.99
solver_config.weight_decay = 0.000005
solver_config.lr_policy = 'inv'
solver_config.gamma = 0.0001
solver_config.power = 0.75
solver_config.max_iter = 8000
solver_config.snapshot = 2000
solver_config.snapshot_prefix = 'net'
solver_config.type = 'Adam'
solver_config.display = 1

# Set devices
# pygt.caffe.enumerate_devices(False)
pygt.caffe.set_devices((options.train_device,))


solverstates = pygt.getSolverStates(solver_config.snapshot_prefix);

# First training method
if (len(solverstates) == 0 or solverstates[-1][0] < solver_config.max_iter):
    solver, test_net = pygt.init_solver(solver_config, options)
    if (len(solverstates) > 0):
        solver.restore(solverstates[-1][1])
    pygt.train(solver, test_net, datasets, [], options)
    






