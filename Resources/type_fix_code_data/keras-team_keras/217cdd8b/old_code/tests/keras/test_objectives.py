import numpy as np

from keras import objectives
from keras import backend as K


allobj = [objectives.mean_squared_error, objectives.root_mean_squared_error,
          objectives.mean_absolute_error, objectives.mean_absolute_percentage_error,
          objectives.mean_squared_logarithmic_error, objectives.squared_hinge,
          objectives.hinge, objectives.categorical_crossentropy, objectives.binary_crossentropy, objectives.poisson,
          objectives.cosine_proximity]

def test_objective_shapes_3d():
    y_a = K.variable(np.random.random((5, 6, 7)))
    y_b = K.variable(np.random.random((5, 6, 7)))
    for obj in allobj:
        objective_output = obj(y_a, y_b)
        assert K.eval(objective_output).shape == (5, 6)

def test_objective_shapes_2d():
    y_a = K.variable(np.random.random((6, 7)))
    y_b = K.variable(np.random.random((6, 7)))
    for obj in allobj:
        objective_output = obj(y_a, y_b)
        assert K.eval(objective_output).shape == (6,)
