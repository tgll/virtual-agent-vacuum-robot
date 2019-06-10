import random
from random import randrange
from copy import deepcopy
from briques import *
objetsStatiques={0:("vide"," "),100:("agent","@"),1:("poussière","P"),-1:("pas d'information","I"),2:("Prise éléctrique","E")}

class Aspirateur(object):
    def __init__(self, capt=[],act=['Gauche','Droite','Aspirer']):
        self._dicAspi={}
        stock=[]
        assert(isinstance(act,(list,tuple))), "Problème actions mauvais type"
        for i in capt:
            assert(isinstance(i,int)), "Problème capteur inconnu"
            assert(i not in stock), "Problème capteur en double"
            stock.append(i)
        self._dicAspi['vivant']=True
        self._dicAspi['capteurs']=capt
        self._dicAspi['actions']=act
        self._dicAspi['rewards']=[]
        self._dicAspi["choice"]=""


    @property
    def choice(self):
        return self._dicAspi['choice']
    @property
    def vivant(self):
        return self._dicAspi['vivant']
    @property
    def capteurs(self):
        return deepcopy(self._dicAspi['capteurs'])
    @property
    def actions(self):
        return deepcopy(self._dicAspi['actions'])
    @property
    def rewards(self):
        return deepcopy(self._dicAspi['rewards'])

    def getLastReward(self):
        if self.rewards==[]:
            return 0.0
        else:
            return self.rewards[len(self.rewards)-1]

    def setReward(self,feedback):
        #collecte le feedback
        assert(isinstance(feedback,(int,float))),None
        self._dicAspi['rewards'].append(float(feedback))

    def getDecision(self,percepts):
        """Prend la décision de l'action à effectuer en fonction de la perception de l'agent"""
        assert(isinstance(percepts,list)),None
        assert (len(percepts)==len(self.capteurs)),None
        for i in percepts:
            assert(i in objetsStatiques),"l'élément n'est pas dans objetsStatique"
        #temporaire
        choice=randrange(len(self.actions))
        self._dicAspi["choice"]=self.actions[choice]
        return self.actions[choice]

    def getEvaluation(self):
        c=0
        for i in self.rewards:
            if i==2:
                c+=1
        evaluation=(c+1) # Cet aspirateur fait ses choix aléatoirement donc len(KB) est nul
        return (evaluation)




    
