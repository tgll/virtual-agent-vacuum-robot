#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Et maintenant ... ça tourne:
Un chromosome pour aspi sans capteurs doit avoir 20 gènes
Un chromosome pour aspi avec capteurs sera basé sur GeneratePercept
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__version__ = "0.3"
__date__ = "15.03.16"
__usage__ = "Utilisation de l'algo génétique"

# remplacer XXXX par votre fichier correspondant au tp02b
from XXXX import objetsStatiques, Aspirateur_PG, MondeSimulation
from XXXX import Simulateur
from briques import ProgramGenetic, mmcUnaire, mmcBinaire, GeneratePercept
from tools_tp02 import generateEnvts
import agslib

class PopAspi(agslib.Population):
    """ création de l'aspect généique avec accès au simulateur pour faire l'évaluation """
    def __init__(self,nbIteration,fichier,capteurs,envt,nbIndiv,szGene,alphabet,decodeur,panne=False):
        self.__sim = Simulateur(nbIteration,fichier,capteurs,panne)
        if capteurs == []: self.__nbG = 20 ; self.__gp = None
        else: self.__gp = GeneratePercept(capteurs,envt) ; self.__nbG = self.__gp.howMany
        self.__prog = ProgramGenetic(szGene,self.__nbG,alphabet,decodeur)
        super().__init__(nbIndiv,self.__nbG,szGene,alphabet)
        for x in self.popAG : x.fitness = lambda _ : self.simEval( _ )
         
    @property
    def simulator(self): return self.__sim
    @property
    def prog(self): return self.__prog
    @property
    def gp(self): return self.__gp
    @property
    def nbGenes(self): return self.__nbG
    def simEval(self,chaine):
        self.prog.program = chaine
        return max(.1,self.simulator.run( self.prog, self.gp )) # garantit des scores positifs


def main(fichier):
    """ utilise fichier ou genere fichier 

    On va évaluer un aspirateur effectuant 10 actions dans différents envts
    On va mettre en compétition 50 aspirateurs du meme type
    p = PopAspi(10,...,50,...)

    L'algorithme génétique fait 25 itérations
    p.run(25,...)

    select(0) = _selectWheel
    select(1) = _selectFraction
    select(2) = _selectRank
    """
    import os
    if fichier in os.listdir():
        print("{} existe".format(fichier))
        _rep = "oO0Yy"
        _you = input("voulez vous utiliser ce fichier "+_rep+" ? ")
        if _you not in _rep :
            print("génération d'environnements de tests")
            generateEnvts(fichier)
    else:
        print("génération d'environnements de tests")
        generateEnvts(fichier)

        
    _base = fichier.split('.')[0]
    p = PopAspi(10,fichier,[2,6,8],objetsStatiques,50,2,'01',
                mmcBinaire,True)
    _oname = _base+"_AG_01.txt"
    p.run(25,_oname,0)
    # ne marche que si vous avez pensé à utiliser historique dans run (agslib)
    p.plotHistory(_base+p.select(0)+'_genes_'+'01'+'_withPanne')
    _oname = _base+"_AG_01_b.txt"
    p.run(25,_oname,1)
    # ne marche que si vous avez pensé à utiliser historique dans run (agslib)
    p.plotHistory(_base+p.select(1)+'_genes_'+'01'+'_withPanne')
    p = PopAspi(10,fichier,[2,6,8],objetsStatiques,50,1,'AGDR',
                mmcUnaire,False)
    _oname = _base+"_AG_AGDR.txt"
    p.run(25,_oname,0)
    # ne marche que si vous avez pensé à utiliser historique dans run (agslib)
    p.plotHistory(_base+p.select(0)+'_genes_'+'AGDR'+'_noPanne')
    _oname = _base+"_AG_AGDR_b.txt"
    p.run(25,_oname,1)
    # ne marche que si vous avez pensé à utiliser historique dans run (agslib)
    p.plotHistory(_base+p.select(1)+'_genes_'+'AGDR'+'_noPanne')

if __name__ == "__main__" :
    main('tyty2.txt')

