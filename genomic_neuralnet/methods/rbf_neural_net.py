import numpy as np

from sklearn.preprocessing import MinMaxScaler
from genomic_neuralnet.config import MAX_EPOCHS, CONTINUE_EPOCHS, TRY_CONVERGENCE
from genomic_neuralnet.common.in_temp_dir import in_temp_dir 
from fann2 import libfann

LEARNING_RATE = 0.01
_MOMENTUM = 0.5
_ITERATIONS_BETWEEN_REPORTS = 1000
_DESIRED_ERROR = 0 # If 0, always train until max epochs.

_TRAIN_FILE = './train.data'
_NETWORK_FILE = './train.net'

def _get_nn(inputs, hidden):
    """
    Construct a neural network.
    """
    ann = libfann.neural_net()
    ann.create_standard_array((inputs, hidden[0], 1))
    ann.set_learning_rate(LEARNING_RATE)
    ann.set_activation_function_hidden(libfann.GAUSSIAN_SYMMETRIC)
    ann.set_activation_function_output(libfann.LINEAR_PIECE_SYMMETRIC)
    ann.set_training_algorithm(libfann.TRAIN_RPROP)
    ann.set_rprop_delta_zero(1e-6)
    return ann

def _train_nn(neuralnet, train_data, train_truth, weight_decay):
    """
    A stateful method that trains the network
    on a dataset.
    """
    _write_training_file(train_data, train_truth)
    # TODO: Implement weight decay and/or quickprop.
    neuralnet.train_on_file(_TRAIN_FILE, MAX_EPOCHS, _ITERATIONS_BETWEEN_REPORTS, _DESIRED_ERROR)
    neuralnet.save(_NETWORK_FILE)
    return neuralnet

def _write_training_file(train_data, train_truth):
    lines = []
    # Write header
    lines.append('{} {} {}'.format(train_data.shape[0], train_data.shape[1], 1))
    # Write data
    for idx in range(train_data.shape[0]):
        input = ' '.join(map(str, tuple(train_data[idx,:])))
        output = str(train_truth[idx])
        lines.append(input)
        lines.append(output)

    with open(_TRAIN_FILE, 'w') as f:
        f.write('\n'.join(lines))

@in_temp_dir
def get_rbf_nn_prediction(train_data, train_truth, test_data, test_truth, hidden=(5,), weight_decay=0.): 
    scaler = MinMaxScaler(feature_range = (-1, 1))
    train_truth = scaler.fit_transform(train_truth)
    test_truth = scaler.transform(test_truth)

    net = _get_nn(train_data.shape[1], hidden)

    _train_nn(net, train_data, train_truth, weight_decay)

    out = []
    for i in range(test_data.shape[0]):
        sample = test_data[i,:]
        res = net.run(sample)
        out.append(res)

    predicted = scaler.inverse_transform(np.array(out))

    return predicted.ravel()
