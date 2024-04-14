import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import random
from functools import reduce
from operator import add

from network import Network


class Optimizer:
    """Class that implements genetic algorithm for MLP optimization."""

    def __init__(self, nn_param_choices, retain=0.4,
                 random_select=0.1, mutate_chance=0.2):
        """

        :param nn_param_choices dict: dictionary with NN parameters
        :param retain float: retain rate per population
        :param random_select float: random selection rate
        :param mutate_chance float: mutation rate per population
        """
        self.mutate_chance = mutate_chance
        self.random_select = random_select
        self.retain = retain
        self.nn_param_choices = nn_param_choices

    def create_population(self, count):
        """
        Create a population of random networks.
        :param count int: Number of networks to generate, aka the size of the population
        :return list: Population of network objects:
        """
        for _ in range(count):
            # Create a random network.
            network = Network(self.nn_param_choices)
            network.create_random()
            # Add the network to our population.
            yield network

    @staticmethod
    def fitness(network):
        """Return the accuracy, which is our fitness function."""
        return network.loss

    def grade(self, pop):
        """
        Find average fitness for a population
        :param pop list: The population of networks
        :return float: The average accuracy of the population
        """
        summed = reduce(add, (self.fitness(network) for network in pop))
        return summed / len(pop)

    def breed(self, mother, father):
        """
        Make two children as parts of their parents.
        :param mother dict: Network parameters
        :param father dict: Network parameters
        :return:
        """
        children = []
        for _ in range(2):

            child = {}

            # Loop through the parameters and pick params for the kid.
            for param in self.nn_param_choices:
                child[param] = random.choice(
                    [mother.network[param], father.network[param]]
                )

            # Now create a network object.
            network = Network(self.nn_param_choices)
            network.create_set(child)

            # Randomly mutate some of the children.
            if self.mutate_chance > random.random():
                network = self.mutate(network)

            children.append(network)

        return children

    def mutate(self, network):
        """
        Randomly mutate one part of the network.
        :param network dict: The network parameters to mutate
        :return object: A randomly mutated network object
        """

        # Choose a random key.
        mutation = random.choice(list(self.nn_param_choices.keys()))

        # Mutate one of the params.
        network.network[mutation] = random.choice(self.nn_param_choices[mutation])

        return network

    def evolve(self, pop):
        """
        Evolve a population of networks.
        :param pop list:  A list of network parameters
        :return list: The evolved population of networks

        """
        # Get scores for each network.
        graded = [(self.fitness(network), network) for network in pop]
        # Sort on the scores.
        graded = [x[1] for x in sorted(graded, key=lambda x: x[0], reverse=False)]

        # Get the number we want to keep for the next gen.
        retain_length = int(len(graded) * self.retain)

        # The parents are every network we want to keep.
        parents = graded[:retain_length]
        # For those we aren't keeping, randomly keep some anyway.
        for individual in graded[retain_length:]:
            if self.random_select > random.random():
                parents.append(individual)

        # Now find out how many spots we have left to fill.
        parents_length = len(parents)
        desired_length = len(pop) - parents_length
        children = []

        # Add children, which are bred from two remaining networks.
        while len(children) < desired_length:

            # Get a random mom and dad.
            male = random.randint(0, parents_length-1)
            female = random.randint(0, parents_length-1)

            # Assuming they aren't the same network...
            if male != female:
                male = parents[male]
                female = parents[female]

                # Breed them.
                babies = self.breed(male, female)

                # Add the children one at a time.
                for baby in babies:
                    # Don't grow larger than desired length.
                    if len(children) < desired_length:
                        children.append(baby)

        parents.extend(children)

        return parents