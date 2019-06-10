#!/usr/local/src/pyzo/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "tests unitaires pour tp01"
__date__ = "11.02.16"
__version__ = "0.9"

#----- import ---------------------------------------
import copy
import random
## remplacer XXX par le nom de votre fichier à tester
import tp01 as tp01
#import corrige_tp01 as tp01
import test_tp00a as ttp00a
#----------------------------------------------------

# NE RIEN MODIFIER A PARTIR D'ICI

# un test est de la forme test_xxx() où xxx est la méthode testée
# un test n'a pas de paramètre
# un sous-test est de la forme subtest_xxx_yyy( params ) il est normalement
# appelé depuis test_xxx pour controler plusieurs sous-cas

def check_property(p:bool,msg:str='default',letter:str='E') -> str:
    """ permet de tester une propriété
    @input p: propriété à tester (vraie ou fausse)
    @input msg: message spécifique en cas d'erreur [defaut=default]
    @input letter: code d'erreur [defaut=E]
    @return letter (echec) . (succes)
    """
    try:
        assert( p ), 'failure %s' % msg
        _ = '.'
    except Exception as _e:
        print(_e)
        _ = letter
        
    return _

def has_failure(string:str,sz:int=1) -> bool:
    """ vérifie si les sz derniers tests ont échoué """
    return string[-sz:] != '.'*sz

def check_integrity(string:str) -> bool:
    return '.'*len(string) == string

def subtest_readonly(obj,lattr):
    """ vérification de chaque attribut de obj en lecture seule """
    _s = ''
    for att in lattr:
        oldv = copy.deepcopy(getattr(obj,att))
        for val in ("a",42,0.2,-3,[],"a b".split(),True,False):
            if val == oldv : continue
            try:
                setattr(obj,att,val)
                if getattr(obj,att) == val : _s += 'E'
                else: _s += '.'
            except Exception:
                _s += '.'
            if has_failure(_s):
                print('%s: avant %s apres %s' % (att,str(oldv),
                                                  str(val)))

    return _s
def subtest_rw_knowledge(obj):
    _s = ''
    kb = tp01.KB()
    _rul = tp01.Rule([],'a',.2)
    kb.add(_rul)
    try:
        obj.knowledge = kb
        _s += '.'
    except:
        _s += '1'

    _s += check_property(str(kb) ==str(obj.knowledge),"knowledge",letter='x')
    _rul = tp01.Rule([],'a',.3)
    kb.add(_rul)
    try:
        obj.knowledge.add(_rul)
        _s += '.'
    except:
        _s += '2'

    _s += check_property(str(obj.knowledge) == str(kb),letter='y')
    return _s

def subtest_rw_apprentissage(obj):
    _s = ''
    _s += check_property(obj.apprentissage == False,letter='1')
    try:
        obj.apprentissage = True
        _s += '.'
    except:
        _s += '2'
    _s += check_property(obj.apprentissage, letter='3')

    for i,v in enumerate([42,0,1,'a',.1,-1,'a b'.split(),[]]):
        try:
            obj.apprentissage = v
            if not obj.apprentissage: _s += str(i+4)
            else: _s += '.'
        except:
            _s += '.'
    
    return _s

def get_info_from_history(h):
    """ 
        renvoie le nombre de pieces nettoyees 
    """
    _pieces_nettoyees = 0
    # _h = [ (table,position),action ... ]
    for ((_,(x,y)),act) in h :
        if act == "Aspirer" and _[x][y] == 1:
            _pieces_nettoyees += 1
    return _pieces_nettoyees

def subtest_historique(monde,letter):
    """
       monde est simulé
    """
    _t = monde.table # c'est supposé etre une copie
    _h = monde.historique # idem
    a,b = monde.posAgent # dernière position de l'agent
    nbl,nbc = len(_t),len(_t[0])
    _pieces_nettoyees = 0
    _position_visitees =  [ [0 for j in range(nbc)] for i in range(nbl)]
    _position_visitees[a][b] = 1
    # _h = [ (table,position),action ... ]
    for ((_,(x,y)),act) in _h :
        _position_visitees[x][y] += 1
        if act == "Aspirer" and _[x][y] == 1:
            _pieces_nettoyees += 1
    _cpt = 0
    for i in range(nbl):
        for j in range(nbc):
            if _position_visitees[i][j] > 2: _cpt += 1
    _pG = (_pieces_nettoyees - _cpt)

    return check_property(monde.perfGlobale == _pG,
                          "perfGlobale {} vs historique {}".format(
                              monde.perfGlobale,_pG),letter)

