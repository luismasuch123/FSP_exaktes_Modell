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
import csv
from pathlib import Path
import os
from fsp_instance_checker import check_instance
from fsp_solution_checker import check_solution
from fsp_plot_solution import plot_solution

# parse script arguments
parser = argparse.ArgumentParser(description='Solves FSP_exaktes_Modell')
parser.add_argument('-y', '--yaml-dirs', nargs='+', default=[], help='directory containing yaml files')
parser.add_argument('-c', '--csv-dir', help='directory to write sol, cb and plot to')
parser.add_argument('--write-solution', action='store_true', default=True, help='write solution to csv')
parser.add_argument('--write-callback', action='store_true', default=True, help='write callback to csv')
parser.add_argument('--display-solution', action='store_true', default=True, help='display solution')
parser.add_argument('--check-instance', action='store_true', default=True, help='check instance')
parser.add_argument('--check-solution', action='store_true', default=True, help='check solution')


args = parser.parse_args()
writeSolution = args.write_solution
writeCallback = args.write_callback
displaySolution = args.display_solution
checkInstance = args.check_instance
checkSolution = args.check_solution

yamlpaths = args.yaml_dirs
csvdir = args.csv_dir

def data_cb(model, where):
    if where == gp.GRB.Callback.MIP:
        cur_lb = model.cbGet(GRB.Callback.MIP_OBJBST)
        cur_ub = model.cbGet(GRB.Callback.MIP_OBJBND)
        cur_gap = (cur_ub - cur_lb) / cur_lb
        cur_time = model.cbGet(GRB.Callback.RUNTIME)

        epsGap = 0.1
        if cur_gap < epsGap and cur_gap > 0:
            model.terminate()

        model._data.append([cur_lb, cur_ub, cur_gap, cur_time])


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
    s_val = data["numberOfSkills"] # Achtung: Level 1-5
    l_val = data["numberOfLevels"] # Achtung: Level 0-4

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

    #parameters for plot
    pos_i_dir = [] #lateral/longitudinal (direction) position of i
    for k in k_set:
        pos_i_dir.append([])
        pos_i_dir[k].append(data["workers"][k]["lateralPosition"])
        pos_i_dir[k].append(data["workers"][k]["longitudinalPosition"])
    for i in in_set:
        pos_i_dir.append([])
        pos_i_dir[i+k_val].append(data["tasks"][i]["lateralPosition"])
        pos_i_dir[i+k_val].append(data["tasks"][i]["longitudinalPosition"])
    print(pos_i_dir)

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
    #TODO: warum ein x 0.9999
    x_i_j_k = m.addVars(i_val, i_val, k_val, vtype=GRB.BINARY, name="x") #TODO: wie i!=j modellieren?
    z_k_in = m.addVars(k_val, in_val, vtype=GRB.BINARY, name="z")

    #real variables
    s_i= m.addVars(i_val,vtype=GRB.CONTINUOUS, name="s")

    #Hilfsvarible

    #objective
    #TODO: Gewichtungsfaktor abhängig von Instanz
    tiebreaker = True
    m.setObjective((gp.LinExpr(p_in, y_in.select("*")) - tiebreaker * 0.001 * sum((x_i_j_k[i, j, k] * t_i_j[i][j] for k in k_set for i in i_set for j in set(j_set[i])))), GRB.MAXIMIZE)

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
    m._data = []
    m.optimize(callback=data_cb)

    if writeCallback:
        header = ['LB', 'UB', 'MIPGap', 'Zeit']
        instanzName = Path(path).stem
        path = os.path.join(csvdir, instanzName)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(path + "/_" + instanzName + '_cb.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(m._data)

    #TODO: in Lösungsdatei schreiben auf die Lösungschecker zugreift
    for v in m.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

    if writeSolution:
        header = ['Instanz', 'Zeit', 'Zfkt.wert', 'MIPGap']
        instanzName = Path(path).stem
        path = os.path.join(csvdir, instanzName)
        data = [instanzName, m.runtime, m.objVal, m.mipgap]
        with open(path + "/_" + instanzName + '_sol.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(data)
    #help(GRB.attr)

    #Instanz-Checker
    if checkInstance:
        check_instance(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l)

    #Lösungs-Checker
    if checkSolution:
        check_solution(k_set, i_set, in_set, s_set, l_set, d_k_s, d_k_e, r_i_s_l, s_k_s_l, y_in, z_k_in, x_i_j_k)

    #Visualisierung
    if displaySolution:
        plot_solution(i_set, k_set, in_set, k_val, y_in, x_i_j_k, z_k_in, pos_i_dir, os.path.join(csvdir, instanzName),Path(path).stem)



