#!/usr/bin/python3

# liste des régions, départements, carte de france


import matplotlib.pyplot as plt
import numpy as np
import json
import matplotlib.patheffects as path_effects
import matplotlib as mpl


# Liste des régions et départements

REGIONS = {
    'Auvergne-Rhône-Alpes': ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74'],
    'Bourgogne-Franche-Comté': ['21', '25', '39', '58', '70', '71', '89', '90'],
    'Bretagne': ['35', '22', '56', '29'],
    'Centre-Val de Loire': ['18', '28', '36', '37', '41', '45'],
    'Corse': ['2A', '2B'],
    'Grand Est': ['08', '10', '51', '52', '54', '55', '57', '67', '68', '88'],
    'Guadeloupe': ['971'],
    'Guyane': ['973'],
    'Hauts-de-France': ['02', '59', '60', '62', '80'],
    'Île-de-France': ['75', '77', '78', '91', '92', '93', '94', '95'],
    'La Réunion': ['974'],
    'Martinique': ['972'],
    'Mayotte': ['976'],
    'Normandie': ['14', '27', '50', '61', '76'],
    'Nouvelle-Aquitaine': ['16', '17', '19', '23', '24', '33', '40', '47', '64', '79', '86', '87'],
    'Occitanie': ['09', '11', '12', '30', '31', '32', '34', '46', '48', '65', '66', '81', '82'],
    'Pays de la Loire': ['44', '49', '53', '72', '85'],
    'Provence-Alpes-Côte d\'Azur': ['04', '05', '06', '13', '83', '84'],
}

DEPARTEMENTS = {
    '01': 'Ain', 
    '02': 'Aisne', 
    '03': 'Allier', 
    '04': 'Alpes-de-Haute-Provence', 
    '05': 'Hautes-Alpes',
    '06': 'Alpes-Maritimes', 
    '07': 'Ardèche', 
    '08': 'Ardennes', 
    '09': 'Ariège', 
    '10': 'Aube', 
    '11': 'Aude',
    '12': 'Aveyron', 
    '13': 'Bouches-du-Rhône', 
    '14': 'Calvados', 
    '15': 'Cantal', 
    '16': 'Charente',
    '17': 'Charente-Maritime', 
    '18': 'Cher', 
    '19': 'Corrèze', 
    '2A': 'Corse-du-Sud', 
    '2B': 'Haute-Corse',
    '21': 'Côte-d\'Or', 
    '22': 'Côtes-d\'Armor', 
    '23': 'Creuse', 
    '24': 'Dordogne', 
    '25': 'Doubs', 
    '26': 'Drôme',
    '27': 'Eure', 
    '28': 'Eure-et-Loir', 
    '29': 'Finistère', 
    '30': 'Gard', 
    '31': 'Haute-Garonne', 
    '32': 'Gers',
    '33': 'Gironde', 
    '34': 'Hérault', 
    '35': 'Ille-et-Vilaine', 
    '36': 'Indre', 
    '37': 'Indre-et-Loire',
    '38': 'Isère', 
    '39': 'Jura', 
    '40': 'Landes', 
    '41': 'Loir-et-Cher', 
    '42': 'Loire', 
    '43': 'Haute-Loire',
    '44': 'Loire-Atlantique', 
    '45': 'Loiret', 
    '46': 'Lot', 
    '47': 'Lot-et-Garonne', 
    '48': 'Lozère',
    '49': 'Maine-et-Loire', 
    '50': 'Manche', 
    '51': 'Marne', 
    '52': 'Haute-Marne', 
    '53': 'Mayenne',
    '54': 'Meurthe-et-Moselle', 
    '55': 'Meuse', 
    '56': 'Morbihan', 
    '57': 'Moselle', 
    '58': 'Nièvre', 
    '59': 'Nord',
    '60': 'Oise', 
    '61': 'Orne', 
    '62': 'Pas-de-Calais', 
    '63': 'Puy-de-Dôme', 
    '64': 'Pyrénées-Atlantiques',
    '65': 'Hautes-Pyrénées', 
    '66': 'Pyrénées-Orientales', 
    '67': 'Bas-Rhin', 
    '68': 'Haut-Rhin', 
    '69': 'Rhône',
    '70': 'Haute-Saône', 
    '71': 'Saône-et-Loire', 
    '72': 'Sarthe', 
    '73': 'Savoie', 
    '74': 'Haute-Savoie',
    '75': 'Paris', 
    '76': 'Seine-Maritime', 
    '77': 'Seine-et-Marne', 
    '78': 'Yvelines', 
    '79': 'Deux-Sèvres',
    '80': 'Somme', 
    '81': 'Tarn', 
    '82': 'Tarn-et-Garonne', 
    '83': 'Var', 
    '84': 'Vaucluse', 
    '85': 'Vendée',
    '86': 'Vienne', 
    '87': 'Haute-Vienne', 
    '88': 'Vosges', 
    '89': 'Yonne', 
    '90': 'Territoire de Belfort',
    '91': 'Essonne', 
    '92': 'Hauts-de-Seine', 
    '93': 'Seine-Saint-Denis', 
    '94': 'Val-de-Marne', 
    '95': 'Val-d\'Oise',
    '971': 'Guadeloupe', 
    '972': 'Martinique', 
    '973': 'Guyane', 
    '974': 'La Réunion', 
    '976': 'Mayotte',
}

