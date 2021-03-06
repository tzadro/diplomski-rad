from core.config import config
from core import utility
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from os.path import exists


class NetworkVisualizer:
	def __init__(self):
		self.node_positions = {}

		num_inputs = len(config.input_keys)
		for i, key in enumerate(config.input_keys):
			x = 0
			if num_inputs == 1:
				y = config.network_canvas_height / 2.
			else:
				y = (num_inputs - (i + 1)) * config.network_canvas_height / (num_inputs - 1)

			self.node_positions[key] = (x, y)

		num_outputs = len(config.output_keys)
		for i, key in enumerate(config.output_keys):
			x = config.network_canvas_width
			if num_outputs == 1:
				y = config.network_canvas_height / 2.
			else:
				y = (num_outputs - (i + 1)) * config.network_canvas_height / (num_outputs - 1)

			self.node_positions[key] = (x, y)

	def visualize_network(self, connections):
		edges = [(connection.from_key, connection.to_key, round(connection.weight, 2)) for connection in connections.values() if connection.enabled]

		G = nx.DiGraph()
		G.add_weighted_edges_from(edges)

		self_loop_keys = [connection.from_key for connection in connections.values() if connection.enabled and connection.from_key == connection.to_key]
		node_colors = ['g' if node_key in self_loop_keys else 'r' for node_key in G]

		nx.draw(G, self.node_positions, node_color=node_colors, with_labels=True)
		labels = nx.get_edge_attributes(G, 'weight')
		nx.draw_networkx_edge_labels(G, self.node_positions, edge_labels=labels)

		plt.show()

	def update_node_positions(self, connections, nodes):
		for key in nodes.keys():
			if key not in self.node_positions:
				neighbor_nodes = [connection.to_key if connection.from_key == key else connection.from_key for connection in connections.values() if (connection.to_key == key or connection.from_key == key) and connection.from_key != connection.to_key]
				x = sum([self.node_positions[node_key][0] for node_key in neighbor_nodes]) / len(neighbor_nodes)
				y = sum([self.node_positions[node_key][1] for node_key in neighbor_nodes]) / len(neighbor_nodes)

				self.node_positions[key] = (x, y)


def log(message):
	if config.verbose:
		print(message)


def plot_overall_fitness(best_fitnesses, avg_fitnesses, stdev_fitnesses):
	num_generations = len(best_fitnesses)

	assert num_generations == len(avg_fitnesses) and num_generations == len(stdev_fitnesses), 'All lists must be the same length'

	generations = range(num_generations)
	best = np.array(best_fitnesses)
	avg = np.array(avg_fitnesses)
	stdev = np.array(stdev_fitnesses)

	# plot fitness over generations
	plt.plot(generations, best, color='red', label='Best')
	plt.plot(generations, avg, color='blue', label='Average')
	plt.plot(generations, avg + stdev, color='blue', linestyle='dashed')
	plt.plot(generations, avg - stdev, color='blue', linestyle='dashed')
	plt.title('Fitness over generations')
	plt.xlabel('Generation')
	plt.ylabel('Fitness')
	plt.legend()
	plt.show()


def plot_structures(avg_num_hidden_nodes, stdev_num_hidden_nodes, avg_num_connections, stdev_num_connections):
	num_generations = len(avg_num_hidden_nodes)

	assert num_generations == len(stdev_num_hidden_nodes) and num_generations == len(avg_num_connections) and num_generations == len(stdev_num_connections), 'All lists must be the same length'

	generations = range(num_generations)
	avg_num_hidden_nodes = np.array(avg_num_hidden_nodes)
	stdev_num_hidden_nodes = np.array(stdev_num_hidden_nodes)
	avg_num_connections = np.array(avg_num_connections)
	stdev_num_connections = np.array(stdev_num_connections)

	# plot structure over generations
	colors = ['blue', 'red']

	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax1.set_xlabel('Generation')

	ax1.plot(generations, avg_num_hidden_nodes, color=colors[0], label='Average num hidden nodes')
	ax1.plot(generations, avg_num_hidden_nodes + stdev_num_hidden_nodes, color=colors[0], linestyle='dashed')
	ax1.plot(generations, avg_num_hidden_nodes - stdev_num_hidden_nodes, color=colors[0], linestyle='dashed')
	ax1.set_ylabel('Number of hidden nodes')

	ax2.plot(generations, avg_num_connections, color=colors[1], label='Average num connections')
	ax2.plot(generations, avg_num_connections + stdev_num_connections, color=colors[1], linestyle='dashed')
	ax2.plot(generations, avg_num_connections - stdev_num_connections, color=colors[1], linestyle='dashed')
	ax2.set_ylabel('Number of connections')

	line1, label1 = ax1.get_legend_handles_labels()
	line2, label2 = ax2.get_legend_handles_labels()
	plt.legend(line1 + line2, label1 + label2)

	ax1.yaxis.label.set_color(colors[0])
	ax2.yaxis.label.set_color(colors[1])

	ax1.tick_params(axis='y', colors=colors[0])
	ax2.tick_params(axis='y', colors=colors[1])

	plt.title('Structure over generations')
	plt.show()


