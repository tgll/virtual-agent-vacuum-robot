#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Architecture de la bibliothèque version pour les étudiants
- On suppose qu'il y a un nombre pair d'individus dans la population
- On suppose que tous les gènes sont de la même taille
- On suppose que tous les gènes utilisent le même alphabet
- On suppose que la taille de la population ne varie pas
- On suppose que l'on fait des croisements simples (1 ou 2 points, 3=uniform)
- On suppose que l'on ne modifie pas les scores des individus
- pas de tournois
- remplacement générationnel (pop à t+1 renouvelée entièrement)
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__version__ = "4.02"
__date__ = "14.03.16"
__usage__ = "version étudiants: bibliotheque simple pour algo genetiques"

from base_agslib import Individu
import random
import math
import sys

# tentative d'importation d'une bibliotheque faisant des courbes
try:
    import matplotlib.pyplot as plt
    HASPLOT = True
except Exception as _e:
    HASPLOT = False
    try:
        import pylab as plt
        HASPLOT = True
    except Exception as _e:
        HASPLOT = False
#---------------------------------------------------

def fitness(chaine):
    """
    prend en entree une chaine de caracteres et renvoie
    une valeur numerique : Il faudra surcharger
    """
    raise NotImplementedError("fitness: undef")

class Population(object):
    """
    tout ce qui a trait a la manipulation de la population
    dans un algorithme génétique
    """
    def __init__(self,nbIndividus,nbGenes,szGene,alphabet):
        """
        creation de la population initiale
        szChrom = nbGenes * szGene

        nbIndividus DOIT etre pair (si ce n'est pas le cas, augmenter de 1)
        genere une liste de taille nbIndividus de
        individu(szChrom,alphabet,fitness)
        """

        self.__szPop = nbIndividus + nbIndividus % 2

        self.__nbGenes = nbGenes
        self.__szGenes = szGene
        self.__alphabet = alphabet
        self.__szChrom = nbGenes * szGene
        del self.crossPoint 
        self.reset()

    def reset(self):
        """ permet de remettre tout à zéro """
        self.__popAG = [ Individu(self.szChrom,self.alphabet,fitness)
                         for _ in range(self.szPop) ]

        self.__proba = (.75,1e-3) # pc & pm par défaut
        self.__taux = .95 # la population a convergé quand 95% ...
        # des variables en cours de tests
        self.__maxAge = 500 # nombre max d'itérations
        self.restart() # tout ce qui est à réinitialiser
        
    def restart(self):
        """ ne remet que les compteurs à zéro """
        self.age = 0
        self.nbMut = 0
        self.nbCross = 0
        del self.best
        del self.history
        del self.scores
        del self.fitvalues
        del self.mostRepresentative
        # des flags
        self.__sorted = False


    #------------#
    # properties #
    #------------#

    #----------------- Attribut Read-Write ---------------------------#
    
    # pc : probabilité de croisement
    @property
    def pc(self):
        return self.__proba[0]
    @pc.setter
    def pc(self,pc):
        assert 0 <= pc <= 1
        self.__proba = pc,self.pm

    # pm : probabilité de mutation
    @property
    def pm(self):
        return self.__proba[1]
    @pm.setter
    def pm(self,pm):
        assert (0 <= pm <= 1)
        self.__proba = self.pc,pm

    # rateCVG : taux pour la convergence
    @property
    def rateCVG(self):
        return self.__taux
    @rateCVG.setter
    def rateCVG(self,taux):
        assert 0 < taux <= 1
        self.__taux = taux

    # la liste des Individus dans la populations courantes
    @property
    def popAG(self): return self.__popAG
    @popAG.setter
    def popAG(self,val):
        assert isinstance(val,list)
        assert len(val) == self.szPop
        for x in val : assert isinstance(x,Individu)
        self.__popAG = val
        del self.scores # les infos sont à recalculer

   # Quel croisement 1 point, 2 points ou uniforme
    def __get_cp(self): return self.__crossPoint
    def __set_cp(self,v):
        if v in (1,2,3) : self.__crossPoint = v
        else: self.__crossPoint = 1 # défaut
    def __del_cp(self):
        self.__crossPoint = 1
    crossPoint = property(__get_cp,__set_cp,__del_cp)

        
    # best: meilleur individu trouvé et la date de première apparition
    # best = bestIndividu, quand
    def __get_best(self):
        return self.__bestIndividu,self.__best_adequation,self.__iteration
    def __set_best(self,v):
        assert isinstance(v,Individu)
        self.__bestIndividu = v
        self.__best_adequation = v.adequation
        self.__iteration = self.age
    def __del_best(self):
        self.__bestIndividu,self.__best_adequation,self.__iteration = None,0,-1
    best = property(__get_best,__set_best,__del_best)

    # age: le nombre d'itérations faites
    @property
    def age(self): return self.__age
    @age.setter
    def age(self,v):
        assert isinstance(v,int)
        self.__age = v

    # nbMut : compte le nombre de mutations effectuées
    @property
    def nbMut(self): return self.__nbMut
    @nbMut.setter
    def nbMut(self,v):
        assert isinstance(v,int)
        self.__nbMut = v

    # nbCross : compte le nombre de croisements effectués
    @property
    def nbCross(self): return self.__nbCross
    @nbCross.setter
    def nbCross(self,v):
        assert isinstance(v,int)
        self.__nbCross = v

    # history garde la trace des stats par génération
    def __get_history(self): return self.__history
    def __del_history(self): self.__history = {}
    history = property(__get_history,None,__del_history)

    # mostRepresentative renvoie le chromosome "convergent"
    def __get_mostRepresentative(self):
        if self.__common is None :
            self.__common = self.__mostRepresentative()
        return self.__common
    def __del_mostRepresentative(self):
        self.__common = None
    mostRepresentative = property(__get_mostRepresentative,None,
                                  __del_mostRepresentative)

    # minimum, moyenne, maximum, somme sur la population
    def __get_scores(self):
        if not self.updated : self.evaluation()
        return self.__scores
    def __del_scores(self):
        self.__scores = None ; self.__updated = False
    # fitvalues & scores sont synonymes, n-uplet de valeurs
    fitvalues = scores = property(__get_scores,None,__del_scores)

    #-------- Attribut Read-Only ------------------------------#

    # nbGenes : le nombre de gènes par chromosome
    @property
    def nbGenes(self): return self.__nbGenes

    # szGenes : la taille d'un gène dans la population
    @property
    def szGenes(self): return self.__szGenes

    # alphabet : les lettres pour un chromosome
    @property
    def alphabet(self): return self.__alphabet

    # szChrom : = nbGenes * szGenes
    @property
    def szChrom(self): return self.__szChrom

    # szPop : nombre d'individus dans la population
    @property
    def szPop(self): return self.__szPop
 
    @property
    def bestEval(self):
        return self.__best_adequation
    @property
    def bestIndividu(self): return self.__bestIndividu
    @property
    def quand(self): return self.__iteration

    @property
    def updated(self): return self.__updated    
    
    ############
    # méthodes #
    ############

    def __str__(self):
        """ 
           affiche les informations de la 1ere et derniere generation 
           indique aussi si la population a convergé ou pas
        """
        _base = '-'*5
        _str = _base+'8<'+_base+'>8'+_base+'\n'
        _s = "nbIt: %d nbMut: %d nbCross: %d\n" %\
           (self.age,self.nbMut,self.nbCross)
        _s += "%d : %r\n" % (0,self.history.get(0,None) )
        _s += "%d : %r\n" % (self.age,self.history.get(self.age,None))
        if self.stable: _s += 'pop a converge generation %d\n' % self.age
        else: _s += "pop n'a pas converge\n"
        return _str+_s+_str

    def showHistory(self):
        """
        affichage de l'evolution de la population au fil des generations
        """
        for key in self.history:
            print( 'Generation %d ' % key, end=' ')
            _val,_best = self.history[key]
            for i,_lab in enumerate( ('min','moy','max') ):
                print( '%s = %2.2f ' % (_lab,_val[i]),end=' ' )
            print(*_best)
            
    def plotHistory(self,name=''):
        """
        permet une sauvegarde graphique de l'evolution de la population
        au fil des generations.
        @param name: chaine de caracteres pour le fichier de sortie
        """
        from os.path import exists, isdir
        _base = 'datas'
        if exists(_base) and isdir(_base): _fmt = _base + '/'
        else: _fmt = ''
            
        _fmt += 'graph%s_%s_%d-%d'
        _name = _fmt % (name,self.alphabet,self.szPop,self.age)

        if HASPLOT:

            _max = self.bestEval
            plt.axis([0, self.age, 0, _max*1.5]) #axes du graphe
            for i,_lab in enumerate( ('min','moy','max') ):
                datas = [ self.history[_][0][i] for _ in range(self.age) ]
                plt.plot(datas,label=_lab)
            _label='%s, pop : %d, bestfitness : %2.3f (age %s) ' %\
                    (name,self.szPop,self.bestEval,self.quand)
            plt.title(_label)
            plt.legend()
            plt.savefig(_name)      #sauvegarde du graphe
            print( 'sauvegarde dans',_name )
            plt.cla()       #efface les axes du graphe

        else:
            print( 'no plotting output available' )

    def sort(self,clef=None,rev=False):
        """
        tri utile pour faire de la selection par rang
            - population B{triee en fonction de la fitness}
            - sorted B{True}
        """
        self.popAG.sort(key=clef,reverse=rev)
        self.__sorted = True

    
    
    def __mostRepresentative(self):
        """ renvoie l'individu dont les gènes sont
        les plus présents dans la population """

        _fitness = self.popAG[0].fitness
        _alphabet = self.popAG[0].alphabet
        _szChrom = self.popAG[0].size
        _indclass = self.popAG[0].__class__
        _chrom = ''
        ng = 0
        while ng < self.nbGenes :
            _dGene = {}
            _istart = ng * self.szGenes
            _ifinal = _istart + self.szGenes
            for i in range(self.szPop):
                _sub = self.popAG[i].genotype[_istart:_ifinal]
                _dGene[_sub] = _dGene.get(_sub,0) + 1

            _taux = self.rateCVG * self.szPop
            _bgene,_vgene = None,0
            for gene in _dGene :
                if _dGene[gene] > _vgene :
                    _bgene = gene
                    _vgene = _dGene[gene]
            _chrom += _bgene
            ng += 1

        return _indclass(_szChrom,_alphabet,_fitness,_chrom)

    
    def nextGeneration(self,code=0):
        """
        reset du chromosome majoritaire
        listeCandidats = selection(population,code)
        tmpPop = croisement(listeCandidats)
        return mutation(tmpPop)
        """

        self._common = None
        _lstC = self.selection(code)
        _tmpC = self.croisement(_lstC)
        return self.mutation(_tmpC)

    def evaluation(self):
        """
        renvoie la valeur minimale, la moyenne, la valeur maximale
        et la valeur totale dans la population
        """
        if not self.updated:
            _min,_moy,_max,_sum = 1e10,0,0,0
            for x in self.popAG :
                x_attr = getattr(x,'adequation')
                _sum += x_attr 
                if _min > x_attr : _min = x_attr
                if _max < x_attr : _max = x_attr

            _moy = _sum / self.szPop

            self.__scores = _min,_moy,_max,_sum
            self.__updated = True
        return self.scores
    

    def select(self,code=0):
        """ la methode de selection """
        _select = {1: '_selectFraction', 2: '_selectRank' }
        return _select.get(code,'_selectWheel')
    
    def selection(self,code=0,nbParents=None):
        """
        Effectue la selection des individus,
        renvoie une liste d'individus de même taille que la population
        ne pas modifier
        """
        ## if code == 1 : return self._selectFraction(nbParents)
        ## else: return self._selectWheel(nbParents) # defaut
        return getattr(self,self.select(code))(nbParents)

    
    def _selectRank(self,nbParents=None):
        def rankPeople(vmax):
            _target = random.randrange(vmax)
            _sum = 0
            _nexti = 1
            while (_sum + _nexti) < _target:
                _sum += _nexti
                _nexti += 1
            return self.popAG[_nexti - 1]

        # tri de la population
        self.sort()
        # 0 + 1 + 2 + ... + n - 1 = n (n - 1) / 2
        _sum = self.szPop * (self.szPop - 1) / 2
        # selection des individus
        _pool = [ rankPeople(_sum) for x in self.popAG ]
        for x in _pool : x.reset()
        if nbParents is None :
            random.shuffle(_pool)
            return _pool
        
        return random.sample(_pool,nbParents)

       
            
    def croisement(self,listeIndividus):
        """
        prend les individus 2 par 2 dans listeIndividus
        R = random.random()
        si R <= pc fait appel à crossOver ; recopie sinon

        en sortie une liste de meme taille que population
        """
        _out = []
        _size = len(listeIndividus)
        for i in range(0,_size,2):
            _r = random.random()
            if _r <= self.pc :
                self.nbCross += 1
                _o = listeIndividus[i].crossOver(listeIndividus[i+1],
                                                 self.crossPoint)
            else:
                _o = listeIndividus[i],listeIndividus[i+1]
            _out.extend( _o )
        return _out


    def mutation(self,listeIndividus):
        """
        effectue une alteration des gènes avec une probabilité pm
        renvoie la population mutante
        """

        _nbMut = int( self.pm * self.szPop * self.nbGenes )
        i = 0
        while i < _nbMut :
            i += 1
            # mutation
            self.nbMut += 1
            x = random.choice(listeIndividus)
            x.mutatis( )

        return listeIndividus

    #----------------------- PARTIE A COMPLETER -------------------------#


    def run(self,nbIterations,fichier=None,code=0):
        """
        nbIterations le nombre maximum de fois ou on calcule une nouvelle
        generation.
        fichier : stockage du chromosome le meilleur
        code: type de selection (roue ou fraction)

        Algo:

        i = 0
        quand = 0
        popAG = initialisation(mettre les bons parametres)
        bestIndividu = max(popAG)
        initialiser l'historique
        while i < nbIterations and not isOver(popAG):
            popAG = nextGeneration(popAG)
            mettre a jour l'historique
            if bestIndividu < max(popAG) :
                bestIndividu = max(popAG)
                quand = i
            i += 1
        if isOver(popAG):
            print('stabilisation iteration',i)
        print('meilleur a iteration',quand,'adequation',bestIndividu.adequation)
        if fichier is not None : # fichier de sauvegarde
            with open(fichier,'w') as f : print(bestIndividu.genotype,file=f)

        return bestIndividu.genotype
        """
        raise Exception("TODO: run")

    def isOver(self):
        """
        renvoie vrai si on a convergence des genes dans la population
        """
        raise Exception("TODO: isOver")

    stable = property(isOver,None,None)
    
    def hasConverged(self,numGene):
        """
        renvoie Vrai si le gène numGene a convergé
        faux sinon
        """
        raise Exception("TODO: hasConverged")

    def _selectWheel(self,nbParents=None):
        """
        effectue un tirage aleatoire de n individus
        renvoie une liste d'individus de meme taille que la population
        voir le point 1 de 3.3 de la fiche de cours

        On construit la liste des probabilités de sélection
        pour chaque individu

        Tant qu'on n'a pas sélectionné assez d'individus
             tirer un nombre aleatoire : R = random.random()
             j = 0
             Tant que R > proba[j]
                R = R - proba[j]
                j = j + 1
             Ajouter individu numero j dans la selection
        Reinitialiser l'adequation de chaque sélectionné
        Renvoyer la sélection
        """
        if nbParents is None : nbParents = self.szPop
        _pop = []
        _min,_moy,_max,_sum = self.evaluation()
        _attr = 'adequation'

        if _sum != 0:
            _proba = [ getattr(x,_attr) / _sum for x in self.popAG ]
        else:
            print("computation failure : '{}'\n"
                  "{}".format(_attr,self.evaluation()))
            return self.popAG
            

        raise Exception("TODO _selectWheel")

    def _selectFraction(self,nbParents=None):
        """
        effectue un tirage aleatoire de n individus
        renvoie une liste d'individus de meme taille que la population
        voir le point 2 de 3.3 de la fiche de cours

        creer deux listes vide selection et residu
        Pour chaque individu x faire
             Ajouter x.adequation // adequation_moyenne fois x dans la selection
             Si x.adequation % adequation_moyenne > 0
                Ajouter x dans residu
        calculer n = taille_pop - len(selection)
        ajouter random.sample(residu,n) dans selection
        Reinitialiser l'adequation de chaque sélectionné
        melanger selection avec random.shuffle(selection)
        renvoyer selection
        """

        _pop = []
        _residu = []
        _min,_moy,_max,_sum = self.evaluation()


        raise Exception("TODO _selectFraction")

    #------------------------ FIN MODIFICATIONS -----------------------#

def test_main(crossP):

    print("_"*10)

    x = Population(10,7,1,'012')
    x.crossPoint = crossP

    for a in x.popAG :
        print (a.genotype,a.adequation)
    print( x.isOver(  ) )
    print("_"*10)
    y = Population(1,7,1,'012')
    y.popAG[0] = y.popAG[1] # on force les individus
    for a in y.popAG :
        print (a.genotype,a.adequation)
    print( y.isOver(  ) )

    for kode in range(4):
        print("_"*10)
        x = Population(23,7,1,'012')
        x.crossPoint = crossP
        x.run(250,code=kode)
        # version sortie graphique
        x.plotHistory(x.select(kode)+'crossP %d'%x.crossPoint)
        ## # version ecran ascii
        ## print(x.select(kode))
        ## x.showHistory()

        print(x,x.bestIndividu.genotype,
              x.bestIndividu.adequation,
              x.bestEval,
              x.bestIndividu.victoires)

        print('*'*5)
            ## input('<pause>')

if __name__ == "__main__" :
    fitness = lambda x: x.count('0') * x.count('2') - x.count('1') + 7

    for i in (1,2,3):
        test_main(i) ; input('<pause>')
