#!/usr/bin/python

import sys
import struct as st # 
#cvw = custom vtk writer
import makevtk as cvw
# Import subprocess library, so system calls can be made
# in this specific case we want to use it to delete old .vtk files
# in case partition size changes etc
import subprocess
import binascii
import numpy as np

#"Global constants":
FIN = "output.dat"  #Std. input file format
FOUT = "output" #Std. output file format

def main(itr):
    print("iter: " + str(itr)) 
    # Delete all vtk files of same name
    subprocess.call("rm " + FOUT + "*.vtk", shell=True);

    # Try to open the file
    try:
        fin = open(FIN,'rb')
    except:
        exit("Could not open file.. exiting")

    # Open output file stream
    try:
        fout = open(FOUT+ "_" + str(itr).zfill(5) + ".vtk",'wb')
    except:
        exit("Cannot create output file... exiting")

    print("Read/write mesh information")
    # The binary file always starts with a user defined string
    title = readInString(fin)

    #Load information from header
    # The binary file contains a header with all the data sizes
    nDom,nPointsT,nCellsT,nPFields,nCFields,nodesPerElement=readHeader(fin)

    # The cell/element and point/node field names:
    pointFieldNames = readInString(fin) 
    cellFieldNames  = readInString(fin)

    # Convert to tuples with, assume names are comma separated. Also strip for whitespaces/trailing characters
    pointFieldNames = [x.strip() for x in pointFieldNames.split(',')]
    cellFieldNames = [x.strip() for x in cellFieldNames.split(',')] 

    # Write Header
    cvw.writeHeader(fout,title)

    print("Read/write mesh data: nodes")
    # Per Point/Node a list with coordinates
    # Assume 3 dimensions
    nDim = 3
    # Convert from binary to float and return in a matrix:
    points = readPoints(fin,nDom,nPointsT,nDim)
    cvw.writeASCIIPoints(fout,nDom,nPointsT,nDim,points)
    points = None # delete from memory

    print("Read/write mesh data: element connectivity")
    # Per Cell/Element a list of Points/Nodes it is connected to
    # Convert from binary to int and return in a matrix:
    cellsConnectivity = readCellsConn(fin,nDom,nCellsT,nodesPerElement) 
    cvw.writeASCIICellsConn(fout,nDom,nCellsT,nodesPerElement,cellsConnectivity) 
    cellsConnectivity = None # delete from memory

    # Per Cell/Element an offset 
    # For the Legacy File Format of VTK this data is not used
    # Convert from binary to int and return in a vector:
    cellsOffset = readCellsOffset(fin,nDom,nCellsT)
    cellsOffset = None # delete from memory

    print("Read/write mesh data: element type")
    # Convert from binary to int and return in a vector:
    cellsType = readCellsType(fin,nDom,nCellsT)
    cvw.writeASCIICellsType(fout,nDom,nCellsT,cellsType)
    cellsType = None # delete from memory

    print("Done writing mesh")

    #Write out a vtk file for the requested dataset
    dataset = 1
    foundRequestedDataset = False
    while(1):
        try:
            iteration = readdata(fin,'L')[0]
            print("Iteration: "+str(iteration))
            print("Optimization iter. " + str(iteration) + " = dataset " + str(dataset) + ", you requested dataset " + str(itr))
        except:
            break #break loop

        if int(dataset)==int(itr):  
            foundRequestedDataset = True
            print("Processing dataset " + str(dataset))

            print("Read/write point/node data")
            # Convert from binary to float and return in a matrix:
            pointData = readPointData(fin,nDom,nPointsT,pointFieldNames)
            cvw.writeASCIIScalarPointData(fout, nDom, nPointsT, pointFieldNames, pointData)
            pointData = None # delete from memory

            print("Read/write cell/mesh data")
            # Convert from binary to float and return in a matrix:
            cellData = readCellData(fin,nDom,nCellsT,cellFieldNames)
            cvw.writeASCIIScalarCellData(fout, nDom, nCellsT, cellFieldNames, cellData)
            cellData = None # delete from memory

            # Close output file
            fout.close()
        else:
            tmp1 = 0
            for i in range(nDom):
                for j in range(nPFields[i]):
                    #fin.read(4*nPointsT[i])
                    # Determine offset, which can be skipped through the binary values, a float has a length of 4 bytes
                    tmp1 += 4*nPointsT[i]
                for j in range(nCFields[i]):
                    #fin.read(4*nCellsT[i])
                    # Determine offset, which can be skipped through the binary values, a float has a length of 4 bytes
                    tmp1 += 4*nCellsT[i]
            # Set offset in file
            fin.seek(tmp1,1)
        dataset += 1

    # Close input file
    fin.close()

    if foundRequestedDataset:
        print("Done")
    else:
        print("!! The requested dataset was NOT found!! ")
        subprocess.call("rm " + FOUT + "*.vtk", shell=True);

def getNoNodes(i):
    if(i==10):
        return 4
    if(i==12):
        return 8
    if(i==1000):
        return 8
    exit("Sorry, but the element type " + str(i) + " is not defined. You may add it to getNoNodes() yourself... exiting")

#If the input file has specified a custom cell number format they can be added here
#and in the getNoNodes()
def convertToVtkCell(i):
    if(i==1000):
        return 12
    return i

def readdata(fin,inpformat):
    # fin = file input
    # inpformat = type of character/string/number to read - see python manual. 
    #  sequence of datatypes
    
    # How many bytes should we read when format is inpformat:
    bytecount = st.calcsize(inpformat)

    # Read the bytes into tuple tmp
    tmp = fin.read(bytecount)
    # print("readdata: tmp=",tmp)
    # print("readdata: type(tmp)=",type(tmp))

    # Convert from binary to e.g. floats and return in a tuple:
    data = st.unpack(inpformat,tmp)
    # print("readdata: data=",data)
    # print("readdata: type(data)=",type(data))

    return data

