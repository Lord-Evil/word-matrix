#!/usr/bin/python3
import sys
import math


class Error(BaseException):

    def __init__(self, m):
        print(m)
        quit()


class Matrix:
    _log = 1
    alphabetSize = 10
    wordSize = 8
    cellSize = 0
    # alphabet="abcdefghijklmnopqrstuvwxyz"
    alphabet = "0123456789"

    brainName = ""

    wordBase = None
    matrixSizeBytes = 0
    matrixSize = 0
    connected = False
    bytesWritten = 0

    class matrixHeader:
        size = 0
        origName = ""
        alphabet = ""
        wordsize = 0

        def countSize(self):
            self.size = 3 + len(self.origName) + 1 + len(self.alphabet) + 1 + 1

        def readstring(self, fw):
            string = ""
            while True:
                c = fw.read(1)
                if(c == b'\0'):
                    break
                string += c.decode("latin1")
            return string
    __header = None
    # cache stuff
    _cache = 0
    _useAddresses = None

    def useCache(self):
        try:
            fw = open(self.brainName + ".cache", "+xb")
            print("No cache file created yet..\nCaching, might take some time...")
            self._useAddresses = set()
            self._cache = 0
            for cell in range(self.matrixSize + 1):
                data = self.read(cell)
                if(len(data) > 0):
                    self._useAddresses.add(cell)
            fw.write(bytes(str(self._useAddresses), "latin1"))
            fw.close()
            self._cache = 1
        except:
            pass

    def updateCache(self, _address=None, _value=None):
        if(_address is not None):
            if(_value is not None):
                if(_value != b'\0' * self.cellSize):
                    if(_address not in self._useAddresses):
                        self._useAddresses.add(_address)
                else:
                    if(_address in self._useAddresses):
                        self._useAddresses.remove(_address)
            else:
                if(_address not in self._useAddresses):
                    self._useAddresses.add(_address)
            try:
                fw = open(self.brainName + ".cache", "+wb")
                fw.write(bytes(str(self._useAddresses), "latin1"))
                fw.close()
                print("Cache updated")
            except:
                print("cache update failed")
        else:
            fw = open(self.brainName + ".cache", "+wb")
            fw.write(bytes(str(self._useAddresses), "latin1"))
            fw.close()
            print("Cache updated")

    def readCache(self):
        self.useCache()
        print("Reading from cache...")
        fr = open(self.brainName + ".cache", "rb", buffering=0)
        self._useAddresses = eval(fr.readall())
        fr.close()
    # end cache stuff

    def __init__(self):
        pass

    def log(self, m_str):
        if(self._log):
            print(m_str)

    def prentend(self, alphabet, wordsize):
        self.alphabet = self.alpha2latin(alphabet)
        self.alphabetSize = len(self.alphabet)
        self.wordSize = wordsize

        cells = int((self.alphabetSize**self.wordSize - 1) /
                    (self.alphabetSize - 1) * self.alphabetSize)
        self.cellSize = math.ceil(cells.bit_length() / 8)
        self.matrixSizeBytes = int(cells * self.cellSize)
        self.log("The Matrix will have %s cells, %d bytes each, totaling %s bytes (%s MB)" % ("{:,}".format(
            cells), self.cellSize, "{:,}".format(self.matrixSizeBytes), "{:,}".format(int(self.matrixSizeBytes / 1024 / 1024))))

    def create(self, alphabet, wordsize, brainName="main"):
        if(len(brainName) - brainName.find(".matrix") == 7):
            self.brainName = brainName.replace(".matrix", "")
        else:
            self.brainName = brainName
        #(3^5-1)/(3-1)*3
        self.alphabet = self.alpha2latin(alphabet)
        self.alphabetSize = len(self.alphabet)
        self.wordSize = wordsize

        cells = int((self.alphabetSize**self.wordSize - 1) /
                    (self.alphabetSize - 1) * self.alphabetSize)
        self.cellSize = math.ceil(cells.bit_length() / 8)
        self.matrixSizeBytes = int(cells * self.cellSize)
        self.log("Creating Matrix %s cells - %s bytes (%s MB)" % ("{:,}".format(cells), "{:,}".format(
            self.matrixSizeBytes), "{:,}".format(int(self.matrixSizeBytes / 1024 / 1024))))
        try:
            fw = open(self.brainName + ".matrix", "+xb")
            self.bytesWritten += fw.write(b'MTX')
            self.bytesWritten += fw.write(
                self.brainName.encode("latin1") + b'\0')
            self.bytesWritten += fw.write(
                self.alphabet.encode("latin1") + b'\0')
            self.bytesWritten += fw.write(self.wordSize.to_bytes(1, "big"))
            for i in range(cells):
                self.bytesWritten += fw.write(bytes(self.cellSize))
            fw.close()
            if(self._cache):
                self._useAddresses = set()
                fw = open(self.brainName + ".cache", "+wb")
                fw.write(bytes(str(self._useAddresses), "latin1"))
                fw.close()
            self.log("Matrix created!")
        except:
            raise Error("File %s already exists!" % self.brainName)

    def connect(self, brainName="main"):
        if(len(brainName) - brainName.find(".matrix") == 7):
            self.brainName = brainName.replace(".matrix", "")
        else:
            self.brainName = brainName
        try:
            self.wordBase = open(
                self.brainName + ".matrix", "+rb", buffering=0)
        except FileNotFoundError:
            raise Error("No such file or directory: '%s'" %
                        (self.brainName + ".matrix"))
        self.__header = self.matrixHeader()
        fileType = self.wordBase.read(3)
        if(fileType != b'MTX'):
            raise Error("File is of the wrong type!")
        self.__header.origName = self.__header.readstring(self.wordBase)
        self.log("Connecting to: " + self.__header.origName)
        self.__header.alphabet = self.__header.readstring(self.wordBase)
        self.alphabet = self.__header.alphabet
        self.alphabetSize = len(self.__header.alphabet)
        self.__header.wordsize = ord(self.wordBase.read(1))
        self.__header.countSize()
        self.wordSize = self.__header.wordsize

        cells = int((self.alphabetSize**self.wordSize - 1) /
                    (self.alphabetSize - 1) * self.alphabetSize)
        self.cellSize = math.ceil(cells.bit_length() / 8)
        self.matrixSizeBytes = int(cells * self.cellSize)
        #print("Loaded %s bytes matrix"%self.matrixSizeBytes)
        #print("Matrix Size: %d cells"%(self.matrixSizeBytes/self.cellSize))
        self.matrixSize = int(self.matrixSizeBytes / self.cellSize)
        self.connected = True
        if(self._cache):
            self.readCache()

    def write(self, address, value):
        self.wordBase.seek(self.__header.size + address * self.cellSize)
        self.bytesWritten += self.wordBase.write(value)
        if(self._cache):
            self.updateCache(address, value)

    def readRange(self, address, cells):
        self.wordBase.seek(self.__header.size + address * self.cellSize)
        ret = list()
        res = self.wordBase.read(self.cellSize * cells)
        for i in range(cells):
            c = int.from_bytes(
                res[i * self.cellSize:(i * self.cellSize + self.cellSize)], "big")
            if(c != 0):
                ret.append(c)
        return ret

    def read(self, address):
        if(self._cache):
            if(address not in self._useAddresses):
                return 0
        self.wordBase.seek(self.__header.size + address * self.cellSize)
        ret = self.wordBase.read(self.cellSize)
        ret = int.from_bytes(ret, "big")
        if(ret):
            return [ret]
        else:
            return []

    def dumpData(self):
        fw = open(self.brainName + ".data", "+w")
        if(self._cache):
            for cell in self._useAddresses:
                data = self.read(cell)
                try:
                    cellName = self.getKey(cell + 1)
                    fw.write("%s %s\n" % (cellName, data[0]))
                except:
                    print(data)
                    quit()
        else:
            for cell in range(self.matrixSize + 1):
                data = self.read(cell)
                if(len(data) > 0):
                    fw.write("%s %s\n" % (self.getKey(cell + 1), data[0]))
        fw.close()

    def getAddress(self, word):
        word = self.alpha2latin(word)
        if(len(word) > self.wordSize):
            print("Word is bigger then allowed word size %s" % self.wordSize)
        else:
            word = word.lower()
            l = len(word)
            address = 0
            for pos in range(len(word)):
                try:
                    i = self.alphabet.index(word[pos])
                except:
                    raise Error("Letter '%s' is not in our alphabet" %
                                word[pos])
                num = self.matrixSize / \
                    (self.alphabetSize**(pos + 1)) * (i) + 1
                address += int(num)

            return address - 1

    def getKey(self, address, mSize=None):
        if(mSize is None):
            mSize = self.matrixSize
        if(address <= 0):
            return ""
        mSize = int(mSize / self.alphabetSize)
        c = int((address - 1) / mSize)
        address -= 1 + c * int(mSize)
        r = self.getKey(address, mSize)
        try:
            return self.alphabet[c] + r
        except:
            print("Bad add %d" % address)
            quit()

    def train(self, word, value, disableCache=False):
        address = self.getAddress(word)
        value = value.to_bytes(self.cellSize, "big")
        if(self._cache):
            if disableCache:
                self._cache = 0
            self.write(address, value)
            if(value != b'\0' * self.cellSize):
                if(address not in self._useAddresses):
                    self._useAddresses.add(address)
            if disableCache:
                self._cache = 1
        else:
            self.write(address, value)

    def trainFile(self, filename):
        tfile = open(filename)
        while(1):
            line = tfile.readline()
            if(len(line) < 2):
                break
            rline = line.rstrip().split(" ")
            # print(line)
            self.train(rline[0], int(rline[1]), True)
        if(self._cache):
            self.updateCache()

    def gain(self, word):
        address = self.getAddress(word)
        result = list()
        if(len(word) == self.wordSize):
            print("Getting one cell")
            result = self.read(address)
        else:
            cells = self.alphabetSize**(self.wordSize - len(word)) + 1
            print("Getting %d cells" % cells)
            result = self.readRange(address, cells)
        return result

    def info(self):
        print('''Matrix info:
	Cell size:		%d
	Word size:		%s
	Alphabet:		"%s"
	Alphabet size:		%d
	Matrix size:		%s bytes - %d cells
			''' % (self.cellSize, self.wordSize, self.alphabet.encode("latin1").decode("cp1251"), self.alphabetSize, self.matrixSizeBytes, self.matrixSize))

    def __del__(self):
        if(self.connected):
            if(self.bytesWritten > 0):
                self.log("Bytes written: %d" % self.bytesWritten)
            self.log("Closing matrix..")
            self.wordBase.close()

    def alpha2latin(self, string):
        return string.encode("cp1251").decode("latin1")

