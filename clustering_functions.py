import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score

def view_dbscan(topic_data, max_epsilon, min_epsilon=0.001, stepsize=1/1000):
    """
    Runs DBSCAN on range of nieighborhood sizes
    Returns dict for plotting
    """
    epsilons = []
    scores = []
    len_mask = []
    k_clusters = []
    sizes = []

    for ε in range(int(min_epsilon/stepsize), int(max_epsilon/stepsize)):
        ε = ε * stepsize
        model = DBSCAN(eps=ε, min_samples=4)
        model.fit(topic_data)
        labels = model.labels_
        mask = labels >= 0
        len_mask.append(sum(~mask) / topic_data.shape[0])
        k_clusters.append(len(set(labels)))
        try:
            silhouette_avg = silhouette_score(topic_data[mask,:], labels[mask])
        except ValueError:
            silhouette_avg = 0
        epsilons.append(ε)
        scores.append(silhouette_avg)

        cluster_sizes = [sum(labels == lbl) for lbl in set(labels)]
        cluster_sizes = sorted(cluster_sizes)[:-2]
        if k_clusters[-1] == 2:
            sizes.append(0)
        else:
            sizes.append(sum(cluster_sizes)/(k_clusters[-1]-2))
    return {"epsilons":epsilons, "scores":scores, "len_mask":len_mask, "k_clusters":k_clusters, "sizes":sizes}

def plot_exploration(epsilons, scores, len_mask, k_clusters, sizes, color="#680888", title=None):
    """
    Plots various metrics from dbscan exploration
    """
    plt.style.use("fivethirtyeight")
    plt.figure(dpi=150, figsize=(16,14))
    plt.suptitle(title, size=40)
    plt.tight_layout()

    plt.subplot(2,2,1)
    plt.ylabel("mean silhouette score (discarding noise)")
    fillplot(epsilons, scores, linewidth=2, color=color)

    plt.subplot(2,2,2)
    plt.ylabel("prevalence of noise in total sample")
    fillplot(epsilons, len_mask, linewidth=2, color=color)

    plt.subplot(2,2,3)
    plt.ylabel("number of clusters")
    fillplot(epsilons, k_clusters, color=color, linewidth=2)
    plt.xlabel("neighborhood size")

    plt.subplot(2,2,4)
    plt.ylabel("mean meaningful cluster size")
    fillplot(epsilons, sizes, color=color, linewidth=2)
    plt.xlabel("neighborhood size");

def fillplot(xs, ys, color, linewidth):
    plt.plot(xs, ys, color=color, linewidth=linewidth)
    base = 0
    plt.fill( xs+[ xs[-1],xs[0] ], ys+[base,base], color=color, alpha=0.3 )

def plot_tsne(X_ne, labels, title="TSNE/DBSCAN"):
    """
    Plots X_ne, with colors y labels
    """
    plt.style.use("fivethirtyeight")
    plt.figure(dpi=150, figsize=(6,5))
    plt.suptitle(title, size="20")
    # mask = (labels >= 0) & (labels <5)
    #mask = labels >= 0
    mask = labels >= -2
    plt.scatter(X_ne[mask, 0], X_ne[mask,1], c=labels[mask],cmap="nipy_spectral_r", alpha=0.6)
    plt.xticks(())
    plt.yticks(())
    plt.colorbar();

def get_clusters(labels, ids):
    """
    Returns dict mapping labels to lists of document ids
    """
    clusters = defaultdict(list)
    for lbl in set(labels):
        for label, id_ in zip(labels, ids):
            if label==lbl:
                clusters[lbl].append(id_)
    return clusters

def profile_labels(labels):
    """
    Prints basic cluster size information
    """
    for label in set(labels):
        mask = labels == label
        print("Cluster {} has {} documents.".format(label, sum(mask)))
