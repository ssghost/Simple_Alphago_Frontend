import config
import numpy as np

import matplotlib.pyplot as plt

from keras.models import load_model, Model
from keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, LeakyReLU, add
from keras.optimizers import SGD
from keras import regularizers

import keras.backend as K
import tensorflow as tf

class AlphaGo():
	def __init__(self, reg_const, learning_rate, input_dim, output_dim):
		self.reg_const = reg_const
		self.learning_rate = learning_rate
		self.input_dim = input_dim
		self.output_dim = output_dim
		self.loss = self.softmax_cross_entropy_with_logits

	def predict(self, x):
		return self.model.predict(x)

	def fit(self, states, targets, epochs, verbose, validation_split, batch_size):
		return self.model.fit(states, targets, epochs=epochs, verbose=verbose, validation_split = validation_split, batch_size = batch_size)

	def write(self, game, version):
		self.model.save("./models/version" + "{0:0>4}".format(version) + ".h5")

	def read(self, game, run_number, version):
		return load_model( "./" + game + "/run" + str(run_number).zfill(4) + "/models/version" + "{0:0>4}".format(version) + ".h5", custom_objects={'softmax_cross_entropy_with_logits': self.loss})

	def viewLayers(self):
		layers = self.model.layers
		for i, l in enumerate(layers):
			x = l.get_weights()
			print('LAYER ' + str(i))

			try:
				weights = x[0]
				s = weights.shape
				fig = plt.figure(figsize=(s[2], s[3]))  
				channel = 0
				filter = 0
				for i in range(s[2] * s[3]):
					sub = fig.add_subplot(s[3], s[2], i + 1)
					sub.imshow(weights[:,:,channel,filter], cmap='coolwarm', clim=(-1, 1),aspect="auto")
					channel = (channel + 1) % s[2]
					filter = (filter + 1) % s[3]

			except:
	
				try:
					fig = plt.figure(figsize=(3, len(x)))  
					for i in range(len(x)):
						sub = fig.add_subplot(len(x), 1, i + 1)
						if i == 0:
							clim = (0,2)
						else:
							clim = (0, 2)
						sub.imshow([x[i]], cmap='coolwarm', clim=clim,aspect="auto")
						
					plt.show()

				except:
					try:
						fig = plt.figure(figsize=(3, 3)) 
						sub = fig.add_subplot(1, 1, 1)
						sub.imshow(x[0], cmap='coolwarm', clim=(-1, 1),aspect="auto")
						
						plt.show()

					except:
						pass

			plt.show()
				
	def softmax_cross_entropy_with_logits(self, y_pred, y_true):  		
		p = y_true
		pi = y_pred
		zero = tf.zeros(shape = tf.shape(pi), dtype=tf.float32)
		where = tf.equal(pi, zero)
		negatives = tf.fill(tf.shape(pi), -100.0) 
		p = tf.where(where, negatives, p)
		loss = tf.nn.softmax_cross_entropy_with_logits(labels = pi, logits = p)
		return loss
    			


class Residual_CNN(AlphaGo):
	def __init__(self, reg_const, learning_rate, input_dim,  output_dim, hidden_layers):
		AlphaGo.__init__(self, reg_const, learning_rate, input_dim, output_dim)
		self.hidden_layers = hidden_layers
		self.num_layers = len(hidden_layers)
		self.model = self._build_model()

	def residual_layer(self, input_block, filters, kernel_size):

		x = self.conv_layer(input_block, filters, kernel_size)

		x = Conv2D(
		filters = filters
		, kernel_size = kernel_size
		, data_format= 'channels_first'
		, padding = 'same'
		, use_bias=False
		, activation='linear'
		, kernel_regularizer = regularizers.l2(self.reg_const)
		)(x)

		x = BatchNormalization(axis=1)(x)

		x = add([input_block, x])

		x = LeakyReLU()(x)

		return (x)

	def conv_layer(self, x, filters, kernel_size):

		x = Conv2D(
		filters = filters
		, kernel_size = kernel_size
		, data_format="channels_first"
		, padding = 'same'
		, use_bias=False
		, activation='linear'
		, kernel_regularizer = regularizers.l2(self.reg_const)
		)(x)

		x = BatchNormalization(axis=1)(x)
		x = LeakyReLU()(x)

		return (x)

	def value_head(self, x):

		x = Conv2D(
		filters = 1
		, kernel_size = (1,1)
		, data_format="channels_first"
		, padding = 'same'
		, use_bias=False
		, activation='linear'
		, kernel_regularizer = regularizers.l2(self.reg_const)
		)(x)


		x = BatchNormalization(axis=1)(x)
		x = LeakyReLU()(x)

		x = Flatten()(x)

		x = Dense(
			20
			, use_bias=False
			, activation='linear'
			, kernel_regularizer=regularizers.l2(self.reg_const)
			)(x)

		x = LeakyReLU()(x)

		x = Dense(
			1
			, use_bias=False
			, activation='tanh'
			, kernel_regularizer=regularizers.l2(self.reg_const)
			, name = 'value_head'
			)(x)
		return (x)

	def policy_head(self, x):

		x = Conv2D(
		filters = 2
		, kernel_size = (1,1)
		, data_format="channels_first"
		, padding = 'same'
		, use_bias=False
		, activation='linear'
		, kernel_regularizer = regularizers.l2(self.reg_const)
		)(x)

		x = BatchNormalization(axis=1)(x)
		x = LeakyReLU()(x)

		x = Flatten()(x)

		x = Dense(
			self.output_dim
			, use_bias=False
			, activation='linear'
			, kernel_regularizer=regularizers.l2(self.reg_const)
			, name = 'policy_head'
			)(x)

		return (x)

	def _build_model(self):

		main_input = Input(shape = self.input_dim, name = 'main_input')

		x = self.conv_layer(main_input, self.hidden_layers[0]['filters'], self.hidden_layers[0]['kernel_size'])

		if len(self.hidden_layers) > 1:
			for h in self.hidden_layers[1:]:
				x = self.residual_layer(x, h['filters'], h['kernel_size'])

		vh = self.value_head(x)
		ph = self.policy_head(x)

		model = Model(inputs=[main_input], outputs=[vh, ph])
		model.compile(loss={'value_head': 'mean_squared_error', 'policy_head': self.loss},
			optimizer=SGD(lr=self.learning_rate, momentum = config.MOMENTUM),	
			loss_weights={'value_head': 0.5, 'policy_head': 0.5}	
			)

		return model

	def convertToModelInput(self, state):
		inputToModel =  state.binary 
		inputToModel = np.reshape(inputToModel, self.input_dim) 
		return (inputToModel)

		
