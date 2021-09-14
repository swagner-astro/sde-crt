# distutils: language = c++

from pybatch.pseudoparticlestate cimport PseudoParticleState
from pybatch.batch cimport PseudoParticleBatch
from libcpp.vector cimport vector
from libcpp.map cimport map
from libcpp.string cimport string


cdef extern from "batch_kruells.cpp":
    pass

cdef extern from "batch_kruells.h":
    cdef cppclass BatchKruells1(PseudoParticleBatch):
        BatchKruells1(map[string, double] params) except +

    cdef cppclass BatchKruells2(PseudoParticleBatch):
        BatchKruells2(map[string, double] params) except +

    cdef cppclass BatchKruells3(PseudoParticleBatch):
        BatchKruells3(map[string, double] params) except +

    cdef cppclass BatchKruells4(PseudoParticleBatch):
        BatchKruells4(map[string, double] params) except +

    cdef cppclass BatchKruells5(PseudoParticleBatch):
        BatchKruells5(map[string, double] params) except +

    cdef cppclass BatchKruells6(PseudoParticleBatch):
        BatchKruells6(map[string, double] params) except +

    cdef cppclass BatchKruells7(PseudoParticleBatch):
        BatchKruells7(map[string, double] params) except +

    cdef cppclass BatchKruells8(PseudoParticleBatch):
        BatchKruells8(map[string, double] params) except +
