import numpy as np
from scipy.optimize import minimize

def shortAndLong(Omega_mu, sr_constraint, lr_constraint, F1):
    if np.array_equal(Omega_mu, Omega_mu.T):
        size = Omega_mu.shape[0]
    else:
        raise ValueError("Covariance matrix must be symmetrical.")
    
    M = np.identity(size) # initialize M

    # Flatten M and omega for scipy.optimize
    m = M.flatten()

    # Get 1-indexed column of a flattened matrix.
    def get_col(x, col):
        return x[(col-1) * size : col * size]

    def objective_func(x):
        # The Forbenius norm of (MM'-Omega)
        recovered = x.reshape((size, size)).T
        return np.linalg.norm(np.dot(recovered, recovered.T)-Omega_mu, 'fro')

    def sr_constraint_func(x, sr_cons):
        return x[size*(sr_cons[1]-1) + sr_cons[0]-1]
    def lr_constraint_func(x, lr_cons):
        return np.dot(F1[lr_cons[0]-1, :], get_col(x, lr_cons[1]))
    cons = []
    for sr_cons in sr_constraint:
        cons.append({'type':'eq', 'fun':sr_constraint_func, 'args':(sr_cons,)})
    for lr_cons in lr_constraint:
        cons.append({'type':'eq', 'fun':lr_constraint_func, 'args':(lr_cons,)})
    
    ftol = 1e-7
    for i, val in np.ndenumerate(Omega_mu):
        if 0<val<ftol:
            ftol = val

    options = {
        'ftol': ftol*1e-3,  # Function tolerance. Must be set carefully as the covariance numbers could be small
        'disp': False    # Display the solver information
    }

    result = minimize(objective_func, m, constraints = cons, options = options)
    M = result.x.reshape((size, size)).T

    # print("Omega_mu:")
    # print(Omega_mu, '\n')
    # print("M*M^{-1}:")
    # print(np.dot(M, M.T), '\n')

    return M

def test():
    Omega_mu = np.array([[0.8,0.5],[0.5,0.8]])
    F1 = np.array([[4,5],[7,8]])
    sr_constraint = []
    lr_constraint = [(1,2)]
    M = shortAndLong(Omega_mu, sr_constraint, lr_constraint, F1)
    print(Omega_mu)
    print(np.dot(M,M.T))


if __name__ == "__main__":
    test()