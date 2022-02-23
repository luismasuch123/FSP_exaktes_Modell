#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to display FSP_sol.

@author: Luis Masuch Ibanez (luismasuchibanez@googlemail.com)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
from matplotlib.collections import LineCollection

def plot_solution(i_set, k_set, in_set, k_val, y_in, x_i_j_k, z_k_in, pos_i_dir, path):

    fig1, ax = plt.subplots()

    depots = [(pos_i_dir[k][0], pos_i_dir[k][1]) for k in k_set]
    tasks = [(pos_i_dir[i+k_val][0], pos_i_dir[i+k_val][1]) for i in in_set]

    x_depots = list(map(lambda x: x[0], depots))
    y_depots = list(map(lambda x: x[1], depots))

    x_tasks = list(map(lambda x: x[0], tasks))
    y_tasks = list(map(lambda x: x[1], tasks))

    colors = cm.rainbow(np.linspace(0, 1, len(tasks)))
    for x, y, c, i in zip(x_tasks, y_tasks, colors, in_set):
        ax.scatter(x, y, color=c, marker="o" , s=100, label="Task "+str(i+1))

    colors = cm.rainbow(np.linspace(0, 1, len(depots)))
    for x, y, c, k in zip(x_depots, y_depots, colors, k_set):
        ax.scatter(x, y, color=c, marker="s", s=100, label="Depot "+str(k+1))

    color = iter(cm.rainbow(np.linspace(0, 1, len(depots))))
    for k in k_set:
        c=next(color)
        for i in i_set:
            for j in i_set:
                if x_i_j_k[i, j, k].X:
                    x = [pos_i_dir[i][0], pos_i_dir[j][0]]
                    y = [pos_i_dir[i][1], pos_i_dir[j][1]]
                    ax.plot(x, y, c=c)

    #ax.legend(bbox_to_anchor=(1,1), loc="upper left")
    ax.grid(True)
    ax.set_title("FSP_Lösung")

    fig1.savefig(os.path.join(path, "alle_Techniker_plot.png"), bbox_inches='tight', dpi=300) #dpi stellt Qualität ein

    color = iter(cm.rainbow(np.linspace(0, 1, len(depots))))
    for kk in k_set:
        cc = next(color)
        fig2, axs = plt.subplots()

        depots = [(pos_i_dir[k][0], pos_i_dir[k][1]) for k in k_set]
        tasks = [(pos_i_dir[i + k_val][0], pos_i_dir[i + k_val][1]) for i in in_set]

        x_depots = list(map(lambda x: x[0], depots))
        y_depots = list(map(lambda x: x[1], depots))

        x_tasks = list(map(lambda x: x[0], tasks))
        y_tasks = list(map(lambda x: x[1], tasks))

        colors = cm.rainbow(np.linspace(0, 1, len(tasks)))
        for x, y, c, i in zip(x_tasks, y_tasks, colors, in_set):
                axs.scatter(x, y, color=c, marker="o", s=100, label="Task " + str(i + 1))

        colors = cm.rainbow(np.linspace(0, 1, len(depots)))
        for x, y, c, k in zip(x_depots, y_depots, colors, k_set):
            axs.scatter(x, y, color=c, marker="s", s=100, label="Depot " + str(k + 1))

        for i in i_set:
            for j in i_set:
                x = x_i_j_k[i, j, kk].X
                if x > 0.9 and x < 1:
                    x = 1
                if x:
                    x = [pos_i_dir[i][0], pos_i_dir[j][0]]
                    y = [pos_i_dir[i][1], pos_i_dir[j][1]]
                    axs.plot(x, y, c=cc)

        # ax.legend(bbox_to_anchor=(1,1), loc="upper left")
        axs.grid(True)
        axs.set_title("%s" % ("Techniker" + str(kk + 1)))
        fig2.savefig(os.path.join(path, "Techniker_" + str(kk+1) + "_plot.png"), bbox_inches='tight', dpi=300)  # dpi stellt Qualität ein
