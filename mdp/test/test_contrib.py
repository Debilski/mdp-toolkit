"""These are test functions for MDP contributed nodes.

Run them with:
>>> import mdp
>>> mdp.test("contrib")

"""

# import ALL stuff we use for standard nodes and delete the
# stuff we don't need. I know, this is a dirty trick.
from test_nodes import *

mc = mdp.nodes

import itertools
import random

def _s_shape(theta):
    """
    returns x,y
      a 2-dimensional S-shaped function
      for theta ranging from 0 to 1
    """
    t = 3*numx.pi * (theta-0.5)
    x = numx.sin(t)
    y = numx.sign(t)*(numx.cos(t)-1)
    return x,y

def _s_shape_1D(n):
    t = numx.linspace(0., 1., n)
    x, z = _s_shape(t)
    y = numx.linspace(0., 5., n)
    return x, y, z, t

def _s_shape_2D(nt, ny):
    t, y = numx.meshgrid(numx.linspace(0., 1., nt),
                         numx.linspace(0., 2., ny))
    t = t.flatten()
    y = y.flatten()
    x, z = _s_shape(t)
    return x, y, z, t

def _compare_neighbors(orig, proj, k):
    n = orig.shape[0]
    err = numx.zeros((n,))
    # compare neighbors indices
    for i in range(n):
        # neighbors in original space
        dist = orig - orig[i,:]
        orig_nbrs = numx.argsort((dist**2).sum(1))[1:k+1]
        orig_nbrs.sort()
        # neighbors in projected space
        dist = proj - proj[i,:]
        proj_nbrs = numx.argsort((dist**2).sum(1))[1:k+1]
        proj_nbrs.sort()
        for idx in orig_nbrs:
            if idx not in proj_nbrs:
                err[i] += 1
    return err

def _randomly_filled_hypercube(widths, num_elem=1000):
    """Fills a hypercube with given widths, centred at the origin.
    """
    p = []
    for i in xrange(num_elem):
        rand_data = numx.random.random(len(widths))
        rand_data = [w*(d - 0.5) for d, w in zip(rand_data, widths)]
        p.append(tuple(rand_data))
    return p

def _randomly_filled_hyperball(dim, radius, num_elem=1000):
    """Fills a hyperball with a number of random elements.
    """
    r = numx.random.random(num_elem)
    points = numx.random.random((num_elem, dim))
    for i in xrange(len(points)):
        norm = numx.linalg.norm(points[i])
        scale = pow(r[i], 1./dim)
        points[i] = points[i] * radius * scale / norm
    return points

def _random_clusters(positions, radius=1, num_elem=1000):
    """Puts random clusters with num_elem elements at the given positions.
    positions - a list of tuples
    """
    data = []
    for p in positions:
        dim = len(p)
        ball = _randomly_filled_hyperball(dim, radius, num_elem)
        ball = [numx.array(b) + numx.array(p) for b in ball]
        data.append(ball)
    return data

def _linear_separable_data(positions, labels, radius=1, num_elem=1000, shuffled=False):
    """Tries to make up some linear separable data.
    num_elem - the number of elements in each
    """
    assert len(positions) == len(labels)
    
    data = numx.vstack( _random_clusters(positions, radius, num_elem) )
    #data = numx.vstack( (numx.random.random( (num_elem,2) ) - dist,
    #                     numx.random.random( (num_elem,2) ) + dist) )
    a_labels = numx.hstack(map(lambda x: [x] * num_elem, labels))
    if shuffled:
        ind = range(len(data))
        random.shuffle(ind)
        return data[ind], a_labels[ind]
    return data, a_labels

