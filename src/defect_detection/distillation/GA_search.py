import os
import sys
import copy
import torch
import random
import logging
import hashlib
import argparse

from tqdm import tqdm
from distill import student_train
from model import biLSTM, biGRU, Roberta, ce_loss_func, mse_loss_func
from torch.utils.data import DataLoader, SequentialSampler, RandomSampler
from transformers import RobertaConfig, RobertaForSequenceClassification, RobertaTokenizer

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


class Genome(object):
    def __init__(self, gene_param=None):
        self.fitness = 0.0
        self.gene_param = gene_param

        if not self.gene_param:
            self.hash = 0
        else:
            self.update_hash()
    
    def update_hash(self):
        gene_string = str(self.gene_param["vocab_size"]) + \
                        str(self.gene_param["input_dim"]) + \
                        str(self.gene_param["hidden_dim"]) + \
                        str(self.gene_param["n_layers"]) + \
                        str(self.gene_param["alpha"]) + \
                        str(self.gene_param["lr"]) + \
                        str(self.gene_param["temperature"])
        self.hash = hashlib.md5(gene_string.encode("UTF-8")).hexdigest()

    def mutation(self, search_space):
        mutated_gene = random.choice(list(self.gene_param.keys()))
        current_value = self.gene_param[mutated_gene]
        possible_choices = copy.deepcopy(search_space[mutated_gene])
        possible_choices.remove(current_value)
        self.gene_param[mutated_gene] = random.choice(possible_choices)
        self.update_hash()


