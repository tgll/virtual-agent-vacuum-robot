#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "tests unitaires pour tp02a"
__date__ = "28.03.16"
__version__ = "0.5"


#----- import ---------------------------------------
import copy
import random
## remplacer XXX par le nom de votre fichier à tester
import tp02a as tp02a
from briques import mmcBinaire, mmcUnaire, ProgramGenetic, GeneratePercept
from test_tp01 import test_getPerception, hide_objets
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

#---------- tools ------------------------------------------------
def get_info_frm_history(h):
    """ 
        renvoie le nombre de pieces nettoyees 
    """
    _pieces_nettoyees = 0
    # _h = [ (table,position),action ... ]
    for ((_,(x,y)),act) in h :
        if act == "Aspirer" and _[x][y] == 1:
            _pieces_nettoyees += 1
    return _pieces_nettoyees

def get_sales_frm_history(h):
    """ pièces sales dans la première ligne """
    ((t,_),_) = h[0]
    return t[0].count(1)
    
def get_action_frm_history(h,action="Repos"):
    """ 
        renvoie le nombre d'actions d'un certain type
    """
    _nbAct = 0
    # _h = [ (table,position),action ... ]
    for ((_,_), act) in h :
        if act == action :
            _nbAct += 1
    return _nbAct

def get_positions_frm_history(h):
    """ 
        renvoie pour chaque pièce le nombre de visite
    """
    pieces = {}
    # _h = [ (table,position),action ... ]
    for ((_,(x,y)), _) in h :
        pieces[(x,y)] = pieces.get( (x,y), 0) +1
    return pieces

def get_repartitions_frm_history(h):
    """ donne la répartition des objets avant après """
    _avant = h[0][0][0]
    _apres = h[-1][0][0]
    repart = {}
    for l1,l2 in zip(_avant,_apres):
        for a,b in zip(l1,l2):
            a1,b1 = repart.get(a,(0,0))
            repart[a] = a1+1,b1
            a1,b1 = repart.get(b,(0,0))
            repart[b] = a1,b1+1
    delta = {}
    for x in repart:
        delta[x] = repart[x][0] - repart[x][1]
    return repart,delta
            
class MyEnv(object):
    """ On force les attributs à etre dans aspi et world """
    __slots__ = ('aspi','world')
    def __init__(self,kap=[],prog=None,gp=None,nbl=1,nbc=2):
        self.aspi = tp02a.Aspirateur_PG(prog,gp,lCap=kap)
        self.world = tp02a.Monde_AG(self.aspi,nbl,nbc)
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
#------ tests Aspirateur ------------------
def test_constructeur():
    """ Vérification des contraintes sur le constructeur """
    _out = ""
    # constructeur vide
    mmc = MyEnv()
    _out += check_property(len(mmc.aspi.program) == 8,
                            "expected 8 gènes found {}"
                            "".format(len(mmc.aspi.program)))
    _out += check_property(len(mmc.aspi.program.program) == 8,
                            "expected chromosome of length 8 found {}"
                            "".format(len(mmc.aspi.program.program)))
    _out += check_property(mmc.aspi.capteurs == [],
                           "expected capteurs [] found {}"
                           "".format(mmc.aspi.capteurs))
    actions = "Aspirer Gauche Droite Repos".split()
    for action in actions:
        _out += check_property(action in mmc.aspi.actions,
                              "{} not a valid action".format(action))
    _out += check_property(len(actions) == len(mmc.aspi.actions),
                           "expected {} actions found {}"
                            "".format(len(actions),len(mmc.aspi.actions)))

    # constructeur avec capteurs
    cap = [8] ; sz = len([ x for x in tp02a.objetsStatiques if 0 <= x < 100])
    mmc = MyEnv(cap)
    _out += check_property(len(mmc.aspi.program) == sz,
                            "expected {} gènes found {}"
                            "".format(sz,len(mmc.aspi.program)))
    _out += check_property(len(mmc.aspi.program.program) == sz,
                            "expected chromosome of length {} found {}"
                            "".format(sz,len(mmc.aspi.program.program)))
    _out += check_property(mmc.aspi.capteurs == cap,
                           "expected capteurs {} found {}"
                           "".format(cap,mmc.aspi.capteurs))
    actions = "Aspirer Gauche Droite Repos".split()
    for action in actions:
        _out += check_property(action in mmc.aspi.actions,
                              "{} not a valid action".format(action))
    _out += check_property(len(actions) == len(mmc.aspi.actions),
                           "expected {} actions found {}"
                            "".format(len(actions),len(mmc.aspi.actions)))

    # constructeur avec gp
    kap = [6,2] ; gp = GeneratePercept(kap,tp02a.objetsStatiques)
    prog = ProgramGenetic(2,gp.howMany,'01',mmcBinaire)
    mmc = MyEnv(kap,prog,gp)
    _out += check_property(len(mmc.aspi.program.program) == 2*gp.howMany,
                            "expected chromosome of length {} found {}"
                            "".format(2*gp.howMany,
                                      len(mmc.aspi.program.program)))
    _out += check_property(mmc.aspi.capteurs == kap,
                           "expected capteurs {} found {}"
                           "".format(cap,mmc.aspi.capteurs))
    actions = "Aspirer Gauche Droite Repos".split()
    for action in actions:
        _out += check_property(action in mmc.aspi.actions,
                              "{} not a valid action".format(action))
    _out += check_property(len(actions) == len(mmc.aspi.actions),
                           "expected {} actions found {}"
                            "".format(len(actions),len(mmc.aspi.actions)))
    
    return _out

