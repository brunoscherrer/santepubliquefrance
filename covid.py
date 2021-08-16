#!/usr/bin/python3

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as path_effects
import colorsys
from datetime import date,timedelta, datetime
import numpy as np
import csv
import os
from unidecode import unidecode


from france import REGIONS, DEPARTEMENTS, plot_france



def add_key(l,x):
    if not (x in l):
        l.append(x)


def fix_date(d):
    if "/" in d: # format à la con
        d=d.split("/")
        d=d[2]+"-"+d[1]+"-"+d[0]
    return(d)
        
def get_data_from_files():
   
    file = "hopitaux.csv"

    deps, genres, dates = [], [], []

    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                [dp, g, d] = row[0:3]
                if g!="0" and dp not in ["","NA"]:
                    d=fix_date(d)
                    add_key(deps, dp)
                    add_key(genres, g)
                    add_key(dates, d)
            line_count+=1                           

    print("Données hopitaux")

     # fix erreur fichier santepubliquefrance date manquante 2020-10-15
    FIX=False
    if "2020-10-15" not in dates:
        print("!!! Correction donnée manquante 2020-10-15 !!!")
        i=dates.index("2020-10-16")
        dates=dates[0:i]+["2020-10-15"]+dates[i:]
        FIX=True

    print(len(deps),"départements,",len(genres),"genres,",len(dates),"dates")
        
    data = np.zeros( (len(deps), len(genres), len(dates), 4) )
   
    with open(file) as csv_file:  
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count != 0:
                [dp, g, d] = row[0:3]
                if g!="0" and dp not in ["","NA"]:
                    d=fix_date(d)
                    r = list(map(int, [row[3],row[4],row[8],row[9]]))
                    data[ deps.index(dp), genres.index(g), dates.index(d) ] = [ r[0], r[1], r[2], r[3] ]
            line_count+=1
            
    # fix erreur fichier santepubliquefrance
    if FIX:
        i=dates.index("2020-10-15")
        data[ :,:,i ] = data[ :,:,i-1]
        
    
            
    print("Données population")

    file = "pop_dep_2021_insee.csv"

    pop = np.zeros( len(deps) )
    
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            pop[ deps.index(row[0]) ] = int(row[1])


    print("Données lits de réa")
            
    file = "drees_lits_2018.csv"

    lits = np.zeros( (len(deps), 2) )

    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count!=0:
                r = list(map(int, row[1:]))
                lits[ deps.index(row[0]) ] = [ r[0] ]
            line_count += 1

    print("Données tests")

    file = "tests.csv"
    
    tests = np.zeros( (len(deps), len(dates), 2) )
    
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        line_count = 0
        for row in csv_reader:
            if line_count != 0 and len(row)==6:
                dp, d, p, t, cat = row[0:5]
                if cat=="0" and dp not in ['975','977','978']:
                    tests[ deps.index(dp), dates.index(d) ] = [ int(t), int(p) ]
            line_count+=1
            
    return deps, genres, dates, data, pop, lits, tests


def mes_couleurs(l):

    lx = np.arange(0.0, 1.0, 1.0/l )
    coul = []
    for x in lx:
        coul.append( colorsys.hsv_to_rgb( x, 1.0, 0.8 ) )  # couleurs réparties dans le spectre
    return( coul )#[ coul[i] for i in range(0,l,2) ] + [ coul[i] for i in range(1,l,2) ] )
    


def ratio(a,b):
    if b==0:
        return 0
    else:
        return a/b

