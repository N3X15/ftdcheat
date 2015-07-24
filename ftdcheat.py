'''
FTDCheat - An automated part unlocker for the game From The Depths

Copyright (c) 2015 Rob Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import os
import sys
import argparse
import shutil

import json

# Persistent Instance Storage template.
# This is how the game stores each mission (+ global headers etc)
PIS_Template = '''
    {
      "Header": {
        "Id": {
          "Id": 695751387
        },
        "Type": 1
      },
      "PriorPerformance": {
        "Completed": false,
        "FastestTime": -1.0,
        "CheapestRun": -1.0,
        "HighestScore": -1.0,
        "Playthroughs": 1
      },
      "PlayerSetup": {
        "ResourcesBought": {
          "Natural": 0.0,
          "Metal": 0.0,
          "Oil": 0.0,
          "Scrap": 0.0,
          "Crystal": 0.0
        },
        "SpawnPointSelection": {
          "Id": 295410601
        }
      },
      "ForceUsageList": [
        {
          "ForceId": {
            "Id": 1236659043
          },
          "FilePath": "",
          "Name": "Javelin",
          "Usage": 0
        },
        {
          "ForceId": {
            "Id": 1284083736
          },
          "FilePath": null,
          "Name": "Ocelot",
          "Usage": 0
        },
        {
          "ForceId": {
            "Id": 1955795313
          },
          "FilePath": null,
          "Name": "Duster",
          "Usage": 0
        },
        {
          "ForceId": {
            "Id": 833204278
          },
          "FilePath": null,
          "Name": "Duster",
          "Usage": 0
        }
      ]
    }
