#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to check FSP_instance.

@author: Luis Masuch Ibanez (luismasuchibanez@googlemail.com)
"""

import os

skillsOfRequiredLevel = []


def check_instance(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l, path):
    with open(path + "/Instance_Checker.txt", "w") as datei:

        text = "\n ---Instanzchecker--- \n"
        datei.write(text)
        print(text)

        text = "Sind alle Skills vorhanden, um die Tasks zu erfüllen? \n"
        datei.write(text)
        print(text)
        can_tasks_be_fulfilled(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l, datei)

        text = "\nGibt es Techniker, die zu keinem Task beitragen können? \n"
        datei.write(text)
        print(text)
        can_technicians_contribute(k_set, in_set, s_set, l_set, r_i_s_l, s_k_s_l, datei)


def can_tasks_be_fulfilled(in_set, s_set, l_set, k_set, r_i_s_l, s_k_s_l, datei):
    allSkillsOfRequiredLevels = True
    for i in in_set:
        skillsOfRequiredLevelHelp = True
        for s in s_set:
            workersWithCharacteristicsCount = 0
            for l in l_set:
                if r_i_s_l[i][s][l] != 0:
                    for k in k_set:
                        workersWithCharacteristicsCount += s_k_s_l[k][s][l]
                    if workersWithCharacteristicsCount == 0:
                        text = "Task " + str(i + 1) + ": Kein Techniker vorhanden, der Skill " + \
                                str(s + 1) + " mit Level " + str(l) + " beherrscht! \n"
                        print(text)
                        datei.write(text)
                        allSkillsOfRequiredLevels = False
                        skillsOfRequiredLevelHelp = False
                    elif workersWithCharacteristicsCount < r_i_s_l[i][s][l]:
                        text = "Task " + str(i + 1) + ": " + str(
                                workersWithCharacteristicsCount) + " Techniker vorhanden, der/die Skill " + str(
                                s + 1) + " mit Level " + str(l) + " beherrscht/beherrschen -> unzureichend! (" + str(
                                r_i_s_l[i][s][l]) + " benötigt) \n"
                        print(text)
                        datei.write(text)
                        allSkillsOfRequiredLevels = False
                        skillsOfRequiredLevelHelp = False
        skillsOfRequiredLevel.append(skillsOfRequiredLevelHelp)

    if allSkillsOfRequiredLevels:
        print("Alle Tasks könnten prinzipiell mit den vorhandenen Skills und den darin bestehenden Leveln erfüllt werden! \n")


def can_technicians_contribute(k_set, in_set, s_set, l_set, r_i_s_l, s_k_s_l, datei):
    techniciansCanContribute = []

    for k in k_set:
        technicianCanContribute = False
        for i in in_set:
            for s in s_set:
                for l in l_set:
                    if r_i_s_l[i][s][l] != 0:
                        if s_k_s_l[k][s][l]:
                            technicianCanContribute = True
        techniciansCanContribute.append(technicianCanContribute)

    allTechniciansCanContribute = True
    for k in k_set:
        if not techniciansCanContribute[k]:
            allTechniciansCanContribute = False
            text = "Techniker " + str(k) + " kann zu keinem Task beitragen! \n"
            print(text)
            datei.write(text)

    if allTechniciansCanContribute:
        text = "Alle Techniker können zu einem Task beitragen! \n"
        print(text)
        datei.write(text)


