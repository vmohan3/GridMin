#Specify the number of Dihedral angles in given protein molecule
num_dihedral = 4

#Specify the initial grid size
increment = 10.0

#Specify the value of angle. The value of angle is varied
#from -M_PI to +M_PI
M_PI = 180

#Calculate the number of iterations needed per angle
iter = 2*(M_PI/increment)

#Specify the initial number of points to be sampled
num_pts = 500

#Specify the number of partitions to do for data of given
#protein molecule
num_part = 40

#Calculate the number of points to take from each partition
points_per_partition=num_pts/num_part

#Calculate total points for a given protein molecule
total_points = pow(iter,num_dihedral)

#Calculate the span. This is the number of points which we have
#in each divided partition.
span = total_points/num_part

#number of points to take. Not used in this implementation
points_to_take = int(0.5*num_pts)

#Specify the number of energy wells
num_energy_wells = 5

#specify the energy threshold for grid
energy_threshold = 0.1

#define the range in which energy is accepted
slack = 2
