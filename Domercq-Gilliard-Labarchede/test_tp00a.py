#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "tests unitaires pour la première réalisation aspi autonome"
__date__ = "11.02.16"
__version__ = "final"

## remplacer XXX par le nom de votre fichier
import tp00a as tp00
#import corrige_tp00a as tp00

# NE RIEN MODIFIER A PARTIR D'ICI
import random
import copy
# un test est de la forme test_xxx() où xxx est la méthode testée
# un test n'a pas de paramètre
# un sous-test est de la forme subtest_xxx_yyy( params ) il est normalement
# appelé depuis test_xxx pour controler plusieurs sous-cas

def check_property(p,msg='default',letter='E'):
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

def has_failure(string,sz=1):
    """ vérifie si les sz derniers tests ont échoué """
    return string[-sz:] != '.'*sz
    

def subtest_readonly(obj,lattr):
    """ vérification de chaque attribut de obj en lecture seule """
    _s = ''
    for att in lattr:
        oldv = copy.deepcopy(getattr(obj,att))
        try:
            _s += '.'
            setattr(obj,att,42)
            if oldv != getattr(obj,att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s,2):
            return '%s: avant %s apres %s' % (att,oldv,getattr(obj,att))

        try:
            _s += '.'
            setattr(obj,att,[-1,0,1])
            if oldv != getattr(obj,att): _s += 'E'
        except Exception:
            _s += '.'
        if has_failure(_s,2):
            return '%s: avant %s apres %s' % (att,oldv,getattr(obj,att))
        
    return _s

#------- Var & Tools --------
class MyEnv(object):
    """ On force les attributs à etre dans aspi et world """
    __slots__ = ('aspi','world')
    _fake = dict()
    for i in (-25, -2, -1, 3, 13, 27, 45, 85, 99, 1001, 100, 228, 42):
        _fake[i] = ('.'*min(abs(i),5),str(i))
    tp00.objetsStatiques = _fake
    def __init__(self,nbl=1,nbc=2):
        self.aspi = tp00.Aspirateur()
        self.world = tp00.Monde(self.aspi,nbl,nbc)
    def __getattr__(self,att):
        if hasattr(self.aspi,att): return getattr(self.aspi,att)
        else: return getattr(self.world,att)

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
    
#------ Tests Aspirateurs -------

def test_init_Aspirateur():
    """ tests sur le constructeur Aspirateur qui doit être 
        Aspirateur() == Aspirateur([],['Gauche''Droite','Aspirer'])
    """
    _out = ''
    _actions = "Droite Gauche Aspirer".split()
    try:
        _a = tp00.Aspirateur()
        _out += '.'
    except Exception:
        _out += 'a'
    if has_failure(_out): return _out
    _out += check_property(_a.capteurs == [],
                           'capteurs par défaut trouvé %s' %  _a.capteurs,'b')  
    if has_failure(_out): return _out
    _out += check_property(len(_a.actions) == 3,
                           'wrong number of actions','c')
    _out += check_property(sorted(_a.actions) == sorted(_actions),
                            "bad actions",'d')
    return _out

def test_capteurs():
    """ les capteurs sont des listes de valeurs distinctes dans 0..8 """
    _out = ''
    try:
        _a = tp00.Aspirateur([ 0 ])
        _out += '.'
    except Exception:
        _out += 'a'
    if has_failure(_out): return _out
    try:
        _a = tp00.Aspirateur([ 'a' ])
        _out += 'b'
    except Exception:
        _out += '.'
    try:
        _a = tp00.Aspirateur([ 0, 0 ])
        if _a.capteurs == [0]: _out += '.'
        else: _out += 'c'
    except Exception:
        _out += '.'
    if has_failure(_out,2): return _out
    _lc = random.sample( range(9), 4 )
    _a = tp00.Aspirateur( _lc )
    
    _out += check_property( len(_a.capteurs) == len(_lc),
                                "bad list of captors",'d')
    _out += check_property( _a.capteurs == _lc,"bad list of captors",'e')
    return _out

