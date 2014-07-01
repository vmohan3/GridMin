tep = 6 // grid step size in degrees

    grid_shrink_factor = 2

    next_wells = {}

wells = {conformation_space}

do {

    if next_wells <> {} then: wells = next_wells

next_wells.clear()

for w in wells:

    for distance in range(num_offsets,1,-1):

        offset_tuples = generate_offset_tuples(distance)

    for (offset in offset_tuples):

grid = run_grid(w, grid_step, offset)

while grid != {}:

candidate_well = find_minimum(grid)

subgrid = expand_boundaries(candidate_well, kT)

if area(w) - area(subgrid) < threshold

next_wells += subgrid

grid -= subgrid

                // TODO: add in early termination condition for offsets

grid_step /= grid_shrink_factor

    } while ( wells != next_wells )

    return wells, wells.size()
