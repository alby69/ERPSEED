"""
Evolutionary Algorithms - Algoritmi genetici per ottimizzazione.

Implementa algoritmi genetici per trovare soluzioni ottimali
in spazi di ricerca complessi.
"""
import random
import copy
from typing import List, Callable, Any, Dict, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


@dataclass
class Individual:
    """Rappresenta un individuo nella popolazione"""
    genes: List[Any]
    fitness: float = 0.0
    
    def __repr__(self):
        return f"<Individual fitness={self.fitness:.4f} genes={self.genes[:3]}...>"


class GeneticOptimizer:
    """
    Algoritmo genetico per ottimizzazione.
    
    Usage:
        def objective(genes):
            x, y = genes
            return -(x**2 + y**2)  # Max at (0,0)
        
        ga = GeneticOptimizer(
            gene_ranges=[(-10, 10), (-10, 10)],
            objective=objective,
            population_size=50
        )
        best = ga.evolve(generations=100)
    """
    
    def __init__(self, gene_ranges: List[Tuple], objective: Callable,
                 population_size: int = 50,
                 elite_size: int = 5,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 tournament_size: int = 3,
                 gene_type: type = float):
        """
        Args:
            gene_ranges: Lista di tuple (min, max) per ogni gene
            objective: Funzione di fitness (maggiore = meglio)
            population_size: Dimensione della popolazione
            elite_size: Numero di individui migliori da preservare
            mutation_rate: Probabilità di mutazione
            crossover_rate: Probabilità di crossover
            tournament_size: Dimensione del tournament selection
            gene_type: Tipo dei geni (float o int)
        """
        self.gene_ranges = gene_ranges
        self.objective = objective
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.gene_type = gene_type
        
        self.population: List[Individual] = []
        self.best_individual: Optional[Individual] = None
        self.generation = 0
        self.fitness_history: List[float] = []
    
    def _create_random_gene(self, gene_range: Tuple) -> Any:
        """Crea un gene casuale"""
        min_val, max_val = gene_range
        if self.gene_type == int:
            return random.randint(min_val, max_val)
        return random.uniform(min_val, max_val)
    
    def _create_individual(self, genes: List[Any] = None) -> Individual:
        """Crea un individuo"""
        if genes is None:
            genes = [self._create_random_gene(r) for r in self.gene_ranges]
        
        individual = Individual(genes=genes)
        individual.fitness = self.objective(genes)
        return individual
    
    def _initialize_population(self):
        """Inizializza la popolazione"""
        self.population = [self._create_individual() for _ in range(self.population_size)]
        self._evaluate_population()
    
    def _evaluate_population(self):
        """Valuta tutta la popolazione"""
        for individual in self.population:
            individual.fitness = self.objective(individual.genes)
        
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        
        if self.best_individual is None or self.population[0].fitness > self.best_individual.fitness:
            self.best_individual = copy.deepcopy(self.population[0])
        
        self.fitness_history.append(self.population[0].fitness)
    
    def _selection(self) -> Individual:
        """Selezione tramite tournament"""
        tournament = random.sample(self.population, self.tournament_size)
        tournament.sort(key=lambda x: x.fitness, reverse=True)
        return tournament[0]
    
    def _crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """Crossover tra due individui"""
        if random.random() > self.crossover_rate:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        point = random.randint(1, len(parent1.genes) - 1)
        
        child1_genes = parent1.genes[:point] + parent2.genes[point:]
        child2_genes = parent2.genes[:point] + parent1.genes[point:]
        
        return self._create_individual(child1_genes), self._create_individual(child2_genes)
    
    def _mutate(self, individual: Individual) -> Individual:
        """Mutazione di un individuo"""
        genes = individual.genes.copy()
        
        for i, gene_range in enumerate(self.gene_ranges):
            if random.random() < self.mutation_rate:
                genes[i] = self._create_random_gene(gene_range)
        
        return self._create_individual(genes)
    
    def _create_next_generation(self):
        """Crea la generazione successiva"""
        new_population = []
        
        for i in range(self.elite_size):
            new_population.append(copy.deepcopy(self.population[i]))
        
        while len(new_population) < self.population_size:
            parent1 = self._selection()
            parent2 = self._selection()
            
            child1, child2 = self._crossover(parent1, parent2)
            
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)
            
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        self.population = new_population[:self.population_size]
        self.generation += 1
    
    def evolve(self, generations: int = 100, verbose: bool = True) -> Individual:
        """
        Esegue l'evoluzione.
        
        Args:
            generations: Numero di generazioni
            verbose: Stampa progressi
            
        Returns:
            Il miglior individuo trovato
        """
        self._initialize_population()
        
        for gen in range(generations):
            self._evaluate_population()
            self._create_next_generation()
            
            if verbose and gen % 10 == 0:
                best = self.population[0]
                avg = sum(i.fitness for i in self.population) / len(self.population)
                logger.info(f"Gen {gen}: Best={best.fitness:.4f} Avg={avg:.4f} Genes={best.genes}")
        
        self._evaluate_population()
        
        return self.best_individual
    
    def get_best(self) -> Optional[Individual]:
        """Ottiene il miglior individuo"""
        return self.best_individual
    
    def get_fitness_history(self) -> List[float]:
        """Ottiene la storia della fitness"""
        return self.fitness_history


class AdaptiveOptimizer(GeneticOptimizer):
    """Ottimizzatore genetico con parametri adattivi."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial_mutation_rate = self.mutation_rate
        self.initial_crossover_rate = self.crossover_rate
    
    def _adapt_parameters(self):
        """Adatta i parametri in base all'evoluzione"""
        if len(self.fitness_history) < 10:
            return
        
        recent = self.fitness_history[-10:]
        if max(recent) - min(recent) < 0.01:
            self.mutation_rate = min(0.5, self.mutation_rate * 1.5)
        else:
            self.mutation_rate = max(0.01, self.mutation_rate * 0.95)


class MultiObjectiveOptimizer:
    """Ottimizzatore multi-obiettivo (NSGA-II semplificato)."""
    
    def __init__(self, objectives: List[Callable], gene_ranges: List[Tuple],
                 population_size: int = 50):
        self.objectives = objectives
        self.gene_ranges = gene_ranges
        self.population_size = population_size
        self.population: List[Individual] = []
    
    def _calculate_dominated(self, individual: Individual, others: List[Individual]) -> bool:
        """Verifica se un individuo è dominato"""
        for other in others:
            if other == individual:
                continue
            
            dominated = True
            for obj in self.objectives:
                if obj(individual.genes) <= obj(other.genes):
                    dominated = False
                    break
            
            if dominated:
                return True
        return False
    
    def evolve(self, generations: int = 50) -> List[Individual]:
        """Trova il fronte di Pareto"""
        self.population = [
            Individual(genes=[random.uniform(r[0], r[1]) for r in self.gene_ranges])
            for _ in range(self.population_size)
        ]
        
        for ind in self.population:
            ind.fitness = sum(obj(ind.genes) for obj in self.objectives)
        
        for _ in range(generations):
            pareto_front = [ind for ind in self.population 
                          if not self._calculate_dominated(ind, self.population)]
            
            if pareto_front:
                self.population = pareto_front + random.sample(
                    self.population, 
                    min(10, len(self.population))
                )
        
        return pareto_front if 'pareto_front' in locals() else self.population
