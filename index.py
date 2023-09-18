import sys

class EnderecoInvalido(Exception):
    def __init__(self, ender):
        self.ender = ender

class RAM:
    def __init__(self, size):
        self.size = size
        self.memory = [0] * size

    def read(self, address):
        if address < 0 or address >= self.size:
            raise EnderecoInvalido(address)
        return self.memory[address]

    def write(self, address, value):
        if address < 0 or address >= self.size:
            raise EnderecoInvalido(address)
        self.memory[address] = value

class Cache:
    def __init__(self, size, cacheline_size, ram):
        self.size = size
        self.cacheline_size = cacheline_size
        self.ram = ram
        self.lines = size // cacheline_size
        self.cache = [None] * self.lines
        self.tags = [-1] * self.lines

    def _get_line_and_tag(self, address):
        line = address // self.cacheline_size % self.lines
        tag = address // self.cacheline_size
        return line, tag

    def read(self, address):
        line, tag = self._get_line_and_tag(address)
        if self.tags[line] != tag:
            # Cache miss
            print(f"MISS: {address} [{line*self.cacheline_size}..{(line+1)*self.cacheline_size-1}]->L{line}")
            self.tags[line] = tag
            start_address = tag * self.cacheline_size
            self.cache[line] = [self.ram.read(start_address + i) for i in range(self.cacheline_size)]
        return self.cache[line][address % self.cacheline_size]

    def write(self, address, value):
        line, tag = self._get_line_and_tag(address)
        if self.tags[line] != tag:
            # Cache miss
            print(f"MISS: {address} L{line}->[{line*self.cacheline_size}..{(line+1)*self.cacheline_size-1}] | [{tag*self.cacheline_size}..{(tag+1)*self.cacheline_size-1}]->L{line}")
            self.tags[line] = tag
            start_address = tag * self.cacheline_size
            self.cache[line] = [self.ram.read(start_address + i) for i in range(self.cacheline_size)]
        self.cache[line][address % self.cacheline_size] = value
        self.ram.write(address, value)

class CPU:
    def __init__(self, cache, io):
        self.cache = cache
        self.io = io

    def run(self, start_address):
        address = start_address
        for _ in range(10):  
            value = self.cache.read(address)
            print(f"   > {address} = {value}")
            address += 1


try:
    ram = RAM(2**22)
    cache = Cache(4 * 2**10, 64, ram)
    cpu = CPU(cache, None)

    inicio = 0

    print("Programa 1")
    ram.write(inicio, 118)
    ram.write(inicio+1, 130)
    cpu.run(inicio)

    print("\nPrograma 2")
    cache.write(inicio, 4155)
    cache.write(inicio+1, 4165)
    cpu.run(inicio)
except EnderecoInvalido as e:
    print("Endereco inválido:", e.ender, file=sys.stderr)
