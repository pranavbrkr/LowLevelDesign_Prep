from abc import ABC, abstractmethod
from enum import Enum
from typing import List

class Coin(Enum):
  FIVE = 5.0
  TWO = 2.0
  ONE = 1.0
  HALF = 0.5
  QUARTER = 0.25

class PaymentType(Enum):
  COIN = "COIN"
  CARD = "CARD"

# Models
class Product:
  def __init__(self, code: str, name: str, price: float, quantity: int):
    self.code = code
    self.name = name
    self.price = price
    self.quantity = quantity
  
  def isAvailable(self):
    return self.quantity > 0
  
  def dispense(self):
    if self.quantity == 0:
      raise Exception(f"{self.name} is out of stock")
    self.quantity -= 1

class TransactionSession:
  def __init__(self, product: Product, payment_type: PaymentType):
    self.product = product
    self.payment_type = payment_type
    self.amount_paid = 0.0

  def addPayment(self, amount: float):
    self.amount_paid += amount
  
  def isFullyPaid(self):
    return self.amount_paid >= self.product.price

  def getChangeAmount(self):
    return round(self.amount_paid - self.product.price, 2)


# Payment handlers
class PaymentHandler(ABC):
  @abstractmethod
  def pay(self):
    pass

class CoinPaymentHandler(PaymentHandler):
  def pay(self, session: TransactionSession, coins: List[Coin]):
    total = sum(coin.value for coin in coins)
    session.addPayment(total)
    return total

class CardPaymentHandler(PaymentHandler):
  def pay(self, session: TransactionSession, card_number: str):
    session.addPayment(session.product.price)
    return session.product.price
  

class ChangeCalculator:
  @staticmethod
  def calculateChange(change_amount: float):
    result = []
    for coin in sorted(Coin, key = lambda c: -c.value):
      while change_amount >= coin.value:
        result.append(coin)
        change_amount = round(change_amount - coin.value, 2)
    return result
  

# Vending state interface
class VendingState(ABC):
  @abstractmethod
  def selectProduct(self, machine, product_code, payment_type):
    pass
  
  @abstractmethod
  def insertCoins(self, machine, coins):
    pass
  
  @abstractmethod
  def insertCard(self, machine, card_number):
    pass
  
  @abstractmethod
  def cancel(self, machine):
    pass
  
  @abstractmethod
  def dispense(self, machine):
    pass


# Concrete states
class IdleState(VendingState):
  def selectProduct(self, machine, product_code, payment_type):
    if product_code not in machine.inventory:
      raise Exception("Invalid product code")
    product = machine.inventory[product_code]
    if not product.isAvailable():
      raise Exception("Product out of stock")
    machine.session = TransactionSession(product, payment_type)
    machine.state = HasProductState()
    return product

  def insertCoins(self, machine, coins):
    raise Exception("Select product first")

  def insertCard(self, machine, card_number):
    raise Exception("Select product first")
  
  def cancel(self, machine):
    raise Exception("Nothing to cancel")
  
  def dispense(self, machine):
    raise Exception("Payment not complete")


class HasProductState(VendingState):
  def selectProduct(self, machine, product_code, payment_type):
    raise Exception("Product already selected")
  
  def insertCoins(self, machine, coins):
    if machine.session.payment_type != PaymentType.COIN:
      raise Exception("Card payment selected")
    CoinPaymentHandler().pay(machine.session, coins)
    if machine.session.isFullyPaid():
      machine.state = PaidState()
  
  def insertCard(self, machine, card_number):
    if machine.session.payment_type != PaymentType.CARD:
      raise Exception("Coin payment selected")
    CardPaymentHandler().pay(machine.session, card_number)
    machine.state = PaidState()
  
  def cancel(self, machine):
    refund = machine.session.amount_paid
    machine.session = None
    machine.state = IdleState()
    return refund
  
  def dispense(self, machine):
    raise Exception("Payment not complete")



class PaidState(VendingState):
  def selectProduct(self, machine, product_code, payment_type):
    raise Exception("Already paid")
  
  def insertCoins(self, machine, coins):
    raise Exception("Already paid")
  
  def insertCard(self, machine, card_number):
    raise Exception("Already paid")
  
  def cancel(self, machine):
    refund = machine.session.amount_paid
    machine.session = None
    machine.state = IdleState()
    return refund
  
  def dispense(self, machine):
    machine.session.product.dispense()
    change_amount = machine.session.getChangeAmount()
    change = ChangeCalculator.calculateChange(change_amount)
    machine.session = None
    machine.state = IdleState()
    return change



# Vending machine
class VendingMachine:
  def __init__(self):
    self.inventory = {
      "A1": Product("A1", "Water", 1.0, 10),
      "A2": Product("A2", "Soda", 2.5, 8),
      "A3": Product("A3", "Chips", 2.0, 5),
      "A4": Product("A4", "Candy Bar", 1.25, 7),
    }
    self.session = None
    self.state: VendingState = IdleState()
  
  def selectProduct(self, code, payment_method):
    return self.state.selectProduct(self, code, payment_method)
  
  def insertCoins(self, coins):
    return self.state.insertCoins(self, coins)
  
  def insertCard(self, card_number):
    return self.state.insertCard(self, card_number)
  
  def cancel(self):
    return self.state.cancel(self)
  
  def dispense(self):
    return self.state.dispense(self)
  

if __name__ == "__main__":
  vm = VendingMachine()

  print("User selects Soda(A2) and pays with coins")
  product = vm.selectProduct("A2", PaymentType.COIN)
  print(f"Selected product: {product.name}, price: ${product.price:.2f}")

  coins_used = [Coin.TWO, Coin.FIVE]
  vm.insertCoins(coins_used)
  inserted_total = sum(coin.value for coin in coins_used)
  print(f"Inserted coins: ${inserted_total:.2f}")

  change = vm.dispense()
  print("Product dispensed. Change returned: ", [f"${c.value:.2f}" for c in change])

  print("**********************")

  print("User selects Candy Bar(A4) and pays with card")
  product = vm.selectProduct("A4", PaymentType.CARD)
  print(f"Selected product: {product.name}, price: ${product.price:.2f}")

  vm.insertCard("1234-5478-9012-3456")
  print("Card payment processed")

  change = vm.dispense()
  print("Product dispensed. Change returned: ", [f"${c.value:.2f}" for c in change])

  print("**********************")

  print("User selects Chips(A4) and cancels before payment")
  product = vm.selectProduct("A3", PaymentType.COIN)
  print(f"Selected product: {product.name}, price: ${product.price:.2f}")

  refund = vm.cancel()
  print(f"Transaction cancelled. Refund: ${refund:.2f}")

  print("**********************")
  
  print("Attempt to dispense without payment")
  try:
    vm.dispense()
  except Exception as e:
    print(f"Expected error: {e}")