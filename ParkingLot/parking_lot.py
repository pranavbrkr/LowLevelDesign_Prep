from datetime import datetime
from enum import Enum
from abc import ABC
from typing import List

class VehicleType(Enum):
  MOTORBIKE = "MOTORBIKE"
  CAR = "CAR"
  TRUCK = "TRUCK"


# Vehicle class
class Vehicle:
  def __init__(self, license_plate: str, vehicle_type: VehicleType):
    self.license_plate = license_plate
    self.vehicle_type = vehicle_type


# Parking Spot
class ParkingSpot:
  def __init__(self, spot_id: int, spot_type: VehicleType):
    self.spot_id = spot_id
    self.spot_type = spot_type
    self.occupied = False
  
  def isAvailable(self, vehicle_type: VehicleType):
    if not self.occupied and self.spot_type == vehicle_type:
      return True
    else:
      return False
  
  def occupy(self):
    self.occupied = True

  def vacate(self):
    self.occupied = False


# Parking level which contains list of parking spots
class ParkingLevel:
  def __init__(self, level_number: int, spots: List[ParkingSpot]):
    self.level_number = level_number
    self.spots = spots
  
  def getAvailableSpot(self, vehicle_type: VehicleType):
    for spot in self.spots:
      if spot.isAvailable(vehicle_type):
        return spot
    return None
  

# Parking lot which will contain list of levels
class ParkingLot:
  def __init__(self, levels: List[ParkingLevel]):
    self.levels = levels
  
  def getAvailableSpot(self, vehicle_type: VehicleType):
    for level in self.levels:
      spot = level.getAvailableSpot(vehicle_type)
      if spot:
        return level, spot
    
    return None



# Ticket class which will contain just vehicle, parking and time details
class Ticket:
  def __init__(self, vehicle: Vehicle, level: ParkingLevel, spot: ParkingSpot):
    self.vehicle = vehicle
    self.level = level
    self.spot = spot
    self.in_time = datetime.now()
    self.out_time = None
  
  def closeTicket(self):
    self.out_time = datetime.now()



# Ticket factory class to create ticket
class TicketFactory:
  @staticmethod
  def createTicket(vehicle: Vehicle, level: ParkingLevel, spot: ParkingSpot):
    return Ticket(vehicle, level, spot)


# Parking spot manager class manages the parking spot occupancy and vacating
class ParkingSpotManager:
  def __init__(self, parking_lot: ParkingLot):
    self.parking_lot = parking_lot
  
  def findAvailableSpot(self, vehicle_type: VehicleType):
    return self.parking_lot.getAvailableSpot(vehicle_type)
  
  def occupySpot(self, spot: ParkingSpot):
    spot.occupy()
  
  def vacateSpot(self, spot: ParkingSpot):
    spot.vacate()


# Ticket manager class: manages tickets
class TicketManager:
  def __init__(self):
    self.tickets = {}
  
  def issueTicket(self, vehicle: Vehicle, level: ParkingLevel, spot: ParkingSpot):
    ticket = TicketFactory.createTicket(vehicle, level, spot)
    self.tickets[vehicle.license_plate] = ticket
    return ticket

  def closeTicket(self, vehicle: Vehicle):
    ticket: Ticket = self.tickets.pop(vehicle.license_plate, None)
    if ticket:
      ticket.closeTicket()
    return ticket



# Pricing strategies
class PricingStrategy(ABC):
  def calculatePrice(self, ticket: Ticket):
    pass

class FlatPricingStrategy(PricingStrategy):
  def calculatePrice(self, ticket: Ticket):
    return 50

class HourlyRatePricing(PricingStrategy):
  def calculatePrice(self, ticket: Ticket):
    duration = (ticket.in_time - ticket.out_time).seconds // 3600 + 1
    return duration * 20


class PriceCalculator:
  def __init__(self, strategy: PricingStrategy):
    self.strategy = strategy
  
  def calculatePrice(self, ticket: Ticket):
    return self.strategy.calculatePrice(ticket)


# Payment Strategy
class PaymentStrategy(ABC):
  def pay(self, amount: float):
    pass

class CardPayment(PaymentStrategy):
  def pay(self, amount: float):
    print(f"Card payment of ${amount} completed")

class CashPayment(PaymentStrategy):
  def pay(self, amount: float):
    print(f"Cash payment of ${amount} completed")


# Payment manager class manages all the payment related stuff
class PaymentManager:
  def __init__(self, payment_strategy: PaymentStrategy, pricing_strategy: PricingStrategy):
    self.payment_strategy = payment_strategy
    self.pricing_strategy = pricing_strategy
  
  def calculateAmount(self, ticket: Ticket):
    calculator = PriceCalculator(self.pricing_strategy)
    return calculator.calculatePrice(ticket)

  def pay(self, amount: float):
    self.payment_strategy.pay(amount)
  
  def performPayment(self, ticket: Ticket):
    amount = self.calculateAmount(ticket)
    self.pay(amount)


# Parking lot service to orchestrate parking and unparking
class ParkingLotService:
  def __init__(self, parking_spot_manager: ParkingSpotManager, ticket_manager: TicketManager):
    self.parking_spot_manager = parking_spot_manager
    self.ticket_manager = ticket_manager
  
  def parkVehicle(self, vehicle: Vehicle):
    result = self.parking_spot_manager.findAvailableSpot(vehicle.vehicle_type)
    if not result:
      print("No spot available")
    
    level, spot = result
    self.parking_spot_manager.occupySpot(spot)
    ticket = self.ticket_manager.issueTicket(vehicle, level, spot)

    print(f"Spot {spot.spot_id} - Level {level.level_number} assigned to Vehicle {vehicle.license_plate}")
  

  def unparkVehicle(self, vehicle: Vehicle):
    ticket = self.ticket_manager.closeTicket(vehicle)
    if not ticket:
      print("No active ticket found")
      return
    
    self.parking_spot_manager.vacateSpot(ticket.spot)
    payment_manager = PaymentManager(CardPayment(), HourlyRatePricing())
    payment_manager.performPayment(ticket)



if __name__ == "__main__":
  level0_spots = [ParkingSpot(f"0-{i}", VehicleType.TRUCK) for i in range(30)]
  level1_spots = [ParkingSpot(f"1-{i}", VehicleType.CAR) for i in range(30)]
  level0 = ParkingLevel(0, level0_spots)
  level1 = ParkingLevel(1, level1_spots)

  parking_lot = ParkingLot([level0, level1])
  parking_spot_manager = ParkingSpotManager(parking_lot)
  ticket_manager = TicketManager()
  parking_lot_service = ParkingLotService(parking_spot_manager, ticket_manager)
  vehicle1 = Vehicle("ABC123", VehicleType.CAR)
  vehicle2 = Vehicle("XZY789", VehicleType.TRUCK)

  parking_lot_service.parkVehicle(vehicle1)
  parking_lot_service.parkVehicle(vehicle2)

  import time
  time.sleep(5)

  parking_lot_service.unparkVehicle(vehicle2)