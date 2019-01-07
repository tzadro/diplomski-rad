from core.config import config
import random
import math
import numpy as np


class Species:
	def __init__(self, key, representative):
		self.key = key
		self.representative = representative.duplicate()
		self.individuals = [representative]
		self.adjusted_fitness = None
		self.num_children = None

		self.max_fitness_ever = -math.inf
		self.num_generations_before_last_improvement = 0

	def add(self, individual):
		self.individuals.append(individual)

	# from best to worst
	def sort(self):
		# sort by unadjusted fitness
		self.individuals.sort(key=lambda x: -x.fitness)

	# leave only first n individuals
	def trim_to(self, n=1):
		self.individuals = self.individuals[:n]

	# returns single element, tuple or a list based on selection size
	def roulette_select(self, size=1, replace=False):
		assert not [individual for individual in self.individuals if individual.fitness < 0], \
			'All fitnesses must be positive for roulette wheel selection'

		fitness_sum = sum([individual.fitness for individual in self.individuals])

		assert fitness_sum > 0, 'Fitness sum must not be zero'

		p = [individual.fitness / fitness_sum for individual in self.individuals]
		individuals = np.random.choice(self.individuals, size, replace, p)

		if size == 1:
			return individuals[0]
		if size == 2:
			return individuals[0], individuals[1]
		else:
			return individuals

	# returns single element, tuple or a list based on selection size
	def random_select(self, size=1, replace=False):
		assert len(self.individuals) > 0, 'No individuals to select from'

		if size == 1:
			return random.choice(self.individuals)

		if replace:
			individuals = random.choices(self.individuals, k=size)
		else:
			assert len(self.individuals) >= size, 'Sample size must not be larger than number of individuals'

			individuals = random.sample(self.individuals, size)

		if size == 2:
			return individuals[0], individuals[1]
		else:
			return individuals

	# returns single element, tuple or a list based on selection size
	def tournament_select(self, size=1, replace=False):
		assert size < config.tournament_size, 'Size must be smaller than tournament size for selection to have effect'

		tournament = self.random_select(config.tournament_size, replace)
		tournament.sort(key=lambda x: -x.fitness)

		if size == 1:
			return tournament[0]
		if size == 2:
			return tournament[0], tournament[1]
		else:
			return tournament[:size]

	def reset(self):
		new_representative = self.random_select()
		self.representative = new_representative.duplicate()
		self.individuals = []
		self.adjusted_fitness = None
		self.num_children = None