if(__name__ == "__main__"):
    m = Matrix()

    if(len(sys.argv) > 2 and sys.argv[1] == "p"):
        m.prentend(sys.argv[2], int(sys.argv[3])	)
    elif(len(sys.argv) > 3 and sys.argv[1] == "c"):
        if(len(sys.argv) < 5):
            m._cache = 1
            m.create(sys.argv[2], int(sys.argv[3]))
            m.connect()
        else:
            m.create(sys.argv[2], int(sys.argv[3]), sys.argv[4])
            m.connect(sys.argv[4])
        m.info()
    elif(len(sys.argv) > 3 and sys.argv[1] == "t"):
        m._cache = 1
        if(len(sys.argv) < 5):
            m.connect()
        else:
            m.connect(sys.argv[4])
        m.train(sys.argv[2], int(sys.argv[3]))
    elif(len(sys.argv) > 2 and sys.argv[1] == "tf"):
        m._cache = 1
        if(len(sys.argv) > 3):
            m.connect(sys.argv[3])
        else:
            m.connect()
        m.trainFile(sys.argv[2])
    elif(len(sys.argv) > 2 and sys.argv[1] == "g"):
        m._cache = 1
        if(len(sys.argv) > 3):
            m.connect(sys.argv[3])
        else:
            m.connect()
        print(m.gain(sys.argv[2]))
    elif(len(sys.argv) > 1 and sys.argv[1] == "test"):
        m._log = 0
        if(len(sys.argv) > 2):
            m.create("abcde", 5, sys.argv[2])
            m.connect(sys.argv[2])
        else:
            m.create("abcde", 5)
            m.connect()

        for i in range(m.matrixSize):
            key = m.getKey(i + 1)
            print("%s %d" % (key, i + 1))
    elif(len(sys.argv) > 1 and sys.argv[1] == "i"):
        if(len(sys.argv) > 2):
            m.connect(sys.argv[2])
        else:
            m.connect()
        m.info()
    elif(len(sys.argv) > 1 and sys.argv[1] == "d"):
        m._cache = 1
        if(len(sys.argv) > 2):
            m.connect(sys.argv[2])
        else:
            m.connect()
        m.dumpData()
    else:
        print('''Usage:
	./matrix.py <command> [params] [matrixfile]

Commands:
	c	<alphabet> <wordsize>		Create Matrix
	p	<alphabet> <wordsize>		Just calculate Matrix
	t	<word> <address(int)>		Train Matrix
	tf	<datasetfile>			Create & Train Matrix from file
	g	<word>				Read Matrix
	d					Dump Matrix data into file
	i					Info Matrix
	test					Print out sample training dataset
			''')