def subtest_learning(monde,letter):
    _s = ''
    _oldKB = copy.deepcopy(monde.aspi.knowledge)
    for i in range(5):
        if i%2 == 0: monde.agent.apprentissage = False
        else: monde.agent.apprentissage = True
        monde.step()
        if i%2 == 0:
            _s += check_property(str(_oldKB) == str(monde.knowledge),
                                "erreur base mode non apprentissage",letter)
        else:
            _s += check_property(str(_oldKB) != str(monde.knowledge),
                                "erreur base mode apprentissage",letter)
            _oldKB = copy.deepcopy(monde.aspi.knowledge)
    return _s
def subtest_explo(monde):
    # Si plusieurs regles avec meme percept
    # le nbUsage devrait etre > pour les moins bon choix
    _tmp =''
    for p in tp01.objetsStatiques:
        if 0 <= p < 100:
            _lrules = monde.aspi.knowledge.find([p])

            _best = None ; _highestUsage = None
            for _rule in _lrules:
                if _best is None or _rule.scoreMoyen > _best.scoreMoyen:
                    _best = _rule
                if (_highestUsage is None or
                    _rule.nbUsage > _highestUsage.nbUsage):
                    _highestUsage = _rule
            _highest = [x for x in _lrules
                        if x.nbUsage == _highestUsage.nbUsage ]
            _tmp += check_property('Aspirer' in [x.conclusion for x in _highest],"Aspirer missing",'1')
            if len(_highest) == 1: 
                _tmp += check_property(_highestUsage.nbUsage > _best.nbUsage,
                                    "wrong usage\nhi={}\nbe={}".format(_highestUsage,_best),'2')
            else:
                _tmp += check_property(_highestUsage.nbUsage >= _best.nbUsage,
                                    "wrong usage\nhi={}\nbe={}".format(_highestUsage,_best),'3')    
            _tmp += check_property(_highestUsage.scoreMoyen <= _best.scoreMoyen,
                                    "wrong score\nhi={}\nbe={}".format(_highestUsage,_best),'4')
            if has_failure(_tmp,2):
                for x in _lrules: print(x)

    print("subtest exploratoire",_tmp)
    return _tmp
#------- Var & Tools --------
def hide_objets(fake=True):
    objetsStatiques = dict()
    if fake:
        for i in (-25, -2, -1, 3, 13, 27, 45, 85, 99, 1011, 101, 228, 42):
            objetsStatiques[i] = ('.'*min(abs(i),5),str(i))
    else:
        objetsStatiques = {
            0: ("propre",' '),
            1: ("sale",'.'),
            3: ("prise",'p'),
            4: ("station",'S'),
           -1: ("dont care", '?'),
          100: ("agent",'@'), }

    ttp00a.tp00.objetsStatiques = objetsStatiques
    tp01.objetsStatiques = objetsStatiques


class MyEnv(object):
    """ On force les attributs à etre dans aspi et world """
    __slots__ = ('aspi','world')
    def __init__(self,kap=[],proba=.75,learn=False,nbl=1,nbc=2):
        self.aspi = tp01.Aspirateur_KB(proba,kap,learn=learn)
        self.world = tp01.World(self.aspi,nbl,nbc)
    def __getattr__(self,att):
        if hasattr(self.aspi,att): return getattr(self.aspi,att)
        else: return getattr(self.world,att)
    def gauche(self):
        i,j = self.posAgent
        j -= 1
        if j < 0: return self.posAgent
        return i,j
    def droite(self):
        i,j = self.posAgent
        j += 1
        if j >= len(self.table[0]): return self.posAgent
        return i,j
    def ici(self):
        return self.posAgent

# des raccourcis pour les controle de type
numeric = float,int
ltup = list,tuple

def getArgs(cls,meth):
    """ On récupère les arguments formels """
    import inspect
    return inspect.getfullargspec(getattr(cls,meth))._asdict()['args']

# Definition des signatures pour chaque méthode
aspiSig = {'setReward': (2,0),
            'getEvaluation': (1,1,numeric),
            'getLastReward': (1,1,numeric),
            'getDecision': (2,1,str)}
