"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
import logging
import time
import unittest
from threading import Lock, current_thread
from logging.handlers import RotatingFileHandler


class TestMarketplace(unittest.TestCase):
    """
    Testing purposes class. It defines a unit test for each method.
    The reader should know that these methods are tested in a single threaded
    and sequential environment.
    """
    def setUp(self):
        """
        Create a dummy marketplace with a max_queue_size_per_producer of 3
        """
        self.marketplace = Marketplace(3)

    def test_register_producer(self):
        """
        Add each producer and check the expected returned id.
        """
        id0 = self.marketplace.register_producer()
        self.assertEqual(id0, 0, "Wrong id. Expected 0.")

        id1 = self.marketplace.register_producer()
        self.assertEqual(id1, 1, "Wrong id. Expected 1.")

        id2 = self.marketplace.register_producer()
        self.assertEqual(id2, 2, "Wrong id. Expected 2.")

        self.assertEqual(self.marketplace.number_of_producers, 3, "Wrong number of producers!")

    def test_publish(self):
        """
        Checks if the producer is allowed to publish 3 products at most
        """

        producer = self.marketplace.register_producer()
        self.assertTrue(self.marketplace.publish(producer, "branza"),
                        "Failed to publish first product!")
        self.assertTrue(self.marketplace.publish(producer, "oua"),
                        "Failed to publish second product!")
        self.assertTrue(self.marketplace.publish(producer, "lapte"),
                        "Failed to publish third product!")

        self.assertEqual(self.marketplace.products_avail[0], "branza", "Unavailable product")
        self.assertEqual(self.marketplace.products_avail[1], "oua", "Unavailable product")
        self.assertEqual(self.marketplace.products_avail[2], "lapte", "Unavailable product")

        self.assertEqual(self.marketplace.products["branza"], producer, "Wrong producer id")
        self.assertEqual(self.marketplace.products["oua"], producer, "Wrong producer id")
        self.assertEqual(self.marketplace.products["lapte"], producer, "Wrong producer id")

        self.assertIn("branza", self.marketplace.producers_queues[producer], "Not added!")
        self.assertIn("oua", self.marketplace.producers_queues[producer], "Not added!")
        self.assertIn("lapte", self.marketplace.producers_queues[producer], "Not added!")

        self.assertFalse(self.marketplace.publish(producer, "ceai"), "Not allowed!")
        self.assertNotIn("ceai", self.marketplace.producers_queues[producer], "Should not be here")
        self.assertNotIn("ceai", self.marketplace.products_avail, "Should not be included!")

    def test_new_cart(self):
        """
        Checks the if the id's issued are correct and carts are actually added.
        """

        id0 = self.marketplace.new_cart()
        id1 = self.marketplace.new_cart()
        id2 = self.marketplace.new_cart()

        self.assertEqual(id0, 0, "Wrong cart id! Expected 0.")
        self.assertEqual(id1, 1, "Wrong cart id! Expected 1.")
        self.assertEqual(id2, 2, "Wrong cart id! Expected 2.")

        self.assertEqual(self.marketplace.number_of_carts, 3, "Wrong number of carts. Expected 3.")
        # Check if empty carts were created
        self.assertEqual(0, len(self.marketplace.carts[0]), "No cart was added!")
        self.assertEqual(0, len(self.marketplace.carts[1]), "No cart was added!")
        self.assertEqual(0, len(self.marketplace.carts[2]), "No cart was added!")

    def test_add_to_cart(self):
        """
        Check if products are correctly added to carts
        """
        producer = self.marketplace.register_producer()
        id0 = self.marketplace.new_cart()
        self.marketplace.publish(producer, "oua")

        self.assertTrue(self.marketplace.add_to_cart(id0, "oua"), "Failed to add existent product!")
        self.assertIn("oua", self.marketplace.carts[id0], "Product should have been inside!")
        self.assertFalse(self.marketplace.add_to_cart(id0, "oua"), "Cannot add same product twice!")

        self.assertFalse(self.marketplace.add_to_cart(id0, "ceai"), "Nonexistent product")
        self.assertNotIn("ceai", self.marketplace.carts[id0], "Product should have not been added!")

    def test_remove_from_cart(self):
        """
        Check if the removed products are no longer in the market
        """
        producer = self.marketplace.register_producer()
        id0 = self.marketplace.new_cart()
        self.marketplace.publish(producer, "oua")
        self.marketplace.publish(producer, "ulei")

        self.assertIn("oua", self.marketplace.products_avail, "Product not available!")
        self.assertIn("ulei", self.marketplace.products_avail, "Product not available!")

        self.marketplace.add_to_cart(id0, "oua")
        self.marketplace.add_to_cart(id0, "ulei")

        self.assertNotIn("oua", self.marketplace.products_avail, "Product available!")
        self.assertNotIn("ulei", self.marketplace.products_avail, "Product available!")

        self.marketplace.remove_from_cart(id0, "oua")
        self.assertNotIn("oua", self.marketplace.carts[id0], "Product should have been removed!")
        self.assertIn("oua", self.marketplace.products_avail, "Product should be available now!")

        self.marketplace.remove_from_cart(id0, "ulei")
        self.assertNotIn("ulei", self.marketplace.carts[id0], "Product should have been removed!")
        self.assertIn("ulei", self.marketplace.products_avail, "Product should be available now!")

    def test_place_order(self):
        """
        Test if the consumer gets all the requested products
        """
        producer = self.marketplace.register_producer()
        id0 = self.marketplace.new_cart()
        self.marketplace.publish(producer, "oua")
        self.marketplace.publish(producer, "ulei")
        self.marketplace.add_to_cart(id0, "oua")
        self.marketplace.add_to_cart(id0, "ulei")

        self.assertEqual(self.marketplace.place_order(id0), ["oua", "ulei"], "Not the same!")


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):

        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        # Maximum number of products a producer is allowed to have
        self.queue_size_per_producer = queue_size_per_producer
        # Internal counter used for assigning different id's to each producer
        self.number_of_producers = 0
        # Internal counter used for assigning different id's to each cart
        self.number_of_carts = 0

        # All the producers' queues
        self.producers_queues = {}
        # Products available in the marketplace
        self.products_avail = []
        # Products added by each producer (product, id_prod)
        self.products = {}
        # All the carts issued in the marketplace (id_cart, [products])
        self.carts = {}

        # Mutexes
        self.register_producer_lock = Lock()
        self.register_cart_semaphore = Lock()

        # Logger declarations
        self.logger = logging.getLogger("myLogger")
        self.handler = RotatingFileHandler('marketplace.log', maxBytes=25000, backupCount=10)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)8s: %(message)s'))
        logging.Formatter.converter = time.gmtime
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.handler)

    def register_producer(self):

        """
        Returns an id for the producer that calls this.
        """

        with self.register_producer_lock:
            # Get the next id for the new producer
            id_producer = self.number_of_producers
            # Add a new queue for the newly added producer
            self.producers_queues[id_producer] = []
            # Increment the number of producers
            self.number_of_producers += 1
            # Log that producer was issued a correct id
            self.logger.info('Producer id returned: %d for thread %s',
                             id_producer, current_thread().name)

        return id_producer

    def publish(self, producer_id, product):

        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """

        if len(self.producers_queues[int(producer_id)]) < self.queue_size_per_producer:
            self.logger.info('Producer %s with id %d published %s',
                             current_thread().name, producer_id, product)
            converted_id = int(producer_id)
            self.producers_queues[converted_id].append(product)
            self.products_avail.append(product)
            self.products[product] = converted_id
            return True

        return False

    def new_cart(self):

        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """

        with self.register_cart_semaphore:
            id_cart = self.number_of_carts
            self.logger.info('New_cart with id %d for consumer %s ',
                             id_cart, current_thread().name)
            self.carts[id_cart] = []
            self.number_of_carts += 1

        return id_cart

    def add_to_cart(self, cart_id, product):

        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        with self.register_cart_semaphore:
            self.logger.info('Product %s bought by consumer %s and added to cart %d',
                             product, current_thread().name, cart_id)
            if product not in self.products_avail:
                return False

            self.products_avail.remove(product)
            self.carts[cart_id].append(product)
            for prod_queue in self.producers_queues.values():
                if product in prod_queue:
                    prod_queue.remove(product)
                    break
        return True

    def remove_from_cart(self, cart_id, product):

        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        if product in self.carts[cart_id]:
            self.logger.info('Removed product %s from cart %d by consumer %s',
                             product, cart_id, current_thread().name)
            self.products_avail.append(self.carts[cart_id].pop(self.carts[cart_id].index(product)))

    def place_order(self, cart_id):

        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        popped = self.carts.pop(cart_id)
        with self.register_producer_lock:
            self.logger.info('Ordered placed for cart %d by consumer %s for product list %s',
                             cart_id, current_thread().name, popped)
            for item in popped:
                print(f"{current_thread().name} bought {item}")
        return popped
