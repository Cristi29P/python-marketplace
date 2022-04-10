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
        Thread.__init__(self, **kwargs)
        self.carts = carts
        self.marketplace = marketplace
        self.retry_wait_time = retry_wait_time

    def run(self):
        for cart in self.carts:
            # For each cart get a new id
            cart_id = self.marketplace.new_cart()
            for elements in cart:
                # For each product try to add or remove it from the cart
                quantity_so_far = 0
                while quantity_so_far < elements["quantity"]:
                    if elements["type"] == "remove":
                        self.marketplace.remove_from_cart(cart_id, elements["product"])
                        quantity_so_far += 1
                        continue

                    if elements["type"] == "add":
                        if self.marketplace.add_to_cart(cart_id, elements["product"]):
                            quantity_so_far += 1
                            continue
                        # Sleep if failed to add and retry next iteration
                        time.sleep(self.retry_wait_time)
            # Order the products
            self.marketplace.place_order(cart_id)