mondeSig = {'getPerception': (2,1,ltup),
            'applyChoix': (2,1,numeric),
            'updateWorld': (1,0),
            'step': (1,0),
            'simulation': (2,1,numeric)}

# Controle de type pour les cas de base
def check_out(dic,meth,*args):
    _mmc = MyEnv()
    _ = getattr(_mmc,meth)(*args)
    if dic[meth][1] == 0: _prop = (_ is None)
    elif dic[meth][1] == 1: _prop = (isinstance(_,dic[meth][2]))
    else: _prop = (dic[meth][1]==len(_)) # à refléchir si le cas arrive
    return check_property(_prop,'%s: bad output type' % meth)

def test_fake(): return '..E..' # génère une erreur intentionnelle
def do_loop(lmeth):
    _s = ''
    for meth in lmeth:
        _meth = 'test_'+meth
        try:
            _msg = eval(_meth)()
            print(meth,_msg)
        except Exception as _e:
            print("failure: {}".format(meth))
            print(_e)
            _msg = 'X'
        _s += _msg
        if not check_integrity(_msg): break
    return _s
#------ oldies ------------------
def test_oldies():
    _s = ''
    _test = "table perfGlobale historique".split()
    for k in _test:
        _out = eval("ttp00a.test_"+k)()
        _s += _out
        if not check_integrity(_out):
            print(k,_out)
            break

    return _s


#------ Tests Aspirateurs -------
def test_setReward():
    """
       vérifie que l'on met à jour la base en cas d'apprentissage
    """
    _s =''
    _m = MyEnv([],learn=True,nbc=13)
    _s += subtest_learning(_m,'a')
    hide_objets(True)
    _m = MyEnv([8],nbc=13)
    for p in tp01.objetsStatiques:
        if 0 <= p < 99:
            _m.aspi.knowledge.add(tp01.Rule([p],"Gauche",.2))
    _s += subtest_learning(_m,'b')
    return _s

def test_getDecision():
    """ 
       on doit récupérer une décision
       * aléatoire
       * dans la base
         - avec le plus gros score
         - avec un score qui n'est pas le meilleur mais positif
    """
    _s = ''
    hide_objets(False) # un environnement simple
    kn = tp01.KB()
    R = tp01.Rule
    for p in tp01.objetsStatiques:
        if 0 <= p < 100: kn.add( R([p],"Gauche",0))
    #----------- tests exploitation ----------------------------------------
    _m = MyEnv([8],proba=1.,learn=False,nbc=7) # exploitation pure
    _m.aspi.knowledge = copy.deepcopy(kn)
    _m.simulation(10)
    _lact = [act for (_,act) in _m.historique]
    _s += check_property(len(_lact)==10,"bad historique size",'a')
    if has_failure(_s): return _s
    _s += check_property(all([x=="Gauche" for x in _lact]),"bad actions",'b')
    _s += check_property(str(_m.aspi.knowledge) == str(kn),"bad knowledge",'c')
    _m.aspi.apprentissage = True 
    _m.simulation(10)
    _lact = [act for (_,act) in _m.historique]
    _s += check_property(len(_lact)==10,"bad historique size",'A')
    if has_failure(_s): return _s
    _s += check_property(all([x=="Gauche" for x in _lact]),"bad actions",'B')
    _s += check_property(str(_m.aspi.knowledge) != str(kn),"bad knowledge",'C')
    
    #----------- tests aleatoire ----------------------------------------
    _m = MyEnv([8],proba=1.,learn=False,nbc=7) 
    _m.simulation(10)
    _lact = [act for (_,act) in _m.historique]
    _s += check_property(len(_lact)==10,"bad historique size",'d')
    _s += check_property(not all([x=="Gauche" for x in _lact]),
                         "bad actions",'e')
    _s += check_property(len(_m.aspi.knowledge) == 0,"bad knowledge",'f')
    _m = MyEnv([8],proba=0.,learn=True,nbc=7) 
    _m.simulation(10)
    _s += check_property(len(_m.aspi.knowledge) > 0,
                        "bad knowledge\n{}".format(_m.aspi.knowledge),'g')

    #----------- tests exploration ----------------------------------------
    kn = tp01.KB()
    R = tp01.Rule
    for p in tp01.objetsStatiques:
        if 0 <= p < 100:
            kn.add( R([p],"Gauche",200))
    _m = MyEnv([8],proba=.0,learn=False,nbc=7) # exploitation faible
    _m.aspi.knowledge = copy.deepcopy(kn)
    _m.simulation(10)
    _lact = [act for (_,act) in _m.historique]
    _s += check_property(not all([x=="Gauche" for x in _lact]),
                         "bad actions",'h')
    _s += check_property(str(_m.aspi.knowledge) == str(kn),"bad knowledge",'i')
    _m.aspi.apprentissage = True 
    for p in tp01.objetsStatiques:
        if 0 <= p < 100:
            kn.add( R([p],"Aspirer",1e-3))
    _m.aspi.knowledge = copy.deepcopy(kn)
    _m.simulation(10)
    _lact = [act for (_,act) in _m.historique]
    _s += check_property(not all([x=="Gauche" for x in _lact]),
                         "bad actions",'j')
    _s += check_property(str(_m.aspi.knowledge) != str(kn),"bad knowledge",'k')
    _s += subtest_explo(_m)
    return _s

