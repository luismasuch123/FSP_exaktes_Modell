#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check FSP_solution.

@author: Luis Masuch Ibanez (luismasuchibanez@googlemail.com)
"""

from fsp_instance_checker import skillsOfRequiredLevel


def check_solution(k_set, i_set, in_set, x_i_j_k, d_k_s, d_k_e, y_in, z_k_in):
    print("\n ---Lösungschecker--- \n")

    print("Fahren Techniker los?")
    do_technicians_leave(k_set, i_set, x_i_j_k, d_k_s)

    print("\nKommen Techniker zum Depot zurück?")
    do_technicians_come_back(k_set, i_set, x_i_j_k, d_k_e)

    print("\nFahren Techniker los ohne einen Task zu erfüllen?")
    do_technicians_fulfill_task(k_set, in_set, z_k_in)

    print("\nWerden Tasks nicht erfüllt, obwohl die dafür benötigten Skills und Level prinzipiell vorhanden wären?")
    do_realisable_tasks_get_fulfilled(in_set, y_in)


def do_technicians_leave(k_set, i_set, x_i_j_k, d_k_s):
    allLeave = True
    for k in k_set:
        leftDepotCount = 0
        for j in i_set:
            leftDepotCount += x_i_j_k[d_k_s[k], j, k].X
        if leftDepotCount < 1:
            print("Techniker " + str(k + 1) + " fährt nicht los!")
            allLeave = False
        elif leftDepotCount > 1:
            print("Techniker " + str(k + 1) + " fährt mehrmals vom Depot los!")
    if (allLeave):
        print("Alle Techniker fahren einmal vom Depot los!")


def do_technicians_come_back(k_set, i_set, x_i_j_k, d_k_e):
    allComeBack = True
    for k in k_set:
        ComeBackToDepotCount = 0
        for i in i_set:
            ComeBackToDepotCount += x_i_j_k[i, d_k_e[k], k].X
        if ComeBackToDepotCount < 1:
            print("Techniker " + str(k + 1) + " kehrt nicht zum Depot zurück!")
            allComeBack = False
        elif ComeBackToDepotCount > 1:
            print("Techniker " + str(k + 1) + " kehrt mehrmals zum Depot zurück!")
    if (allComeBack):
        print("Alle Techniker kehren einmal zum Depot zurück!")


def do_technicians_fulfill_task(k_set, in_set, z_k_in):
    allWork = True
    for k in k_set:
        worksOnTaskCount = 0
        for i in in_set:
            worksOnTaskCount += z_k_in[k, i].X
        if worksOnTaskCount < 1:
            print("Techniker " + str(k + 1) + " erfüllt keinen Task!")
            allWork = False
    if (allWork):
        print("Alle Techniker fahren los und erfüllen einen Task!")


def do_realisable_tasks_get_fulfilled(in_set, y_in):
    for i in in_set:
        if y_in[i].X != skillsOfRequiredLevel[i]:
            print(
                "Task " + str(i + 1) + " wurde nicht erfüllt, obwohl die notwendigen Qualifikationen vorhanden wären!")