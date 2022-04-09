import numpy as np
import config
import logging

class Node():
	def __init__(self, state):
		self.state = state
		self.playerTurn = state.playerTurn
		self.id = state.id
		self.edges = []

	def isLeaf(self):
		if len(self.edges) > 0:
			return False
		else:
			return True

class Edge():

	def __init__(self, inNode, outNode, prior, action):
		self.id = inNode.state.id + '|' + outNode.state.id
		self.inNode = inNode
		self.outNode = outNode
		self.playerTurn = inNode.state.playerTurn
		self.action = action

		self.stats =  {
					'N': 0,
					'W': 0,
					'Q': 0,
					'P': prior,
				}
				

class MCTS():
	def __init__(self, root, cpuct):
		self.root = root
		self.tree = {}
		self.cpuct = cpuct
		self.addNode(root)
		self.log = self.setup_logger('logger_mcts', './logs/logger_mcts.log')
	
	def __len__(self):
		return len(self.tree)

	def moveToLeaf(self):
		breadcrumbs = []
		currentNode = self.root

		done = 0
		value = 0

		while not currentNode.isLeaf():		
			maxQU = -99999

			if currentNode == self.root:
				epsilon = config.EPSILON
				nu = np.random.dirichlet([config.ALPHA] * len(currentNode.edges))
			else:
				epsilon = 0
				nu = [0] * len(currentNode.edges)

			Nb = 0
			for action, edge in currentNode.edges:
				Nb = Nb + edge.stats['N']

			for idx, (action, edge) in enumerate(currentNode.edges):

				U = self.cpuct * \
					((1-epsilon) * edge.stats['P'] + epsilon * nu[idx] )  * \
					np.sqrt(Nb) / (1 + edge.stats['N'])
					
				Q = edge.stats['Q']
				if Q + U > maxQU:
					maxQU = Q + U
					simulationAction = action
					simulationEdge = edge

			lg.logger_mcts.info('action with highest Q + U...%d', simulationAction)

			newState, value, done = currentNode.state.takeAction(simulationAction) 
			currentNode = simulationEdge.outNode
			breadcrumbs.append(simulationEdge)

		return currentNode, value, done, breadcrumbs



	def backFill(self, leaf, value, breadcrumbs):
		logger_mcts = self.log
		currentPlayer = leaf.state.playerTurn

		for edge in breadcrumbs:
			playerTurn = edge.playerTurn
			if playerTurn == currentPlayer:
				direction = 1
			else:
				direction = -1

			edge.stats['N'] = edge.stats['N'] + 1
			edge.stats['W'] = edge.stats['W'] + value * direction
			edge.stats['Q'] = edge.stats['W'] / edge.stats['N']

			logger_mcts.info('updating edge with value %f for player %d... N = %d, W = %f, Q = %f'
				, value * direction
				, playerTurn
				, edge.stats['N']
				, edge.stats['W']
				, edge.stats['Q']
				)

			edge.outNode.state.render(logger_mcts)

	def addNode(self, node):
		self.tree[node.id] = node

	def setup_logger(name, log_file, level=logging.INFO):
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		handler = logging.FileHandler(log_file)
		handler.setFormatter(formatter)
		logger = logging.getLogger(name)
		logger.setLevel(level)
		if not logger.handlers:
			logger.addHandler(handler)
		return logger
