import matplotlib.pyplot as plt


class Graph(object):
    def pie(self, title, labels, sizes, name='fig.png'):
        colors = []

        for label in labels:
            if label == 'За':
                colors.append("#2ca02c")
            elif label == 'Против':
                colors.append("#1f77b4")
            elif label == 'Воздержались':
                colors.append("#8c564b")
            elif label == 'Не голосовали':
                colors.append("#9467bd")
        explode = [0.1]
        for i in range(0, len(labels) - 1):
            explode.append(0)
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        plt.title(title)
        plt.savefig(name)
        plt.cla()