def test_getEvaluation():
    """ suppose que setReward est ok """
    _s = ''
    for learn in (True, False) :
        _m = MyEnv([8],learn=learn,nbc=7)
        _m.simulation(11)
        _cpt = get_info_from_history(_m.historique)
        _sz = len(_m.knowledge)
        if learn: _s += check_property(0 < _sz < 7)
        else:  _s += check_property(0 == _sz)
        _s += check_property(_m.getEvaluation() == (_cpt + 1)/(_sz+1))

    kn = tp01.KB()
    R = tp01.Rule
    kn.add(R([1],"Aspirer",1))
    kn.add(R([1],"Gauche",-.5))
    kn.add(R([1],"Droite",-.5))
    kn.add(R([0],"Gauche",.5))
    kn.add(R([0],"Droite",.5))
    kn.add(R([0],"Aspirer",-1))
    for p in tp01.objetsStatiques:
        if 1 < p < 100: kn.add(R([p],"Gauche",.2))
    _zs = len(kn)

    for learn in (True, False) :
        _m = MyEnv([8],learn=learn,nbc=7)
        _m.aspi.knowledge = copy.deepcopy(kn)
        _m.simulation(7)
        _cpt = get_info_from_history(_m.historique)
        _sz = len(_m.knowledge)
        if not learn:
            _s += check_property(_sz == _zs,"apprentissage {}".format(learn))
        else:
            _s += check_property(_sz >= _zs,"apprentissage {}".format(learn))

        _s += check_property(_m.getEvaluation() == (_cpt + 1)/(_sz+1))
    return _s
#------ Tests Mondes ------------
def test_applyChoix():
    _s = ''
    _mmc = MyEnv(nbc=17)
    _mvt = {"Gauche": _mmc.gauche,
            "Droite": _mmc.droite,
            "Aspirer": _mmc.ici }
    _reward = {# succes, echec
        "Gauche": (1,-1),
        "Droite": (1,-1),
        "Aspirer": (2,0),
        }
    for i in range(10):
        for k in _mvt:
            _old = _mmc.posAgent
            _ovu = _mmc.table[_old[0]][_old[1]]
            _moi = _mvt[k]()
            _toi = _mmc.applyChoix(k)
            _lui = _mmc.posAgent
            _nvu = _mmc.table[_moi[0]][_moi[1]]
            _s += check_property(_moi == _lui,
                                "{}: bad position expected {} got {}".format(k,_moi,_lui),
                                str(i+1))
            if has_failure(_s): break
            if k in "Gauche Droite".split():
                _val = _reward[k][_moi == _old]
            else:
                _val = _reward[k][_ovu == _nvu]
                if _ovu == 1:
                    _s += check_property(_nvu == 0,
                                "{}: failed expected {} got {}".format(k,0,_nvu),
                                str(i+1))
            _s += check_property(_toi == _val,
                                 "bad return at {} for {}".format(i,k),str(i+1))
            if has_failure(_s): break

    return _s

