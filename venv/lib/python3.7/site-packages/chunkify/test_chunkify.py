import unittest
from chunkify import chunkify, ChunkingError


class TestGetChunk(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def testOneChunk(self):
        self.assertEquals(chunkify(self.data, 1, 1), self.data)

    def testNGreaterThanTotal(self):
        self.assertRaises(ChunkingError, chunkify, self.data, 2, 1)

    def testMultipleChunks(self):
        self.assertEquals(chunkify(self.data, 3, 5), [5, 6])

    def testNotEvenlyDivisibleWithExtra(self):
        self.assertEquals(chunkify(self.data, 2, 4), [4, 5, 6])

    def testNotEvenlyDivisibleWithoutExtra(self):
        self.assertEquals(chunkify(self.data, 3, 4), [7, 8])

    def testNotEvenlyDivisibleWithoutExtraSubsequentChunk(self):
        self.assertEquals(chunkify(self.data, 4, 4), [9, 10])

    def testIterable(self):
        self.assertEquals(list(chunkify(xrange(1, 11), 2, 5)), [3, 4])

    def test_magical35(self):
        self.assertNotEqual(list(chunkify(xrange(1, 36), 10, 10)), [])
