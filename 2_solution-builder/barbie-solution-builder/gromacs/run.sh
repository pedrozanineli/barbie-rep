#!/bin/bash

#SBATCH --job-name=b1_min_opt
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH -p gpu
#SBATCH --time=48:00:00

module load gromacs/2023.3

export OMP_NUM_THREADS=1

init="step3_input"
mini_prefix="step4.0_minimization"
equi_prefix="step4.1_equilibration"
prod_prefix="step5_production"
prod_step="step5"

# Minimizacao
gmx_mpi grompp -f "${mini_prefix}.mdp" -o "${mini_prefix}.tpr" -c "${init}.gro" -r "${init}.gro" -p topol.top -n index.ndx -maxwarn 0
gmx_mpi mdrun -v -deffnm "${mini_prefix}"

# Equilibrio
gmx_mpi grompp -f "${equi_prefix}.mdp" -o "${equi_prefix}.tpr" -c "${mini_prefix}.gro" -r "${init}.gro" -p topol.top -n index.ndx
gmx_mpi mdrun -v -deffnm "${equi_prefix}"

# Producao
set cnt    = 1
set cntmax = 10

while ( ${cnt} <= ${cntmax} )
    @ pcnt = ${cnt} - 1
    set istep = "${prod_step}_${cnt}"
    set pstep = "${prod_step}_${pcnt}"

	if ( ${cnt} == 1 ) then
        set pstep = ${equi_prefix}
        gmx_mpi grompp -f "${prod_prefix}.mdp" -o "${istep}.tpr" -c "${pstep}.gro" -p topol.top -n index.ndx
	else
        gmx_mpi grompp -f "${prod_prefix}.mdp" -o "${istep}.tpr" -c "${pstep}.gro" -t "${pstep}.cpt" -p topol.top -n index.ndx
	endif
	gmx_mpi mdrun -v -deffnm ${istep}
	@ cnt += 1
end