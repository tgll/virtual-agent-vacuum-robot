#!/usr/bin/python3
# -*- coding: utf-8 -*-

__usage__ = "Mise en place du TP02a"
__date__ = "10.03.16"
__version__ = "0.2"

# remplacer XXX par votre fichier issu du TD2 (le 00a)
from tp00a import objetsStatiques, Aspirateur, Monde
from briques import ProgramGenetic, GeneratePercept
import copy, random

class Aspirateur_PG(Aspirateur):
    """
        lCap: valeur par défaut []
        prog: un programme genetique, par défaut None
    """
    def __init__(self,prog=None,gp=None,lCap=[]):
        # gestion du GeneratePercept choisir la variable de stockage
        if gp is not None: generatep = gp
        elif lCap == []: generatep = None
        else: generatep = GeneratePercept(lCap,objetsStatiques)


        #Création du programme génétique
        if prog is None:
            # choisir le nom de votre variable, remplacez les ...
            dicaction={"A":"Aspirer","G":"Gauche","D":"Droite","R":"Repos"}
            if lCap==[]:
                programme = ProgramGenetic(1,8,['A','G','D','R'],dicaction)
            else:
                programme = ProgramGenetic(1,generatep.howMany,['A','G','D','R'],dicaction)
        elif isinstance(prog,ProgramGenetic):
            if lCap!=[]:
                if gp.howMany!=len(prog):
                    raise AssertionError("the generatepercept don't match the program")
            programme = prog
        else:
            raise AssertionError("{} expected got {}"
                                 .format(ProgramGenetic,type(prog)))
        
        # récupération des actions depuis votre variable
        # attention ce n'est pas une 'list' c'est un 'set'
        lAct = list(programme.actions)
        super().__init__(lCap,lAct)
        self._dicAspi["gp"]=generatep
        self._dicAspi["programme"]=programme
        # choisir la variable pour energie
        self._dicAspi["energie"]= 100
        self._dicAspi["cpt"]=0
        self.reset()

    def reset(self):
        """ initialisation de certaines variables pour chaque simulation """
        self.vivant = True
        self.cpt = 0
        self.energie=100
        self._dicAspi["nbTours"]=0
	#ici rajouter celles dont vous pensez avoir besoin
        
    @property
    def energie(self): return self._dicAspi["energie"]
    @energie.setter
    def energie(self,v):
        assert isinstance(v,int), "int expected found {}".format(type(v))
        self._dicAspi["energie"] = max(0,min(100,v)) # force la valeur entre 0 et 100
        # attention si energie passe a 0 ...
        if self.energie==0:self._dicAspi["vivant"]=False

    # On surcharge vivant
    @property
    def vivant(self): return self._dicAspi["vivant"]
    @vivant.setter
    def vivant(self,v):
        if isinstance(v,bool): self._dicAspi["vivant"] = v
    @property
    def nbTours(self): return self._dicAspi["nbTours"]
    @property
    def cpt(self): return self._dicAspi["cpt"]
    @cpt.setter
    def cpt(self,v):
        assert isinstance(v,int)
        self._dicAspi["cpt"]=max(0,v%len(self.program)) # attention cpt est contraint entre 0 et le nombre de genes
        
    @property
    def program(self): return self._dicAspi["programme"]
    @property
    def gp(self): return self._dicAspi["gp"]

    def getEvaluation(self):
        """ renvoie l'évaluation de l'agent """
        score=0
        if self.sale!=0:
            score = (self.nettoyage/self.sale) * 10

        if not self.vivant:score -= 100
        elif self.energie < 25 :score += 1/2 * self.energie / 100
        elif self.energie < 50 : score += 2/3 * self.energie / 100
        elif self.energie < 75 : score += 3/4 * self.energie / 100
        else: score += self.energie / 100

        return score
    
    def getDecision(self,percepts):
        """ deux cas à traiter suivant que percepts = [] ou pas """
        self._dicAspi["nbTours"]+=1
        if percepts == []:
            # on utilise cpt pour savoir ce qu'il faut lire/récupérer
            choix=self.program.decoder(self.cpt)
            self.cpt+=1
            if self.cpt==len(self.program):
                self.cpt=0
            return choix
        # a partir d'ici on est dans le cas ou l'agent percoit
        # il faut associer au percepts un numéro et aller regarder
        # quelle est l'instruction à renvoyer
        choix=self.program.decoder(self._dicAspi["gp"].find(percepts))
        return choix


class Monde_AG(Monde):
    def __init__(self,agent,nbLignes=1,nbColonnes=2):
        # On regarde si l'agent à une variable energie
        assert hasattr(agent,'energie'), "attribut 'energie' is required"
        super().__init__(agent,nbLignes,nbColonnes)

    
    def initialisation(self):
        #Done
        super().initialisation()
        # ajouter à l'agent un compteur de pièces nettoyées, initalisé à 0
        # ajouter à l'agent le nombre de pièces sales au départ
        # On regarde si l'agent a une commande reset
        if hasattr(self.agent,'reset') and callable(self.agent.reset):
            self.agent.reset()
        #placement des prises en suivant la contrainte: si monde a plus de 3 cases, exactement 3 prises
        if self._d["col"]*self._d["row"]>3:
            place1,place2,place3=(0,0),(0,0),(0,0)
            while place1==place2 or place1==place3 or place2==place3:
                    place1=(random.randrange(self._d["row"]),random.randrange(self._d["col"]))
                    place2=(random.randrange(self._d["row"]),random.randrange(self._d["col"]))
                    place3=(random.randrange(self._d["row"]),random.randrange(self._d["col"]))
            self._d["table"][place1[0]][place1[1]]=2
            self._d["table"][place2[0]][place2[1]]=2
            self._d["table"][place3[0]][place3[1]]=2

        #nombre de cases nettoyées par l'agent
        self.agent.nettoyage=0.0
        #nombre de fois où l'agent s'est reposé
        self.agent.repos=0.0
        #Compte le nombre de cases sales
        self.agent.sale=0.0
        for i in self.table:
            self.agent.sale+=i.count(1)
    def getPerception(self,capteurs):
        #getPerception terminé
        """ informe l'agent en fonction des capteurs """
        # code similaire à celui de World
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
       #ApplyChoix terminé
        """ 
            modifie table & posAgent en fonction de choix 
            modifie l'energie de l'aspirateur
        """
        assert (action in self.agent.actions),"L'aspirateur ne connait pas cette action"
        self._d["historique"].append(((self.table,self.posAgent),action))
        if action =="Aspirer" :
            self.agent.energie=self.agent.energie-5
            if self._d["table"][self.posAgent[0]][self.posAgent[1]]==1:
                feedback=2
                self._d["table"][self.posAgent[0]][self.posAgent[1]]=0
                self.agent.nettoyage+=1
            else:
                feedback=-1.0
        elif action=="Gauche" :
            self.agent.energie=self.agent.energie-1
            if self._d["posAgent"][1]!=0:
                self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]-1)
                feedback=1.0
            else:
                feedback=-1.0
        elif action=="Droite" :
            self.agent.energie=self.agent.energie-1
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

    @property
    def perfGlobale(self):
        # cf fiche TP02-A
        return (self.agent.getEvaluation()/self.optimumTheorique-self.agent.repos+len(self.table[0]))
    @property
    def optimumTheorique(self):
        #maximum theorique:toutes les cases sales du départ sont nettoyées et l'aspirateur a 100 d'energie
        return 11

