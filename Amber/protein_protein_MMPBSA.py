# Dash
### Referance : https://ambermd.org/tutorials/advanced/tutorial3/py_script/index.htm

### COMMANDS
##python pp_MD_BE.py -c ras-raf.pdb -p1 ras.pdb -p2 raf.pdb -ff ff99SB -r mbondi2 -mc ras-raf_mutant.pdb -mp1 ras_mutant.pdb -cuda y
###

import os
import sys
import subprocess
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-c', required=True, help = "Complex pdb")
parser.add_argument('-p1',  required=True, help = "Protein1 pdb")
parser.add_argument('-p2', required=True, help = "Protein2 pdb")
parser.add_argument('-ff',  required=True, help = "protein ForceField")
parser.add_argument('-r',  required=True, help = "Radii")
parser.add_argument('-mc', help = "Mutant Complex pdb")
parser.add_argument('-mp1', help = "Mutant protein1 pdb")
parser.add_argument('-cuda', default=False, action="store_true", help = "Run using GPU")

args = parser.parse_args()


#INPUT FILES & VARIABLES
pdb_complex = args.c
pdb_protein_1 = args.p1
pdb_protein_2 = args.p2
receptor_ff = args.ff
radii =  args.r

mutant_complex =  args.mc
mutant_protein1 =  args.mp1

cuda = args.cuda

c_name = os.path.splitext(os.path.basename(pdb_complex))[0]
p1_name = os.path.splitext(os.path.basename(pdb_protein_1))[0]
p2_name = os.path.splitext(os.path.basename(pdb_protein_2))[0]



if receptor_ff == 'ff99SB':
    tleap_in = 'source oldff/leaprc.ff99SB\n'
elif receptor_ff == 'ff14SB':
    tleap_in = 'source leaprc.protein.ff14SB\n'
else:
    sys.exit('The receptor force field is invalid')


# Build the starting structure and run a simulation to obtain an equilibrated system.


# TLEAP SCRIPT
tleap_in += 'source leaprc.water.tip3p\n'
tleap_in += f'com = loadpdb {pdb_complex}\n'
tleap_in += f'{p1_name} = loadpdb {pdb_protein_1}\n'
tleap_in += f'{p2_name} = loadpdb {pdb_protein_2}\n'
tleap_in += f'set default PBRadii {radii}\n'
tleap_in += f'saveamberparm com {c_name}.prmtop {c_name}.inpcrd\n'
tleap_in += f'saveamberparm {p1_name} {p1_name}.prmtop {p1_name}.inpcrd\n'
tleap_in += f'saveamberparm {p2_name} {p2_name}.prmtop {p2_name}.inpcrd\n'
tleap_in += f'charge com\n'

tleap_in += f'solvatebox com TIP3PBOX 12.0\n'
tleap_in += f'saveamberparm com {c_name}_solvated.prmtop {c_name}_solvated.inpcrd\n'

if ((mutant_complex != None) or (mutant_protein1 != None)):
	mc_name = os.path.splitext(os.path.basename(mutant_complex))[0]
	mp1_name = os.path.splitext(os.path.basename(mutant_protein1))[0]

	tleap_in += f'com_mutant = loadpdb {mutant_complex}\n'
	tleap_in += f'ras_mutant = loadpdb {mutant_protein1}\n'
	tleap_in += f'saveamberparm com_mutant {mc_name}.prmtop {mc_name}.inpcrd\n'
	tleap_in += f'saveamberparm {mp1_name} {mp1_name}.prmtop {mp1_name}.inpcrd\n'
	tleap_in += f'quit'
else:
	tleap_in += f'quit'



print('COMPLEX PDB: ', pdb_complex)
print('PROTEIN 1 PDB: ', pdb_protein_1)
print('PROTEIN 2 PDB: ', pdb_protein_2)
print('SELECTED FORCEFIELD: ', receptor_ff)
print('RADII: ', radii)
print('MUTANT COMPLEX PDB: ', mutant_complex)
print('MUTANT PROTEIN 1 PDB: ', mutant_protein1)


print('TLEAP SCRIPT: \n', tleap_in)


# SAVE TLEAP COMMANDS IN TLEAP.IN FILE
with open('tleap.in','w') as out:
	out.write(tleap_in)

tleap_cmd = f'tleap -s -f tleap.in'

print('TLEAP Command: ', tleap_cmd)

print('Running TLEAP COMANDS: \n')

os.system(tleap_cmd)


print('TLEAP Command Execution Complete!\n')


# Equilibrate the solvated complex 

# MINIMIZATION
# EDIT THIS LINES FOR CHANGING MINIMIZATION PARAMETERS 


