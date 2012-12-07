
import scipy
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


def spread_plot(y, x=None, resol=10, color='blue', axes=None):
    """Create a running density plot of sample values.

    This function visualizes the distribution of values in each row of
    y. This is done by showing overlapping polygons which represent
    varying quantile ranges. The number of overlapping polygons is
    determined by resol.

    Parameters
    ----------
    y: array_like
        A 2-dimensional array of data, where each column is treated as a sample of
        some metric. NaN values are treated as missing. The median, 0.25 and
        0.75 quantiles, minimum and maximum of the sample are plotted for each
        column of y.
    x: array_like or None, optional
        A 1-dimensional array of x values that should be used in plotting,
        where x[i] corresponds to y[:, i]. If x is None (default), then the
        indices of the columns of y are used as x values.
    resol: int
        (2 * resol) quantile partitions are rendered.
    color: matplotlib color specification, optional
        The color with which to plot the samples. The default is 'blue'.
    axes: matplotlib.axes.AxesSubplot object or None, optional
        Axes on which the plot should be created. If None (default), then a new
        figure is created and new axes are created on this figure.

    Returns
    -------
    h: list
        List of handles to Patch ojects that are created on the
        specified axes.
    """
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)
    else:
        fig = axes.get_figure()
    y = np.atleast_2d(y)
    if y.ndim != 2:
        raise ValueError("y must be a 2-dimensional array")
    m, n = y.shape
    quantiles = scipy.stats.mstats.mquantiles(y,
            np.linspace(0.0, 1.0, 2 * (resol + 1)), axis=0).filled()
    if x is None:
        x = np.arange(n, dtype=float)
    x = np.asarray(x)
    if not x.size == n:
        raise ValueError('x size does not match number of columns of y')
    x_replicated = np.concatenate((x, x[::-1]), axis=0)
    # Plot empirical density
    for i in xrange(resol + 1):
        poly = matplotlib.patches.Polygon(
            np.column_stack((x_replicated,
                np.concatenate((quantiles[i, :], quantiles[-(i + 1), ::-1]), axis=0))),
                facecolor=color, fill=True, edgecolor='none')
        poly.set_alpha(1.0 / resol)
        axes.add_patch(poly)
    # Adjust axes
    axes.autoscale_view()
    return fig

def dstat(p, q):
  return np.max(np.abs(np.cumsum(p) - np.cumsum(q)))

def variance_plot(arr3d, pcts):

    if not np.all(arr3d[0,-1,:] == arr3d[1,-1,:]):
        raise Exception("don't know where truth is in arr3d")
    truth = arr3d[0,-1,:]

    dstat_arr = np.apply_along_axis(dstat, 2, arr3d, truth)


    vars = np.apply_along_axis(np.var, 0, dstat_arr)
    plt.plot(pcts, vars, 'g-')
    plt.title('Variance of D-statistic')
    plt.xlabel('Sampling Percentage')
    plt.ylabel('Variance')


def threshold_plot(arr3d, pcts):


    if not np.all(arr3d[0,-1,:] == arr3d[1,-1,:]):
        raise Exception("don't know where truth is in arr3d")
    truth = arr3d[0,-1,:]

    dstat_arr = np.apply_along_axis(dstat, 2, arr3d, truth)
    critical_quantiles = np.apply_along_axis(stats.mstats.mquantiles, 0, dstat_arr, .95)
    critical_quantiles = np.squeeze(critical_quantiles)

    thresholds = np.linspace(0., 1., 100)
    y = np.array([pcts[np.argwhere(critical_quantiles <= thresh)[0]] for thresh in thresholds])
    y = np.squeeze(y)

    plt.plot(thresholds, y, 'rx')
    plt.title("Threshold Plot")
    plt.xlabel('D-statistic threshold')
    plt.ylabel('Minimum Sampling Pct for 95% confidence <= threshold')

### example
pcts = np.linspace(.1,1,11) # THIS IS A LIE! how can I read in the sampling percentages used?`
dd_arr = np.fromfile('dd_mx', sep = ' ').reshape((100, 11, 1384))

### this first plot is not used
spread_plot(np.apply_along_axis(lambda x: np.sum(np.arange(1384) * x),
				2, dd_arr), x=pcts)
plt.title("average degree")
plt.show()

spread_plot(np.apply_along_axis(dstat, 2, dd_arr, dd_arr[0,10,:]), x=pcts)
plt.title('D-statistic Diribution')
plt.xlabel('Sampling Percentage')
plt.ylabel('Distribution of D-statistic')
plt.show()

variance_plot(dd_arr, pcts)
plt.show()

threshold_plot(dd_arr, pcts)
plt.title('threshold plot')
plt.show()