def test_reset():
    """ 
       vivant est vrai, cpt est 0 
       (optionnel: nbTours est 0, energie est 100) 
    """
    _out = ''
    mmc = MyEnv()
    _out += check_property(mmc.aspi.vivant,"vivant is wrong")
    _out += check_property(mmc.aspi.cpt == 0,
                           "cpt is wrong")
    _out += check_property(mmc.aspi.nbTours == 0,
                           "nbTours is wrong")
    _out += check_property(mmc.aspi.energie == 100,
                           "energie is wrong")
    mmc.aspi.vivant = False
    mmc.aspi.cpt = 23
    mmc.aspi.energie = 50
    _out += check_property(not mmc.aspi.vivant,"vivant is wrong")
    _out += check_property(mmc.aspi.cpt == 23 % len(mmc.aspi.program),
                           "cpt is wrong")
    _out += check_property(mmc.aspi.energie == 50,
                           "energie should be 50")

    mmc.aspi.reset()
    _out += check_property(mmc.aspi.vivant,"vivant is wrong")
    _out += check_property(mmc.aspi.cpt == 0,
                           "cpt is wrong")
    _out += check_property(mmc.aspi.nbTours == 0,
                           "nbTours is wrong")
    _out += check_property(mmc.aspi.energie == 100,
                           "energie has not been reset",'w')
    if has_failure(_out): _out = _out[:-1]+'.'
    # Un nouvel environnement, une simulation de taille 5
    mmc = MyEnv(nbc=7)
    for k in (5,7,13):

        mmc.world.simulation(k)

        _out += check_property(mmc.aspi.vivant,"vivant is wrong")
        _out += check_property(mmc.aspi.cpt == k % len(mmc.aspi.program),
                               "cpt is wrong")
        _out += check_property(mmc.aspi.nbTours == k, "nbTours is wrong")
        _out += check_property(0 < mmc.aspi.energie <= 100, "energie is wrong")
        
        mmc.aspi.reset()
    return _out

def test_nbTours():
    """ doit etre conforme a la longueur de l'historique """
    _out = ''
    for col in (3,7,11,13):
        mmc = MyEnv(nbc = col)
        for nb in (5,7,11,13,17):
            mmc.world.simulation(nb)
            szh = len(mmc.world.historique)
            _out += check_property(mmc.aspi.nbTours == szh,
                                   "nbTours expected {} got {}"
                                   "".format(szh,mmc.aspi.nbTours))
    return _out

def test_energie():
    """ entre 0 et 100 (à 0 vivant est faux) """
    _out = ''
    mmc = MyEnv()
    mmc.aspi.energie = -1
    _out += check_property( mmc.aspi.energie == 0,
                            "energie found {} expected 0..100"
                            "".format(mmc.aspi.energie))
    _out += check_property( not mmc.aspi.vivant,
                            "vivant should be False found {}"
                            "".format(mmc.aspi.vivant))
    mmc.aspi.reset()

    mmc.aspi.energie = 111
    _out += check_property( mmc.aspi.energie == 100,
                            "energie found {} expected 0..100"
                            "".format(mmc.aspi.energie))
    _out += check_property( mmc.aspi.vivant,
                            "vivant should be True found {}"
                            "".format(mmc.aspi.vivant))
    
    return _out

def test_cpt():
    """ doit toujours etre dans 0..n-1 """
    _out = ''
    mmc = MyEnv()
    _out += check_property(mmc.aspi.cpt == 0,
                           "cpt is wrong",'a')
    mmc.aspi.cpt = 23
    _out += check_property(mmc.aspi.cpt == 23 % len(mmc.aspi.program),
                           "cpt is wrong",'b')
    mmc.aspi.reset()
    _out += check_property(mmc.aspi.cpt == 0,
                           "cpt is wrong",'c')
    
    # Un nouvel environnement, une simulation de taille 5
    mmc = MyEnv(nbc=7)
    for k in (5,7,13,17):

        mmc.world.simulation(k)

        _out += check_property(mmc.aspi.cpt == k % len(mmc.aspi.program),
                               "cpt is wrong",str(k))
        
        mmc.aspi.reset()
    return _out

