#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check FSP_solution.

@author: Luis Masuch Ibanez (luismasuchibanez@googlemail.com)
"""

import os

from fsp_instance_checker import skillsOfRequiredLevel


def check_solution(k_set, i_set, in_set, s_set, l_set, d_k_s, d_k_e, r_i_s_l, s_k_s_l, y_in, z_k_in, x_i_j_k, path):
    with open(path + "/Solution_Checker.txt", "w") as datei:

        text = "\n ---Lösungschecker--- \n"
        print(text)
        datei.write(text)

        text = "Fahren Techniker los? \n"
        print(text)
        datei.write(text)
        do_technicians_leave(k_set, i_set, x_i_j_k, d_k_s, datei)

        text = "\nKommen Techniker zum Depot zurück? \n"
        print(text)
        datei.write(text)
        do_technicians_come_back(k_set, i_set, x_i_j_k, d_k_e, datei)

        text = "\nFahren Techniker los ohne einen Task zu erfüllen? \n"
        print(text)
        datei.write(text)
        do_technicians_fulfill_task(k_set, in_set, z_k_in, datei)

        text = "\nWerden Tasks nicht erfüllt, obwohl die dafür benötigten Skills und Level prinzipiell vorhanden wären? \n"
        print(text)
        datei .write(text)
        do_realisable_tasks_get_fulfilled(in_set, y_in, datei)

        text = "\nSind alle Techniker, die dem Team zugewiesen sind, um einen Task zu erfüllen, qualifiziert? \n"
        print(text)
        datei.write(text)
        are_members_of_teams_qualified(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l, y_in, z_k_in, datei)


def do_technicians_leave(k_set, i_set, x_i_j_k, d_k_s, datei):
    allLeave = True
    for k in k_set:
        leftDepotCount = 0
        for j in i_set:
            x = x_i_j_k[d_k_s[k], j, k].X
            if x > 0.9 and x < 1:
                x = 1
            leftDepotCount += x
        if leftDepotCount < 1:
            text = "Techniker " + str(k + 1) + " fährt nicht los! \n"
            print(text)
            datei.write(text)
            allLeave = False
        elif leftDepotCount > 1:
            text = "Techniker " + str(k + 1) + " fährt mehrmals vom Depot los! \n"
            print(text)
            datei.write(text)
    if (allLeave):
        text = "Alle Techniker fahren einmal vom Depot los! \n"
        print(text)
        datei.write(text)


def do_technicians_come_back(k_set, i_set, x_i_j_k, d_k_e, datei):
    allComeBack = True
    for k in k_set:
        ComeBackToDepotCount = 0
        for i in i_set:
            x = x_i_j_k[i, d_k_e[k], k].X
            if x > 0.9 and x < 1:
                x = 1
            ComeBackToDepotCount += x
        if ComeBackToDepotCount < 1:
            text = "Techniker " + str(k + 1) + " kehrt nicht zum Depot zurück! \n"
            print(text)
            datei.write(text)
            allComeBack = False
        elif ComeBackToDepotCount > 1:
            text = "Techniker " + str(k + 1) + " kehrt mehrmals zum Depot zurück! \n"
            print(text)
            datei.write(text)
    if (allComeBack):
        text = "Alle Techniker kehren einmal zum Depot zurück! \n"
        print(text)
        datei.write(text)


def do_technicians_fulfill_task(k_set, in_set, z_k_in, datei):
    allWork = True
    for k in k_set:
        worksOnTaskCount = 0
        for i in in_set:
            worksOnTaskCount += z_k_in[k, i].X
        if worksOnTaskCount < 1:
            text = "Techniker " + str(k + 1) + " erfüllt keinen Task! \n"
            print(text)
            datei.write(text)
            allWork = False
    if (allWork):
        text = "Alle Techniker fahren los und erfüllen einen Task! \n"
        print(text)
        datei.write(text)


def do_realisable_tasks_get_fulfilled(in_set, y_in, datei):
    for i in in_set:
        if y_in[i].X != skillsOfRequiredLevel[i]:
            text = "Task " + str(i + 1) + " wurde nicht erfüllt, obwohl die notwendigen Qualifikationen vorhanden wären! \n"
            print(text)
            datei.write(text)


def are_members_of_teams_qualified(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l, y_in, z_k_in, datei):
    allTeamsQualified = True
    for i in in_set:
        if y_in[i].X:
            for s in s_set:
                for l in l_set:
                    if r_i_s_l[i][s][l] != 0:
                        worksOnTaskWithSkillCount = 0
                        for k in k_set:
                            if z_k_in[k, i].X and s_k_s_l[k][s][l]:
                                worksOnTaskWithSkillCount += y_in[i].X
                        if int(worksOnTaskWithSkillCount) != r_i_s_l[i][s][l]:
                            allTeamsQualified = False
                            text = "Task " + str(i) + ": Skill " + str(s+1) + " benötigt " + str(r_i_s_l[i][s][l]) + " Techniker! (" + str(int(worksOnTaskWithSkillCount)) + " zugewiesen) \n"
                            print(text)
                            datei.write(text)
    if allTeamsQualified:
        text = "Alle Skills in den erfüllten Tasks können von den am Team beteiligten, qualifizierten Technikern erbracht werden! \n"
        print(text)
        datei.write(text)



