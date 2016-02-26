# encoding: utf8

from unittest import TestCase
import sys

from pyexpect import expect

class PerformanceTest(TestCase):
    
    def _test_raw_timeing(self):
        import timeit
        time = timeit.timeit("expect('foo') == 'foo'", "from pyexpect import expect", number=100000)
        self.fail(time)
    
    def _test_cprofile(self):
        import cProfile
        cProfile.run("from pyexpect import expect; expect('foo') == 'foo'")
        self.fail()
    
    def _test_line_profiler(self):
        import line_profiler
        profiler = line_profiler.LineProfiler()
        import pyexpect
        profiler.add_module(pyexpect)
        profiler.run("from pyexpect import expect; expect('foo') == 'foo'")
        profiler.print_stats(stripzeros=True)
        self.fail()