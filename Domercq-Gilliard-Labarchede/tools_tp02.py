#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Outils pour la simulation
* generateEnvts : écrit dans un fichier différents monde
* readerEnvts : lit un fichier produit par generateEnvts et stocke 
  les informations dans un dictionnaire
* readChromFromFile : lit une chaine dans un fichier
* findDiff : trouve le nombre de gènes différents entre deux chromosomes
* distance : un peu comme findDiff
* repartition : regarde le nombre de gènes de chaque sorte (renvoie un dictionnaire)
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__version__ = "0.3"
__date__ = "14.03.16"
__usage__ = "Quelques outils nécessaires pour la simulation génétique"


import random

def generateEnvts(fic,sample=5):
    """
    des tailles 3, 7, 11 pour les mondes avec deux objets
    des tailles 7, 11, 13 pour les mondes avec tous les objets
    un monde de taille 17.

    sample nombre de positions envisagées
    """
    def where(_t):
        """ cherche une position ou inserer un typ_ dans _t, 
            renvoie l'index choisi, on cherche en priorité une case propre
            On cherche a partir d'une position aléatoire entre _ et _ -1
        """
        _ = random.randrange(sz)
        _proba = random.random()
        if _proba <= .5:
            _found = False
            i = _
            _propre = _t.count(0)
            _val = 1 if _propre == 0 else 0
            while not _found:
                if _t[i] != _val: i = (i+1)%sz
                else: _found = True
            return i
        return -1

    random.seed() # initialisation du générateur aléatoire
    _obj = (0,1)
    with open(fic,"w") as f:
        # environement uniquement pour aspi sans capteurs (0)
        # que des 0,1 comme objets
        _taille = (3,5,7)
        for sz in _taille:
            _table = [ random.choice (_obj) for _ in range(sz)]
            if sample > sz: _pos = list(range(sz))
            else: _pos = random.sample( range(sz), sample)
            _ligne = [0, sz]+_table+_pos
            for x in _ligne: f.write("{} ".format(x))
            f.write('\n')
        # environement uniquement pour aspi sans et avec capteurs (2)
        # que des 0,1 comme objets
        _taille = (3,3,7,7,11,11)
        for sz in _taille:
            _table = [ random.choice (_obj) for _ in range(sz)]
            if sample > sz: _pos = list(range(sz))
            else: _pos = random.sample( range(sz), sample)
            _ligne = [2, sz]+_table+_pos
            for x in _ligne: f.write("{} ".format(x))
            f.write('\n')
        # environement uniquement pour aspi sans et avec capteurs (2)
        # 3 prises, au plus un objet deplaçable et un objet aspirable
        _taille = (7,7, 11,11,13,13,17)
        for sz in _taille:
            _table = [ random.choice (_obj) for _ in range(sz)]
            # 3 prises
            _prises = random.sample(range(sz),3)
            for _ in _prises: _table[_] = 2
            for v in (3,4):
                i = where(_table)
                if i > -1 : _table[i] = v
            if sample > sz: _pos = list(range(sz))
            else: _pos = random.sample( range(sz), sample)
            _ligne = [1, sz]+_table+_pos
            for x in _ligne: f.write("{} ".format(x))
            f.write('\n')
        f.close()

def readerEnvts(fic):
    """
    lit un fichier dont les lignes sont de la forme
    type colonne table p1 ... pk
    Toutes les valeurs sont des entiers
    renvoie un dictionnaire (typ,nbCol,table,positions) indexé sur les lignes
    """

    # print(fic)
    # import os
    # if fic in os.listdir(): print('ok')
    # else: print(fic,"not in",os.listdir())
    
    with open(fic,"r") as f:
        l = f.readlines()
        f.close()

    dic = {}
    #l contient des chaines
    for i,ligne in enumerate(l):
        values = [int(x) for x in ligne.strip().split()] # des entiers
        dic[i+1] = (values[0],values[1],
                    values[2:2+values[1]],values[2+values[1]:])

    return dic

#---- Utilitaires pour les chromosomes --------------------------------------#

def readChromFromFile(fichier):
    """ lecture d'un chromosome depuis un fichier """
    with open(fichier,"r") as f :
        _chrom = f.read().rstrip() # pas le '\n'
    return _chrom

def findDiff(chrom1,chrom2,szGene=1,verbose=True):
    """
    compare deux chromosomes et detecte le nombre de gènes
    différents
    """
    _ndiff = 0
    assert len(chrom1) == len(chrom2), "{} <> {}".format(len(chrom1),len(chrom2))
    nbGenes = len(chrom1) // szGene
    assert len(chrom1) == nbGenes * szGene, "{} <> {}*{}".format(len(chrom1),nbGenes,szGene)
    for gene in range(nbGenes) :
        _istart = gene * szGene
        _sub1 = chrom1[_istart:_istart+szGene]
        _sub2 = chrom2[_istart:_istart+szGene]
        if _sub1 != _sub2 :
            _ndiff += 1
            if verbose: print("gène %d : %s %s" % (gene,_sub1,_sub2))
    print("{} vs {} : {}%".format(_ndiff,nbGenes,round(100*_ndiff/nbGenes,2)))
    return _ndiff

def distance(ch1,ch2,szG=1):
    """
    calcul la distance entre deux chaines
    c'est le nombre de similarites des genes / nombre de gènes
    ou le nombre d'informations / la taille
    """
    lch1 = len(ch1) ; lch2 = len(ch2)
    assert lch1 == lch2, "bad size found %d vs d" % (lch1,lch2)
    if lch1 % szG != 0: _sz = lch1 ; _szg = 1
    else: _sz = lch1 // szG ; _szg = szG
    _sum = 0
    for i in range(_sz):
        d,f = i*_szg, (i+1)*_szg
        a,b = ch1[d:f],ch2[d:f]
        if a == b : _sum += 1
    return _sum / _sz

def repartition(chaine,szG=2,alphabet='01'):
    """ renvoie la répartition en fonction d'un alphabet et de la taille des gènes """
    store = dict()
    sz = len(chaine)
    assert sz % szG == 0, "{} is not k*{}".format(sz,szG)
    nbG = len(chaine) // szG
    for g in range(nbG):
        gene = chaine[g*szG:(g+1)*szG]
        store[gene] = store.get(gene,0) +1
    return store
