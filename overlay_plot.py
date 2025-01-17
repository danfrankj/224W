import os
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
    plt.plot(x, np.mean(y, axis=0), 'm--', linewidth=2.0, hold=True)
    axes.autoscale_view()
    #return fig

def dstat(p, q):
    p = p / np.sum(p)
    q = q / np.sum(q)
    return np.max(np.abs(np.cumsum(p) - np.cumsum(q)))

def variance_plot(dstat_arr, pcts, metric=None, line_style='g-', graph=None):
    vars = np.apply_along_axis(np.var, 0, dstat_arr)
    plt.plot(pcts, vars, line_style, linewidth=2.5, label=graph)
    title = 'Variance of D-statistic'
    title = title + ' (' + metric.upper() + ')' if metric is not None else title
    plt.title(title)
    plt.legend(loc='upper right')
    plt.xlabel('Sampling Percentage')
    plt.ylabel('Variance')


def threshold_plot(dstat_arr, pcts, metric=None, line_style='r-', graph=None):

    critical_quantiles = np.apply_along_axis(stats.mstats.mquantiles, 0, dstat_arr, .95)
    critical_quantiles = np.squeeze(critical_quantiles)

    thresholds = np.linspace(0., 1., 100)
    y = np.array([pcts[np.argwhere(critical_quantiles <= thresh)[0]] for thresh in thresholds])
    y = np.squeeze(y)

    plt.plot(thresholds, y, line_style, linewidth=2.5, label=graph)

    title = 'Smallest Acceptable Sample Size'
    title = title + ' (' + metric.upper() + ')' if metric is not None else title
    plt.title(title)
    plt.legend(loc='upper right')
    plt.xlabel('D-statistic threshold')
    plt.ylabel('Minimum Sampling Pct for 95% confidence <= threshold')


def create_plots(metric='cc', graphs=['enron_new','dblp'], show=True):

    
    sampling_pcts = [np.fromfile(os.path.join('.', graph, metric+ '_samples'), sep=' ') for graph in graphs]
    dimensions = [np.fromfile(os.path.join('.', graph, metric + '_dim'), sep=' ') for graph in graphs]
    metric_arrs = [np.fromfile(os.path.join('.', graphs[i], metric + '_mx'), sep = ' ' ).reshape(dimensions[i]) for i in range(len(graphs))]

    """
    if dimension.size == 3:
        if not np.all(metric_arr[0,-1,:] == metric_arr[1,-1,:]):
            raise Exception("don't know where to find truth in 3d array")
        truth = metric_arr[0,-1,:]
        dstat_arr = np.apply_along_axis(dstat, 2, metric_arr, truth)
    elif dimension.size == 2:
        dstat_arr = metric_arr
    else:
        raise Exception("don't know what to do with a not 2 or 3 dim metric")
    """
    line_styles = ['r-', 'g-', 'b-', 'c-', 'm-', 'y-', 'k-']
    for i in range(len(graphs)):
        graph = graphs[i]   
        spread_plot(metric_arrs[i], x=sampling_pcts[i])
        plt.title('D-statistic Distribution ('+ metric.upper()+ ')' )
        plt.xlabel('Sampling Percentage')
        plt.ylabel('Distribution of D-statistic')
        plt.savefig(os.path.join('.', graph, 'figs', '_'.join((graph, metric, 'dstatdistn')) + '.pdf'))
        if show:
            plt.show()

    for i in range(len(graphs)):
        variance_plot(metric_arrs[i], sampling_pcts[i], metric=metric, line_style=line_styles[i], graph=graphs[i])
    plt.savefig(os.path.join('.', 'figs', '_'.join((metric, 'dstatvar_overlay')) + '.pdf'))
    if show:
        plt.show()

    for i in range(len(graphs)):
        threshold_plot(metric_arrs[i], sampling_pcts[i], metric=metric, line_style=line_styles[i], graph=graphs[i])
    plt.savefig(os.path.join('.','figs', '_'.join((metric, 'threshold_overlay')) + '.pdf'))
    if show:
        plt.show()
