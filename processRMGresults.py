# this version updated by RHW in January 2009
"""
Postprocess a load of RMG Results
"""
import os, sys, shutil

def drawMolecules(RMG_results):
    """Draw pictures of each of the molecules in the RMG dictionary.
    
    Also creates MolarMasses.txt. Puts its results inside RMG_results directory"""
    
    import openbabel, pybel
    # please cite:
    # Pybel: a Python wrapper for the OpenBabel cheminformatics toolkit
    # Noel M O'Boyle, Chris Morley and Geoffrey R Hutchison
    # Chemistry Central Journal 2008, 2:5
    # doi:10.1186/1752-153X-2-5
    
    picfolder=os.path.join(RMG_results,'pics')
    molfolder=os.path.join(RMG_results,'mols')
    for path in [picfolder,molfolder]:
        os.path.isdir(path) or os.mkdirs(path)
    
    periodicTableByNumber={ 1: 'H',  2: 'He',  3: 'Li',  4: 'Be',  5: 'B',  6: 'C',  7: 'N',  8: 'O',  9: 'F',  10: 'Ne',  11: 'Na',  12: 'Mg',  13: 'Al',  14: 'Si',  15: 'P',  16: 'S',  17: 'Cl',  18: 'Ar',  19: 'K',  20: 'Ca',  21: 'Sc',  22: 'Ti',  23: 'V',  24: 'Cr',  25: 'Mn',  26: 'Fe',  27: 'Co',  28: 'Ni',  29: 'Cu',  30: 'Zn',  31: 'Ga',  32: 'Ge',  33: 'As',  34: 'Se',  35: 'Br',  36: 'Kr',  37: 'Rb',  38: 'Sr',  39: 'Y',  40: 'Zr',  41: 'Nb',  42: 'Mo',  43: 'Tc',  44: 'Ru',  45: 'Rh',  46: 'Pd',  47: 'Ag',  48: 'Cd',  49: 'In',  50: 'Sn',  51: 'Sb',  52: 'Te',  53: 'I',  54: 'Xe',  55: 'Cs',  56: 'Ba',  57: 'La',  58: 'Ce',  59: 'Pr',  60: 'Nd',  61: 'Pm',  62: 'Sm',  63: 'Eu',  64: 'Gd',  65: 'Tb',  66: 'Dy',  67: 'Ho',  68: 'Er',  69: 'Tm',  70: 'Yb',  71: 'Lu',  72: 'Hf',  73: 'Ta',  74: 'W',  75: 'Re',  76: 'Os',  77: 'Ir',  78: 'Pt',  79: 'Au',  80: 'Hg',  81: 'Tl',  82: 'Pb',  83: 'Bi',  84: 'Po',  85: 'At',  86: 'Rn',  87: 'Fr',  88: 'Ra',  89: 'Ac',  90: 'Th',  91: 'Pa',  92: 'U',  93: 'Np',  94: 'Pu',  95: 'Am',  96: 'Cm',  97: 'Bk',  98: 'Cf',  99: 'Es',  100: 'Fm',  101: 'Md',  102: 'No',  103: 'Lr',  104: 'Rf',  105: 'Db',  106: 'Sg',  107: 'Bh',  108: 'Hs',  109: 'Mt',  110: 'Ds',  111: 'Rg',  112: 'Uub',  113: 'Uut',  114: 'Uuq',  115: 'Uup',  116: 'Uuh',  117: 'Uus',  118: 'Uuo'}
    periodicTableBySymbol=dict([(val, key) for key, val in periodicTableByNumber.items()])   
    OBMolBondTypes={'S':1, 'D':2, 'T':3, 'B':5 }
    
    infile='RMG_Dictionary.txt'
    path=os.path.join(RMG_results,infile)
    RMGfile=file(path)
    
    masses=file(os.path.join(RMG_results,'MolarMasses.txt'),'w')
    
    for i in range(1,30000): # only does 30,000 [core] molecules
        print 'Molecule', i,'\t',
        name=''
        try:
            while name=='':
                name=RMGfile.next().strip()
        except StopIteration:
            print 'No more molecules'
            break
        print name
        graph=[]
        line=RMGfile.next()
        while line.strip():
            graph.append(line)
            line=RMGfile.next()
        # now have 'name' and 'graph'
    
        mol = openbabel.OBMol()
        re_bond=re.compile('\{(?P<atomnum>\d+),(?P<bondtype>[SDTB])\}')
        for line in graph:
            #print 'line:',line.strip()
            if len(line.split())>3:
                (number, element, radical, bonds)=line.split(None,3)
            else:
                (number, element, radical )=line.split(None)
            a = mol.NewAtom()
            a.SetAtomicNum(periodicTableBySymbol[element])  # 6 for a carbon atom
            if int(radical[0]): # the [0] is so we take the first character of the string, in case it's something like "2T"
                a.SetSpinMultiplicity(int(radical[0])+1)
                # note that for non-radicals it's 0, but single radicals are 2, double radicals are 3...
                # http://openbabel.org/wiki/Radicals_and_SMILES_extensions#How_OpenBabel_does_it
            for bond in bonds.split():
                matchobject=re_bond.match(bond)
                if matchobject:
                    fromAtom=int(number)
                    toAtom=int(matchobject.group('atomnum'))
                    bondType=matchobject.group('bondtype')
                    if toAtom>fromAtom:
                        continue # because toAtom hasn't been placed yet!
                    # print "%s bond from %d to %d"%(bondType,fromAtom,toAtom)
                    mol.AddBond(fromAtom,toAtom,OBMolBondTypes[bondType])
                else:
                    raise "couldn't figure out this bond: %s"%bond
        pymol=pybel.Molecule(mol)
        print pymol.write().strip(), 
        chemkinformula=pymol.formula+'J'*(pymol.spin-1)
        print chemkinformula
        if pymol.OBMol.NumHvyAtoms()>1:
            pymol.removeh()
        pymol.draw(filename=os.path.join(picfolder,name+'.png'), update=True, show=False)
        pymol.write(format='mol',filename=os.path.join(molfolder,name+'.mol'),overwrite=True)
        
        masses.write(name+'\t'+str(pymol.exactmass)+'\n')
    masses.close()
    RMGfile.close()