class GA_search():
    def __init__(self, args, search_space, retain_chance=0.3, mutate_chance=0.3):
        self.args = args
        self.search_space = search_space
        self.retain_chance = retain_chance
        self.mutate_chance = mutate_chance
        self.population = []

    def is_duplicate(self, new_genome):
        for genome in self.population:
            if new_genome.hash == genome.hash:
                return True

    def initialization(self):
        count = 0

        while count < self.args.population_size:
            gene_param = []
            for key in self.search_space:
                gene_param[key] = random.choice(self.search_space[key])
            new_genome = Genome(gene_param)
            
            if len(self.population) > 0:
                while self.is_duplicate(new_genome):
                    new_genome.mutation()

            self.population.append(new_genome)
            count += 1
        
        logger.info(self.population)

    def fitness(self):
        config = RobertaConfig.from_pretrained("microsoft/codebert-base")
        config.num_labels = 2
        
        tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        tokenizer.do_lower_case = True

        if self.args.block_size <= 0:
            self.args.block_size = tokenizer.max_len_single_sentence
        self.args.block_size = min(self.args.block_size, tokenizer.max_len_single_sentence)

        teacher_model = Roberta(RobertaForSequenceClassification.from_pretrained("microsoft/codebert-base", config=config))
    
        n_labels = 2

        if args.std_model == "biLSTM":
            student_model = biLSTM(args.vocab_size, args.input_dim, args.hidden_dim, n_labels, args.n_layers)
        elif args.std_model == "biGRU":
            student_model = biGRU(args.vocab_size, args.input_dim, args.hidden_dim, n_labels, args.n_layers)
        elif args.std_model == "Roberta":
            std_config = RobertaConfig.from_pretrained("microsoft/codebert-base")
            std_config.num_labels = n_labels
            std_config.hidden_size = args.hidden_dim
            std_config.max_position_embeddings = args.block_size + 2
            std_config.vocab_size = args.vocab_size
            std_config.num_attention_heads = 8
            std_config.num_hidden_layers = args.n_layers
            student_model = Roberta(RobertaForSequenceClassification(std_config))

        if args.do_train:
            train_dataset = DistilledDataset(args, tokenizer, args.vocab_size, args.train_data_file)
            train_sampler = RandomSampler(train_dataset)
            train_dataloader = DataLoader(train_dataset, sampler=train_sampler, batch_size=args.train_batch_size)
        
        eval_dataset = DistilledDataset(args, tokenizer, args.vocab_size, args.eval_data_file)
        eval_sampler = SequentialSampler(eval_dataset)
        eval_dataloader = DataLoader(eval_dataset, sampler=eval_sampler, batch_size=args.eval_batch_size, num_workers=8, pin_memory=True)
        
        student_model.to(args.device)

        if args.do_train:
            student_train(teacher_model, student_model, args, train_dataloader, eval_dataloader)
        return self.fitness

    def crossover_and_mutation(self, parents):
        children = []
        parent_1, parent_2 = parents
        genome_len = len(self.search_space)
        recomb_loc = random.randint(1, genome_len - 1)

        child_1 = {}
        child_2 = {}

        keys = list(self.search_space)
        keys = sorted(keys)

        for x in range(0, genome_len):
            if x < recomb_loc:
                child_1[keys[x]] = parent_1.geneparam[keys[x]]
                child_2[keys[x]] = parent_2.geneparam[keys[x]]
            else:
                child_1[keys[x]] = parent_2.geneparam[keys[x]]
                child_2[keys[x]] = parent_1.geneparam[keys[x]]

        genome_1 = Genome(child_1)
        genome_2 = Genome(child_2)

        if self.mutate_chance > random.random():
            genome_1.mutation()

        if self.mutate_chance > random.random():
            genome_2.mutation()

        while self.is_duplicate(genome_1):
            genome_1.mutation()

        while self.is_duplicate(genome_2):
            genome_2.mutation()

        children.append(genome_1)
        children.append(genome_2)

        return children

    def generation(self):
 
        graded_genome = [(self.fitness(genome), genome) for genome in self.population]
        graded_genome = [x[1] for x in sorted(graded_genome, key=lambda x: x[0], reverse=True)]
        retain_length = int(len(graded_genome) * self.retain_chance)
        new_generation = graded_genome[:retain_length]
        desired_length = len(self.population) - len(new_generation)

        children = []
        while len(children) < desired_length:
            parents_id = random.sample(range(len(new_generation)-1), k=2)
            parents = (new_generation[parents_id[0]], new_generation[parents_id[1]])
            babies = self.crossover_and_mutation(parents)

            for baby in babies:
                if len(children) < desired_length:
                    children.append(baby)

        new_generation.extend(children)
        self.population = new_generation


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--population_size", default=10, type=int, required=True)
    parser.add_argument("--generation_size", default=20, type=int, required=True)
    parser.add_argument("--train_data_file", default=None, type=str, required=True,
                        help="The input training data file")
    parser.add_argument("--eval_data_file", default=None, type=str,
                        help="An optional input evaluation data file to evaluate the perplexity on")
    parser.add_argument("--block_size", default=-1, type=int,
                        help="Optional input sequence length after tokenization.")
    parser.add_argument("--model_dir", default="./", type=str,
                        help="The output directory where the model predictions and checkpoints will be written.")
    parser.add_argument("--model", default="biLSTM", type=str, required=True,
                        help="Student Model Type.")
    parser.add_argument("--loss_func", default="ce", type=str,
                        help="Loss Function Type.")
    parser.add_argument("--train_batch_size", default=16, type=int,
                        help="Batch size per GPU/CPU for training.")
    parser.add_argument("--eval_batch_size", default=16, type=int,
                        help="Batch size per GPU/CPU for evaluation.")
    parser.add_argument('--seed', type=int, default=42,
                        help="random seed for initialization")
    parser.add_argument('--epochs', type=int, default=42,
                        help="random seed for initialization")

    args = parser.parse_args()
    search_space = {
        "vocab_size": [*range(1000, 51000, 1000)],
        "input_dim": [*range(1, 769)],
        "hidden_dim": [*range(1, 769)],
        "n_layers": [*range(1, 13)],
        "alpha": torch.arange(0.75, 1, 0.02).tolist(),
        "lr": [1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4], 
        "temperature": [*range(1, 11)]
    }

    logger.info("***Start GA search for %d generations and %d population***" %
          (args.generation_size, args.population_size))

    searcher = GA_search(args, search_space)
    searcher.initialization(args.population_size)

    for gen in tqdm(args.generation_size):
        logger.info("***Start generate %d***" %(gen))
        searcher.fitness()
        searcher.generation()
    
    graded_genome = [(searcher.fitness(genome), genome) for genome in searcher.population]
    graded_genome = [x[1] for x in sorted(graded_genome, key=lambda x: x[0], reverse=True)]

    logger.info(graded_genome[:3])


if __name__ == "__main__":
    main()