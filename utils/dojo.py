"""A training dojo for algorithms."""
from copy import deepcopy
import itertools
from time import time

__all__ = ["Dojo", "TimingDojo", "FitnessDojo"]

INFINITY = float("inf")


class Dojo(object):
    """A testing class for competing algorithms."""
    def __init__(self, algorithms, environ, runs=100):
        self.algorithms = list(algorithms)
        self.environ = environ
        self.runs = runs

    def train(self, *args):
        """Executes the algorithms, comparing their performance.

        This has to be implemented by inheriting classes.
        """
        raise NotImplementedError("not implemented")


class TimingDojo(Dojo):
    """A testing class for competing algorithms, measuring the execution time
    of each.
    """
    def train(self, *args):
        """Trains the algorithms."""
        var = list(itertools.permutations(self.algorithms))
        variants = itertools.chain(*var)
        results = {}
        for v in variants:
            runresult = 0
            for r in range(self.runs):
                env = deepcopy(self.environ)
                start = time()
                v(env, *args)
                runresult += time() - start
            runresult /= self.runs
            if results.get(v, INFINITY) > runresult:
                results[v] = runresult
        return min(results, key=results.get)


class FitnessDojo(Dojo):
    """A testing class for competing algorithms, measuring the fitness of each.
    """
    def __init__(self, algorithms, environ, runs=100, cmpfunc=min):
        super(FitnessDojo, self).__init__(algorithms, environ, runs)
        self.cmpfunc = cmpfunc

    def train(self, *args):
        """Trains the algorithms."""
        var = list(itertools.permutations(self.algorithms))
        variants = itertools.chain(*var)
        results = {}
        for v in variants:
            runresult = 0
            for r in range(self.runs):
                runresult += v(deepcopy(self.environ), *args)
            runresult /= self.runs
            if results.get(v, INFINITY) > runresult:
                results[v] = runresult
        return self.cmpfunc(results, key=results.get)