LISTE_REGIONS =  [ x for x in REGIONS ]
LISTE_REGIONS_OUTRE_MER =  ['Guadeloupe','Guyane', 'La Réunion','Martinique', 'Mayotte']
LISTE_REGIONS_METROP = LISTE_REGIONS.copy()
for x in LISTE_REGIONS_OUTRE_MER:
    LISTE_REGIONS_METROP.remove(x)
    
LISTE_DEPARTEMENTS = [ x for x in DEPARTEMENTS ]
LISTE_DEPARTEMENTS_OUTRE_MER = ['971','972','973','974','976']
LISTE_DEPARTEMENTS_METROP = LISTE_DEPARTEMENTS.copy()
for x in LISTE_DEPARTEMENTS_OUTRE_MER:
    LISTE_DEPARTEMENTS_METROP.remove(x)


#### charge la géométrie

def charge_geometrie(carte, file, filter, key='code', factor=1):

    with open(file) as f:
        data = json.load(f)
    
        for x in data['features']:
            loc = x['properties'][key]
            if loc in filter:
                y = x['geometry']
                if y['type']=='MultiPolygon':
                    poly = [ np.array(i[0]) for i in y['coordinates']]
                else:
                    poly = list(map(np.array, y['coordinates']))
                if factor!=1:
                    for i in range(len(poly)):
                        poly[i] = np.array(list(poly[i][::factor, :])+[ poly[i][-1,:] ])
                carte[loc] = poly
                    

carte = dict()
charge_geometrie(carte, 'departements-avec-outre-mer.geojson', LISTE_DEPARTEMENTS_OUTRE_MER, factor=30)
for x in LISTE_REGIONS_OUTRE_MER:
    carte[x] = carte[REGIONS[x][0]]

charge_geometrie(carte, 'departements-version-simplifiee.geojson', LISTE_DEPARTEMENTS_METROP)
charge_geometrie(carte, 'regions-version-simplifiee.geojson', LISTE_REGIONS_METROP, 'nom')



### positionne les départements d'outre-mer et une copie de la couronne parisienne près de la métropole


metrop = LISTE_DEPARTEMENTS_METROP.copy()
for y in ['2A','2B','75','92','93','94']:
    metrop.remove(y)

for x in ['75','92','93','94']:
    carte['_'+x] = [ z.copy() for z in carte[x] ]# copie
    metrop.append('_'+x)


lrsc = LISTE_REGIONS_METROP.copy()
lrsc.remove('Corse')
details = [ (metrop + lrsc,                [ 0,   0,  13.3736     ] ), 
            (['2A','2B','Corse'],   [ 12,  7,  1.694       ] ),
            (['75','92','93','94'], [ 0,   6.7,  6 * 0.46985 ] ),
            (['971'],               [ 0,   0,  1.5 * 0.8075      ] ),
            (['972'],               [ 0, 1.5,  2 * 0.49011     ] ),
            (['973'],               [ 1.5, 2,  .4* 3.6368      ] ),
            (['974'],               [ 0,   3,  1.5 * 0.62015     ] ),
            (['976'],               [ 0, 4.5,  2.5 * 0.36867     ] )   ]