class Monde(object):
    def __init__(self,aspi,row=1,col=2):
        assert(isinstance(aspi,Aspirateur)),None 
        self._d={}
        self._d["agent"]=aspi
        self._d["col"]=col
        self._d["row"]=row
        self._d["objets"]=[k for k in objetsStatiques if (0<=k<100 and k!=2)]
        self.initialisation()
    @property
    def agent(self):
        return self._d["agent"]
    @property
    def table(self):
        table=deepcopy(self._d["table"])
        return table
    @property
    def posAgent(self):
        return deepcopy(self._d["posAgent"])
    @property
    def perfGlobale(self):
        if len(self.historique)==0:
            return 0.0
        table1=self.historique[0][0][0]
        tablefinale=self.historique[len(self.historique)-1][0][0]
        #nombre de cases nettoyées
        clean=0
        for i in range(self._d["row"]):
            for j in range(self._d["col"]):
                if table1[i][j]==1 and tablefinale[i][j]==0:
                    clean+=1
        #nombre de cases visitées plus de 3 fois
        tablevisit=[[0 for i in range(self._d["col"])]for j in range(self._d["row"])]
        time=0
        for i in self.historique:
            tablevisit[i[0][1][0]][i[0][1][1]]+=1
        for i in tablevisit:
            for j in i:
                if j>=3:
                    time+=1
        return (clean-time)

        
    @property
    def historique(self):
        return deepcopy(self._d["historique"])
    @property
    def objets(self):
        return deepcopy(self._d["objets"])

    
    def initialisation(self):
        """Initialise le monde"""
        self._d["historique"]=[]
        self._d["table"]=[[random.choice(self.objets) for i in range (self._d["col"])] for j in range (self._d["row"])]
        self._d["posAgent"]=(randrange(self._d["row"]),randrange(self._d["col"]))

    def simulation(self,n):
        """Effectue une simulation"""
        self.initialisation()
        i=0
        while (i<n) and (self.agent.vivant):
            self.step()
            i+=1
        #renvoi note performance
        return self.perfGlobale

    def step(self):
        """Pas de la simulation"""
        percepts=self.getPerception(self.agent.capteurs)
        action=self.agent.getDecision(self.getPerception(self.agent.capteurs))
        self.agent.setReward(self.applyChoix(action))
        self.updateWorld()
        

    def updateWorld(self):
        """Evenements du monde indépendants de l'agent"""
        return None

        
    def applyChoix(self,action):
        """Effectue l'action de l'agent et le stock dans l'historique"""
        assert (action in self.agent.actions),"L'aspirateur ne connait pas cette action"
        self._d["historique"].append(((self.table,self.posAgent),action))
        #Erreur feedback action inconnue
        feedback=-5.0
        if action=="Aspirer":
            if self._d["table"][self.posAgent[0]][self.posAgent[1]]==1:
                feedback=2.0
                self._d["table"][self.posAgent[0]][self.posAgent[1]]=0
            else:
                feedback=0.0
        elif action=="Gauche" and self._d["posAgent"][1]!=0:
            self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]-1)
            feedback=1.0
        elif action=="Gauche":
            feedback=-1.0
        elif action=="Droite" and self._d["posAgent"][1]!=self._d["col"]-1:
            feedback=1.0
            self._d["posAgent"]=(self._d["posAgent"][0],self._d["posAgent"][1]+1)
        elif action=="Droite":
            feedback=-1.0
        return feedback
                                                
    def getPerception(self,capteurs):
        """"Indique quels sont les objets perçus par l'agent"""
        percept=[]
        for i in range(len(capteurs)):
            if capteurs[i]==0 and self.posAgent[0]!=0:
                percept.append(self.table[self.posAgent[0]-1][self.posAgent[1]])
            elif capteurs[i]==1 and self.posAgent[0]!=0 and self.posAgent[1]!=self._d["col"]-1:
                percept.append(self.table[self.posAgent[0]-1][self.posAgent[1]+1])
            elif capteurs[i]==2 and self.posAgent[1]!=self._d["col"]-1:
                percept.append(self.table[self.posAgent[0]][self.posAgent[1]+1])
            elif capteurs[i]==3 and self.posAgent[0]!=self._d["row"]-1 and self.posAgent[1]!=self._d["col"]-1:
                percept.append(self.table[self.posAgent[0]+1][self.posAgent[1]+1])
            elif capteurs[i]==4 and self.posAgent[0]!=self._d["row"]-1 :
                percept.append(self.table[self.posAgent[0]+1][self.posAgent[1]])
            elif capteurs[i]==5 and self.posAgent[0]!=self._d["row"]-1 and self.posAgent[1]!=0:
                percept.append(self.table[self.posAgent[0]+1][self.posAgent[1]-1])
            elif capteurs[i]==6 and self.posAgent[1]!=0:
                percept.append(self.table[self.posAgent[0]][self.posAgent[1]-1])
            elif capteurs[i]==7 and self.posAgent[0]!=self._d["row"]-1 and self.posAgent[1]!=0:
                percept.append(self.table[self.posAgent[0]-1][self.posAgent[1]-1])
            elif capteurs[i]==8:
                percept.append(self.table[self.posAgent[0]][self.posAgent[1]])
            else:
                percept.append(-1)
        return percept
            
                    
    def __str__(self):
        """Permet d'afficher le monde"""
        chain="+"
        tableaffich=self.table
        for i in range(self._d['col']):
            chain+="--+"
        chain+="\n"
        for j in range(self._d['row']):
            chain+="|"
            for i in range (self._d["col"]):
                if self._d["posAgent"]==(j,i):
                    chain+=objetsStatiques[100][1]
                else:
                    chain+=" "
                chain+=objetsStatiques[tableaffich[j][i]][1]
                chain+="|"
            chain+="\n"
        chain+="+"
        for i in range(self._d['col']):
            chain+="--+"
        return chain