def plot_species_sizes(species_sizes, compatibility_thresholds):
	num_generations = len(species_sizes)

	assert num_generations == len(compatibility_thresholds), 'All lists must be the same length'

	num_species = len(species_sizes[-1])
	generations = range(num_generations)

	curves = np.zeros((num_species, num_generations))
	num_active_species = []
	avg_sizes = []

	for i, row in enumerate(species_sizes):
		for j, element in enumerate(row):
			curves[j][i] = element

		num_active = np.count_nonzero(row)
		num_active_species.append(num_active)

		avg_size = sum(row) / num_active
		avg_sizes.append(avg_size)

	# plot distribution of individuals per species
	plt.stackplot(generations, curves)
	plt.title('Distribution of individuals per species')
	plt.xlabel('Generation')
	plt.ylabel('Number of individuals')
	plt.show()

	# plot species stats over generations
	colors = ['blue', 'red', 'green']

	fig, ax1 = plt.subplots()
	ax2 = ax1.twinx()
	ax3 = ax1.twinx()
	ax3.spines['right'].set_position(('axes', 1.2))
	ax1.set_xlabel('Generation')

	ax1.plot(generations, avg_sizes, color=colors[0], label='Average species size')
	ax1.set_ylabel('Number of individuals')

	ax2.plot(generations, num_active_species, color=colors[1], label='Number of species')
	ax2.set_ylabel('Number of species')

	ax3.plot(generations, compatibility_thresholds, color=colors[2], label='Compatibility threshold')
	ax3.set_ylabel('Value')

	line1, label1 = ax1.get_legend_handles_labels()
	line2, label2 = ax2.get_legend_handles_labels()
	line3, label3 = ax3.get_legend_handles_labels()
	plt.legend(line1 + line2 + line3, label1 + label2 + label3)

	ax1.yaxis.label.set_color(colors[0])
	ax2.yaxis.label.set_color(colors[1])
	ax3.yaxis.label.set_color(colors[2])

	ax1.tick_params(axis='y', colors=colors[0])
	ax2.tick_params(axis='y', colors=colors[1])
	ax3.tick_params(axis='y', colors=colors[2])

	plt.title('Species stats over generations')
	plt.show()


def plot_distances(avg_Es, avg_Ds, avg_weight_diffs):
	num_generations = len(avg_Es)

	assert num_generations == len(avg_Ds) and num_generations == len(avg_weight_diffs), 'All lists must be the same length'

	generations = range(num_generations)
	labels = ['Average excess', 'Average disjoint', 'Average weight diff']

	# plot average individuals distances through generations
	plt.stackplot(generations, avg_Es, avg_Ds, avg_weight_diffs, labels=labels)
	plt.title('Average individuals distances through generations')
	plt.xlabel('Value')
	plt.ylabel('Number of individuals')
	plt.legend()
	plt.show()


def print_info(individual):
	print('Individual info:')
	print('\tScore: {:.2f}'.format(individual.fitness))
	num_hidden = len(individual.nodes) - config.num_starting_nodes
	print('\tNum nodes: {:d}'.format(num_hidden))
	num_conn = len([conn for conn in individual.connections.values() if conn.enabled])
	print('\tNum connections: {:d}'.format(num_conn))


def print_evaluation_stats(num_evaluations, num_hidden_nodes, num_connections):
	avg_ev = np.mean(num_evaluations)
	avg_gen = avg_ev / config.pop_size
	std_ev = np.std(num_evaluations)
	std_gen = std_ev / config.pop_size
	worst_run = max(num_evaluations)
	worst_run_gen = worst_run / config.pop_size
	avg_hidden = np.mean(num_hidden_nodes)
	std_hidden = np.std(num_hidden_nodes)
	avg_conn = np.mean(num_connections)
	std_conn = np.std(num_connections)
	num_finished_runs = len(num_evaluations)

	print('Num evaluations:')
	print('\tavg: {:.2f} (~{:d} generations)'.format(avg_ev, int(avg_gen)))
	print('\tstdev: {:.2f} (~{:d} generations)'.format(std_ev, int(std_gen)))
	print('\tworst: {:.2f} (~{:d} generations)'.format(worst_run, int(worst_run_gen)))
	print('Structure:')
	print('\tavg num hidden nodes: {:.2f} (std {:.2f})'.format(avg_hidden, std_hidden))
	print('\tavg num connections: {:.2f} (std {:.2f})'.format(avg_conn, std_conn))
	print('From {:d} finished runs (of {:d} total runs)'.format(num_finished_runs, config.num_runs))


def demonstrate_if_exists(agent_file_name, env, video_file_name=None):
	if exists(agent_file_name):
		response = input('Do you wish to [t]rain new agent or [d]emonstrate existing one: ')

		if response == 't':
			return False

		if response != 'd':
			return True

		agent = utility.load(agent_file_name)
		env.evaluate(agent, render=True, video_file_name=video_file_name)

		return True

	return False