def positionne(loc, dx=0, dy=0, beta=1.0):
    
    xmax, ymax,  xmin, ymin = -np.inf, -np.inf, np.inf, np.inf
    for c in loc:
        poly = carte[c]
        for z in poly:
            xmax = max(xmax, max(z[:,0]))
            xmin = min(xmin, min(z[:,0]))
            ymax = max(ymax, max(z[:,1]))
            ymin = min(ymin, min(z[:,1]))

    alpha = max(xmax-xmin, ymax-ymin)/beta
    for c in loc:
        for i in range(len(carte[c])):
            carte[c][i][:,0] = dx + (carte[c][i][:,0]-xmin)/alpha
            carte[c][i][:,1] = dy + (carte[c][i][:,1]-ymin)/alpha

for (l, args) in details:
    positionne(l,*args)                                  

### définit les positions centrales

centre = dict()

for d in carte:
    
    poly = carte[d]
    #x,y,t = 0,0,0
    xmax, ymax,  xmin, ymin = -np.inf, -np.inf, np.inf, np.inf
    for z in poly:
        xmax = max(xmax, max(z[:,0]))
        xmin = min(xmin, min(z[:,0]))
        ymax = max(ymax, max(z[:,1]))
        ymin = min(ymin, min(z[:,1]))
        #x+=np.sum(z[:,0])
        #y+=np.sum(z[:,1])
        #t+=z.shape[0]
    #centre[d] = (x/t,y/t)
    centre[d] = [ xmin+(xmax-xmin)/2, ymin+(ymax-ymin)/2 ]

# petits réglages

for d,dx,dy in [ ('07', 0, -0.1),
                 ('66', 0, -0.1),
                 ('65', 0, -0.1),
                 ('56', 0,  0.1),
                 ('22', 0, -0.1),
                 ('29', 0.3,  0),
                 ('54', 0, -0.3),
                 ('92',-0.3,  0),
                 ('59', 0.3,-0.3),
                 ('69',-0.1,  0),
                 ('42',-0.1,  0),
                 ('41', 0, -0.1),
                 ('31', 0,  0.1),
                 ('971',0.2, -0.1),
                 ('972',0, -0.6),
                 ('976',0, -0.6)
]:
    centre[d][0] += dx
    centre[d][1] += dy

###

def plot_dep(ax, code, coul, alpha, dep_code=True, dep_contour=True):

    poly = carte[code]
    for z in poly:
        if dep_contour:
            ax.plot(z[:,0],z[:,1],"-",color='grey', lw=0.5)
        ax.fill(z[:,0], z[:,1], alpha=alpha, color=coul, lw=0.5)

    if code[0]!="_" and dep_code: # traitement special pour les départements de la couronne parisienne (affiché 2 fois)
        x,y = centre[code]
        ax.text(x, y, code, va='center',ha='center')#,path_effects=[path_effects.Stroke(linewidth=1, foreground='white'), path_effects.Normal()])


def plot_france(ax, d, cmap, ax2=None, rg=None, cb_args={ "orientation":'horizontal', "extend":'both' }, alpha=1.0, dep_contour=True, dep_code=True, reg_contour=True, reg_name=True):
    
    ax.axis('off')
    if rg==None: # on la détermine automatiquement
        v = [ d[x] for x in d ]
        rg=( min(v), max(v) )
    
    for x in LISTE_DEPARTEMENTS+['_75','_92','_93','_94']:
        if x[0]=='_':
            y=x[1:]
        else:
            y=x
        if y in d:
            c = cmap( (d[y]-rg[0] )/( rg[1]-rg[0]) )
        else:
            c = (.8,.8,.8)
        plot_dep(ax, x,c, alpha, dep_code=dep_code)

    if reg_contour:
        for x in LISTE_REGIONS:
            for z in carte[x]:
                ax.plot(z[:,0],z[:,1],"-",color='black', lw=1)
        
    plt.tight_layout()

    if ax2!=None:    
        norm = mpl.colors.Normalize(vmin=rg[0], vmax=rg[1])
        mpl.colorbar.ColorbarBase(ax2, norm=norm, cmap=cmap, **cb_args)
        