def test_actions():
    """
        actions renvoie la liste des actions disponibles
    """
    _out = ''
    try:
        _a = tp00.Aspirateur([],1)
        _out += check_property(isinstance(_a.actions,(list,tuple)),
                                   "list or tuple expected found %s" % type(_a.actions),'a')
    except Exception:
        _out += '.'
    if has_failure(_out): return _out
    _a = tp00.Aspirateur([],['o','u','t'])
    _out += check_property(len(_a.actions)==len("out"),
                               "wrong number of actions",'b')
    _out += check_property(sorted(_a.actions) == sorted("out"),
                               "wrong actions",'c')
    return _out
    
def test_vivant():
    _out = ''
    _a = tp00.Aspirateur()
    _out += check_property( isinstance(_a.vivant,bool), "boolean required", '1')
    _out += check_property( _a.vivant,
                            "should be alive, found %s" % _a.vivant, '2')
    return _out
        
def test_setReward():
    _out = ''
    _out += check_out(aspiSig,'setReward',42)
    return _out

def test_getLastReward():
    _out = ''
    _out += check_out(aspiSig,'getLastReward')
    _a = tp00.Aspirateur()
    _a.setReward(42)
    _out += check_property(42 == _a.getLastReward(),
                            "42 expected found %s" % _a.getLastReward())
    return _out

def test_getEvaluation():
    _out = ''
    _out += check_out(aspiSig,'getEvaluation')
    return _out

def test_getDecision():
    _out = ''
    _out += check_out(aspiSig,'getDecision',[])
    _a = tp00.Aspirateur([],"A E I O U".split())
    for i in range(10):
        _ = _a.getDecision([])
        _out += check_property(_ in "AEIOU", "%s is not an action" % _,
                                str(i))
    return _out

#------- Monde ------
def test_table():
    """ une nouvelle contrainte est apparue dans TP00 """
    _out = ''
    _old = tp00.objetsStatiques
    _mmc = MyEnv(11,10)
    _out += check_property(len(_mmc.table) == 11,'nbLig is wrong','a')
    _out += check_property(len(_mmc.table[0]) == 10, 'nbCol is wrong','b')
    _val = [ _mmc.table[i][j] for i in range(len(_mmc.table)) 
             for j in range(len(_mmc.table[0])) if 0 <= _mmc.table[i][j] < 100 ]
    _out += check_property( len(_val) == 11*10, 'bad number of elements', 'c')
    _out += check_property( _val.count(0)+_val.count(1) != 11*10, 'bad elements','d')
    return _out 
    
def test_agent():
    _out = ''
    try:
        _m = tp00.Monde(1)
        _out += '1'
    except:
        _out += '.'
    _a = tp00.Aspirateur()
    try:
        _m = tp00.Monde(_a)
        _out += '.'
    except:
        _out += 'b'
    _out += check_property(_a == _m.agent,"where is %s ?" % _a,'c')
    return _out

def test_perfGlobale():
    _out = ''
    _mmc = MyEnv()
    _a = _mmc.simulation(5)
    _out += check_property(isinstance(_mmc.perfGlobale,numeric),"bad type",'1')
    if has_failure(_out): return _out
    _out += check_property(_a == _mmc.perfGlobale,"wrong perfGlobale",'2')
    return _out

def test_historique():
    _out = ''
    _mmc = MyEnv(3,5)
    _out += check_property(_mmc.historique == [],"historique wrong init",'a')
    _a = _mmc.simulation(5)
    _out += check_property(len(_mmc.historique) == 5,
                            "historique wrong length",'b')
    # vérification du contenu historique
    for i,x in enumerate(_mmc.historique): # chr(50)='2'
        _out += check_property(isinstance(x,tuple),
                                   "tuple expected",chr(ord('c')+i))
        _out += check_property(len(x)==2,
                                '2 are expected got %d' % len(x),'+')
        _out += check_property(isinstance(x[0],tuple),
                                "tuple expected",chr(ord('p')+i))
        _out += check_property(len(x[0])==2,
                                '%s is wrong' % str(x[0]),'-') # table,posAgent
        _out += check_property(len(x[0][1]) == 2,
                                '%s is not a posAgent' % str(x[0][1]),
                                ':') # posAgent
        _out += check_property(len(x[0][0]) == 3,'wrong nbl',';') # table
        _out += check_property(len(x[0][0][1]) == 5,'wrong nbc','!') # table[1]
        _out += check_property(x[0][0][2][3] in MyEnv._fake,
                                'table is wrongly filled','#')
    return _out

