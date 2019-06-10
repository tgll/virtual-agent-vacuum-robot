#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Mise en place de la bibliothèque pour algo génétique simple
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__version__ = "3.02"
__date__ = "14.03.16"
__usage__ = "individu pour la bibliotheque simple algo genetiques"
#---- import ----------
import random
import copy
import math
import inspect # histoire de regarder
#----------------------

def int2bin(val,sz):
    """ transforme un entier val en nombre binaire de taille sz """
    l = bin(val)[2:]
    d = sz - len(l)
    _l = '0'*d + l
    return _l
    
class SomeOne(object):
    """
    Un individu est créé à partir
    d'une taille de la chaine, de l'alphabet de référence
    d'une fonction d'évaluation
    """
    def __init__(self,size,alphabet,fun_fitness):
        self.__sz = size
        self.__alphabet = alphabet
        self.__genotype = ''
        self.fitness = fun_fitness
        self.reset()

    def __str__(self):
        """
        chaine a afficher
        """
        if self.__evaluation is not  None:
            _str = '\nfitness : %02.3f,' % self.__evaluation
        else:
            _str = ' Non evalue'
        return _str

    def __repr__(self):
        """ chaine affichable """
        return self.genotype

    def __lt__(self,other):
        """
        comparaison entre deux chromosomes
        """
        return (self.adequation < other.adequation)

    @property
    def fitness(self):
        """ renvoie la fonction d'évaluation utilisée """
        return self.__fitness
    @fitness.setter
    def fitness(self,fun):
        #assert hasattr(fun,"__call__") # doit etre callable
        assert inspect.isfunction(fun),\
          "a callable was expected"
        assert len(inspect.getfullargspec(fun).args) == 1,\
          "Only one argument allowed"
        self.__fitness = fun
        self.reset()
        
    @property
    def adequation(self):
        """
        B{accesseur}: en lecture
        @return: evaluation du chromosome
        """
        if self.__evaluation is None:
            self.__evaluation = self.fitness(self.genotype)
        return self.__evaluation

    @adequation.setter
    def adequation(self,val):
        """
        B{accesseur}: en ecriture
        affectation de la valeur de fitness
        """
        self.__evaluation = val

    @property
    def victoires(self):
        """
        B{accesseur}: en lecture
        @return: nombre de victoires du chromosome
        """
        return self.__victory
    @victoires.setter
    def victoires(self,val):
        """
        B{accesseur}: en ecriture
        """
        self.__victory = val

    def reset(self):
        """ raz de l'adequation et des victoires """
        self.__evaluation = None
        self.__victory = 0
        
    @property
    def alphabet(self):
        """
        B{accesseur}: en lecture
        @return: alphabet du chromosome
        """
        return self.__alphabet

    @property
    def size(self):
        """
        B{accesseur}: en lecture
        @return: taille du chromomsome
        """
        return self.__sz

    @property
    def genotype(self):
        """
        B{accesseur}: en lecture
        @return: la chaine des valeurs du chromosome
        """
        return self.__genotype

    @genotype.setter
    def genotype(self,val):
        """
        B{accesseur}: en ecriture
        permet de modifier une chaine codante
        raz adequation
        """
        assert(len(val) == self.size)
        self.__genotype = val
        self.__evaluation = None

    def split(self,x):
        """
        decoupe d'un chromosome, 
        @param x: point de coupure
        @return: les deux sous-chaines
        """
        return self.genotype[:x],self.genotype[x:]


    def crossOver(self,other,way=1,verbose=False):
        """
        effectue le croisement de deux individus
        @return: deux nouveaux sous forme de tuple

            >>> x.genotype
            10111001
            >>> y.genotype
            00100101
            >>> x.crossOver(y)
            (101|00101,001|11001)
        """
        # on controle que le croisement est possible
        assert(isinstance(other,SomeOne))
        assert(self.alphabet == other.alphabet)
        assert(self.size == other.size)
        assert(self.fitness.__name__ == other.fitness.__name__),\
          "%s vs %s" % (self.fitness.__name__,other.fitness.__name__)
        xx = inspect.getfullargspec(self.fitness)
        yy = inspect.getfullargspec(other.fitness)
        assert xx == yy
        
        _individu = self.__class__

        if way == 3: # uniform
            _n = random.randrange(self.size-1)
            _mask = int2bin(_n,self.size)
            _ch1 = self.genotype
            _ch2 = other.genotype
            _one = ''.join([_ch1[i] if _mask[i] == '0' else _ch2[i]
                            for i in range(self.size)])
            _two = ''.join([_ch2[i] if _mask[i] == '0' else _ch1[i]
                            for i in range(self.size)])
            if verbose:
                print("chaine",_ch1)
                print("chaine",_ch2)
                print("mask  ",_mask)
                print(_one)
                print(_two)
            return ( _individu(self.size,self.alphabet,self.fitness,
                              _one),
                     _individu(self.size,self.alphabet,self.fitness,
                              _two)
                     )
        elif way == 2: # crossover 2 points
            ch1 = self.genotype
            ch2 = other.genotype
            
            _x,_y = random.sample(range(1,self.size),2)
            if _x > _y : _x,_y = _y,_x

            _one = ch1[:_x],ch1[_x:_y],ch1[_y:]
            _two = ch2[:_x],ch2[_x:_y],ch2[_y:]
            if verbose:
                print('point de coupure en %d et %d' % (_x,_y) )
                print(_one[0],'|',_one[1],'|',_one[2])
                print(_two[0],'|',_two[1],'|',_two[2])
            return ( _individu(self.size,self.alphabet,self.fitness,
                              _one[0]+_two[1],_one[2]),
                     _individu(self.size,self.alphabet,self.fitness,
                              _two[0]+_one[1],_two[2])
                     )
            
        else:
            _x = random.randrange(1,self.size)
            if verbose: print('point de coupure',_x)
            _one = self.split(_x)
            if verbose: print(_one[0],' . ',_one[1])
            _two = other.split(_x)
            if verbose: print(_two[0],' . ',_two[1])
            return ( _individu(self.size,self.alphabet,self.fitness,
                              _one[0],_two[1]),
                     _individu(self.size,self.alphabet,self.fitness,
                              _two[0],_one[1])
                     )

    def mutatis(self,pos = None):
        """
        effectue une mutation sur la coordonnee pos
        si pos, n'est pas fournie on tire au hasard
        @param pos[defaut: B{None}]: un index

            >>> x.genotype
            01122
            >>> x.mutatis(3).genotype
            011_0_2
        """
        if pos is not None: _pos = pos
        else: _pos = random.randrange( self.size )
        _old = self.genotype[_pos]
        _lst = self.alphabet.split(_old)
        _new = random.choice(_lst[0] + _lst[1])
        _gen = list(self.genotype)
        _gen[_pos] = _new
        # modif du genotype => reset adequation
        self.genotype = ''.join(_gen)
        self.__evaluation = None


