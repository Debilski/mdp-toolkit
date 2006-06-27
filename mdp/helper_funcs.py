## Automatically adapted for numpy Jun 26, 2006 by 

import mdp

def pca(x, **kwargs):
    """Filters multidimensioanl input data through its principal components.

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node PCANode. If any
    keyword arguments are specified, they are passed to its constructor.
    """
    pca = mdp.nodes.PCANode(**kwargs)
    pca.train(x)
    return pca.execute(x)
                              
def whitening(x, **kwargs):
    """Filters multidimensioanl input data through its principal components,
    rescaling the output signals such that they have unit variance.

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node WhiteningNode.
    If any keyword arguments are specified, they are passed to its constructor.
    """
    white = mdp.nodes.WhiteningNode(**kwargs)
    white.train(x)
    return white.execute(x)

def fastica(x, **kwargs):
    """Perform Independent Component Analysis on input data using the FastICA
    algorithm by Aapo Hyvarinen.

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node FastICANode.
    If any keyword arguments are specified, they are passed to its constructor.
    """
    ica = mdp.nodes.FastICANode(**kwargs)
    ica.train(x)
    return ica.execute(x)

def cubica(x, **kwargs):
    """Perform Independent Component Analysis on input data using the CuBICA
    algorithm by Tobias Blaschke.

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node CuBICANode.
    If any keyword arguments are specified, they are passed to its constructor.
    """
    ica = mdp.nodes.CuBICANode(**kwargs)
    ica.train(x)
    return ica.execute(x)

def sfa(x, **kwargs):
    """Perform Slow Feature Analysis on input data using the SFA
    algorithm by Laurenz Wiskott.

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node SFANode.
    If any keyword arguments are specified, they are passed to its constructor.
    """
    sfa = mdp.nodes.SFANode(**kwargs)
    sfa.train(x)
    return sfa.execute(x)

def get_eta(x, **kwargs):
    """Compute eta values (a slowness measure) of the input data.

    The delta value of a signal is a measure of its temporal
    variation, and is defined as the mean of the derivative squared,
    i.e. delta(x) = mean(dx/dt(t)^2).  delta(x) is zero if
    x is a constant signal, and increases if the temporal variation
    of the signal is larger.

    The eta value is a more intuitive measure of temporal variation,
    defined as
       eta(x) = T/(2*pi) * sqrt(delta(x))
    If x is a signal of length T which consists of a sine function
    that accomplishes exactly N oscillations, then eta(x)=N.

    Input data are normalized to have unit variance, such that it is
    possible to compare the temporal variation of two signals
    independently from their scaling.    

    Observations of the same variable are stored on rows, different variables
    are stored on columns.

    This is a shortcut function for the corresponding node EtaComputerNode.
    If any keyword arguments are specified, they are passed to its constructor.
    """
    eta = mdp.nodes.EtaComputerNode()
    eta.train(x)
    return eta.get_eta(**kwargs)
 