def test_updateWorld():
    _out = ''
    _out += check_out(mondeSig,'updateWorld')
    return _out

def test_applyChoix():
    _out = ''
    _out += check_out(mondeSig,'applyChoix','Aspirer')    
    return _out

def test_getPerception():
    _out = ''
    _out += check_out(mondeSig,'getPerception',[])
    return _out

def test_step():
    _out = ''
    _out += check_out(mondeSig,'step')
    return _out

def test_simulation():
    _out = ''
    _out += check_out(mondeSig,'simulation',5)
    return _out

def main():
    _msg = ''
    _s = ''
    _toDO = []
    try:
        _mmc = MyEnv()
    except Exception:
        return "test_tp00 is required to succeed"
        
    # Controle des attributs/méthodes requis
    _attr = "capteurs actions vivant".split()
    _toDO.extend( _attr )
    _meth = "setReward getLastReward getEvaluation getDecision".split()
    _toDO.extend( _meth )
    
    for _ in _attr:
        _msg += check_property(hasattr(tp00.Aspirateur,_),'%s inconnu' % _)
    print("attributs Aspirateur:",_msg)
    _s += _msg ; _msg = ''
    
    if '.'*len(_s) == _s:
        _msg = subtest_readonly(_mmc,_attr)
        print("attributs are ReadOnly",_msg)
        _s += _msg ; _msg = ''
        
    
    for _ in _meth:
        _msg += check_property(hasattr(tp00.Aspirateur,_),'%s inconnu' % _)
        if _msg[-1] == '.' :
            _msg += check_property(callable(getattr(tp00.Aspirateur,_)),
                                       '%s pas une méthode' % _)
    print("méthodes Aspirateur:",_msg)
    _s += _msg ; _msg = ''

    for _ in aspiSig:
        _msg += check_property(len(getArgs(tp00.Aspirateur,_)) == aspiSig[_][0],
                                "%s pas le bon nombre d'arguments" % _)
    print("input Aspirateur",_msg)
    _s += _msg ; _msg = ''
    
    _attr = "agent perfGlobale historique table".split()
    _toDO.extend( _attr )
    _meth = "updateWorld applyChoix getPerception step simulation".split()
    _toDO.extend( _meth )
    
    for _ in _attr:
        _msg += check_property(hasattr(tp00.Monde,_),'%s inconnu' % _)
    print("attributs Monde:",_msg)
    _s += _msg ; _msg = ''
    
    if '.'*len(_s) == _s:    
        _msg = subtest_readonly(_mmc,_attr)
        print("attributs are ReadOnly",_msg)
        _s += _msg ; _msg = ''
    
    for _ in _meth:
        _msg += check_property(hasattr(tp00.Monde,_),'%s inconnu' % _)
        if _msg[-1] == '.' :
            _msg += check_property(callable(getattr(tp00.Monde,_)),
                                       '%s pas une méthode' % _)
    print("méthodes Monde:",_msg)
    _s += _msg ; _msg = ''

    for _ in mondeSig:
        _msg += check_property(len(getArgs(tp00.Monde,_)) == mondeSig[_][0],
                                "%s pas le bon nombre d'arguments" % _)
    print("input Monde",_msg)
    _s += _msg ; _msg = ''

    _msg = test_init_Aspirateur()
    print("Constructeur Aspirateur",_msg)
    _s += _msg ; _msg = ''
    
    if '.'*len(_s) != _s :
        print(_s)
        print('correction needed, something missing')
    else:
        # On passe aux tests plus complexes
        for meth in _toDO :
            meth = 'test_'+meth
            try:
                _msg = eval(meth)()
                print(meth,_msg)
            except Exception as _e:
                print("failure: {}".format(meth))
                print(_e)
                _msg = "X"
            if has_failure(_msg): break
            _s += _msg
    
        
    # Bilan
    _all = len(_s) 
    _ok = _s.count('.')
    return _ok, (_all-_ok), _all, round(100 * _ok / _all, 2)

if __name__ == '__main__' :
    try:
        _result = main()
        print("succ %d fail %d sum %d, rate = %.2f" % _result)
    except Exception as _e:
        print(_e)
    print("expected >> succ {0} fail 0 sum {0} rate = 100.00".format(147))