def test_getPerception():
    """ on donne des capteurs on récupère des éléments du monde """
    _s = ''

    _mmc = MyEnv(nbc=13)
    _capt = {
        6: _mmc.gauche,
        2: _mmc.droite,
        8: _mmc.ici }
        
    for i in range(5):
        for k in _capt:
            _mmc.initialisation()
            x,y = _mmc.posAgent
            _out = _mmc.getPerception( [k] )
            a,b = _capt[k]()
            if k != 8 and (x,y) == (a,b): _exp = -1
            else: _exp = _mmc.table[a][b]
            _s += check_property(_out[0] == _exp,
                                     ("un capteur [{}]"
                                          "got {} expected {}".format(k,_out[0],_exp)),'1')
            if has_failure(_s):
                print(_mmc.table,_mmc.posAgent,k)
                return _s

    _mmc = MyEnv(nbc=7)
    _capt = {
        6: _mmc.gauche,
        2: _mmc.droite,
        8: _mmc.ici }

    for i in range(5):
        for lc in ([6,2],[6,8],[2,8],[6,2,8]):
            _mmc.initialisation()
            x,y = _mmc.posAgent
            _out = _mmc.getPerception( lc )
            _r = [ _capt[_]() for _ in lc ]
            _th = []
            for j,p in enumerate(lc):
                a,b = _r[j]
                if p != 8 and (x,y) == _r[j]: _th.append(-1)
                else: _th.append(_mmc.table[a][b])
            _s += check_property(_out == _th,
                                 ("plusieurs capteurs: {}"
                                  "expected {} got {}".format(lc,_th,_out)),
                                  '2')
            if has_failure(_s):
                print(_mmc.table,_mmc.posAgent,lc)
                return _s
    return _s

def test_perfGlobale_TP01():
    """
    # On va faire une simulation et regarder la variable historique
    # pour récupérer les pièces nettoyées
    # pour récupérer les position
    # Attention manque la dernière position
    #(on peut la calculer ou la demander)
    """
    hide_objets(False)
    _s = ''
    for learn in (False,True):
        for i in range(5):
            _m = MyEnv([8], nbc=7,learn=learn)
            _m.simulation(7)
            _s += subtest_historique(_m,str(i+1))
    return _s

#------ main --------------------
def main():
    # l'existence de certaines choses est requise
    _s = ''
    try:
        _mmc = MyEnv()
    except Exception:
        print("constructeur are required to succeed")
        return 0
    
    _all = "Aspirateur Aspirateur_KB Monde World objetsStatiques".split()
    for att in _all:
        _s += check_property(hasattr(tp01,att),att)
    print("existence:",_s)

    _s += check_property(issubclass(tp01.Aspirateur_KB,tp01.Aspirateur),
                         "Aspirateur_KB wrong class")
    _s += check_property(issubclass(tp01.World,tp01.Monde),
                         "World wrong class")
    _atts = "knowledge apprentissage probaExploitation".split()
    _msg =''
    for _ in _atts:
        _msg += check_property(hasattr(tp01.Aspirateur_KB,_),
                               "{} missing".format(_))
        _msg += check_property(not hasattr(tp01.Aspirateur,_),
                               "{} misplaced".format(_))

    _aspi = tp01.Aspirateur_KB(.75)
    _msg += subtest_readonly(_aspi,["probaExploitation"])
    _msg += subtest_rw_knowledge(_aspi)
    _msg += subtest_rw_apprentissage(_aspi)
    print("Attributs Aspirateurs:",_msg)
    _s += _msg ; _msg = ''

    _atts = "table posAgent".split()
    for cls in (tp01.Monde,tp01.World):
        for _a in _atts:
            _msg += check_property(hasattr(cls,_a),
                               "{1} is missing in {0}".format(cls.__class__.__name__,_a))
    # attributs doivent etre read-only
    _msg += subtest_readonly(tp01.World(_aspi),_atts)
    print("Attributs Monde:",_msg)
    _s += _msg ; _msg = ''
    
    if not check_integrity(_s):
        print("something missing")
    else:
        _msg = test_oldies()
        print("oldies:",_msg)
        _s += _msg ; _msg = ''

    _todo = """applyChoix getPerception setReward perfGlobale_TP01 
               getDecision getEvaluation""".split()
    _s += do_loop(_todo)
    # Bilan
    _all = len(_s) 
    _ok = _s.count('.')
    return _ok, (_all-_ok), _all, round(100 * _ok / _all, 2)


if __name__ == "__main__" :

    print("succ %d fail %d sum %d, rate = %.2f" % main())
    print("expected >> succ {0} fail 0 sum {0} rate = 100.00".format(253))

