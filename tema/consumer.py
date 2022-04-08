"""
This module represents the Consumer.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

from threading import Thread
import time


class Consumer(Thread):
    """
    Class that represents a consumer.
    """

    def __init__(self, carts, marketplace, retry_wait_time, **kwargs):
        """
        Constructor.

        :type carts: List
        :param carts: a list of add and remove operations

        :type marketplace: Marketplace
        :param marketplace: a reference to the marketplace

        :type retry_wait_time: Time
        :param retry_wait_time: the number of seconds that a producer must wait
        until the Marketplace becomes available

        :type kwargs:
        :param kwargs: other arguments that are passed to the Thread's __init__()
        """
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

        self.name = kwargs["name"]
        self.kwargs = kwargs
        Thread.__init__(self, **kwargs)

    def run(self):
        for cart in self.carts:
            cart_id = self.marketplace.new_cart()

            for elements in cart:
                quantity = 0
                while quantity < elements["quantity"]:
                    if elements["type"] == "remove":
                        self.marketplace.remove_from_cart(cart_id, elements["product"])
                        quantity += 1
                        continue

                    if elements["type"] == "add":
                        if self.marketplace.add_to_cart(cart_id, elements["product"]):
                            quantity += 1
                            continue
                        time.sleep(self.retry_wait_time)

            products_acquired = self.marketplace.place_order(cart_id)

            for item in products_acquired:
                print(f"{self.name} bought {item}")
