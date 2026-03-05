# Climate reaction

## Template for a project
This project, will simulate a how climate change, and a natural disaster can affect a city with some people. It will simulate how people react to rising water levels, and how they will get to safety.


## Getting Started

This repository provides the scaffolding for a simulated city research workshop.
The current example focuses on a flood scenario where rising sea levels affect
people walking along the coast of Køge.

Run the automated tests to verify the library is functioning:

```bash
py -m pytest
```

Configuration is stored in `config.yaml`; see `docs/config.md` for details,
including the optional `flood:` section used by the workshop notebooks.

### Step 1: Define Your Simulation (Before Any Code)

Use this template to describe your project. Think about these four components and the messages they send between each other:

### My Smart City Project: [City flooded]

#### 1. The Trigger (Who/What is moving?)
There is 20 people walking in the coastal area of Køge. They walk along the beach road and some of the 20 people are walking in Køge city itself.The weather is sunny, but the sea is acting abnormal. Due to climate change, the water is rising and there is a chance that the sea will flood the inner city of køge.
*Example: A person is walking along the beach and is observing the weird and sudden rise in levels of the sea.*

#### 2. The Observer (What does the city see?)
What **Sensor** picks up the information? 
A weather station, with sensors, can pick up the sudden change in water level, which indicates a flood is coming, in advance. They can notify people in good time and the people walking along the beach will also notify the sudden change at sea.
*Example: A sensor in Køge bay can detect difference water levels rising and the power of the flood.

#### 3. The Control Center (The Logic)
The weather station, pick up the data and information given by the sensor, and thereafter proces the data. If the water level rises to 1 meter or higher, then they will send out a warning signal to the people near Køge on their phones.
*Example: If the water level rises to 1 meter or higher then the metoerologists will send out warning signals to peoples phone, to get away from the beach and towards the inner city of Køge.*

#### 4. The Response (What happens next?)
What follows is the people around the beach, who get the warning signal, will make the choice to go towards the inner city, which is higher elevated above the sea than, the beach.
*Example: the vibration of their phones telling them to get away quickly, and proceed towards the inner city or further inland, will make the people choose to go  further inland*
