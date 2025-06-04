from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List

class ElevatorState(Enum):
  UP = auto()
  DOWN = auto()
  IDLE = auto()


# Associate zone with each floor
# Top bottom middle zoning: Top 25%, Middle 50% and Bottom 25%
# Odd even zoning: Based on odd/even floor numbers
def getZoneForFloor(floor: int, total_floors: int = 200, strategy: str = "TOP_MIDDLE_BOTTOM"):
  if strategy == "TOP_MIDDLE_BOTTOM":
    if floor > total_floors * 0.75:
      return "TOP"
    elif floor <= total_floors * 0.25:
      return "BOTTOM"
    else:
      return "MIDDLE"
  elif strategy == "ODD_EVEN":
    return "ODD" if floor % 2 == 1 else "EVEN"
  else:
    return "DEFAULT"
  

# Door class
class Door:
  def __init__(self):
    self.is_open = False

  def open(self):
    self.is_open = True
    print("Door opened")

  def close(self):
    self.is_open = False
    print("Door closed")


# Button panel to choose the floors
class ButtonPanel:
  def __init__(self, floor: int):
    self.floor = floor
  
  def pressButton(self):
    print(f"Button for floor {self.floor} pressed")


class Floor:
  def __init__(self, number: int):
    self.number = number
    self.button_panel = ButtonPanel(number)
  
  def callElevator(self, direction: ElevatorState):
    print(f"Elevator called at floor {self.number} to go {direction.name}")



# Elevator car: controls the door and movement
class ElevatorCar:
  def __init__(self, id: int, max_load: int, max_speed: float, capacity: int, zone: str):
    self.id = id
    self.current_floor = 0
    self.max_load = max_load
    self.max_speed = max_speed
    self.capacity = capacity
    self.state = ElevatorState.IDLE
    self.door = Door()
    self.zone = zone
    self.requests = []
  
  def moveTo(self, floor: int):
    print(f"Elevator {self.id} moving from floor {self.current_floor} to {floor}")
    self.state = ElevatorState.UP if floor > self.current_floor else ElevatorState.DOWN
    self.current_floor = floor
    self.state = ElevatorState.IDLE
    self.openDoor()
  
  def openDoor(self):
    self.door.open()
  
  def closeDoor(self):
    self.door.close()
  
  def emergencyStop(self):
    print(f"Elevator {self.id} emergency stop!")
    self.state = ElevatorState.IDLE
  
  def zoneMatches(self, floor: int, total_floors: int = 200, strategy: str = "TOP_MIDDLE_BOTTOM"):
    request_zone = getZoneForFloor(floor, total_floors, strategy)
    return self.zone == request_zone


# Request and scheduling using strategy pattern
class Request:
  def __init__(self, floor: int, direction: ElevatorState):
    self.floor = floor
    self.direction = direction

class SchedulingAlgorithm(ABC):
  @abstractmethod
  def schedule(self, request: Request, elevators: List[ElevatorCar]):
    pass

# FCFS: Choose first ide elevator
class FCFSAlgorithm(SchedulingAlgorithm):
  def schedule(self, request: Request, elevators: List[ElevatorCar]):
    for elevator in elevators:
      if elevator.state == ElevatorState.IDLE and elevator.zoneMatches(request.floor):
        return elevator
    return None

# SSTF: Shortest seek time first
# Selects idle elevator with minimum distance to the request floor
class SSTFAlgorithm(SchedulingAlgorithm):
  def schedule(self, request: Request, elevators: List[ElevatorCar]):
    eligible_elevators = [e for e in elevators if e.state == ElevatorState.IDLE and e.zoneMatches(request.floor)]
    if not eligible_elevators:
      return None
    return min(eligible_elevators, key = lambda e: abs(e.current_floor - request.floor))

# Elevator moves in one direction fulfilling all requests
# Then reverses the direction when no further requests exist
class SCANAlgorithm(SchedulingAlgorithm):
  def schedule(self, request: Request, elevators: List[ElevatorCar]):
    eligible_elevators = []
    for elevator in elevators:
      if elevator.zoneMatches(request.floor):
        if (elevator.state == ElevatorState.IDLE or (elevator.state == request.direction and (
          (request.direction == ElevatorState.UP and elevator.current_floor <= request.floor) or 
          (request.direction == ElevatorState.DOWN and elevator.current_floor >= request.floor)
        ))):
          eligible_elevators.append(elevator)
    if not eligible_elevators:
      return None
    return min(eligible_elevators, key = lambda e: abs(e.current_floor - request.floor))
  

# Dispatcher: coordinates between floor requests and available elevators
class Dispatcher:
  def __init__(self, elevators: List[ElevatorCar], scheduling_algorithm: SchedulingAlgorithm):
    self.elevators = elevators
    self.scheduling_algorithm = scheduling_algorithm
    self.request_queue: List[Request] = []
  
  def addRequest(self, request: Request):
    print(f"Dispatcher received request at floor {request.floor} going to {request.direction.name}")
    self.request_queue.append(request)
    self.dispatch()
  
  def dispatch(self):
    while self.request_queue:
      request = self.request_queue.pop(0)
      elevator: ElevatorCar = self.scheduling_algorithm.schedule(request, self.elevators)
      if elevator:
        print(f"Dispatching elevator {elevator.id} to floor {request.floor}")
        elevator.moveTo(request.floor)
      else:
        print("No available elevator, re-queueing request")
        self.request_queue.append(request)
        break


# Elevator system class
class ElevatorSystem:
  def __init__(self, total_floors: int = 200, num_elevators: int = 50, scheduling_algorithm: SchedulingAlgorithm = None):
    self.total_floors = total_floors
    self.floors = [Floor(i) for i in range(1, total_floors + 1)]
    self.elevators: List[ElevatorCar] = self.createElevators(num_elevators)
    if scheduling_algorithm is None:
      scheduling_algorithm = FCFSAlgorithm()
    self.dispatcher = Dispatcher(self.elevators, scheduling_algorithm)
  
  def createElevators(self, num_elevators: int):
    elevators = []
    for i in range(num_elevators):
      if i < num_elevators * 0.25:
        zone = "BOTTOM"
      elif i < num_elevators * 0.75:
        zone = "MIDDLE"
      else:
        zone = "TOP"
      elevator = ElevatorCar(id = i, max_load = 1000, max_speed = 10.0, capacity = 10, zone = zone)
      elevators.append(elevator)

    return elevators

  def callElevator(self, floor: int, direction: ElevatorState):
    request = Request(floor, direction)
    self.dispatcher.addRequest(request)
  
  def emergencyAlarm(self, elevator_id: int):
    for elevator in self.elevators:
      if elevator.id == elevator_id:
        elevator.emergencyStop()
  
  def monitorSystem(self):
    print("System monitoring")
    for elevator in self.elevators:
      print(f"Elevator {elevator.id}: Floor {elevator.current_floor}, State {elevator.state.name}, Zone {elevator.zone}")


if __name__ == "__main__":
  system = ElevatorSystem(total_floors = 200, num_elevators = 50, scheduling_algorithm = FCFSAlgorithm())
  system.callElevator(10, ElevatorState.UP)
  system.emergencyAlarm(1)
  system.monitorSystem()