def plot( endroit, total, titre, size=5 ):

    if NO_PLOT:
        return
    
    geomx, geomy = 2,3
    
    plt.figure(figsize=(geomy*1.5*size,geomx*1.1*size))
    
    plt.suptitle("Evolution de l'épidémie (hôpital et tests), "+titre,fontsize=size*3.6)
    if endroit=="France" and total:
        zones = dict()
        zones["France"] = [x for x in DEPARTEMENTS] 
    elif endroit=="France" and not total:
        zones = REGIONS
    elif endroit in REGIONS and total:
        zones = dict()
        zones[endroit] = [x for x in REGIONS[endroit]]
    elif endroit in REGIONS and not total:
        zones = dict()
        for x in REGIONS[endroit]:
            zones[ DEPARTEMENTS[x] ] = [x] 
    elif endroit in DEPARTEMENTS and total:
        zones = dict()
        zones[endroit] = [endroit]
    else:
         print(endroit,total," non reconnu!")
         exit(1)
    coul = mes_couleurs(len(zones))
    
    
    # graphe 1

    ax = plt.subplot(geomx,geomy,1)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

    plt.title("Nombre de personnes à l'hôpital et sorties de l'hôpital")
    
    plt.grid(True, which="both")
    
    xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]

    plt.plot(xr, [0.0]*len(xr), "-", color="black", lw=1)

    a = np.zeros(ld)

    nc=0
    for x in zones:
        c = np.sum( sum( [ data[ deps.index(d),:,:,3 ] for d in zones[x] ] ), axis=0 )
        args = { "facecolor":coul[nc] }  
        b = a - c
        plt.plot(xr, b, "-", color=coul[nc], alpha=0.1)
        plt.fill_between(xr, b, a, alpha=0.1, **args)
        a=b
        nc+=1
    plt.plot(xr, b, "--", color="black", alpha=0.5, lw=1)

    nc=0
    for x in zones:
        c = np.sum( sum( [ data[ deps.index(d),:,:,2 ] for d in zones[x] ] ), axis=0 )
        args = { "facecolor":coul[nc] }
        b = a - c
        plt.plot(xr, b, "-", color=coul[nc], alpha=0.1)
        plt.fill_between(xr, b, a, alpha=0.1, **args)
        a=b
        nc+=1
    plt.plot(xr, b, "--", color="black", alpha=0.5, lw=1)
        
    a = np.zeros(ld)
    nc=0
    for x in zones:
        c = np.sum( sum( [ data[ deps.index(d),:,:,: ] for d in zones[x] ] ), axis=0 )
        args = { "facecolor":coul[nc] }
        b = a + c[:,0]
        if len(zones)==1:
            plt.plot(xr, a+c[:,1], ":", color=coul[nc], alpha=0.7)
        plt.plot(xr, b, "-", color=coul[nc], alpha=0.5)
        plt.fill_between(xr, a, b, alpha=0.4, **args, label=x)
        a=b
        nc+=1
    plt.plot(xr, b, "-", color="black", lw=1)

    
    c = sum ( [ np.sum( sum( [ data[ deps.index(d),:,-1,: ] for d in zones[x] ] ), axis=0 ) for x in zones ] )
    args = { "color":"black", "ha":"right", "va":"center" }#, "path_effects":[path_effects.Stroke(linewidth=2, foreground='white'), path_effects.Normal()] }
    plt.text(xr[-1], (c[0])/2., "Hospitalisés", **args)
    if len(zones)==1:
        plt.text(xr[-1], (c[1])/2., "en réanimation",  **args)
        mortalite = (c[3]/(c[2]+c[3]))*100
        plt.text(xr[0],-c[2]-c[3], "Mortalité (en sortie): %.1f%%"%(mortalite), color='black', ha='left', va='bottom', bbox=dict(boxstyle="round", ec=(1., 0.5, 0.5), fc=(1., 0.8, 0.8)) )
    plt.text(xr[-1], -c[3]-c[2]/2., "Retours à domicile", **args)
    if c[3]>0:
        plt.text(xr[-1], -c[3]/2., "Décès", **args)

    if len(zones)>1:
        plt.legend(loc='upper left', fontsize=7)

    #    plt.yscale('symlog', linthreshy=1000)
        

    # graphe 2
    
    ax = plt.subplot(geomx,geomy,2)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    
    if len(zones)==1:
        plt.title("Flux quotidiens à l'hôpital")
    else:
        plt.title("Nombre de nouvelles hospitalisations pour 100.000 habitants")
        #plt.yscale('log')
        
    plt.grid(True, which="both")

    xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+2,1) ]
    
    plt.plot(xr,[0.0]*len(xr), color="grey", lw=1)
    
    
    for z in range(2):
        nc=0
        for x in zones:

            popx = sum( [ pop[deps.index(d)] for d in zones[x] ] )/100000.0

            c = np.sum( sum( [ [d_data,d_s_data][1-z][ deps.index(d),:,:,: ] for d in zones[x] ] ), axis=0 )
            
            if z==1: # real data
                if len(zones)>1:
                    args = { "color":coul[nc], 'lw':1 }
                    plt.plot(xr, (c[:,0]+c[:,2]+c[:,3])/popx, "o", markersize=2, **args)
                else:
                    plt.plot(xr, c[:,0]+c[:,2]+c[:,3], "o", markersize=2, color='black')
                    #plt.plot(xr, c[:,0], "o", markersize=2, color='blue')
                    #plt.plot(xr, c[:,1], "o", markersize=2, color='crimson')
                    plt.plot(xr, -c[:,2], "o", markersize=2, color='forestgreen')
                    plt.plot(xr, -c[:,3], "o", markersize=2, color='mediumvioletred')
            else:
                if nc==0 and len(zones)==1:
                    args = { 'lw':1, "path_effects":[path_effects.Stroke(linewidth=2, foreground='white'), path_effects.Normal()] }
                    plt.plot(xr, c[:,0]+c[:,2]+c[:,3], "-", color='black', label="Nouvelles hospitalisations", **args)
                    #plt.plot(xr, c[:,0], "-", color='blue', label="Variation du nb de personnes hospitalisées", **args)
                    #plt.plot(xr, c[:,1], "-", color='crimson', label="Variation du nb de personnes en réanimation", **args)
                    plt.plot(xr, -c[:,3], "-", color='mediumvioletred', label="- Nb de décès", **args)
                    plt.plot(xr, -c[:,2], "-", color='forestgreen', label="- Nb de retours à domicile", **args)
                else:
                    args = { "color":coul[nc], "path_effects":[path_effects.Stroke(linewidth=2, foreground='white'), path_effects.Normal()]  }
                    plt.plot(xr, (c[:,0]+c[:,2]+c[:,3])/popx, "-", **args, label=x, lw=1)

            nc+=1
            
        if z==0:
            ymin,ymax = ax.get_ylim()

    if len(zones)>1:
        ymin = 0.01
    plt.ylim(ymin,ymax)
    
        
        
    plt.legend(loc="upper left", fontsize=7)


    # graphe 3

    for (ng, tit, kk) in [ (3, "Taux (%) d'occupation des lits de réanimation", 0) ]:
                           #(3, "Part (%) du nb de personnes hospitalisées / nb lits (DREES, 2018)", 1) ]:
    
        ax = plt.subplot(geomx,geomy,ng)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

        plt.title( tit )
        xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]

        plt.plot(xr,[100]*len(xr),"--",zorder=2, color="black",lw=2)

        nc=0
        for x in zones:
            c = np.sum( sum( [ data[ deps.index(d),:,:,: ] for d in zones[x] ] ), axis=0 )
            l = sum( [ lits[ deps.index(d), kk] for d in zones[x] ] )
            if len(zones)>1:
                args = { "color":coul[nc] }
            else:
                args = { "color":'black' }
            z = 100*c[:,1]/l
            plt.plot(xr, smooth(z), "-", **args, label=x, lw=1)
            plt.plot(xr, z, "o", markersize=2, **args)
            nc+=1

        plt.grid(True, which="both")

        if len(zones)>1:
            plt.legend(loc="upper left", fontsize=7)
    

    # graphe 4
            
    ax = plt.subplot(geomx,geomy,4)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        
    plt.title("Taux (%) de positivité")
        
    nc = 0
    mx = 0
    ymax=0
    for x in zones:
        popx = sum( [ pop[deps.index(d)] for d in zones[x] ] )/100000.0
        c1 = sum( [ tests[ deps.index(d),:,0 ] for d in zones[x] ] )
        c2 = sum( [ tests[ deps.index(d),:,1 ] for d in zones[x] ] )
        c = [ 100*ratio(c2[i],c1[i]) for i in range(56,len(c2)-3) ] 
        xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]
        xr = xr[56:-3]
        cs = smooth(c)
        if len(zones)>1:
            args = { "color":coul[nc] }
        else:
            args = { "color":'black' }
        plt.plot(xr,c, "o", markersize=2, **args)
        plt.plot(xr,cs, "-", **args, label=x, lw=1)
        nc+=1
        plt.grid(True, which="both")
        ymax=max(max(cs),ymax)
    plt.ylim(0,ymax*1.05)
    if len(zones)>1:
        plt.legend(loc="upper left", fontsize=7)

    
    # graphe 5
    
    ax = plt.subplot(geomx,geomy,5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    if len(zones)>1:
        plt.title("Taux d'incidence hebdomadaire pour 100.000 habitants")
    else:
        plt.title("$7\\times$nombre de cas positifs et taux d'incidence hebdo pour 100.000 habitants")
        
    nc = 0
    mx = 0
    for x in zones:
        popx = sum( [ pop[deps.index(d)] for d in zones[x] ] )/100000.0
        c = sum( [ tests[ deps.index(d),:,1 ] for d in zones[x] ] )
        c = c/popx # normalisaiton par la population
        c = c[56:-3]
        cs = smooth(c)
        xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]
        xr = xr[56:-3]
        xr2 = xr[6:]
        c2 = [ np.sum( c[t-6:t+1] ) for t in range(6,len(c)) ]  # sum sur les 7 derniers jours (correction bord gauche)
        #c2s = smooth(c2)
        if len(zones)>1:
            args = { "color":coul[nc] }
        else:
            args = { "color":'black' }
        #plt.plot(xr2,c2, "o", markersize=2, **args)
        if len(zones)>1:
            plt.plot(xr2,c2, "-", **args, label=x, lw=1)
        else:
            plt.plot(xr2,c2, "-", **args, label="Taux d'incidence (J-6 $\\rightarrow$ J)", lw=1)
            plt.plot(xr,7*np.array(c), "o", markersize=2, **args, alpha=0.5)
            plt.plot(xr,7*np.array(cs), "--", **args, label="$7\\times$nombre de cas", lw=1, alpha=0.5)
        nc+=1
    plt.grid(True, which="both")
    #if len(zones)>1:
    #    plt.ylim(0,50)
    plt.legend(loc="upper left", fontsize=7)
    
        
    # graphe 6
    
    ax = plt.subplot(geomx,geomy,6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    
    plt.title("Taux d'incidence hebdomadaire pour 100.000 habitants (log)")
            
    nc = 0
    mx = 0
    for x in zones:
        popx = sum( [ pop[deps.index(d)] for d in zones[x] ] )/100000.0
        c = sum( [ tests[ deps.index(d),:,1 ] for d in zones[x] ] )
        c = c/popx # normalisaiton par la population
        c = c[56:-3]
        cs = smooth(c)
        xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]
        xr = xr[56:-3]
        xr2 = xr[6:]
        c2 = [ np.sum( c[t-6:t+1] ) for t in range(6,len(c)) ]  # sum sur les 7 derniers jours (correction bord gauche)
        #c2s = smooth(c2)
        if len(zones)>1:
            args = { "color":coul[nc] }
        else:
            args = { "color":'black' }
        #plt.plot(xr2,c2, "o", markersize=2, **args)
        plt.plot(xr2,c2, "-", **args, label=x, lw=1)
        nc+=1
    plt.grid(True, which="both")
    plt.yscale('log')
    if len(zones)>1:
        plt.legend(loc="upper left", fontsize=7)
    
    # finalisation des graphiques
    
    plt.tight_layout()

    plt.subplots_adjust(top=0.9)

    nomfic=clean_string(endroit)
    if total:
        nomfic = nomfic+"_total"
    plt.savefig("./fig/"+nomfic+".png", dpi=DPI)
    plt.savefig("./fig/"+nomfic+".pdf")
    plt.close()



