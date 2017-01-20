import numpy as np

from tikypy import BasePrior
import tikypy.utils as tikutils


class CustomPrior(BasePrior):
    '''Specify a custom prior
    '''
    def __init__(self, *args, **kwargs):
        '''
        '''
        super(CustomPrior, self).__init__(*args, **kwargs)


class PriorFromPenalty(BasePrior):
    '''
    '''
    def __init__(self, penalty, **kwargs):
        '''
        '''
        prior = np.zeros_like(penalty)

        super(PriorFromPenalty, self).__init__(prior, **kwargs)

        # overwrite penalty after init
        self.penalty = penalty.copy()
        self.wishart = np.eye(penalty.shape[0])
        self.wishart_lambda = 0.0

    def prior2penalty(self, regularizer=0.0, dodetnorm=True):
        if regularizer > 0.0:
            # make sure we have a valid prior
            assert not np.allclose(self.prior, 0)
            penalty = super(PriorFromPenalty, self).prior2penalty(regularizer=regularizer,
                                                                  dodetnorm=dodetnorm)
        elif dodetnorm:
            # re-scale
            penalty = self.penalty / tikutils.determinant_normalizer(self.penalty)
        else:
            # exact
            penalty = self.penalty
        return penalty

    def set_wishart(self, wishart_prior):
        '''
        '''
        if isinstance(wishart_prior, BasePrior):
            wishart_prior = wishart_prior.asarray
        assert np.allclose(wishart_prior.shape, self.penalty.shape)
        self.wishart = wishart_prior

    def update_prior(self, wishart_lambda=0.0, dodetnorm=False):
        '''
        '''
        self.wishart_lambda = wishart_lambda

        # compute prior
        prior = np.linalg.inv(self.penalty + self.wishart_lambda*self.wishart)
        # update object prior
        self.prior = prior

        if dodetnorm:
            # normalize
            self.normalize_prior()


class SphericalPrior(BasePrior):
    '''Equivalent to ridge.
    '''
    def __init__(self, nfeatures=20, **kwargs):
        '''
        '''
        raw_prior = np.eye(nfeatures)
        super(SphericalPrior, self).__init__(raw_prior, **kwargs)

    def update_prior(self, nfeatures):
        self.prior = np.eye(nfeatures)
