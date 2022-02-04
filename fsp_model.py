#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to solve FSP_exaktes_Modell with Gurobi.

@author: Luis Masuch Ibanez (luismasuchibanez@googlemail.com)
"""
import math

import yaml
import gurobipy as gp
from gurobipy import GRB
import argparse
from fsp_instance_checker import check_instance
from fsp_solution_checker import check_solution

# parse script arguments
parser = argparse.ArgumentParser(description='Solves FSP_exaktes_Modell')
parser.add_argument('-y', '--yamldirs', nargs='+', default=[], help='directory containing yaml files')
args = parser.parse_args()

yamlpaths = args.yamldirs

for path in yamlpaths:
    if not path:
        print("No paths to look for yaml files were provided. Exiting.")
        exit()

    with open(path, "r") as stream:
        data = yaml.safe_load(stream)

    #indeces
    i_val = len(data["tasks"]) + len(data["workers"])
    in_val = len(data["tasks"])
    k_val = len(data["workers"])
    s_val = 5 # Achtung: Level 1-5 #TODO: in yaml-Datei
    l_val = 5 # Achtung: Level 0-4

    #sets
    i_set = range(i_val)
    in_set = range(in_val)
    k_set = range(k_val)
    s_set = range(s_val)
    l_set = range(l_val)
    j_set = []
    for i in i_set:
        j_set.append([])
        for j in i_set:
            if i != j:
                j_set[i].append(j)

    #parameters
    t_i_j = []
    for i in i_set:
        t_i_j.append([])
        for j in i_set:
            if i < k_val and j < k_val:
                traveltime = math.sqrt(math.pow(data["workers"][i]["lateralPosition"] - data["workers"][j]["lateralPosition"], 2) + math.pow(data["workers"][i]["longitudinalPosition"] - data["workers"][j]["longitudinalPosition"], 2))
                t_i_j[i].append(traveltime)
            elif i < k_val and j >= k_val:
                traveltime = math.sqrt(math.pow(data["workers"][i]["lateralPosition"] - data["tasks"][j-k_val]["lateralPosition"], 2) + math.pow(data["workers"][i]["longitudinalPosition"] - data["tasks"][j-k_val]["longitudinalPosition"], 2))
                t_i_j[i].append(traveltime)
            elif i >= k_val and j >= k_val:
                traveltime = math.sqrt(math.pow(data["tasks"][i-k_val]["lateralPosition"] - data["tasks"][j-k_val]["lateralPosition"], 2) + math.pow(data["tasks"][i-k_val]["longitudinalPosition"] - data["tasks"][j-k_val]["longitudinalPosition"], 2))
                t_i_j[i].append(traveltime)
            elif i >= k_val and j < k_val:
                traveltime = math.sqrt(math.pow(data["tasks"][i-k_val]["lateralPosition"] - data["workers"][j]["lateralPosition"], 2) + math.pow(data["tasks"][i-k_val]["longitudinalPosition"] - data["workers"][j]["longitudinalPosition"], 2))
                t_i_j[i].append(traveltime)
    #print(t_i_j)

    d_k_s = [int(data["workers"][i]["workerId"])-1 for i in k_set] #Achtung: startet mit Depot 0
    d_k_e = d_k_s

    o_i = [float(data["workers"][i]["dateTimeWindows"][0]["openingTime"]) for i in k_set] + [float(data["tasks"][i]["dateTimeWindows"][0]["openingTime"]) for i in in_set]
    c_i = [float(data["workers"][i]["dateTimeWindows"][0]["closingTime"]) for i in k_set] + [float(data["tasks"][i]["dateTimeWindows"][0]["closingTime"]) for i in in_set]

    t_i = [0 for k in k_set] + [float(data["tasks"][i]["serviceDuration"]) for i in in_set]
    p_in = [float(data["tasks"][i]["priority"]) for i in in_set]

    r_i_s_l = [] #id's start with 0
    """
    for i in in_set:
        r_i_s_l.append([])
        helps = 0
        for s in range(int(data["tasks"][i]["requiredSkills"][len(data["tasks"][i]["requiredSkills"])-1]["id"])):
            r_i_s_l[i].append([])
            if helps < len(data["tasks"][i]["requiredSkills"]):
                if int(data["tasks"][i]["requiredSkills"][helps]["id"]) - 1 == s:
                    for l in range(int(data["tasks"][i]["requiredSkills"][helps]["level"])):
                        r_i_s_l[i][s].append(0)
                    for l in range(int(data["tasks"][i]["requiredSkills"][helps]["level"]), int(data["tasks"][i]["requiredSkills"][helps]["level"])+1):
                        r_i_s_l[i][s].append(int(data["tasks"][i]["requiredSkills"][helps]["requiredWorkers"]))
                    helps += 1
                else:
                    r_i_s_l[i][s].append(0)
    """
    for i in in_set:
        r_i_s_l.append([])
        helps = 0
        for s in range(s_val):
            r_i_s_l[i].append([])
            if helps < len(data["tasks"][i]["requiredSkills"]):
                if int(data["tasks"][i]["requiredSkills"][helps]["id"]) - 1 == s:
                    for l in range(int(data["tasks"][i]["requiredSkills"][helps]["level"])):
                        r_i_s_l[i][s].append(0)
                    for l in range(int(data["tasks"][i]["requiredSkills"][helps]["level"]), int(data["tasks"][i]["requiredSkills"][helps]["level"])+1):
                        r_i_s_l[i][s].append(int(data["tasks"][i]["requiredSkills"][helps]["requiredWorkers"]))
                    for l in range(int(data["tasks"][i]["requiredSkills"][helps]["level"])+1, l_val):
                        r_i_s_l[i][s].append(0)
                    helps += 1
                else:
                    for l in l_set:
                        r_i_s_l[i][s].append(0)
            else:
                for l in l_set:
                    r_i_s_l[i][s].append(0)

    s_k_s_l = []
    """
    for k in k_set:
        s_k_s_l.append([])
        helps = 0
        for s in range(int(data["workers"][k]["skills"][len(data["workers"][k]["skills"])-1]["id"])):
            s_k_s_l[k].append([])
            if helps < len(data["workers"][k]["skills"]):
                if (int(data["workers"][k]["skills"][helps]["id"])-1 == s):
                    for l in range(int(data["workers"][k]["skills"][helps]["level"])+1):
                        s_k_s_l[k][s].append(1)
                    helps += 1
                else:
                    s_k_s_l[k][s].append(0)
    """
    for k in k_set:
        s_k_s_l.append([])
        helps = 0
        for s in range(s_val):
            s_k_s_l[k].append([])
            if helps < len(data["workers"][k]["skills"]):
                if (int(data["workers"][k]["skills"][helps]["id"])-1 == s):
                    for l in range(int(data["workers"][k]["skills"][helps]["level"])+1):
                        s_k_s_l[k][s].append(1)
                    for l in range(int(data["workers"][k]["skills"][helps]["level"])+1, l_val):
                        s_k_s_l[k][s].append(0)
                    helps += 1
                else:
                    for l in l_set:
                        s_k_s_l[k][s].append(0)
            else:
                for l in l_set:
                    s_k_s_l[k][s].append(0)

    dplus_i = []
    """
    for i in i_set:
        dplus_i.append([])
        if i < k_val:
            dplus_i[i].append(list(range(k_val, i_val)))
        else:
            dplus_i[i].append(list(range(k_val, i)) + list(range(i+1, i_val)))
    """
    for i in i_set:
        dplus_i.append(set(j_set[i]))

    dminus_i = []
    """
    for i in i_set:
        dplus_i.append([])
        if i < k_val:
            dplus_i[i].append(list(range(k_val, i_val)))
        else:
            dplus_i[i].append(list(range(k_val, i)) + list(range(i + 1, i_val)))
    """
    for i in i_set:
        dminus_i.append(set(j_set[i]))

    M = 1000000

    # Create a new model
    m = gp.Model("fsp")
    m.setParam("TimeLimit", 1*10)
    #TODO: Epsilon

    # variables
    # binary decision variables #
    y_in = m.addVars(in_val, vtype=GRB.BINARY, name="y")
    x_i_j_k = m.addVars(i_val, i_val, k_val, vtype=GRB.BINARY, name="x") #TODO: wie i!=j modellieren?
    z_k_in = m.addVars(k_val, in_val, vtype=GRB.BINARY, name="z")

    #real variables
    s_i= m.addVars(i_val,vtype=GRB.CONTINUOUS, name="s")

    # objective
    m.setObjective(gp.LinExpr(p_in, y_in.select("*")), GRB.MAXIMIZE)

    # constraints
    m.addConstrs(((gp.quicksum(x_i_j_k[d_k_e[k], i, k] for i in dplus_i[d_k_e[k]]) == gp.quicksum(x_i_j_k[j, d_k_s[k], k] for j in dminus_i[d_k_s[k]])) for k in k_set), "c6.1")
    m.addConstrs(((gp.quicksum(x_i_j_k[j, d_k_s[k], k] for j in dminus_i[d_k_s[k]]) == 1) for k in k_set), "c6.2")

    m.addConstrs(((gp.quicksum(x_i_j_k[j, i, k] for j in dminus_i[i]) == gp.quicksum(x_i_j_k[i, h, k] for h in dplus_i[i])) for i in in_set for k in k_set), "c7")

    m.addConstrs(((s_i[i] + t_i_j[i][j] + t_i[i] - s_i[j] <= M * (1 - x_i_j_k[i, j, k])) for k in k_set for i in i_set for j in set(j_set[i])), "c8") #if i!=j möglich

    m.addConstrs(((o_i[i] <= s_i[i]) for i in i_set), "c9.1")
    m.addConstrs(((s_i[i] <= c_i[i]) for i in i_set), "c9.2")

    m.addConstrs(((y_in[i] * r_i_s_l[i][s][l] <= gp.quicksum(z_k_in[k, i] * s_k_s_l[k][s][l] for k in k_set)) for i in in_set for s in s_set for l in l_set), "c10")

    m.addConstrs(((z_k_in[k, i] <= gp.quicksum(x_i_j_k[i+k_val, j, k] for j in dminus_i[i+k_val])) for i in in_set for k in k_set), "c11")

    # Optimize model
    m.optimize()

    for v in m.getVars():
        print('%s %g' % (v.varName, v.x)) #TODO: in Lösungsdatei schreiben auf die Lösungschecker zugreift

    print('Obj: %g' % m.objVal)

    #Instanz-Checker
    check_instance(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l)

    #Lösungs-Checker
    check_solution(k_set, i_set, in_set, x_i_j_k, d_k_s, d_k_e, y_in, z_k_in)