def plot_deces( titre, size=5 ):

    if NO_PLOT:
        return
    
    print("Données décès en France")
    file = "deces.csv"
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            deces = list(map(int, row[len(row)-ld:len(row)]))
        
    plt.figure(figsize=(3*1.5*size,1.1*size))
    
    plt.suptitle(titre,fontsize=size*3.6)

    zones = REGIONS
    coul = mes_couleurs(len(zones))
    
    # graphe de gauche
    ax = plt.subplot(1,3,1)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    
    plt.title("Nombre cumulé de décès à l'hôpital et hors hôpital")
    
    plt.grid(True, which="both")
    
    xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,1) ]

    a = np.zeros(ld)

    nc=0
    for x in zones:
        c = np.sum( sum( [ data[ deps.index(d),:,:,3 ] for d in zones[x] ] ), axis=0 )
        args = { "facecolor":coul[nc] }  
        b = a + c
        #plt.plot(xr, b, "-", color=coul[nc], alpha=0.1)
#        plt.fill_between(xr, a, b, alpha=0.5, **args, label=x)
        a=b
        nc+=1
    plt.fill_between(xr, [0.0]*ld, b, color="red", alpha=0.4, label="A l'hôpital")
    plt.plot(xr, b, "-", color="red", lw=1, alpha=0.3)

    deces = [ max(deces[i],a[i]) for i in range(len(deces)) ]
    plt.fill_between(xr, a, deces, color="black", alpha=0.4, label="Hors hôpital (JHU CSSE)")
    plt.plot(xr, deces, color="black", lw=1)
        
    plt.legend(loc='upper left', fontsize=9)

    # Nombre de données à supprimer:
    NDS = 1
    
    xr = [ datetime.strptime(dates[-1],"%Y-%m-%d")+timedelta(i) for i in range(-ld+1,-NDS) ]

    a = a[:ld-NDS] # suppression dernière donnée
    s_a = smooth(a)
    d_a = [a[i+1]-a[i] for i in range(ld-NDS-1)]
    s_d_a = smooth(d_a)#[d_a[i+1]-d_a[i] for i in range(ld-NDS-1)]

    deces = [deces[i]-a[i] for i in range(ld-NDS)]
    s_deces = smooth(deces)
    d_deces = [deces[i+1]-deces[i] for i in range(ld-NDS-1)]
    s_d_deces = smooth(d_deces)#[d_deces[i+1]-d_deces[i] for i in range(ld-NDS-1)]
    
    # graphe du centre et de droite
    for z in [2,3]:
        
        ax = plt.subplot(1,3,z)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))

        if z==2:
            plt.title("Nombre de décès par jour à l'hôpital et hors hôpital")
            plt.ylim(0,1500)
        else:
            plt.title("Nombre de décès par jour à l'hôpital et hors hôpital (échelle log)")
            plt.yscale('log')
            plt.ylim(6,1500)
        
        plt.grid(True, which="both")
        
        plt.plot(xr, d_a, "o", markersize=2, color="crimson")
        plt.plot(xr, s_d_a, color="crimson", lw=1, label="Nombre de décès à l'hôpital")

        plt.plot(xr, d_deces, "o", markersize=2, color="black")
        plt.plot(xr, s_d_deces, color="black",lw=1, label='Nombre de décès hors hôpital')

        plt.plot(xr, np.array(d_a) + np.array(d_deces), "o", markersize=2, color="blue")
        plt.plot(xr, np.array(s_d_a) + np.array(s_d_deces), color="blue",lw=1, label='Total (JHU CSSE)')

        plt.legend(loc='upper right', fontsize=9)


    
    # finalisation
    
    plt.tight_layout()

    plt.subplots_adjust(top=0.85)

    nomfic = "deces"
    plt.savefig("./fig/"+nomfic+".png", dpi=DPI)
    plt.savefig("./fig/"+nomfic+".pdf")
    plt.close()
    
    