def test_vivant():
    """ vivant permet de dire la valeur energie """
    _out = ''
    mmc = MyEnv()
    _out += check_property(mmc.aspi.vivant,"vivant is wrong")
    _out += check_property(0 < mmc.aspi.energie <= 100,"vivant is wrong")

    mmc.aspi.vivant = False

    _out += check_property(not mmc.aspi.vivant,"vivant is wrong")


    mmc.aspi.reset()
    _out += check_property(mmc.aspi.vivant,"vivant is wrong")
    
    # Un nouvel environnement, une simulation de taille 5
    mmc = MyEnv(nbc=7)
    for k in (5,7,13):

        mmc.world.simulation(k)

        _out += check_property(mmc.aspi.vivant,"vivant is wrong")
        _out += check_property(0 < mmc.aspi.energie <= 100, "energie is wrong")
        
        mmc.aspi.reset()
    return _out

def test_program():
    """ On teste le code génétique GAD sur tous les mondes de taille 2 """
    _out = ''

    prog = ProgramGenetic(1,4,"AGDR",mmcUnaire)
    mmc = MyEnv( prog = prog )
    mmc.aspi.program.program = "GADA"
    _out += check_property( mmc.aspi.program.program == "GADA",
                            "wrong program")

    for i in range(25):
        expected = {'Repos': 0, 'Aspirer': 3, 'Droite': 2, 'Gauche': 2}
        mmc.world.simulation(7)
        mmc.aspi.energie = 100 # On force au cas ou reset ne le fait pas
        memo = {}
        _out += check_property(len(mmc.historique) == 7,
                               "historique is wrong found {} expected {}"
                               "".format(len(mmc.historique),7))

        for act in mmc.aspi.actions:
            memo[act] = get_action_frm_history(mmc.historique,act)
            _out += check_property( memo[act] == expected[act],
                                    "{} expected {} found {}"
                                    "".format(act,expected[act],memo[act]) )
    return _out

def test_getEvaluation():
    """ nettoyees / sales * 10 + alpha energie / 100 """
    def almost(a): return round(float(a),4)
    from fractions import Fraction
    def rateEnergy(x):
        """ renvoie le coefficient associé au niveau d'énergie """

        alfa = { (0,25): "1/2", (25,50): "2/3", (50,75): "3/4", (75,101): "1" }
        for a,b in alfa:
            if a <= x < b: return Fraction(alfa[a,b])
            continue
        raise ValueError("{} not in range 0..100".format(x))

    _out = ''
    for col in (2,3,5,7,11,13,17,19):
        hide_objets(False)
        mmc = MyEnv(nbc=col)
        # energie est à 100
        _out += check_property( mmc.aspi.energie == 100,
                                "{} should be 100".format(mmc.aspi.energie),"e")
        # on lance la simulation
        mmc.simulation(10)
        # on récupère le score calculé
        _ev = mmc.aspi.getEvaluation()
        # on controle le résultat
        _e = mmc.aspi.energie
        energy = rateEnergy(_e) * Fraction(_e,100)
        cleaned = get_info_frm_history( mmc.world.historique )
        dirty =  get_sales_frm_history( mmc.world.historique )
        # pour voir le calcul effectif
        #print("{}/{} * 10 + {} = {}".format(cleaned,dirty,energy,_ev))
        if dirty == 0 :
            _score = energy
        else:
            _score = Fraction(cleaned*10,dirty) + energy

        _out += check_property( almost(_ev) == almost(_score),
                                    "found {} expected {}".format(_ev,_score))

    return _out

def test_getDecision():
    """ doit tester le cas sans capteur et le cas avec capteur """
    _out = ''
    return _out

#------ tests Monde ------------------

def test_initialisation():
    """ vérifie que reset est appelé """
    _out = ''
    mmc = MyEnv()
    atts = "vivant cpt energie".split()
    val = (False,5,42)
    _avt = {}
    for a,v in zip(atts,val):
        setattr(mmc.aspi,a,v)
        _avt[a] = v
    _aft = {}
    mmc.aspi.reset()
    for a in atts: _aft[a] = getattr(mmc.aspi,a)
    for a,v in zip(atts,val):
        setattr(mmc.aspi,a,v)
    mmc.world.simulation(0)
    _bft = {}
    for a in atts: _bft[a] = getattr(mmc.aspi,a)
    for a in atts:
        _out += check_property( _aft[a] == _bft[a],
                                "{} should be {} found {}"
                                "".format(a,_aft[a],_bft[a]),a[0] )
    # On remet dans l'état de départ
    return _out


