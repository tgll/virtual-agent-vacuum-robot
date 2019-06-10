from tp01 import Aspirateur_KB, World, KB, Rule, objetsStatiques
import numpy as np # pour faire des stats simples

def test_performance(w,n,nb=10):
    """
        w: le monde qui fait la simulation
        n: la durée d'une simulation
        nb: le nombre total de simulation
        
        ATTENTION: compteurs est un dictionnaire que j'ai ajouté à Aspirateur_KB et qui est réinitialisé
        à chaque simulation, il est rempli dans Aspirateur_KB.getDecision
    """
    assert isinstance(w,World),"World instance required"
    _resultat={'agent': [], 'world': [], }
    for i in range(nb):
        print("simulation %02d" % (i+1))
        w.simulation(n)
        print(w.agent.compteurs)
        _resultat['agent'].append(w.agent.getEvaluation())
        _resultat['world'].append(w.perfGlobale)
        print("eval agent {0[agent]} vs perf globale {0[world]}".format(_resultat))
        print(w) ; print("table: {0.table} posAgent is {0.posAgent}".format(w))
        print(w.agent.knowledge)
        print("Historique")
        for i,((t,p),a) in enumerate(w.historique):
            print("%02d: table %s position %s action %s" % (i,t,p,a))
        print("_"*23)
    _evalAgent = {'v':np.array( _resultat['agent'] ), 'name':"Evaluation Agent"}
    _globalPerf = { 'v': np.array( _resultat['world'] ), 'name': "Performance Globale"}
    for data in (_evalAgent,_globalPerf):
        print("statistiques",data['name'])
        arr = data['v']
        print("moyenne", round(np.mean( arr ),3))
        print("mediane", round(np.median( arr ),3) )
        print("minimum", round(np.min( arr ),3))
        print("maximum", round(np.max( arr ),3))
        print("EcT", round(np.std( arr ),3))
    

def build_base():
    """ exemple pour 2 capteurs [8,2] """
    _maBase = KB()
    _obj = [ _ for _ in objetsStatiques if 0<= _ < 100 ] # objets possibles
    _objBord = _obj[:] # Obligatoire si on ne veut pas que _obj subisse la modification suivante
    _objBord.append(-1) # objets possibles + bord du monde (erreur)
    # Aspirer si 1 en 8
    for x in _objBord:
        _maBase.add( Rule([1,x],'Aspirer',.2) )
    # Aller à Droite si 0 en 8, n'importe en 2
    for x in _obj:
        _maBase.add( Rule([0,x],'Droite',.1) )
    # Aller à Gauche si n'importe quoi en 8 et -1 en 2
    for x in _obj:
        if x!= 1: _maBase.add( Rule([x,-1], 'Gauche', .1) )
    return _maBase
    
if __name__ == "__main__":
    input("Aléatoire")
    a = Aspirateur_KB(.7)
    w = World(a)
    test_performance(w,4)
    input("Apprenant")
    b = Aspirateur_KB(.7,[8,2],learn=True)
    w = World(b)
    test_performance(w,4)
    input("Base forcée")
    c = Aspirateur_KB(.7,[8,2])
    c.knowledge = build_base()
    w = World( c )
    test_performance(w,4)
    
