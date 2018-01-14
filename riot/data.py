from riot import config
from riot.models import Champion

from django.db.models.base import ObjectDoesNotExist

from collections import namedtuple
from io import BytesIO
from math import sqrt
from PIL import Image
import random
import json
import requests

class DataProcessingManager(object):
    def get_palette_from_champion(self, champ_id):
        champ = None
        try:
            champ = Champion.objects.get(champion_id=champ_id)
        except ObjectDoesNotExist:
            champ_name = config.CHAMP_ID_TO_NAME[champ_id]
            champ_palette = self.create_palette_from_champion(champ_id)
            champ = Champion.objects.create(champion_id=champ_id,
                                            name=champ_name,
                                            palette=champ_palette)
        if not champ:
            raise ValueError('Champion with id: %s could not be created' % champ_id)

        return champ.palette

    def create_palette_from_champion(self, champion_id, n=8):
        name = config.CHAMP_ID_TO_NAME[champion_id]
        if not name:
            raise ValueError('Champion with id: %s could not be found.' % champion_id)
        
        jpg_url = "http://ddragon.leagueoflegends.com/cdn/img/champion/loading/%s_0.jpg" % (name)
        r = requests.get(jpg_url)
        if r.status_code != requests.codes.ok:
            raise ValueError('URL: %s is invalid' % jpg_url)
        
        # Adapted from http://charlesleifer.com/blog/using-python-and-k-means-to-find-the-dominant-colors-in-images/
        img = Image.open(BytesIO(r.content))
        img.thumbnail((200, 200))
        w, h = img.size

        points = self.get_points(img)
        clusters = self.kmeans(points, n, 1)
        rgbs = [map(int, c.center.coords) for c in clusters]
        rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))
        return " ".join(list(map(rtoh, rgbs)))

    Point = namedtuple('Point', ('coords', 'n', 'ct'))
    Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

    def get_points(self, img):
        points = []
        w, h = img.size
        for count, color in img.getcolors(w * h):
            points.append(self.Point(color, 3, count))
        return points

    def euclidean(self, p1, p2):
        return sqrt(sum([
            (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
        ]))

    def calculate_center(self, points, n):
        vals = [0.0 for i in range(n)]
        plen = 0
        for p in points:
            plen += p.ct
            for i in range(n):
                vals[i] += (p.coords[i] * p.ct)
        return self.Point([(v / plen) for v in vals], n, 1)

    def kmeans(self, points, k, min_diff):
        clusters = [self.Cluster([p], p, p.n) for p in random.sample(points, k)]

        while 1:
            plists = [[] for i in range(k)]

            for p in points:
                smallest_distance = float('Inf')
                for i in range(k):
                    distance = self.euclidean(p, clusters[i].center)
                    if distance < smallest_distance:
                        smallest_distance = distance
                        idx = i
                plists[idx].append(p)

            diff = 0
            for i in range(k):
                old = clusters[i]
                center = self.calculate_center(plists[i], old.n)
                new = self.Cluster(plists[i], center, old.n)
                clusters[i] = new
                diff = max(diff, self.euclidean(old.center, new.center))

            if diff < min_diff:
                break

        return clusters
