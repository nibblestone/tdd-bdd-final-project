# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        id_before_update = product.id
        updated_description = "updated"
        product.description = updated_description
        product.update()
        self.assertEqual(product.id, id_before_update)
        self.assertEqual(product.description, updated_description)
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, id_before_update)
        self.assertEqual(products[0].description, updated_description)

    def test_update_product_without_id(self):
        """It should raise an exception if updated without ID"""
        product = ProductFactory()
        product.id = None
        self.assertRaisesRegex(
            DataValidationError, "called with empty ID", product.update
        )

    def test_delete_a_product(self):
        """It should Delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertEqual(len(Product.all()), 1)
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all products"""
        self.assertEqual(len(Product.all()), 0)
        entries = 5
        for _ in range(entries):
            product = ProductFactory()
            product.id = None
            product.create()
        self.assertEqual(len(Product.all()), entries)

    def test_find_product_by_name(self):
        """It should Find products by name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        expected_count = sum(1 for p in products if p.name == name)
        found_products = Product.find_by_name(name)
        self.assertEqual(found_products.count(), expected_count)
        for product in found_products:
            self.assertEqual(product.name, name)

    def test_find_products_by_availability(self):
        """It should Find products by availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        expected_count = sum(1 for p in products if p.available == available)
        found_products = Product.find_by_availability(available)
        self.assertEqual(found_products.count(), expected_count)
        for product in found_products:
            self.assertEqual(product.available, available)

    def test_find_products_by_category(self):
        """It should Find products by category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        expected_count = sum(1 for p in products if p.category == category)
        found_products = Product.find_by_category(category)
        self.assertEqual(found_products.count(), expected_count)
        for product in found_products:
            self.assertEqual(product.category, category)

    def test_find_products_by_price(self):
        """It should Find products by price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        expected_count = sum(1 for p in products if p.price == price)
        found_products = Product.find_by_price(str(price))
        self.assertEqual(found_products.count(), expected_count)
        for product in found_products:
            self.assertEqual(product.price, price)

    def test_deserialize_with_invalid_availability(self):
        """It should raise an exception if deserialized with non-bool availability"""
        product = ProductFactory()
        data = product.serialize()
        data["available"] = "not a bool"
        self.assertRaisesRegex(
            DataValidationError, "Invalid type for boolean", product.deserialize, data
        )

    def test_deserialize_with_invalid_category(self):
        """It should raise an exception if deserialized with non-existing category"""
        product = ProductFactory()
        data = product.serialize()
        data["category"] = "not a category"
        self.assertRaisesRegex(
            DataValidationError, "Invalid attribute", product.deserialize, data
        )

    def test_deserialize_with_invalid_category_type(self):
        """It should raise an exception if deserialized when category is not a string"""
        product = ProductFactory()
        data = product.serialize()
        data["category"] = None  # not a string
        self.assertRaisesRegex(
            DataValidationError,
            "Invalid product: body of request contained bad or no data",
            product.deserialize,
            data,
        )