class ContribTestSuite(NodesTestSuite):
    def __init__(self, testname=None):
        NodesTestSuite.__init__(self, testname=testname)
        self.mat_dim = (100, 3)
        self._cleanup_tests()

    def _set_nodes(self):
        self._nodes = [mc.JADENode,
                       mc.NIPALSNode,
                       (mc.XSFANode, [(mc.PolynomialExpansionNode, (1,), {}),
                                      (mc.PolynomialExpansionNode, (1,), {}),
                                      True],None),
                       (mc.LLENode, [3, 0.001, False], None),
                       (mc.LLENode, [3, 0.001, True], None),
                       (mc.HLLENode, [10, 0.001, False], None),
                       (mc.HLLENode, [10, 0.001, True], None)]

    def _fastica_test_factory(self):
        # we don't want the fastica tests here
        pass

    def _cleanup_tests(self):
        # remove all nodes test that belong to the NodesTestSuite
        # yes, I know is a dirty trick.
        test_ids = [x.id() for x in self._tests]
        i = 0
        for test in test_ids:
            if test[:4] == "test":
                try:
                    getattr(NodesTestSuite, test)
                    # if we did not get an exception
                    # the test belongs to NodesTestSuite
                    self._tests.pop(i)
                    i -= 1
                except Exception, e:
                    pass
            i += 1

    def testJADENode(self):
        trials = 3
        for i in range(trials):
            try: 
                ica = mdp.nodes.JADENode(limit = 10**(-self.decimal))
                ica2 = ica.copy()
                self._testICANode(ica, rand_func=numx_rand.exponential)
                self._testICANodeMatrices(ica2)
                return
            except Exception, exc:
                pass
        raise exc
    
    def testNIPALSNode(self):
        line_x = numx.zeros((1000,2),"d")
        line_y = numx.zeros((1000,2),"d")
        line_x[:,0] = numx.linspace(-1,1,num=1000,endpoint=1)
        line_y[:,1] = numx.linspace(-0.2,0.2,num=1000,endpoint=1)
        mat = numx.concatenate((line_x,line_y))
        des_var = std(mat,axis=0)
        utils.rotate(mat,uniform()*2*numx.pi)
        mat += uniform(2)
        pca = mdp.nodes.NIPALSNode(conv=1E-15, max_it=1000)
        pca.train(mat)
        act_mat = pca.execute(mat)
        assert_array_almost_equal(mean(act_mat,axis=0),\
                                  [0,0],self.decimal)
        assert_array_almost_equal(std(act_mat,axis=0),\
                                  des_var,self.decimal)
        # test a bug in v.1.1.1, should not crash
        pca.inverse(act_mat[:,:1])
        # try standard PCA on the same data and compare the eigenvalues
        pca2 = mdp.nodes.PCANode()
        pca2.train(mat)
        pca2.stop_training()
        assert_array_almost_equal(pca2.d, pca.d, self.decimal)
        
    def testNIPALSNode_desired_variance(self):
        mat, mix, inp = self._get_random_mix(mat_dim=(1000, 3))
        # first make them white
        pca = mdp.nodes.WhiteningNode()
        pca.train(mat)
        mat = pca.execute(mat)
        # set the variances
        mat *= [0.6,0.3,0.1]
        #mat -= mat.mean(axis=0)
        pca = mdp.nodes.NIPALSNode(output_dim=0.8)
        pca.train(mat)
        out = pca.execute(mat)
        # check that we got exactly two output_dim:
        assert pca.output_dim == 2
        assert out.shape[1] == 2
        # check that explained variance is > 0.8 and < 1
        assert (pca.explained_variance > 0.8 and pca.explained_variance < 1)

    def testLLENode(self):
        # 1D S-shape in 3D
        n, k = 50, 2
        x, y, z, t = _s_shape_1D(n)
        data = numx.asarray([x,y,z]).T

        res = mdp.nodes.LLENode(k, output_dim=1, svd=False)(data)
        # check that the neighbors are the same
        err = _compare_neighbors(data, res, k)
        assert err.max() == 0

        # with svd=True
        res = mdp.nodes.LLENode(k, output_dim=1, svd=True)(data)
        err = _compare_neighbors(data, res, k)
        assert err.max() == 0
        
        # 2D S-shape in 3D
        nt, ny = 40, 15
        n, k = nt*ny, 8
        x, y, z, t = _s_shape_2D(nt, ny)
        data = numx.asarray([x,y,z]).T
        res = mdp.nodes.LLENode(k, output_dim=2, svd=False)(data)
        res[:,0] /= res[:,0].std()
        res[:,1] /= res[:,1].std()

        # test alignment
        yval = y[::nt]
        tval = t[:ny]
        for yv in yval:
            idx = numx.nonzero(y==yv)[0]
            assert numx.all(res[idx,1]-res[idx[0],1]<1e-2),\
                   'Projection should be aligned as original space'
        for tv in tval:
            idx = numx.nonzero(t==tv)[0]
            assert numx.all(res[idx,0]-res[idx[0],0]<1e-2),\
                   'Projection should be aligned as original space'

    def testLLENode_outputdim_float_bug(self):
        # 1D S-shape in 3D, output_dim
        n, k = 50, 2
        x, y, z, t = _s_shape_1D(n)
        data = numx.asarray([x,y,z]).T

        res = mdp.nodes.LLENode(k, output_dim=0.9, svd=True)(data)
        # check that the neighbors are the same
        err = _compare_neighbors(data, res, k)
        assert err.max() == 0

    def testHLLENode(self):
        # 1D S-shape in 3D
        n, k = 250, 4
        x, y, z, t = _s_shape_1D(n)
        data = numx.asarray([x,y,z]).T

        res = mdp.nodes.HLLENode(k, r=0.001, output_dim=1, svd=False)(data)
        # check that the neighbors are the same
        err = _compare_neighbors(data, res, k)
        assert err.max() == 0

        # with svd=True
        res = mdp.nodes.HLLENode(k, r=0.001, output_dim=1, svd=True)(data)
        err = _compare_neighbors(data, res, k)
        assert err.max() == 0
        
        # 2D S-shape in 3D
        nt, ny = 40, 15
        n, k = nt*ny, 8
        x, y, z, t = _s_shape_2D(nt, ny)
        data = numx.asarray([x,y,z]).T
        res = mdp.nodes.HLLENode(k, r=0.001, output_dim=2, svd=False)(data)
        res[:,0] /= res[:,0].std()
        res[:,1] /= res[:,1].std()

        # test alignment
        yval = y[::nt]
        tval = t[:ny]
        for yv in yval:
            idx = numx.nonzero(y==yv)[0]
            assert numx.all(res[idx,1]-res[idx[0],1]<1e-2),\
                   'Projection should be aligned as original space'
        for tv in tval:
            idx = numx.nonzero(t==tv)[0]
            assert numx.all(res[idx,0]-res[idx[0],0]<1e-2),\
                   'Projection should be aligned as original space'

    def testXSFANode(self):
        T = 5000
        N = 3
        src = numx_rand.random((T, N))*2-1
        # create three souces with different speeds
        fsrc = numx_fft.rfft(src, axis=0)

        for i in range(N):
            fsrc[(i+1)*(T/10):, i] = 0.

        src = numx_fft.irfft(fsrc,axis=0)
        src -= src.mean(axis=0)
        src /= src.std(axis=0)

        #mix = sigmoid(numx.dot(src, mdp.utils.random_rot(3)))
        mix = src

        flow = mdp.Flow([mc.XSFANode()])
        # let's test also chunk-mode training
        flow.train([[mix[:T/2, :], mix[T/2:, :]]])
        
        out = flow(mix)
        #import bimdp
        #tr_filename = bimdp.show_training(flow=flow,
        #                                  data_iterators=[[mix[:T/2, :], mix[T/2:, :]]])
        #ex_filename, out = bimdp.show_execution(flow, x=mix)

        corrs = mdp.utils.cov_maxima(mdp.utils.cov2(out, src))
        assert min(corrs) > 0.8, ('source/estimate minimal'
                                  ' covariance: %g' % min(corrs))

    def testShogunSVMClassifier(self):
        # TODO: Implement parameter ranges
        num_train = 10
        num_test = 10
        dist = 1
        width = 2.1
        C = 1
        epsilon = 1e-5
        for positions in [#((1,), (-1,)),
                          ((1,1), (-1,-1), (1, -1), (-1, 1)),
                          #((1,1,1), (-1,-1,1)),
                          #((1,1,1,1), (-1,1,1,1)),
                          #((1,1,1,1), (-1,-1,-1,-1))
                          ]:

            radius = 0.3

            if len(positions) == 2:
                labels = (-1, 1)
            elif len(positions) == 3:
                labels = (-1, 1, 1)
            elif len(positions) == 4:
                labels = (-1, -1, 1, 1)
            traindata_real, trainlab = _linear_separable_data(positions, labels, radius, num_train)
            testdata_real, testlab = _linear_separable_data(positions, labels, radius, num_test)
            
            
            from shogun import Classifier
            def is_shogun_classifier(test_classifier):
                try:
                    return issubclass(test_classifier, (Classifier.CKernelMachine, Classifier.LinearClassifier))
                except (TypeError, NameError):
                    # need to fetch NameError for some swig reasons
                    return False

            default_shogun_classifiers = []
            for cl in dir(Classifier):
                test_classifier = getattr(Classifier, cl)
                if is_shogun_classifier(test_classifier):
                    default_shogun_classifiers.append(test_classifier)
            
            print default_shogun_classifiers
            
            kernels = list(mdp.nodes.ShogunSVMClassifier.kernel_parameters.keys())
            combinations = {'classifier': default_shogun_classifiers, # ["libsvm", "SVMLin"],
                            'kernel': kernels}
            for comb in utils.orthogonal_permutations(combinations):
                if comb['kernel'] in ['PyramidChi2', 'Chi2Kernel']:
                    # We don't have good init arguments for that one
                    continue
                if comb['classifier'].__name__ in ['LaRank', 'LibLinear', 'LibSVMMultiClass',
                                                   'MKLClassification', 'MKLMultiClass', 'MKLOneClass',
                                                   'MultiClassSVM', 'SVM', 'SVMOcas', 'SVMSGD', 'ScatterSVM',
                                                   'SubGradientSVM']:
                    # We don't have good init arguments for that one
                    continue
                #print "Trying", comb
                try:
                    sg_node = mdp.nodes.ShogunSVMClassifier(classifier=comb['classifier'])
                except mdp.NodeException:
                    print "%s failed to initialise" % comb['classifier']
                    continue
                
                if sg_node.classifier.takes_kernel:
                    sg_node.set_kernel(comb['kernel'])
                    
                # train in two chunks to check update mechanism
                sg_node.train( traindata_real[:num_train], trainlab[:num_train] )
                sg_node.train( traindata_real[num_train:], trainlab[num_train:] )
                
                out = sg_node.classify(testdata_real)
                # Test also for inverse
                test_okay = numx.all(numx.sign(out) == testlab) or numx.all(numx.sign(out) != testlab)
                if not test_okay:
                    print comb, "failed"
                    print numx.sign(out).astype(int), testlab
                #assert testerr, ('classification result', comb)

    def testLibSVMClassifier(self):
        num_train = 100
        num_test = 100
        dist = 0.4
        width = 2.1
        C = 1
        epsilon = 1e-5
        for pos_1, pos_2 in [((1,), (-1,)),
                             ((1,1), (-1,-1)),
                             ((1,1,1), (-1,-1,1)),
                             ((1,1,1,1), (-1,1,1,1)),
                             ((1,1,1,1), (-1,-1,-1,-1))]:
            radius = 0.3

            traindata_real, trainlab = _linear_separable_data((pos_1, pos_2), (-1, 1), radius, num_train, True)
            testdata_real, testlab = _linear_separable_data((pos_1, pos_2), (-1, 1), radius, num_test, True)
        
            combinations = {'kernel': mdp.nodes.LibSVMClassifier.kernels,
                            'classifier': mdp.nodes.LibSVMClassifier.classifiers}
        
            for comb in utils.orthogonal_permutations(combinations):
                svm_node = mdp.nodes.LibSVMClassifier()
                svm_node.set_kernel(comb['kernel'])
                svm_node.set_classifier(comb['classifier'])
                
                # train in two chunks to check update mechanism
                svm_node.train( traindata_real[:num_train], trainlab[:num_train] )
                svm_node.train( traindata_real[num_train:], trainlab[num_train:] )

                out = svm_node.classify(testdata_real)

                testerr = numx.all(numx.sign(out) == testlab)
                # TODO: Cross-validation testing
                #svm_node._cross_validation(3, svm_node.parameter)
                #print r.probability(testdata_real)
        
                assert testerr, ('classification result for ', comb)

def get_suite(testname=None):
    return ContribTestSuite(testname=testname)

if __name__ == '__main__':
    numx_rand.seed(1268049219)
    unittest.TextTestRunner(verbosity=2).run(get_suite())



