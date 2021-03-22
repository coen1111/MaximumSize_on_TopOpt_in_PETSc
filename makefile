PETSC_DIR=/home/pi/petsc-3.7.4
PETSC_ARCH=arch-linux2-c-debug
CFLAGS = -I.
FFLAGS=
CPPFLAGS=-I.
FPPFLAGS=
LOCDIR='pwd'
EXAMPLESC=
EXAMPLESF=
MANSEC=
CLEANFILES=
NP=


include ${PETSC_DIR}/lib/petsc/conf/variables
include ${PETSC_DIR}/lib/petsc/conf/rules
include ${PETSC_DIR}/lib/petsc/conf/test

topopt: main.o TopOpt.o LinearElasticity.o MMA.o Filter.o PDEFilter.o MPIIO.o chkopts
	rm -rf topopt
	-${CLINKER} -o topopt main.o TopOpt.o LinearElasticity.o MMA.o Filter.o PDEFilter.o MPIIO.o ${PETSC_SYS_LIB}
	${RM}  main.o TopOpt.o LinearElasticity.o MMA.o Filter.o PDEFilter.o MPIIO.o 
	rm -rf *.o

myclean:
	rm -rf topopt *.o output* binary* log* makevtk.pyc Restart* 

