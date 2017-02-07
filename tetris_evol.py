#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Genetic algorithm for Tetris AI. Fitness based on lines cleared.


from random import randrange as rand
import sys, random, queue, tetris_bot

def mate(m, f):
    child = [(m[0] * m[1][x] + f[0] * f[1][x]) / (m[0] + f[0])  for x in range(len(m[1]))]
    if random.random() < 0.7:
        mut = (int) (random.random() * 7)
        child[mut] += random.random() * 0.4 - 0.2
        child[mut] = abs(child[mut])
        if child[mut] >= 1:
            child[mut] -= 2 * (child[mut] - 1)
    return child

if __name__ == '__main__':
    fout = open("tetris_data.txt", mode = "w", encoding = "utf-8")
    n = 16
    gen = 1
    # If you want to start from an existing data set, enter it in population and set children to be an empty list.
    population = []
    scores = 0
    children = [[random.random() for x in range(7)] for y in range(n)]
    while(1):
        print("Generation", gen, file = fout, flush = True)
        print("Generation", gen, flush = True)
        for x in range(len(population)):
            print(population[x][0], end = "\t", file = fout, flush = True)
            print(population[x][0], end = "\t")
            for y in range(7):
                print(population[x][1][y], end = "\t", file = fout, flush = True)
                print(population[x][1][y], end = "\t")
            print(file = fout, flush = True)
            print()
        for x in range(len(children)):
            scores = 0
            tetris_bot.p = children[x]
            for i in range(10):
                App = tetris_bot.TetrisBot()
                scores += App.run()
            population.append((scores, p))
            print(scores, end = "\t", file = fout, flush = True)
            print(scores, end = "\t", flush = True)
            for x in range(7):
                print(p[x], end = "\t", file = fout, flush = True)
                print(p[x], end = "\t", flush = True)
            print(file = fout, flush = True)
            print()
        children.clear()
        while len(children) < 4:
            s = random.sample(population, 4)
            s.sort(key = lambda l: l[0])
            children.append(mate(s[2], s[3]))
        population.sort(key = lambda l: l[0], reverse = True)
        for x in range(4):
            population.pop()
        gen += 1
        num = input("Continue? ")
        if not num:
            break
        print(file = fout, flush = True)
        print()
