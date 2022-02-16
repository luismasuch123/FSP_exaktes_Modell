import os
import copy
import yaml
import decimal
import random
from pathlib import Path

instanceSets = ["pr01_10",
                #"c_r_rc_100_100"
                ]

numberOfSkills = 3
numberOfLevels = 3
percentageTasksHaveSkills = 100
percentageWorkersHaveSkills = 100
probabilityWorkersMoreThanOneSkill = 0.5
probabilityTasksMoreThanOneSkill = 0.5
useRealisticGeoCoordinates = False


def calcLateralPosition(inputPosition):
    if useRealisticGeoCoordinates:
        return 51.5 + inputPosition / 100.0
    return inputPosition


def calcLongitudinalPosition(inputPosition):
    if useRealisticGeoCoordinates:
        return 10 + inputPosition / 100.0
    return inputPosition


decimal.getcontext().prec = 4;
for entry in instanceSets:
    folder = "/Users/luismasuchibanez/Desktop/Hiwi/Katharina/Instanzen/" + entry
    for filepath in os.listdir(folder):
        with open(folder + "/" + filepath, 'r') as original:
            data = original.read()

        lines = data.split('\n')

        # TODO provisorisch, speichert nicht alle Informationen!!
        instance = {}
        if useRealisticGeoCoordinates:
            instance['instance'] = []
            instance['instance'].append({'instanceId': filepath[:-4],
                                         'mode': 'operational'})

        instance['numberOfSkills'] = numberOfSkills
        instance['numberOfLevels'] = numberOfLevels
        instance['workers'] = []
        instance['tasks'] = []

        # basic data
        line = lines[0].split()
        number_nodes = int(line[2])
        number_workers = int(line[1])

        # workers
        line = lines[2].split()
        lateralPosition = calcLateralPosition(float(line[1]))
        longitudinalPosition = calcLongitudinalPosition(float(line[2]))
        openingTime = float(line[-2])  # second to last entry
        closingTime = float(line[-1])  # last entry
        if useRealisticGeoCoordinates:
            closingTimeFactor = 8.0000 / closingTime  # Normierung auf 8 Stunden Arbeitstage
        else:
            closingTimeFactor = 1

        for i in range(0, number_workers):
            hasSkill = random.random() * 100 < percentageWorkersHaveSkills
            skills = []
            if hasSkill:
                numberSkills = 0
                for s in range(numberOfSkills):
                    if random.random() < probabilityWorkersMoreThanOneSkill:
                        numberSkills += 1
                        skills.append({
                        'id': str(s),
                        'level': int(random.randint(0, numberOfLevels - 1))
                        })
                if numberSkills == 0:
                    skills.append({
                    'id': str(random.randint(0, numberOfSkills - 1)),
                    'level': int(random.randint(0, numberOfLevels - 1))
                    })

            instance['workers'].append({'workerId': str(i),
                                        'velocity': float(1),
                                        'lateralPosition': lateralPosition,
                                        'longitudinalPosition': longitudinalPosition,
                                        'dateTimeWindows': [{
                                            'openingTime': openingTime * closingTimeFactor,
                                            'closingTime': closingTime * closingTimeFactor,
                                            'day': 0
                                        }],
                                        'skills': skills
                                        })

        # iterate over customer nodes
        for i in range(0, number_nodes):
            line = lines[3 + i].split()
            extId = str(line[0])  # id
            lateralPosition = calcLateralPosition(float(line[1]))  # x
            longitudinalPosition = calcLongitudinalPosition(float(line[2]))  # y
            serviceDuration = float(line[3])  # service time
            priority = float(line[4])  # profit
            openingTime = float(line[-2])  # openingTime for start of service
            closingTime = float(line[-1]) + serviceDuration  # last entry   # closingTime for end of service
            if useRealisticGeoCoordinates:
                serviceDuration = serviceDuration * closingTimeFactor * 4
            hasSkill = random.random() * 100 < percentageTasksHaveSkills
            skills = []
            if hasSkill:
                numberSkills = 0
                for s in range(numberOfSkills):
                    if random.random() < probabilityTasksMoreThanOneSkill:
                        skills.append({
                        'id': str(s),
                        'level': int(random.randint(0, numberOfLevels - 1)),
                        'requiredWorkers': int(random.randint(1, number_workers)) #war zuvor auf 1 gesetzt TODO: normieren bzw. Wahrscheinlichkeit viele benötigt je nach Anzahl Worker anpassen?
                        })
                if numberSkills == 0:
                    skills.append({
                        'id': str(random.randint(0, numberOfSkills - 1)),
                        'level': int(random.randint(0, numberOfLevels - 1)),
                        'requiredWorkers': int(random.randint(1, number_workers))  # war zuvor auf 1 gesetzt
                    })
            instance['tasks'].append({'extId': extId,
                                      'lateralPosition': lateralPosition,
                                      'longitudinalPosition': longitudinalPosition,
                                      'serviceDuration': serviceDuration,
                                      'priority': priority,
                                      'dateTimeWindows': [{
                                          'openingTime': openingTime * closingTimeFactor,
                                          'closingTime': closingTime * closingTimeFactor,
                                          'day': 0
                                      }],
                                      'requiredSkills': skills
                                      })

        print(instance)

        path = "_"

        if percentageTasksHaveSkills > 0:
            path += "skills_{}_{}_".format(percentageTasksHaveSkills, percentageWorkersHaveSkills)
        if useRealisticGeoCoordinates:
            path += "realisticGeoCodes_"
        path += "yaml_"
        Path(folder + path).mkdir(parents=True, exist_ok=True)
        #TODO: Zielordner anpassen
        fstream = open(folder + path + filepath[:-4] + '.yaml', 'w')
        yaml.dump(instance, fstream)
        fstream.close()