import unittest

import mdp.parallel as parallel
from mdp import numx as n


class TestScheduler(unittest.TestCase):

    def test_scheduler(self):
        """Test scheduler with 6 tasks."""
        scheduler = parallel.Scheduler(copy_callable=False)
        for i in range(6):
            scheduler.add_task(i, lambda x: x**2)
        results = scheduler.get_results()
        scheduler.shutdown()
        # check result
        results = n.array(results)
        self.assertTrue(n.all(results == n.array([0,1,4,9,16,25])))
        

def get_suite(testname=None):
    # this suite just ignores the testname argument
    # you can't select tests by name here!
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestScheduler))
    return suite
            
if __name__ == '__main__':
    unittest.main() 