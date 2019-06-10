#!/usr/bin/python3
# -*- coding: utf-8 -*-

__usage__ = "Mise en place du TP01"
_date__ = "09.02.16"
__version__ = "0.1"

# remplacer XXX par votre fichier issu du TD2
from tp00a import objetsStatiques, Aspirateur, Monde
from briques import Rule, KB
import copy
import random
from random import randrange

class Aspirateur_KB(Aspirateur):
##        probaExploitation: explo
##        lCap: [2]
##        lAct: act='Aspirer'
##        learn: False #(pas d'apprentissage)

    def __init__(self,probaExploitation,lCap=[],lAct="Gauche Droite Aspirer".split(),learn=False):
        super(Aspirateur_KB,self).__init__(lCap,lAct)
        assert 0 <= probaExploitation <= 1, "Probability expected"
        assert isinstance(learn,bool), "Boolean expected got %s" % type(learn)
        self._dicAspi["know"] = KB() # base de données vide
        self._dicAspi["exploit"] = probaExploitation
        self._dicAspi["learn"] = learn
        self._dicAspi["lastaction"] = None # dernière action choisie
        self._dicAspi["lastpercept"] = None # dernier percept reçu
        self.compteurs = {'alea': 0, 'exploitation' : 0, 'total' : 0, 'exploration': 0}


   
    @property
    def apprentissage(self): return self._dicAspi["learn"]
    @apprentissage.setter
    def apprentissage(self,v):
        assert(isinstance(v,bool)),"Learn doit etre un booléen"
        self._dicAspi["learn"]=v

    @property
    def knowledge(self): return copy.deepcopy(self._dicAspi["know"])
    @knowledge.setter
    def knowledge(self,v):
        assert(isinstance(v,KB)),"La base de connaissance doit être un KB"
        self._dicAspi["know"]=v
    @property
    def probaExploitation(self): return self._dicAspi["exploit"]
    
    def getEvaluation(self):
        c=self.rewards.count(2) #nombre de pieces néttoyées
        evaluation=(c+1)/(len(self.knowledge)+1) 
        return (evaluation)
        
    def getDecision(self,percepts):
        assert isinstance(percepts,(list,tuple)), "%s should be list or tuple" % percepts
        assert len(percepts) == len(self.capteurs), "percepts and capteurs do not match"
        assert all([ x in objetsStatiques for x in percepts ]), "bad percepts %s" % percepts
        self._dicAspi["lastpercept"]=percepts
        regles=self.knowledge.find(percepts)
        bestact=Rule([],"",-5)
        
        if len(regles)==0:
            action=random.choice(self.actions)
            self.compteurs['alea'] += 1
        else:
            for j in regles:
                if bestact.scoreMoyen<j.scoreMoyen:bestact=j
            regles.remove(bestact)
            if ((randrange(100))/100)<self.probaExploitation:
                action=bestact.conclusion
                self.compteurs['exploitation'] += 1
            else:
                if len(regles)!=0:
                    choix=random.choice(regles)
                    if choix.scoreMoyen<0:
                        action=random.choice(self.actions)
                    else:
                        action=choix.conclusion
                else:
                    action=random.choice(self.actions)
                self.compteurs['exploration'] += 1
        self.compteurs['total'] += 1
        self._dicAspi["lastaction"]=action
        return action
    def setReward(self,value):
        super(Aspirateur_KB,self).setReward(value)
        if self.apprentissage:
            r=Rule(self._dicAspi["lastpercept"],self._dicAspi["lastaction"],self.getLastReward())
            self._dicAspi["know"].add(r)
            
        
class World(Monde):
    """ constructeur avec 3 paramètres, syntaxe identique au constructeur de Monde """
    def __init__(self,agent,nbLignes=1,nbColonnes=2):
        super(World,self).__init__(agent,nbLignes,nbColonnes)
        self.initialisation()
        
    def initialisation(self):
        super(World,self).initialisation()
        # creer une variable privée qui va servir à compter le nombre de fois ou l'agent est dans
        # une case donnée. La variable est donc une liste de liste dont chaque valeur est à 0
        self._d["count"] = [ [0 for j in range(len(self.table[0])) ] for i in range(len(self.table))]
        i,j = self.posAgent
        self._d["count"][i][j] = 1
        # ajoute à l'agent un compteur de pièces nettoyées, initalisé à 0
        self.agent.nettoyage = 0


    def getPerception(self,capteurs):
        """ informe l'agent en fonction des capteurs """
        # renvoie la liste des valeurs contenues dans self.table[nx][ny]
        delta = [ (-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1), (0,0) ]
        percept=[]
        for x in capteurs:
            nx = self.posAgent[0]+delta[x][0]
            ny = self.posAgent[1]+delta[x][1] 
            if  self._d["row"]>nx >= 0 and self._d["col"]> ny >= 0  :
                percept.append(self.table[nx][ny])
            else:
                percept.append(-1)
        return percept
        
    def applyChoix(self,action):
        """ modifie table & posAgent en fonction de choix """
        assert (action in self.agent.actions),"L'aspirateur ne connait pas cette action"
        self._d["historique"].append(((self.table,self.posAgent),action))
        if action =="Aspirer" :
            if self._d["table"][self.posAgent[0]][self.posAgent[1]]==1:
                feedback=2
                self._d["table"][self.posAgent[0]][self.posAgent[1]]=0
                self.agent.nettoyage+=1
            else:
                feedback=0
        elif action=="Gauche" :
            if self._d["posAgent"][1]!=0:
                self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]-1)
                feedback=1.0
            else:
                feedback=-1.0
        elif action=="Droite" :
            if self._d["posAgent"][1]!=self._d["col"]-1:
                feedback=1.0
                self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]+1)
            else:
                feedback=-1.0
        self._d["count"][self._d["posAgent"][0]][self._d["posAgent"][1]]+=1
        return feedback    
    @property
    def count(self):
        return copy.deepcopy(self._d["count"])
    @property
    def perfGlobale(self):
        # return nombre de pièces nettoyées − nombre de pièces visitées 3 fois ou plus
        times=0
        for i in self._d["count"]:
            for j in i:
                if j>=3:times+=1
        return(self.agent.nettoyage-times)
