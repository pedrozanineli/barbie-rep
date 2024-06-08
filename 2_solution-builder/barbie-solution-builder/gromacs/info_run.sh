#!/bin/bash

#SBATCH --job-name=infos
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH -p gpu
#SBATCH --time=48:00:00

module load gromacs/2023.3

echo 12 | gmx_mpi energy -f step4.1_equilibration.edr -o potential_energy.xvg

# gmx_mpi trjconv -s step5_10.tpr -f step5_10.xtc -o traj_final.pdb
# echo 0 | gmx_mpi trjconv -s step4.1_equilibration.tpr -f step4.1_equilibration.xtc -o traj_equilibration.pdb