def test_applyChoix():
    """ plein de cas à tester """
    _out = ''
    return _out


#------ main --------------------
def main():
    # l'existence de certaines choses est requise
    _s = ''
    try:
        _mmc = MyEnv()
    except Exception as _e:
        print(_e)
        print("constructeur are required to succeed")
        return 0,1,1,0
    #--- existence des méthodes --------------------------------------
    _msg = '.'
    _all = "Aspirateur Aspirateur_PG Monde Monde_AG objetsStatiques".split()
    for att in _all:
        _msg += check_property(hasattr(tp02a,att),att)
        
    _msg += check_property(issubclass(tp02a.Aspirateur_PG,tp02a.Aspirateur),
                         "Aspirateur_KB wrong class")
    _msg += check_property(issubclass(tp02a.Monde_AG,tp02a.Monde),
                         "World wrong class")
    # méthodes / attribut
    _atts = "nbTours energie vivant cpt program".split()

    _sig = {
        "reset": (None,None),
        "nbTours": int,
        "energie": int,
        "vivant": bool,
        "cpt": int,
        "program": ProgramGenetic }

    keys = ['reset']
    for att in _atts:
        _msg += check_property(hasattr(_mmc.aspi,att),
                               "{} not found".format(att))
        if not has_failure(_msg): keys.append(att)
    print("Existence:",_msg)
    stats["Existence"] = len(_msg)
    _s += _msg ; _msg = ''

    mmc = MyEnv()
    _msg += subtest_readonly(mmc.aspi,['nbTours'])

    for k in keys:
        try:
            if isinstance(_sig[k],tuple):
                if _sig[k][0] is None:
                    _out = getattr(_mmc.aspi,k)()
                else:
                    _out = getattr(_mmc.aspi,k)(*_sig[k][0])
            else:
                _out = getattr(_mmc.aspi,k)
            _msg += '.'
        except:
            print("{} missing".format(k))
            _msg += 'E'
        if has_failure(_msg): break

        if isinstance(_sig[k],tuple):
            if _sig[k][1] is None:
                _msg += check_property(_out is None,
                                    "{} expected None found {}"
                                    "".format(_sig[k],type(_out)))
            else:
                _msg += check_property(isinstance(_out,_sig[k][1]),
                                       "{} expected {} found {}"
                                       "".format(k,_sig[k][1],type(_out)))
        else:
            _msg += check_property(isinstance(_out,_sig[k]),
                                "{} expected {} got {}"
                                "".format(k,_sig[k],_out))
    print("Signatures:",_msg)
    stats["Signatures"] = len(_msg)
    _s += _msg ; _msg = ''

    _ok = keys
    _ok.extend( ['constructeur', 'getEvaluation', 'getDecision'] )
    _ok.extend( ['initialisation', 'getPerception', 'applyChoix'])
    #========= test_XXX est appelé =====================================
    for att in _ok:
        meth = 'test_'+att
        try:
            _msg = eval(meth)()
            if _msg == '': print(meth,': en cours de développement')
            else: print(meth,_msg) ; stats[meth] = len(_msg)
        except Exception as _e:
            print("failure: {}".format(meth))
            print(_e)
            _msg = 'X'
        if _msg == '': continue # pas de test effectué
        _s += _msg
        if has_failure(_msg): break

            
    # Bilan
    _all = len(_s) 
    _ok = _s.count('.')
    return _ok, (_all-_ok), _all, round(100 * _ok / _all, 2)


if __name__ == "__main__" :
    stats = {}
    expected = {
        "Existence": 13,
        "Signatures": 19,
        "test_getPerception": 35,
        'test_constructeur': 23,
        'test_reset': 23,
        'test_nbTours': 20,
        'test_energie': 4,
        'test_applyChoix': 0,
        'test_initialisation': 3,
        'test_getDecision': 0,
        'test_getEvaluation': 16,
        'test_program': 126,
        'test_vivant': 10,
        'test_cpt': 7,
        }
    somme = sum([x for x in expected.values() if isinstance(x,int)])
    print("succ %d fail %d sum %d, rate = %.2f" % main())
    print("expected >> succ {0} fail 0 sum {0} rate = 100.00"
          "".format(somme))
    print("_"*10,"résumé","_"*10)
    for x in stats:
        diag = 'ok' if stats[x]==expected[x] else 'nok'
        print("{}: got {} expected {} : {}"
              "".format(x,stats[x],expected[x],diag))