class Individu(SomeOne):
    """
    cree un individu a partir du prefixe et du suffixe,
    eventuellement on comble avec une partie mediane
    """
    def __init__(self,size,alphabet,fun_fitness,pref='',suf=''):
        """
        constructeur de classe
        @param size: taille du chromosome
        @param alphabet: alphabet autorise
        @param fun_fitness: la fonction d'évaluation
        @param pref: [defaut B{''}] prefixe obligatoire
        @param suf: [defaut B{''}] suffixe obligatoire

        construction d'un individu de taille size, sur l'alphabet
        fourni tel que self.genotype = pref + lack + suf

        """
        super(Individu,self).__init__(size,alphabet,fun_fitness)
        # effectue l'initialisation du chromosome
        _lack = size - (len(pref) + len(suf))
        assert(_lack >= 0)
        for x in pref : assert(x in alphabet)
        for x in suf : assert(x in alphabet)
        _mid = [random.choice(alphabet) for i in range(_lack)]
        self.genotype = pref + ''.join(_mid) + suf

if __name__ == "__main__" :
    random.seed() # initialisation du générateur aléatoire
    def myf(ch):
        """ fonction cherchant le nombre de 0 """
        _s = 0
        for x in ch :
            if x == '0' : _s += 1
        return _s

    print("un individu commençant par 000, finissant par 102")
    # un individu 000 ??? 102
    x = Individu(9,'012',myf,'000','102')
    print(x.genotype)
    # un individu ??? ??? ???
    print("un individu aléatoire sur l'alphabet 012")
    y = Individu(9,'012',myf,'','')
    print(y.genotype)
    # croisement aleatoire
    for i in (1,2,3):
        a,b = x.crossOver(y,i,True) # trace explicite
        print("on verifie fitness(u.genotype) = u.adequation, ici le nb de 0")
        for u in (a,b,x,y):
            assert(myf(u.genotype) == u.adequation)
            print('>',u.genotype,u)
        assert(a.adequation + b.adequation == x.adequation + y.adequation)

    print("peut-on changer de fonction d'evaluation comme on veut ?")
    def value(ch):
        _v = 'aeiouy'
        _s = 0
        for x in ch :
            if x in _v : _s += 1
        return _s * 100 / len(ch)

    value("exemple")
    x = Individu(7,"abcdefghijklmnopqrstuvwxyz",value)
    print('>',x.genotype,x.adequation)
    x.genotype ='exemple'
    print('>',x.genotype,x.adequation)

    def fun_val(ch):
        _r = value(ch) * len(ch) / 100
        return (len(ch) - _r) / len(ch)
    print("changement de fitness ...")
    x.fitness = fun_val
    print('>',x.genotype,x.adequation)
    
        

