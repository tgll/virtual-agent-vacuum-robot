#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Mise en place de la correction en fonction du descriptif TP02-B
Complétez les informations en fonction des directives de la fiche
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__version__ = "0.1"
__date__ = "14.03.16"
__usage__ = "Le simulateur"

# remplacer XXX par le fichier du TP02-A
from tp02a import objetsStatiques, Aspirateur_PG, Monde
#from corrige_tp02a import objetsStatiques, Aspirateur_PG, Monde
from briques import ProgramGenetic, mmcUnaire, mmcBinaire, GeneratePercept
from tools_tp02 import readerEnvts
import copy, random

# On ajoute dans objetsStatiques 2, 3 et 4 et -1
#2 et -1 déja dans tp00a
objetsStatiques[3] = ("jouet aspirable","J")
objetsStatiques[4] = ("objet déplaçable","D")


class MondeSimulation(Monde):
    def __init__(self,agent,nbLignes=1,nbColonnes=2):
        assert hasattr(agent,'energie'), "attribut 'energie' is required"
        super().__init__(agent,nbLignes,nbColonnes)

    def simulation(self,n,envt=None,position=None):
        """ 
            la simulation dure max n tours et s'arrete des que l'agent 
            n'est plus opérationnel
        """
        
        self.initialisation(envt,position)
        self.NbTourMax=n
        c=0
        while (c<n and self.agent.vivant):
            self.step()
            c+=1
        return self.perfGlobale

    def initialisation(self,envt=None,position=None):
        super().initialisation()
        if envt is not None: self._d["table"] = [ envt ]
        if position is not None: self.d["posAgent"] = 0,position
        
        #nombre de cases nettoyées par l'agent
        self.agent.nettoyage=0.0
        #nombre de fois où l'agent s'est reposé
        self.agent.repos=0.0
        #Compte le nombre de cases sales
        self.agent.sale=0.0
        for i in self.table:
            self.agent.sale+=i.count(1)
        #Compte le nombre d'objets aspirables
        self.agent.aspirable=0.0
        for i in self.table:
            self.agent.aspirable+=i.count(3)
    
        # print(self.table) facultatif
        if hasattr(self.agent,'reset') and callable(self.agent.reset):
            self.agent.reset() 
        
    @property
    def perfGlobale(self):
        # Voir fiche TP02-B
        aspirablerestant=0.0
        for i in self.table:
            aspirablerestant+=i.count(3)
        result=(self.agent.energie/100)+(self.agent.nettoyage/self.sale)+(aspirablerestant/self.agent.aspirable)+(self.agent.nbTours/self.NbTourMax)
    def getPerception(self,capteurs):
        """ 
           informe l'agent en fonction des capteurs 
           gestion des risques de panne (proba fixée à .1) 1 parmi k
        """
        _d = [ (-1,0), (-1,1), (0,1), (1,1),
                (1,0), (1,-1), (0,-1), (-1,-1), (0,0) ]

        kapteurs = capteurs[:] # on fait une copie pour les pannes
        if 8 in kapteurs: kapteurs.remove(8) # pas de panne sur le 8
        _panne = -1 # pas de panne
        if (hasattr(self.agent,'panne') and
            getattr(self.agent,'panne') and
            len(kapteurs) > 0):
            _proba = random.random()
            if _proba < .1 : _panne = random.choice(kapteurs)

        #if _panne > -1: print("panne sur le capteur {}".format(_panne))
        
        # calculer ce que voit l'agent, s'il y a une panne sur le capteur
        # _panne : mettre -1 au lieu de l'information dans la table
        # renvoyer la réponse (une liste de la taille de capteurs)
        percept=[]
        for x in capteurs:
            if x==_panne:
                percept.append(-1)
            else:
                nx = self.posAgent[0]+delta[x][0]
                ny = self.posAgent[1]+delta[x][1] 
                if  self._d["row"]>nx >= 0 and self._d["col"]> ny >= 0  :
                    percept.append(self.table[nx][ny])
                else:
                    percept.append(-1)
        return percept
    def applyChoix(self,choix):
        """
           Modifie table & posAgent en fonction de choix
           Modifie la fonction d'énergie de l'Aspirateur
           Renvoie la récompense numérique adéquate

           Récompenses :
           Aspirer : 2 si poussière, -3 si jouets aspirables, -1 sinon
           Gauche / Droite : 1 si possible, -1 sinon
           Repos : 2 si prise électrique, 0 sinon

           Effet Energie
           Aspirer: -5
           Gauche / Droite : -2
           Repos sans capteur +3
           Repos avec capteur +20 si prise électrique, 0 sinon
        """
        # Appliquer les opérations demandées
        # mise à jour de self.agent.energie
        # renvoie de la récompense
        # mise à jour des compteurs utiles
        assert (action in self.agent.actions),"L'aspirateur ne connait pas cette action"
        self._d["historique"].append(((self.table,self.posAgent),action))
        if action =="Aspirer" :
            self.agent.energie=self.agent.energie-5
            if self._d["table"][self.posAgent[0]][self.posAgent[1]]==1:
                feedback=2
                self._d["table"][self.posAgent[0]][self.posAgent[1]]=0
                self.agent.nettoyage+=1
            elif self._d["table"][self.posAgent[0]][self.posAgent[1]]== 3:
                feedback=-3
                self._d["table"][self.posAgent[0]][self.posAgent[1]]=0
            else:
                feedback=-1.0

        elif action=="Gauche" :
            self.agent.energie=self.agent.energie-2
            if self._d["posAgent"][1]!=0:
                self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]-1)
                feedback=1.0
            else:
                feedback=-1.0

        elif action=="Droite" :
            self.agent.energie=self.agent.energie-2
            if self._d["posAgent"][1]!=self._d["col"]-1:
                feedback=1.0
                self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]+1)
            else:
                feedback=-1.0

        elif action=="Repos":
            self.agent.repos+=1
            if self.agent.capteurs==[]:
                self.agent.energie=self.agent.energie+3
                feedback=0.0
            elif self._d["table"][self.posAgent[0]][self.posAgent[1]]==2:
                self.agent.energie=self.agent.energie+20
                feedback=2.0
            else:
                feedback=0.0
        
        return feedback   
        
