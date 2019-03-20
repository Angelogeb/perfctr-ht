% Performance counters analysis for Hyper-Threading
% Beatrice Bevilacqua, Anxhelo Xhebraj
% March 2019

Performance counters analysis for Hyper-Threading
=================================================


Performance Counters Frameworks
-------------------------------
The complexity of newer architectures has led to the necessity of
a better knowledge of the underlying hardware in order to get peak
performance. Following these trends new interfaces have been made
available to developers for spotting performance bottlenecks in their
applications such as Performance Monitoring Units (PMU).

PMUs enable developers to observe and count events in the CPU such as
branch mispredictions, cache misses and other finer grained details over
the whole pipeline. Although powerful, dealing with such information
remains burdensome given the diversity of the events, making it difficult
to truly identify optimization opportunities.
Depending by the processor family, on average 4 counters can be read
contemporarily at any time using Model Specific Registers. In order
to read more than 4 events, various tools multiplex such registers
in a *time-sharing* fashion.

Many tools for performance analysis based on PMUs have been developed
ranging from *raw* event count to more sofisticated and aggregated
measures as follows:

* `msr`: direct access to the device files `/dev/cpu/*/msr`
* [PAPI] : A Performance Application Programming Interface that
  offers a set of APIs for using performance counters.
  Supports multiple architectures and multiplexing.
* [likwid] : A suite of applications and libraries for analysing
  High Performance Computing applications. It
  contains out of the box utilies to work with MPI,
  power profiling and architecture topology.
* [Intel Vtune Amplifier] : Application for performance analysis on
  intel architectures. Gives insights regarding possible bottlenecks
  of the application annotating its source code and provides
  possible solutions.
* [perf] : In a similar vein to Intel Vtune Amplifier shows which
  functions are more critical to the application. Additionally
  provides more high level information such as I/O and Networking.
  It is possible to analyse raw hardware performance counters but
  its main goal is abstracting over them.
* [pmu-tools] : is a collection of tools for profile collection
  and performance analysis on Intel CPUs on top of Linux perf


`likwid`
--------
Given that the goal of this document is to analyze system behaviour
through performance counters to provide insights regarding new
possible scheduling strategies in Hyper-Threading systems, we choose
to use the `likwid` applications and libraries for our task. The choice
was especially driven by the presence of useful benchmarks in the `likwid`
repository for stressing FPU and other core subsystems. Additionally
Intel Vtune Amplifier was used to profile the benchmarks in order to
characterize their workload.

`likwid-perfctr -e` allows to query all the available events for
the current architecture while `likwid-perfctr -a` shows the pre-configured
event sets, called performance groups, with useful pre-selected event
sets and derived metrics. Multiple modes of execution of performance monitoring
are available as documented in the `likwid` wiki. Of main interest are
**wrapper mode** and **timeline mode**. The former produces a summary of the
events, while the latter outputs performance metrics at a specified
frequency (specified through the `-t` flag).
In case multiple groups need to be monitored multiplexing is performed
at the granularity set through the `-t` flag (in timeline mode, otherwise
`-T` for wrapper mode) and the output produced are the id of the group read
at a given timestep and its values.

 >Tests have shown that for measurements below 100 milliseconds, the
  periodically printed results are not valid results anymore (they are higher
  than expected) but the behavior of the results is still valid. E.g. if you
  try to resolve the burst memory transfers, you need results for small
  intervals. The memory bandwidth for each measurement may be higher than
  expected (could even be higher than the theoretical maximum of the machine)
  but the burst and non-burst traffic is clearly identifiable by highs and
  lows of the memory bandwidth results.


Benchmarks
----------

The benchmark available in `likwid` can be run through the `likwid-bench`
command. For an overview of the available benchmarks run `likwid-bench -a`.
All benchmarks perform operations over one-dimensional arrays. The benchmarks
used in our setting are:

  * `ddot_sp`: Single-precision dot product of two vectors, only scalar
               operations
  * `copy`: Double-precision vector copy, only scalar operations
  * `ddot_sp_avx`: Single-precision dot product of two vectors, optimized for AVX
  * `sum_int`: Custom benchmark similar to `sum` but working on integers

All benchmarks are run with multiple configurations of number of threads (with or
without Hyper-Threading), processor frequencies with TurboBoost disabled, working
set size. The latter is needed in order to emulate *core-bound* executions
(working set fitting in cache) and *memory-bound* ones.


Details
-------

The tests were run on a Dell XPS 9750 with i7-8750H. With TurboBoost disabled
the available frequencies range from 1.0 to 2.2 GHz. There is one socket with
6 Physical cores and 12 Logical cores (in Hyper Threading).

[PAPI]: http://icl.utk.edu/papi/
[PAPI]: https://bitbucket.org/icl/papi.git
[PAPI]: http://icl.utk.edu/projects/papi/wiki/PAPIC:Overview

[likwid]: https://github.com/RRZE-HPC/likwid

[Intel Vtune amplifier]: https://software.intel.com/en-us/vtune

[perf]: http://www.brendangregg.com/perf.html

[pmu-tools]: https://github.com/andikleen/pmu-tools