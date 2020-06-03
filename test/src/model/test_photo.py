import unittest
from src.model.photo import Photo

class TestUnitsPhoto(unittest.TestCase):
    def test_target_crop_big_image(self):
        left, top, right, bottom = Photo.get_target_crop_square(1000,1000,200)
        self.assertEqual(left, 400)
        self.assertEqual(right, 600)
        self.assertEqual(top, 400)
        self.assertEqual(bottom, 600)

    def test_target_crop_small_image(self):
        left, top, right, bottom = Photo.get_target_crop_square(150,150,200)
        self.assertEqual(left, 0)
        self.assertEqual(right, 150)
        self.assertEqual(top, 0)
        self.assertEqual(bottom, 150)