min_in ='''Minimization : raf-ras
 &cntrl
  imin=1,maxcyc=1000,ncyc=500,
  cut=8.0,ntb=1,
  ntc=2,ntf=2,
  ntpr=100,
  ntr=1, restraintmask=':1-242',
  restraint_wt=2.0
 /

 '''
with open('min.in','w') as out:
	out.write(min_in)


 
# sander -O -i min.in -o min.out -p ras-raf_solvated.prmtop -c ras-raf_solvated.inpcrd -r min.rst -ref ras-raf_solvated.inpcrd
min_cmd =f'sander -O -i min.in -o min.out -p {c_name}_solvated.prmtop -c {c_name}_solvated.inpcrd -r min.rst -x min.mdcrd -ref {c_name}_solvated.inpcrd && '

if cuda == True:
    min_cmd =f'pmemd.cuda -O -i min.in -o min.out -p {c_name}_solvated.prmtop -c {c_name}_solvated.inpcrd -r min.rst -x min.mdcrd -ref {c_name}_solvated.inpcrd &&'

min_cmd+=' gzip -9 min.mdcrd'

print('Minimization Command: ', min_cmd)

print('Running MINIMIZATION COMAND: \n')

os.system(min_cmd)

print('MINIMIZATION Command Execution Complete!\n')

# HEAT
# EDIT THIS LINES FOR CHANGING HEAT PARAMETERS 


heat_in ='''Heat : raf-ras
 &cntrl
  imin=0,irest=0,ntx=1,
  nstlim=25000,dt=0.002,
  ntc=2,ntf=2,
  cut=8.0, ntb=1,
  ntpr=500, ntwx=500,
  ntt=3, gamma_ln=2.0,
  tempi=0.0, temp0=300.0, ig=-1,
  ntr=1, restraintmask=':1-242',
  restraint_wt=2.0,
  nmropt=1
 /
 &wt TYPE='TEMP0', istep1=0, istep2=25000,
  value1=0.1, value2=300.0, /
 &wt TYPE='END' /

 '''
with open('heat.in','w') as out:
	out.write(heat_in)

# sander -O -i heat.in -o heat.out -p ras-raf_solvated.prmtop -c min.rst -r heat.rst -x heat.mdcrd -ref min.rst
heat_cmd =f'sander -O -i heat.in -o heat.out -p {c_name}_solvated.prmtop -c min.rst -r heat.rst -x heat.mdcrd -ref min.rst &&'

if cuda == True:
    heat_cmd =f'pmemd.cuda -O -i heat.in -o heat.out -p {c_name}_solvated.prmtop -c min.rst -r heat.rst -x heat.mdcrd -ref min.rst &&'

heat_cmd +=' gzip -9 heat.mdcrd'

print('HEAT Command: ', heat_cmd)

print('Running HEAT COMAND: \n')

os.system(heat_cmd)

print('HEAT Command Execution Complete!\n')

# DENSITY
# EDIT THIS LINES FOR CHANGING DENSITY PARAMETERS 


density_in ='''Density : raf-ras
 &cntrl
  imin=0,irest=1,ntx=5,
  nstlim=25000,dt=0.002,
  ntc=2,ntf=2,
  cut=8.0, ntb=2, ntp=1, taup=1.0,
  ntpr=500, ntwx=500,
  ntt=3, gamma_ln=2.0,
  temp0=300.0, ig=-1,
  ntr=1, restraintmask=':1-242',
  restraint_wt=2.0,
 /

 '''
with open('density.in','w') as out:
	out.write(density_in)

# sander -O -i density.in -o density.out -p ras-raf_solvated.prmtop -c heat.rst -r density.rst -x density.mdcrd -ref heat.rst
density_cmd =f'sander -O -i density.in -o density.out -p {c_name}_solvated.prmtop -c heat.rst -r density.rst -x density.mdcrd -ref heat.rst &&'

if cuda==True:
    density_cmd =f'pmemd.cuda -O -i density.in -o density.out -p {c_name}_solvated.prmtop -c heat.rst -r density.rst -x density.mdcrd -ref heat.rst &&'

density_cmd +=' gzip -9 density.mdcrd'

print('DENSITY Command: ', density_cmd)

print('Running DENSITY COMAND: \n')

os.system(density_cmd)

print('DENSITY Command Execution Complete!\n')

# EQUILIBRIUM
# EDIT THIS LINES FOR CHANGING EQUILIBRIUM PARAMETERS 


equil_in ='''Equil : raf-ras
 &cntrl
  imin=0,irest=1,ntx=5,
  nstlim=250000,dt=0.002,
  ntc=2,ntf=2,
  cut=8.0, ntb=2, ntp=1, taup=2.0,
  ntpr=1000, ntwx=1000,
  ntt=3, gamma_ln=2.0,
  temp0=300.0, ig=-1,
 /

 '''
