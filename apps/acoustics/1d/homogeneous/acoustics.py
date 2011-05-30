#!/usr/bin/env python
# encoding: utf-8
    
def acoustics(use_PETSc=False,kernel_language='Fortran',soltype='classic',iplot=False,htmlplot=False,outdir='./_output'):
    """
    This example solves the 1-dimensional acoustics equations in a homogeneous
    medium.
    """
    from numpy import sqrt, exp, cos

    #=================================================================
    # Import the appropriate classes, depending on the options passed
    #=================================================================
    if use_PETSc:
        import petclaw as pyclaw
    else:
        import pyclaw

    if soltype=='classic':
        solver = pyclaw.ClawSolver1D()
    elif soltype=='sharpclaw':
        solver = pyclaw.SharpClawSolver1D()
    else: raise Exception('Unrecognized value of soltype.')

    #========================================================================
    # Instantiate the solver and define the system of equations to be solved
    #========================================================================
    solver.kernel_language=kernel_language
    from riemann import rp_acoustics
    solver.mwaves=rp_acoustics.mwaves
    if kernel_language=='Python': 
        solver.rp = rp_acoustics.rp_acoustics_1d
 
    solver.mthlim = pyclaw.limiters.MC

    #========================================================================
    # Instantiate the grid and set the boundary conditions
    #========================================================================
    left_BC =pyclaw.BC.reflecting
    right_BC=pyclaw.BC.outflow
    x = pyclaw.Dimension('x',0.0,1.0,100,mthbc_lower=left_BC,mthbc_upper=right_BC)
    grid = pyclaw.Grid(x)
    grid.mbc=solver.mbc

    #========================================================================
    # Set problem-specific variables
    #========================================================================
    rho = 1.0
    bulk = 1.0
    grid.aux_global['rho']=rho
    grid.aux_global['bulk']=bulk
    grid.aux_global['zz']=sqrt(rho*bulk)
    grid.aux_global['cc']=sqrt(rho/bulk)

    #========================================================================
    # Set the initial condition
    #========================================================================
    grid.meqn=rp_acoustics.meqn
    grid.zeros_q()
    xc=grid.x.center
    beta=100; gamma=0; x0=0.75
    grid.q[0,:] = exp(-beta * (xc-x0)**2) * cos(gamma * (xc - x0))
    
    #========================================================================
    # Set up the controller object
    #========================================================================
    claw = pyclaw.Controller()
    claw.solutions['n'] = pyclaw.Solution(grid)
    claw.solver = solver
    claw.outdir = outdir
    claw.tfinal = 1.0

    # Solve
    status = claw.run()

    # Plot results
    from petclaw import plot
    if htmlplot:  plot.plotHTML(outdir=outdir,format=claw.output_format)
    if iplot:     plot.plotInteractive(outdir=outdir,format=claw.output_format)

if __name__=="__main__":
    import sys
    from petclaw.util import _info_from_argv
    args, kwargs = _info_from_argv(sys.argv)
    error=acoustics(*args,**kwargs)