class Simulateur(objet):
    """ En entrée:
        - le nombre maximum d'itérations
        - le fichier des environnements
        - la liste des Capteurs
        - le fait qu'il peut y avoir des pannes
    """
    def __init__(self,nbMaxIter,ficEnvt,lCap=[],panne=False):
        # stocker les parametres dans 4 variables privées self.__XXX
        self.__maxiter=nbMaxIter
        self.__fichier=ficEnvt
        self.__cap=lCap
        self.__panne=panne
    @property
    def panne(self): return self.__panne
    @panne.setter
    def panne(self,v):
        """
           si pas de capteur on se moque de v, on force xxx à False
           si capteur alors on prend bool(v) comme valeur
        """
        if self.__cap!=[]:
            self.__panne=bool(v)
    def run(self,prog,gp=None):
        """
        prog est un ProgramGenetic
        gp est un GeneratePercept optionnel
        
        crée l'aspirateur Aspirateur_PG
        ajoute l'information panne à l'aspirateur
        met un compteur a 0
        détermine quels environnements seront utilisables 0, 1, 2
        pour chaque environnement
             s'il n'est pas utilisable : continue
             creer m = MondeSimulation(aspirateur,1,nbCol)
             pour chaque position a tester
                 compteur = compteur + m.simulation(nbIter,table,position)
        renvoyer compteur
        
        renvoie le score total obtenu pour chaque simulation,
        on aurait pu prendre non pas le score de la imulation mais
        celui de la performance de l'agent ou une combinaison des deux
            exemple: alpha perfGlobale + beta getEvaluation()
            total_sim = 0 ; total_agent = 0
            alpha = .5 ; beta = 1 - alpha
            ....
            for p in _lpos:
                total_sim += m.simulation( .... )
                total_agent += m.agent.getEvaluation()
            ...
            return alpha * total_sim + beta * total_agent
        """
        aspi=Aspirateur_PG(prog,gp,self.__cap)
        aspi.panne=self.panne
        envs=[0,1,2]
        #envt 0: obj={0,1} cap=[]
        #envt 1: obj={0,1,2} cap!=[]
        #envt 2: obj={1,2,3,4}
        for i in envs:
            pass