with open('equil.in','w') as out:
	out.write(equil_in)

# sander -O -i equil.in -o equil.out -p ras-raf_solvated.prmtop -c density.rst -r equil.rst -x equil.mdcrd
equil_cmd =f'sander -O -i equil.in -o equil.out -p {c_name}_solvated.prmtop -c density.rst -r equil.rst -x equil.mdcrd &&'

if cuda==True:
    equil_cmd =f'pmemd.cuda -O -i equil.in -o equil.out -p {c_name}_solvated.prmtop -c density.rst -r equil.rst -x equil.mdcrd &&'

equil_cmd+=' gzip -9 equil.mdcrd'

print('EQUILIBRIUM Command: ', equil_cmd)

print('Running EQUILIBRIUM COMAND: \n')

os.system(equil_cmd)

print('EQUILIBRIUM Command Execution Complete!\n')


## EXTRA
# os.system('process_mdout.pl heat.out density.out equil.out')

# Run the production simulation and obtain an ensemble of snapshots.

# PRODUCTION
# EDIT THIS LINES FOR CHANGING PRODUCTION PARAMETERS 


prod_in ='''Production : raf-ras
&cntrl
  imin=0,irest=1,ntx=5,
  nstlim=250000,dt=0.002,
  ntc=2,ntf=2,
  cut=8.0, ntb=2, ntp=1, taup=2.0,
  ntpr=5000, ntwx=5000,
  ntt=3, gamma_ln=2.0,
  temp0=300.0, ig=-1,
 /

 '''
with open('prod.in','w') as out:
	out.write(prod_in)

# pmemd.cuda -O -i mdin -o mdout -p prmtop -c inpcrd -r restrt -x mdcrd -inf mdinfo
# pmemd -O -i prod.in -o prod1.out -p ras-raf_solvated.prmtop -c equil.rst -r prod1.rst -x prod1.mdcrd

#prod_cmd =f'pmemd -O -i prod.in -o prod1.out -p {c_name}_solvated.prmtop -c equil.rst -r prod1.rst -x prod1.mdcrd &&'
prod_cmd =f'sander -O -i prod.in -o prod1.out -p {c_name}_solvated.prmtop -c equil.rst -r prod1.rst -x prod1.mdcrd &&'
if cuda == True:
	prod_cmd =f'pmemd.cuda -O -i prod.in -o prod1.out -p {c_name}_solvated.prmtop -c equil.rst -r prod1.rst -x prod1.mdcrd &&'

prod_cmd+= ' gzip -9 prod*.mdcrd'

print('PRODUCTION Command: ', prod_cmd)

print('Running PRODUCTION COMAND: \n')

os.system(prod_cmd)

print('PRODUCTION Command Execution Complete!\n')


# MMPBSA 
# EDIT THIS LINES FOR CHANGING MMPBSA PARAMETERS 


mmpbsa_in ='''Input file for running PB and GB
&general
   endframe=50, verbose=1,
#  entropy=1,
/
&gb
  igb=2, saltcon=0.100
/
&pb
  istrng=0.100,
/
'''

print('MMPBSA FILE: ', mmpbsa_in)

with open('mmpbsa.in','w') as out:
	out.write(mmpbsa_in)

# MMPBSA.py -O -i mmpbsa.in -o FINAL_RESULTS_MMPBSA.dat -sp ras-raf_solvated.prmtop -cp ras-raf.prmtop -rp ras.prmtop -lp raf.prmtop -y *.mdcrd

if ((mutant_complex == None) or (mutant_protein1 == None)):
	mmpbsa_cmd =f'MMPBSA.py -O -i mmpbsa.in -o FINAL_RESULTS_MMPBSA.dat -sp {c_name}_solvated.prmtop -cp {c_name}.prmtop -rp {p1_name}.prmtop -lp {p2_name}.prmtop -y *.mdcrd'
else:
	mmpbsa_cmd =f'MMPBSA.py -O -i mmpbsa.in -o FINAL_RESULTS_MMPBSA.dat -sp {c_name}_solvated.prmtop -cp {c_name}.prmtop -rp {p1_name}.prmtop -lp {p2_name}.prmtop -y *.mdcrd -mc {mc_name}.prmtop -mr {mp1_name}.prmtop'


print('MMPBSA Command: ', mmpbsa_cmd)

print('Running MMPBSA COMAND: \n')

os.system(mmpbsa_cmd)

print('MMPBSA Command Execution Complete!\n')

print('PLEASE Check FINAL_RESULTS_MMPBSA.dat')
