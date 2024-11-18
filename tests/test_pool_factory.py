import unittest

from src.utils.pool import PoolFactory


class TestPoolFactory(unittest.TestCase):
    def test_create_pool_strategy_invalid_type(self):
        with self.assertRaises(ValueError):
            PoolFactory.create_pool_strategy("invalid_type", max_workers=2)

    def test_create_pool_strategy_negative_workers(self):
        with self.assertRaises(ValueError):
            PoolFactory.create_pool_strategy("thread", max_workers=-1)


if __name__ == "__main__":
    unittest.main()