'''


def getMyDocuments():
  import ctypes.wintypes
  CSIDL_PERSONAL = 5       # My Documents
  SHGFP_TYPE_CURRENT = 1   # Get current, not default value

  buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
  ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
  return buf.value

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-p', '--planet', dest='planet', default='Neter', help='Planet to load')
  parser.add_argument('player', help='Name of the player to hack')
  parser.add_argument('ftdhome', help='Location of From The Depths')

  opts = parser.parse_args()

  planetID = ''
  planetPath = os.path.join(opts.ftdhome, 'From_The_Depths_Data', 'StreamingAssets', 'Worlds', opts.planet)
  pispath = os.path.join(getMyDocuments(), 'From The Depths', 'Player Profiles', opts.player, 'Planet Instance Config')
  print('planet path: {}'.format(planetPath))
  print('PIS path: {}'.format(pispath))

  with open(planetPath + '.planet', 'r') as f:
    data = json.load(f)
    planetID = data['PlanetIdentifier']  # UUID
    print('Planet {0} maps to {1}'.format(opts.planet, planetID))

  pispath = os.path.join(pispath, '{}.persistence'.format(planetID))

  # This is a big fucking file.
  missions = {}
  with open(planetPath + '.mission', 'r') as f:
    data = json.load(f)
    '''
          "Instances": [
            {
              "Header": {
                "Id": {
                  "Id": 695751387
                },
                "Type": 1,
                "Name": "Blockade Run",
                "Summary": "Adjutant.. it's time you had your first taste of operations. Our hunter killer fleet left an Onxy Watch fleet crippled yesterday. I need you to break through their blockade and reach the remains of the fleet. A successful salvage haul on this mission might see you with your own command one day.",
                "DescriptionParagraphs": [
                  {
                    "Header": "Break through the line",
                    "Paragraph": "Build the fastest ship you can and break through their line. We're sending two Dusters to provide air support. You'll be an embarressment to me if you die "
                  },
                  {
                    "Header": "Capture the Ocelot salvage ship.",
                    "Paragraph": "Once through the line you'll need to find the 'Ocelot' salvage ship. It ran out of fuel on the way back from the strike and we believe it is still out there, undetected. Capture it to win the mission. "
                  }
                ],
                "MissionHeader": {
                  "MissionIndex": 1,
                  "FactionId": {
                    "Id": 993971311
                  },
                  "ParTime": 60.0,
                  "HasBeenSetup": false
                },

            /Instances[0]/Header/MissionHeader/MissionIndex
            /Instances[0]/Header/MissionHeader/FactionId

            Unfortunately, we have to load the entire goddamn mission into memory, since we have to fake persistence for it.
        '''
    for mission in data['Instances']:
      missionIdx = mission['Header']['MissionHeader']['MissionIndex']
      missionFaction = mission['Header']['MissionHeader']['FactionId']['Id']
      missionID = '{}:{}'.format(missionFaction,missionIdx)
      missions[missionID] = mission

  unlocks = []
  newInstances = {}
  with open(planetPath + '.world', 'r') as f:
    data = json.load(f)
    for unlock in data['Unlocks']['Unlocks']:  # C# typemapping is bogus, but whatever.
      '''
        {
          "Name": "Complete Deep Water Guard mission one",
          "PreCompletionDescription": "Breaking through and making your escape in operation \"Blockade Run\" will hopefully open the admiralties eyes to the benefits of the larger propeller technology",
          "PostCompletionDescription": "Your performance in Operation \"Blockade Run\" has persuaded the admiralty to invest in larger propeller technology",
          "UnlockNotes": "Unlock the huge propeller component for sea vehicles!",
          "CheckType": 1,
          "FirstArgument": 1.0,
          "FirstObjectId": {
            "Id": 993971311
          },
          "Targets": [
            {
              "Name": "The huge propeller",
              "TargetType": 0,
              "FirstArguement": 0,
              "FirstString": "9710b923-9e8c-4762-aa74-bffefb263a7e"
            }
          ]
        }
      Out of this, we want to generate a fake completed mission.
      '''
      # Check that this is a mission-based unlock.
      if unlock['CheckType'] != 1:
        continue

      # This is some stupid, obfuscated bullshit, but whatever.
      factionID = unlock['FirstObjectId']['Id']
      missionIdx = int(unlock['FirstArgument'])  # Truncate to int.
      missionKey = '{}:{}'.format(factionID, missionIdx)
      mission = missions[missionKey]

      # Populate template
      instance = json.loads(PIS_Template)
      # Find the player's faction
      factionData = {}
      for fac in mission['Factions']['Factions']:
        if fac['Id']['Id'] == factionID:
          factionData = fac
          break
      # ID must be the same as the mission attempted
      instance['Header']['Id']['Id'] = mission['Header']['Id']['Id']
      instance['PlayerSetup']['SpawnPointSelection']['Id'] = factionData['Players']['SpawnPoints'][0]['Id']['Id']
      print(repr(instance.keys()))
      instance['PriorPerformance']['Completed'] = True  # The important part!
      instance['PriorPerformance']['Playthroughs'] = 1  # Just to be sure
      # Load forces
      instance['ForceUsageList'] = []
      for fleet in factionData['Fleets']['Fleets']:
        for force in fleet['Forces']:
          '''
              {
                "ForceId": {
                  "Id": 1236659043
                },
                "FilePath": "",
                "Name": "Javelin",
                "Usage": 0
              }
          '''
          iforce = {}
          iforce['ForceId'] = {'Id': force['Id']['Id']}
          iforce['FilePath'] = None  # Sometimes also ''? (Javelin)
          iforce['Name'] = force['Name']
          iforce['Usage'] = 0  # honk
          instance['ForceUsageList'].append(iforce)
      newInstances[instance['Header']['Id']['Id']] = instance

  InstanceStorage = {'PersistentInfoStore': []}
  foundInstance = {}
  if os.path.isfile(pispath):
    print('Opening PIS for read: {}...'.format(pispath))
    with open(pispath, 'r') as f:
      for instance in json.load(f)['PersistentInfoStore']:
        iid = instance['Header']['Id']['Id']
        if iid in newInstances:
          if instance['PriorPerformance']['Completed']:
            InstanceStorage['PersistentInfoStore'].append(instance)
            del newInstances[iid]
          else:
            print('Dumping mission instance {}: marked as incomplete'.format(iid))
            continue
      print('  Loaded {} instances.'.format(len(InstanceStorage['PersistentInfoStore'])))
    if os.path.isfile(pispath + '.BACKUP'):
      os.remove(pispath + '.BACKUP')
    shutil.copy(pispath, pispath + '.BACKUP')
  else:
    print('{} does not have PIS for this player, skipping load.'.format(opts.planet))

  for instance in newInstances.values():
    InstanceStorage['PersistentInfoStore'].append(instance)

  print('Adding {} new instances to {}'.format(len(InstanceStorage['PersistentInfoStore']), pispath))
  with open(pispath,'w') as f:
      json.dump(InstanceStorage, f, indent=2)
