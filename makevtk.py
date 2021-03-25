#!/usr/bin/python

import struct as st
import binascii as ba

FOUT = "vtktest.vtk"

def main():
    try:
        fout = open(FOUT,'wb')
    except:
        exit("Couldn't create file...")

    # writeHeader(fout,"Test file")
    # lP = [0, 0, 0, 2, 0, 0, 0, 0, 2, 1, 1, 1]
    # writePoints(fout,lP)
    # lConn =[0, 1, 2, 3]
    # lOffset = [4]
    # lTypes = [10]
    # writeCells(fout,lConn,lOffset,lTypes)
    # lldata = []
    # lldata.append(["Scalars",1,2,-1,0.5])
    # lldata.append(["OtherSet",1.0,2,3,127.3])
    # writeScalarPointData(fout,lldata)
    # lldata = []
    # lldata.append(["Scalars",1.0])
    # lldata.append(["Scalars2",27.0])
    # writeScalarCellData(fout,lldata)
    fout.close()


def writeHeader(fout,title):
    fout.write("# vtk DataFile Version 2.0\n")
    fout.write(title)

def writeASCIIPoints(fout,nDom,nPointsT,nDim,points):
    fout.write("ASCII\n")
    # Assuming an UNSTRUCTURED_GRID
    fout.write("DATASET UNSTRUCTURED_GRID\n")
    # Write first rule; number of points, datatype
    fout.write("POINTS "+str(nPointsT[0])+" float\n")
    for p in range(nPointsT[0]):
        for d in range(nDim):
            # [Coordinate1, Coordinate2, ... , nDim]
            fout.write("{:.5e} ".format(points[p][d])) # Format in float, scientific notation
        # Set to next line
        fout.write("\n")

    # Add an empty line after all the Points
    fout.write("\n")

def writeASCIICellsConn(fout,nDom,nCellsT,nodesPerElement,cellsConn):
    # Write first rule; CELLS, number of cells, total number of data points
    fout.write("CELLS "+str(nCellsT[0])+" "+str(nCellsT[0]*(nodesPerElement + 1))+"\n")
    for c in range(nCellsT[0]):
        # First column; number of nodes per element
        fout.write(str(nodesPerElement)+" ")
        # [Second ... nodesPerElement] column; Points/Nodes for a Cell/Element
        for n in range(nodesPerElement):
            fout.write("{:d} ".format(cellsConn[c][n])) 
        # Set to next line
        fout.write("\n")

    # Add an empty line after all the Cells Connectivity
    fout.write("\n")

def writeASCIICellsType(fout,nDom,nCellsT,cellsType):
    # Write first rule; CELL_TYPES, number of cells
    fout.write("CELL_TYPES "+str(nCellsT[0])+"\n")
    for c in range(nCellsT[0]):
        # First column; cell type and set to next line
        fout.write("{:d}\n".format(cellsType[c][0])) 

    # Add an empty line after all the Cells Types
    fout.write("\n")

def writeASCIIHeaderPointData(fout, nDom, nPointsT):
    # Write first rule; POINT_DATA, number of points
    fout.write("POINT_DATA "+str(nPointsT[0])+"\n")

def writeASCIIScalarPointData(fout, nDom, nPointsT, pointFieldNames, pointData):
    for d in range(len(pointFieldNames)):
        # SCALARS dataName dataType numComp
        fout.write("SCALARS "+str(pointFieldNames[d])+ " float 1\n")
        fout.write("LOOKUP_TABLE default\n")
        for p in range(nPointsT[0]):
            fout.write("{:.5e}\n".format(pointData[p][d])) # Format in float, scientific notation

        # Add an empty line after a Scalar Point Data
        fout.write("\n")

def writeASCIIVectorsPointData(fout, nDom, nPointsT, vectorFieldNames, vectorData):
    for v in range(len(vectorFieldNames)):
        # VECTORS dataName dataType
        fout.write("VECTORS "+str(vectorFieldNames[v])+ " float\n")
        for p in range(nPointsT[0]):
            for d in range(len(vectorData[v][p])):
                fout.write("{:.5e} ".format(vectorData[v][p][d])) # Format in float, scientific notation
            fout.write("\n") # Set to next line

        # Add an empty line after a Vector Point Data
        fout.write("\n")

def writeASCIIHeaderCellData(fout, nDom, nCellsT):
    # Write first rule; CELL_DATA, number of cells
    fout.write("CELL_DATA "+str(nCellsT[0])+"\n")

def writeASCIIScalarCellData(fout, nDom, nCellsT, cellFieldNames, cellData):
    for d in range(len(cellFieldNames)):
        # SCALARS dataName dataType numComp
        fout.write("SCALARS "+str(cellFieldNames[d])+ " float 1\n")
        fout.write("LOOKUP_TABLE default\n")
        for p in range(nCellsT[0]):
            fout.write("{:.5e}\n".format(cellData[p][d])) # Format in float, scientific notation

        # Add an empty line after a Scalar Cell Data
        fout.write("\n")

    # Returns Int containing data size + data
    # everything in base64 encoding
def writeBin64(bindata):
    datalen = st.pack('Q',len(bindata))
    # Note that \n is removed from datalen
    # - which btw is a ridiculous design choice
    # as it makes the data size grow by 33% (4/3-1)
    return ba.b2a_base64(datalen)[0:-1]+ba.b2a_base64(bindata)

if __name__ == "__main__":
    main()