def clean_string(s): # enlève tous les caractères spéciaux

    s = unidecode(s)
    s = s.replace(' ','_')
    s = s.replace("'","_")
    s = s.replace("-","_")
    
    return(s)



def my_map(f, data):
    data2 = data.copy()
    for i in range(len(deps)):
        for j in range(len(genres)):
            for t in range(len(dates)):
                for l in [2,3]:
                    data2[i,j,t,l] = f( data2[i,j,t,l] )
    return data2


SMOOTH = 7

def smooth(f, sm=20, c=3.0):
    lf=len(f)
    sf=[]
    for t in range(lf):
        ll=f[ max(0,t-SMOOTH):t+1 ]
        sf.append( sum(ll)/len(ll) )
    return(sf)
    

def smooth2(data, sm=50, c=3.0):
    l=data.shape[2]
    data2 = data.copy()
    data3 = data.copy()
    for t in range(1,l):
        ll = [ data3[:,:,k,:]  for k  in range( max(0,t-SMOOTH),t+1 ) ]
        data2[:,:,t,:] = sum(ll)/len(ll)
    return(data2)


def diff(data):
    
    return ( data[:,:,1:ld,: ] - data[:,:,0:ld-1,:] )


def cartes():

    DELTA = 10*7 # nombre de jours glissants sur lesquels on génère une animation
    
    if NO_PLOT:
        return
    
    # Cartes fixes
    
    cartes_fixes = [ ("Nombre de lits de réanimation pour 100.000 hab. (DREES, 2018)",         'Greens_r',   'lits_rea'),
                     ("Taux (%) d'occupation moyen des lits de réa ("+dates[ld-1]+")", 'Purples',  'tension_moy'),
                     ("Part (%) des décès parmi les sorties de l'hôpital ("+dates[ld-1]+")",             'Blues',   'mortalite')
    ]
    
    cartes_animees = [
        [ "", 'posit',
          [ ( "Taux de positivité",                  'Reds',  'posit'),
            ( "Variation hebdomadaire du taux de positivité",     'bwr',   'var_posit')
          ] ],
        [ "", 'incid',
          [ ( "Taux d'incidence entre J-6 et J pour 100.000 hab.",                  'Reds',  'incid'),
            ( "Variation hebdomadaire du taux d'incidence",     'bwr',   'var_incid')
          ] ],
        [ "Taux (%) d'occupation des lits de réanimation, ", 'tension',
          [ ("",                'Purples',  'tension')
          ] ],
        [ "", 'cumul_hosp',
          [ ( "Nb cumulé d'hospitalisations pour 100.000 hab.",           'Greys',  'cumul_hosp'),
            ( "Nb de nouvelles hospitalisations pour 100.000 hab.",               'Greens',  'nouv_hosp')
          ] ],
        [ "", 'hosp',
          [ ( "Nb de personnes hospitalisées pour 100.000 hab.",                  'Reds',  'hosp'),
            ( "Variation quotidienne du nb de pers. hosp. pour 100.000 hab.",     'bwr',   'var_hosp')
          ] ],
        [ "", 'rea',
          [ ("Nb de personnes en réanimation pour 100.000 hab.",                  'Reds',  'rea'),
            ("Variation quotidienne du nb de réa pour 100.000 hab.",     'bwr',   'var_rea')          
          ] ],
        [ "", 'cumul_deces',
          [ ("Nb cumulé de décès pour 100.000 hab.",                        'Greys',  'cumul_deces'),
            ("Nb quotidien de décès pour 100.000 hab.",                       'Greens',  'deces')
          ] ]
    ]
                           
    # fabrication des dictionnaires pour les données

    les_vars = ['posit', 'var_posit', 'incid', 'var_incid', 'cumul_hosp','nouv_hosp','hosp','var_hosp','rea','var_rea','tension', 'cumul_deces', 'deces', 'mortalite', 'lits_rea','tension_moy']
    dicos = dict()
    for x in les_vars+['lits_rea','tension_moy']:
        dicos[x] = dict()

        
    for d in deps:
        
        ind = deps.index(d)
        
        c = np.sum( data[ ind,:,:,:  ], axis=0 )  # additionne hommes et femmes
        d_s_c = np.sum( d_s_data[ ind,:,:,:  ], axis=0 )  # additionne hommes et femmes
        popu = pop[ind] / 100000 # (pour 100000 personnes)
        l = lits[ ind, 0]

        # calcul de l'incidence
        incid = tests[ ind,:,1 ][56:ld-3]
        incid = [ sum( incid[t-6:t+1] ) for t in range(6,len(incid)) ]
        incid = np.array([0]*62 + smooth(incid) + [0,0,0] )
        var_incid = incid[7:]-incid[0:-7]

        # calcul de la positivité
        v1 = tests[ ind,:,1 ][56:ld-3]
        v2 = tests[ ind,:,0 ][56:ld-3]
        posit = smooth ( [ 100*ratio(v1[i],v2[i]) for i in range(len(v1)) ] )     # léger lissage
        posit = np.array([0]*56 + posit + [0,0,0] )
        var_posit = posit[7:]-posit[0:-7]
        
        # vecteurs (du temps)
        dicos['cumul_deces'][d] = c[:,3] / popu 
        dicos['deces'][d] = d_s_c[:,3] / popu
        dicos['hosp'][d] = c[:,0] / popu
        dicos['var_hosp'][d] = d_s_c[:,0] / popu
        dicos['rea'][d] = c[:,1] / popu
        dicos['var_rea'][d] = d_s_c[:,1] / popu
        dicos['cumul_hosp'][d] = (c[:,0]+c[:,1]+c[:,2]+c[:,3]) / popu
        dicos['nouv_hosp'][d] = (d_s_c[:,0]+d_s_c[:,1]+d_s_c[:,2]+d_s_c[:,3]) / popu
        dicos['tension'][d] = c[:,1] / l * 100 
        dicos['mortalite'][d] = (c[:,3] / (c[:,2]+c[:,3])) * 100
        dicos['incid'][d] = incid / popu
        dicos['var_incid'][d] = var_incid / popu
        dicos['posit'][d] = posit
        dicos['var_posit'][d] = var_posit
        
        # valeurs (fixes)
        dicos['lits_rea'][d] = l / popu
        dicos['tension_moy'][d] = np.mean( dicos['tension'][d] )

        
    # détermination semi-automatique des bornes pour les cartes animées
    
    zmin, zmax = dict(), dict()
    for x in les_vars:
        zmin[x], zmax[x] = np.infty, -np.infty     
        z = dicos[x]
        for d in deps:
            if np.size(z[d])!=1:
                toto=max(0,(np.size(z[d])-DELTA) )
                zzz=z[d][toto:]
            else:
                zzz=z[d]
            zmin[x] = min( zmin[x],  np.min(zzz) )
            zmax[x] = max( zmax[x],  np.max(zzz) )
        if x in ['var_hosp','var_rea','var_incid','var_posit']: # symmétrise
            zz = max( zmax[x], -zmin[x] )
            zmin[x],zmax[x] = -zz,zz
    
    zmin['nouv_hosp']=0 # petite correction des incohérences des fichiers Santé Publique France!
    #zmax['tension']=100 # bloque à 300% le max
    zmin['lits_rea']=0
    #zmax['lits_rea']=20
    zmax['mortalite']=30
    zmin['deces']=0
    zmax['incid'] = 600
    zmin['var_incid'] = -150
    zmax['var_incid'] = 150
    zmin['var_posit'] = -10
    zmax['var_posit'] = 10
    zmax['tension'] = 100
    zmin['posit'] = 0
    zmax['posit'] = min(zmax['posit'],25)
    
    print("Génération des cartes de France (fixes)")
        
    # génération des cartes fixes
    for (tit, cmap_name, var) in cartes_fixes:
        
        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot(111)
        ax2 = fig.add_axes([0.05, 0.05, 0.9, 0.03])

        cmap = cm.get_cmap(cmap_name)
        if cmap_name=='Greens_r':
            colors = cmap(np.arange(cmap.N))[100:]
            cmap = LinearSegmentedColormap.from_list('my_green_r', colors)
        
        print(tit)
        z = dicos[var].copy()
        if type(z['01'])==np.ndarray:
            for x in deps:
                z[x]=z[x][-1]
                
        plot_france(ax, z, cmap, ax2, rg=[zmin[var], zmax[var]])
        
        plt.suptitle(tit, fontsize=13)
        plt.savefig('fig/carte_'+var+'.png',dpi=DPI)
        plt.savefig('fig/carte_'+var+'.pdf')
        plt.close()
        
    print("\n Génération des animations")
    
    # génération des animations
    for [grostitre, fic, liste] in cartes_animees:

        print(grostitre,fic)
        
        tmin,tmax=1,ld
        if fic in ['incid','posit']:
            tmin,tmax=63,ld-3

        tmin = max(tmin, tmax-DELTA) #10 semaines 
            
        for t in range(tmin,tmax):

            tit2 = grostitre + dates[t]
            print(tit2)
        
            ng = len(liste)
            fig = plt.figure(figsize=(ng*7,7))
            plt.suptitle(tit2, fontsize=13)
            
            for i in range(ng):
                
                (tit, cmap, var) = liste[i]

                ax = fig.add_subplot(1,ng,i+1)
                plt.title(tit,fontsize=13)
                
                ax2 = fig.add_axes([0.05+i*1.0/ng, 0.05, 0.9/ng, 0.03])
            
                cmap = cm.get_cmap(cmap)
                z = dicos[var].copy()
                for x in deps:
                    z[x]=z[x][ len(z[x])-ld+t ]
                
                plot_france(ax, z, cmap, ax2, rg=[zmin[var], zmax[var]], dep_code=True)#(t==ld-1))

            plt.savefig('tmp/carte_'+fic+'_%02d.png'%t,dpi=DPI)
            if t==tmax-1:
            #    plt.savefig('fig/carte_'+fic+'.png')
                plt.savefig('fig/carte_'+fic+'.pdf')
            
            plt.close()

        anim_command = "convert -verbose -loop 0 "
        src = " ".join([ "tmp/carte_"+fic+"_%02d.png"%i for i in range(tmin,tmax-7) ])
        src2 = " ".join([ "tmp/carte_"+fic+"_%02d.png"%i for i in range(tmax-7,tmax) ])
        last = "tmp/carte_"+fic+"_%02d"%(tmax-1)
        print("Generate animations : "+src)
        os.system( anim_command+" -delay 10 "+src+" -delay 10 "+src2+" -delay 400 "+last+".png ./fig/carte_"+fic+".gif" )
        os.system( "rm "+src+" "+src2 )

        