def readInString(fin):
    # Reads in a string until an end line symbol is detected
    string = ''
    while(1):
        try:
            tmp = readdata(fin,"c")[0] # The c means data of character type (length 1)
        # print("readInString: tmp=",tmp)
        # print("readInString: type(tmp)=",type(tmp))
            string += tmp
        except:
            exit("File ended while scanning for string. String not present or properly terminated?... exiting")
        
        # Break if end character detected
        if(tmp == '\x01'):
            string = string[0:-1]; # Dont want to save last character
            break
    return string

def readHeader(fin):
    #Should be called right after fin.open()
    try:
        nDom = readdata(fin,'i')[0]
        # print("nDom =%d" % nDom)
        nPointsT = list(readdata(fin,'L')[0:nDom])
        # print("nPointsT =*%s" % nPointsT)
        nCellsT = list(readdata(fin,'L')[0:nDom])
        # print("nCellsT =*%s" % nCellsT)
        nPFields = list(readdata(fin,'i')[0:nDom])
        # print("nPFields =*%s" % nPFields)
        nCFields = list(readdata(fin,'i')[0:nDom])
        # print("nCFields =*%s" % nCFields)
        nodesPerElement = readdata(fin,'i')[0]
        # print("nodesPerElement =%d" % nodesPerElement)

    except:
        exit("Could not read header format... exiting")

    return nDom,nPointsT,nCellsT,nPFields,nCFields,nodesPerElement

def readPoints(fin,nDom,nPointsT,nDim):
    try:
        # Assign memory
        points = np.zeros((nPointsT[0],nDim)) #, dtype=float32? Also loop over i?

        # Read the points
        # Rows: point, starting from 0
        # Cols: coordinate x=[p][0], y=[p][1], z=[p][2]
        for p in range(nPointsT[0]):
            for d in range(nDim):
                points[p][d] = readdata(fin,'f')[0]
            # print("point[p=%s]=%s" % (p, points[p][0:nDim]))

    except:
        exit("Could not read Points... exiting")

    return points

def readCellsConn(fin,nDom,nCellsT,nodesPerElement):
    try:
        # Assign memory
        cellsConn = np.zeros((nCellsT[0],nodesPerElement), dtype=int) # Also loop over i?

        # Read the Connectivity per Cell/Element
        # Rows: Cell/Element, starting from 0
        # Cols: Points/Nodes
        for c in range(nCellsT[0]):
            for n in range(nodesPerElement):
                cellsConn[c][n] = readdata(fin,'L')[0]
            # print("cellsConn[c=%s]=%s" % (c, cellsConn[c][0:nodesPerElement]))

    except:
        exit("Could not read Cells Connectivity... exiting")
    return cellsConn

def readCellsOffset(fin,nDom,nCellsT):
    try:
        # Assign memory
        cellsOffset = np.zeros((nCellsT[0],1), dtype=int) # Also loop over i?

        # Read the Offset per Cell/Element
        # Rows: Cell/Element, starting from 0
        # Cols: Offset
        for c in range(nCellsT[0]):
            cellsOffset[c][0] = readdata(fin,'L')[0]
            # print("cellsOffset[c=%s]=%s" % (c, cellsOffset[c][0]))

    except:
        exit("Could not read Cells Offset... exiting")

    return cellsOffset

def readCellsType(fin,nDom,nCellsT):
    try:
        # Assign memory
        cellsType = np.zeros((nCellsT[0],1), dtype=int) # Also loop over i?

        # Read the Type per Cell/Element
        # Rows: Cell/Element, starting from 0
        # Cols: Type
        for c in range(nCellsT[0]):
            cellsType[c][0] = readdata(fin,'L')[0]
            # print("cellsType[c=%s]=%s" % (c, cellsType[c][0]))

    except:
        exit("Could not read Cells Type... exiting")

    return cellsType

def readPointData(fin,nDom,nPointsT,pointFieldNames):
    try:
        #Also loop over i?
        # for i in range(nDom):

        # Assign memory
        pointData = np.zeros((nPointsT[0],len(pointFieldNames)))

        # Read the points
        # Rows: pointData, starting from 0
        # Cols: scalarData1, scalarData2, ..., len(pointFieldNames)
        for d in range(len(pointFieldNames)):
            # print("pointFieldNames[d=%s]=%s" % (d, pointFieldNames[d]))
            for p in range(nPointsT[0]):
                pointData[p][d] = readdata(fin,'f')[0]
                # print("pointData[p=%s]=%s" % (p, pointData[p][d]))

    except:
         exit("Could not read Point Data... exiting")

    return pointData

def readCellData(fin,nDom,nCellsT,cellFieldNames):
    try:
        #Also loop over i?
        # for i in range(nDom):

        # Assign memory
        cellData = np.zeros((nCellsT[0],len(cellFieldNames)))

        # Read the points
        # Rows: cellData, starting from 0
        # Cols: scalarData1, scalarData2, ..., len(cellFieldNames)
        for d in range(len(cellFieldNames)):
            # print("cellFieldNames[d=%s]=%s" % (d, cellFieldNames[d]))
            for c in range(nCellsT[0]):
                cellData[c][d] = readdata(fin,'f')[0]
                # print("cellData[c=%s]=%s" % (c, cellData[c][d]))

    except:
          exit("Could not read Cell Data... exiting")

    return cellData

# Make sure main is only called when the file is executed
if __name__ == "__main__":
    itr = 0
    if len(sys.argv) > 1:
            itr = sys.argv[1]

    main(itr)

