#HW5 page rank calcs
import numpy as np

#Calculate pagerank steps until matrix converges
def pr_convergence(m, v, max_steps):
    for i in range(2,max_steps):
        #calculate transition matrix after i steps
        prob_m = np.linalg.matrix_power(m,i)*v

        #check if each row is uniform
        row_uniformity = [np.allclose(row, row[0], atol=1e-9, rtol=0) for row in prob_m] 

        if all(row_uniformity):
            #calculate transition matrix at previous step
            prob_c = np.linalg.matrix_power(m,i-1)*v

            #check if matrix has converged
            if (np.allclose(prob_m, prob_c, atol=1e-9, rtol=0)): 
                print(f'Convergence matrix after {i} steps:')
                print(prob_m)
                print()
                print('Pageranks:')
                print(np.sum(prob_m, axis=1))
                return np.sum(prob_m, axis=1)


a = np.array([
    [  0,   1,   1,   0],#A
    [1/2,   0,   0, 1/2],#Y
    [  0,   0,   0, 1/2],#B
    [1/2,   0,   0,   0] #X
    # A    Y    B    X
    ])

v4 = np.array([1/4,1/4,1/4,1/4])

pr_convergence(a, v4, 75)


b = np.array([
    [0, 1/2,   1],#A
    [1,   0,   0],#Y
    [0, 1/2,   0] #X
    #A   Y    X
    ])

v3 = np.array([1/3,1/3,1/3]) 

print()
b_con = pr_convergence(b, v3, 75)

pr_Q = 0 * b_con[0] + 1/3 * b_con[1] + 1/2 * b_con[2]
print(pr_Q)