def tension_mort():

    print("Graphe relation tension/mortalité")
    
    # Relation tension/mortalité
    
    txtargs={ 'va':'center', 'ha':'center', 'size':10, "path_effects":[path_effects.Stroke(linewidth=2, foreground='white'), path_effects.Normal()] }

    cmap = cm.get_cmap('Greys')
    
    for time in [ld]:#range(1,ld+1):
        print(dates[time-1])
        plt.figure(figsize=(10,7))
        plt.xlim(0, 100)
        plt.ylim(0, 36)
        m, t = np.zeros(len(deps)), np.zeros(len(deps))
        lx,ly = [], []
        for d in deps:
            ind = deps.index(d)
            c = np.sum( data[ ind,:,0:time,:  ], axis=0 )  # additionne hommes et femmes
            l = lits[ ind, 0]
            t = 100*c[:,1]/l # tension
            m = (c[:,3]/(c[:,2]+c[:,3]))*100 # mortalité
            x,y = np.mean(t),m[time-1]#np.mean(t), m[time-1]
            lx.append(x)
            ly.append(y)
            intensity = min(0.9, np.sum( c[time-1,:] )/pop[ind]*250)
            if intensity>.0:
                plt.text(x, y, d, color=cmap(intensity), **txtargs, zorder=int(100*intensity))
            #plt.plot( smooth(list(t)), smooth(list(m)), "-", alpha=0.2)
        plt.xlabel("Taux (%) d'occupation des lits de réa (moyenne depuis le 17/3)")
        plt.ylabel("Part (%) des décès parmi les sorties de l'hôpital ("+dates[time-1]+") ")
        plt.grid(True,which='both')
        plt.title("Relation entre tension moyenne en réanimation et mortalité à l'hôpital ("+dates[time-1]+") ")
        plt.tight_layout()
        plt.savefig("./tmp/%02d.png"%time, dpi=DPI)
        if time==ld:
            plt.savefig("./fig/tension_mort.png",dpi=DPI)
            plt.savefig("./fig/tension_mort.pdf")
        plt.close()

        
        
        