def convertChemkin2Cantera(RMG_results):
    """Convert the Chemkin file into a Cantera file.
    
    Does its work inside RMG_results/chemkin"""
    
    from Cantera import ck2cti
    starting_dir = os.path.getcwd()
    chemkin_dir = os.path.join(RMG_results,'chemkin')
    os.path.chdir(chemkin_dir)
    try:
        infile='chem.inp'
        thermodb=''
        trandb=''
        nm='chem'
        ck2cti.ck2cti(infile = infile, thermodb = thermodb,  trandb = trandb, idtag = nm, debug=0, validate=1)
    finally:
        os.path.chdir(starting_dir)

def convertFinalModel2MixMaster(RMG_results):
    """Convert the Final_Model.txt into appropriate CSV data file for mixmaster.
    
    Needs a MolarMasses.txt file, which is created in another function"""
    
    massesfilename=os.path.join(RMG_results,'MolarMasses.txt')
    print "Reading molar masses from",massesfilename
    massesfile=file(massesfilename)
    massesdict=dict()
    for line in massesfile:
        (species,mass)=line.split()
        massesdict[species]=mass
    massesfile.close()
    
    temperature=273+150
    pressure=208*101325
    print "Using these settings:\n Temperature: %f K \t Pressure: %f Pa\n"%(temperature,pressure)
    
    # load file
    filename ='Final_Model.txt'
    filepath = os.path.join(RMG_results,filename)
    resultFile=file(filepath)
    
    # search for "Mole Fraction Profile Output"
    line=resultFile.next()
    while (line.find('Mole Fraction Profile Output')<0):
        line=resultFile.next()
    # add "T \t P" to the  following line
    titles=resultFile.next()
    print "Species:",titles
    output=titles.strip()+"\tT\tP\tnothing\n"
    items=titles.split()
    assert items[0]=='Time'
    speciesnames=items[1:]
    masses=list()
    for species in speciesnames:
        masses.append(float(massesdict[species]))
    	
    # add the temperature IN KELVIN and pressure IN PASCAL to all the following nonblank lines
    line=resultFile.next()
    while (line.strip()):
        massfractions=[]
        massfractionsum = 0
        items = line.split()
        time = items[0]
        molefracs = items[1:]
        for i,molefrac in enumerate(molefracs):
            massfrac = float(molefrac)*masses[i]
            massfractions.append(massfrac)
            massfractionsum += massfrac
        massfractions = [str(m/massfractionsum) for m in massfractions]
        output += str(time)+'\t'
        output += '\t'.join(massfractions)
        output +=  "\t%f\t%f\t0\n"%(temperature,pressure)
        line=resultFile.next()
    # turn whitespaces into commas
    # save the output
    outputFile=file(os.path.join(RMG_results,'ForMixMaster.csv'),'w')
    outputFile.write(output.replace('\t',','))
    outputFile.close()
    print "ForMixMaster.csv now contains mass fractions, as required by MixMaster"
    

def makeTableOfSpecies(RMG_results):
    """Make a pretty table of species"""
    ### make pretty table of species
    import ctml_writer
    from ctml_writer import *
    # these lists store top-level entries. Empty them!
    ctml_writer._elements = []
    ctml_writer._species = []
    ctml_writer._speciesnames = []
    ctml_writer._phases = []
    ctml_writer._reactions = []
    ctml_writer._atw = {}
    ctml_writer._enames = {}
    ctml_writer._valsp = ''
    ctml_writer._valrxn = ''
    ctml_writer._valexport = ''
    ctml_writer._valfmt = ''
    
    execfile('chem.cti')
    
    import jinja2
    env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'))
    template = env.get_template('rxnlist.html')
    outstring=template.render(title=infile, reactionList=ctml_writer._reactions)
    outfile=file('ReactionList'+'.html','w')
    outfile.write(outstring)
    outfile.close()

def loadMixMaster(RMG_results):
    """Load MixMaster"""
    os.path.chdir(RMG_results)
    from MixMaster import MixMaster
    o=MixMaster()
    o.loadmech('','chem.cti')
    
if __name__ == "__main__":
    RMG_results = "RMG_result"
    print "Taking results from ",os.path.realpath(RMG_results)
    drawMolecules(RMG_results)
    convertChemkin2Cantera(RMG_results)
    convertFinalModel2MixMaster(RMG_results)
    makeTableOfSpecies(RMG_results)