#####################
# Partie principale

# récupération des données

deps, genres, dates, data, pop, lits, tests = get_data_from_files()
ld = len(dates)

# lissage léger des données

s_data = smooth2(data)

# différentiation

d_data = diff(data)
d_s_data = smooth2(d_data)# diff(s_data)


def genere_page():

    fic_md = open(r"README.md","w")

    fic_md.write("<html lang=\"fr\"><head><meta charset=\"UTF-8\">\n\n**Des représentations graphiques de l'évolution mondiale sont disponibles [ici](http://www.iecl.univ-lorraine.fr/~Bruno.Scherrer/git/conarvirus/).**\n<br>**Pages similaires:**\nle [site de Germain Forestier](https://germain-forestier.info/covid/), le [site de Guillaume Rozier](https://covidtracker.fr/)\n")

    fic_md.write("## Evolution des données hospitalières en France concernant le Covid-19 <a name=\"top\"> \n\n")

    fic_md.write("L'organisme [*Santé Publique France*](https://www.santepubliquefrance.fr/maladies-et-traumatismes/maladies-et-infections-respiratoires/infection-a-coronavirus/articles/infection-au-nouveau-coronavirus-sars-cov-2-covid-19-france-et-monde#block-242818) diffuse des [données hospitalières](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/) et des [données sur les tests virologiques](https://www.data.gouv.fr/fr/datasets/donnees-relatives-aux-resultats-des-tests-virologiques-covid-19/).\n\n Entre le "+dates[0]+" et le "+dates[-1]+", on dispose \n\n- du nombre *quotidien* de personnes hospitalisées (dont le nombre de personnes en réanimation);\n- du nombre *cumulé* des retours à domicile;\n- du nombre *cumulé* des décès.\n\nLa somme de ces nombres correspond au nombre total de personnes passées par l'hôpital (et sa variation correspond chaque jour aux nouvelles admissions).\n\nEntre le "+dates[56]+" et le "+dates[-4]+", on dispose du nombre de tests et de cas positifs, ce qui permet d'estimer le taux d'incidence hebdomadaire (nombre de cas sur 7 jours glissants pour 100.000 habitants) ainsi que le taux de positivité.\n\n")

    fic_md.write("Ces informations sont représentées dans cette page sous forme de\n\n- **graphiques**\n    - [pour la France entière](#france)\n    - [par région](#par_regions)\n    - [par département](#par_departements)\n- **cartes**:\n	- [cumul des hospitalisations](#cumul_hosp)\n	- [cumul des décès](#cumul_deces)\n	- [hospitalisations](#hosp)\n	- [personnes en réanimations](#rea)\n	- [nombre de lits de réanimation et tension](#lits)\n	- [mortalité](#mortalite)\n	- [taux d'incidence](#incid)\n	- [taux de positivité](#posit).\n\n*Tous les graphiques sont accessibles sous forme de fichier pdf (en cliquant sur les images). Cette page est générée automatiquement par un [script python accessible sur github](https://github.com/brunoscherrer/santepubliquefrance).* \n ")

    plot_deces("Bilan des décès en France")
    
    fic_md.write("\n- - - -\n\n **<ins>Avertissement</ins>: Les graphiques de cette page ne concernent que les personnes qui ont été hospitalisées; en particulier, cela ne concerne pas celles qui sont décédées à cause du Covid-19 sans être passées par l'hôpital (en noir et grisé ci-dessous).**\n\n<br>\n")
    fic_md.write("[![](./fig/deces.png)](./fig/deces.pdf)<br>\n")

    print("FRANCE")
    
    fic_md.write("\n- - - -\n\n- - - -\n\n### France (graphiques)<a name=\"france\">\n\n")
    fic_md.write("\n#### France entière<a name=\"france_total\"><br>\n")
    fic_md.write("[![](./fig/France_total.png)](./fig/France_total.pdf)<br>\n")
    fic_md.write("\n#### France, par régions (graphiques)<a name=\"france_regions\">\n\n")
    fic_md.write("[![](./fig/France.png)](./fig/France.pdf)<br>\n")
    plot( "France", True, "France entière (total)" )
    plot( "France", False, "France entière (par régions)" )
    
    print("REGIONS")
    fic_md.write("\n- - - -\n### Régions <a name=\"par_regions\"> ([Retour au sommaire](#top))\n\n")
    for r in REGIONS:
        if len(REGIONS[r])>1:
            fic_md.write("- "+r+" : *[total](#"+clean_string(r)+"), [par département](#"+clean_string(r)+"_detail)*\n")
        else:
            fic_md.write("- "+r+" : *[total](#"+clean_string(r)+")*\n")

    fic_md.write("\n")

    for r in REGIONS:
        print(r)
        fic_md.write("\n - - - -\n\n<a name=\""+clean_string(r)+"\"> \n")
        fic_md.write("[![](./fig/"+clean_string(r)+"_total.png)](./fig/"+clean_string(r)+"_total.pdf) <br>\n")
        plot( r, True, "Région "+r+" (total)")
        fic_md.write("\n[Retour au sommaire](#top)\n\n")
        ds = REGIONS[r]
        if len(ds)>1:
            fic_md.write("<a name=\""+clean_string(r)+"_detail\">\n[![](./fig/"+clean_string(r)+".png)](./fig/"+clean_string(r)+".pdf) <br>\n")
            plot( r, False, "Région "+r+" (par départements)")
            fic_md.write("\n Par département de la région "+r+"\n\n")
            for d in ds:
                fic_md.write("- ["+d+": "+DEPARTEMENTS[d]+"](#"+d+")\n")
            fic_md.write("\n")
            fic_md.write("[Retour au sommaire](#top)\n")

    print("DEPARTEMENTS")
    fic_md.write("\n- - - -\n\n### Départements  <a name=\"par_departements\"> ([Retour au sommaire](#top))\n\n")
    for d in range(len(deps)):
        fic_md.write("- ["+deps[d]+": "+DEPARTEMENTS[deps[d]]+"](#"+deps[d]+")\n")

    fic_md.write("\n") 
    for d in range(len(deps)):
        print(deps[d])
        fic_md.write("\n - - - -\n<a name=\""+deps[d]+"\"> [![](./fig/"+deps[d]+"_total.png)](./fig/"+deps[d]+"_total.pdf) <br>\n [Retour au sommaire](#top)\n\n")
        plot( deps[d], True, DEPARTEMENTS[deps[d]]+" ("+deps[d]+")" )


    fic_md.write("\n- - - -\n\n- - - -\n\n### France par départements (cartes)<a name=\"france_cartes\">\n")    
    fic_md.write("\n - - - -\n#### Hospitalisations, patients en réanimation et décès à l'hôpital\n")
    fic_md.write("[![](./fig/carte_cumul_hosp.gif)](./fig/carte_cumul_hosp.pdf)<a name=\"cumul_hosp\"><br>\n")
    fic_md.write("[![](./fig/carte_cumul_deces.gif)](./fig/carte_cumul_deces.pdf)<a name=\"cumul_deces\"><br>\n")
    fic_md.write("[![](./fig/carte_hosp.gif)](./fig/carte_hosp.pdf)<a name=\"hosp\"><br>\n")
    fic_md.write("[![](./fig/carte_rea.gif)](./fig/carte_rea.pdf)<a name=\"rea\"><br>\n")
    fic_md.write("\n - - - -\n#### Nombre de lits de réanimation (source [DREES 2018](https://drees.solidarites-sante.gouv.fr/etudes-et-statistiques/publications/article/nombre-de-lits-de-reanimation-de-soins-intensifs-et-de-soins-continus-en-france)) et tension en réanimation<a name=\"lits\">\n")
    fic_md.write("[![](./fig/carte_lits_rea.png)](./fig/carte_lits_rea.pdf)")
    fic_md.write("[![](./fig/carte_tension.gif)](./fig/carte_tension.pdf)")
    fic_md.write("[![](./fig/carte_tension_moy.png)](./fig/carte_tension_moy.pdf)<br>\n")
    fic_md.write("\n - - - -\n#### Mortalité en sortie de l'hôpital, relation avec la tension en réanimation<a name=\"mortalite\">\n")
    fic_md.write("[![](./fig/carte_mortalite.png)](./fig/carte_mortalite.pdf)")
    fic_md.write("[![](./fig/tension_mort.png)](./fig/tension_mort.pdf)<br>\n")
    fic_md.write("\n- - - -\n\n#### Taux d'incidence par départements (nombre de cas sur 7 jours glissants pour 100.000 habitants)<a name=\"incid\">\n")
    fic_md.write("[![](./fig/carte_incid.gif)](./fig/carte_incid.pdf)<br>\n")
    fic_md.write("#### Taux de positivité <a name=\"posit\">\n")
    fic_md.write("[![](./fig/carte_posit.gif)](./fig/carte_posit.pdf)<br>\n")

    fic_md.write("</html>")
    fic_md.close()

    os.system("markdown README.md > README.html")

    print("README.html produit!")



### Fait tout:

NO_PLOT=False

DPI=70

genere_page()

tension_mort()

cartes()

