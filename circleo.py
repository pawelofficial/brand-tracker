import matplotlib.pyplot as plt
import numpy as np
import math 
import random 
from matplotlib.patches import FancyArrowPatch
def plot_intersecting_circles_from_df_old(df,r=1):
    # Create figure and axis
    fig, ax = plt.subplots()

    # Plot circles
    for no,row in df.iterrows():
        x=row['x']
        y=row['y']
        who=row['who']
        color=row['color']
        circle = plt.Circle( (x,y),r, color='green', alpha=0.5)
        ax.add_artist(circle)
        
        vx=x*r*1.5
        vy=y*r*1.5
        print(vx,vy,who)
        ax.text(x+vx, y+vy, f"{who}") 
#    circle1 = plt.Circle(df.iloc[0,:2], df.iloc[0,2], color='green', alpha=0.5)
#    circle2 = plt.Circle(df.iloc[1,:2], df.iloc[1,2], color='blue', alpha=0.5)
#    ax.add_artist(circle1)
#    ax.add_artist(circle2)

    # Set limits and aspect ratio
#    ax.set_xlim(df.iloc[:,0].min() - df.iloc[:,2].max() - 1, df.iloc[:,0].max() + df.iloc[:,2].max() + 1)
#    ax.set_ylim(df.iloc[:,1].min() - df.iloc[:,2].max() - 1, df.iloc[:,1].max() + df.iloc[:,2].max() + 1)
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    ax.set_aspect('equal')

    # Show plot
    plt.show()
import matplotlib.image as mpimg

def plot_intersecting_circles_from_df(df,r=0.1,who='who',color='color',coord='coord'):
    # Create figure and axis
    fig, ax = plt.subplots()
    N=np.pi
    step=4*np.pi/len(df)
    steps=np.linspace(- N,N,len(df) )

    # Plot circles
    legend_handles=[]
    for no,row in df.iterrows():
        angle = row[coord]
        dist=r*10
        x=dist * np.cos(angle)
        y=dist * np.sin(angle)
        circle = plt.Circle( (x,y),r, color=row[color], alpha=0.2)
        ax.add_artist(circle)
        legend_handles.append(circle)
        
        vx=x*r*1.5
        vy=y*r*1.5
        #print(vx,vy,who)
        ax.text(x, y, f"{row[who]}") 
    ax.set_xlim(-2,2)
    ax.set_ylim(-1,2)
    ax.set_aspect('equal')
    ax.set_xlabel('nie tak jak PIS <---                     ---> tak jak PIS  ')
    plt.legend(legend_handles, df[who], loc='upper left')

    # Show plot
    ax.grid(True)
    plt.show()


def plot_polar(df,r=0.1,who='who',color='color',coord='coord'):
    fig,ax=plt.subplots(subplot_kw={'projection':'polar'})
    legend_handles=[]
    
    # Add left arrow
    left_arrow = FancyArrowPatch((0, 0), (np.pi, 1), arrowstyle='->', mutation_scale=20, label='Left Arrow',color='green')
    ax.add_patch(left_arrow)
    ax.text(np.pi, 1, '     inaczej niż pis', ha='left', va='top',color='green')
    
    # Add right arrow
    right_arrow = FancyArrowPatch((0, 0), (0,1), arrowstyle='->', mutation_scale=20, label='Right Arrow',color='red')
    ax.add_patch(right_arrow)
    ax.text(0, 1, 'tak jak pis   ', ha='right', va='top',color='red')
    
    for no,row in df.iterrows():
        angle=row[coord]
        dist=r*10
        label = row[who]
        handle = ax.plot(angle,dist,'o',color=row[color],markerfacecolor=row[color],markeredgewidth=2,label=label,alpha=0.5,markersize=10)
        ax.text(angle,dist+0.2,label,ha='center', va='top')
        legend_handles.append(handle[0])



    plt.legend(handles=legend_handles, loc='lower center')
    ax.grid(True)
    ax.set_xticklabels([],verticalalignment='center')  # remove angles text
    ax.set_yticklabels([],rotation=90)  # remove angles text
    ax.set_xlabel('JAK ONI GŁOSUJĄ ! ')
    plt.show()





 

 
import pandas as pd
# 'color': ['green', 'blue','red','yellow','purple']}
#kolorki={'pis':'blue','ko':'purple','lewica':'red','psl':'green','2050':'yellow','memcen':'black','random':'orange'}
#partie=['pis','ko','lewica','psl','2050','memcen']


partie=['pinokio','rudy lis','zojdberg','koalicjant ponad podzialami','Szymek','Memcen','antypis']
kolorki={'pinokio':'blue','rudy lis':'purple','zojdberg':'red','koalicjant ponad podzialami':'green','Szymek':'yellow','Memcen':'black','antypis':'pink'}


d={'glosowanie':['polski lad','swiadczenie integracyjne','tanie paliwo','telewizor+','wyroby medyczne','dekoder+','14 emerytura','uran','dostep do broni','ukraincy+']
   ,'pinokio':[1,1,0,1,1,1,1,1,0,1]
   ,'antypis':[0 ,0,1,0,0,0,0,0,1,0] # przeciwnie do pis 
   ,'rudy lis':[0,1,1,1,1,1,1,0,0,1]
   ,'zojdberg':[0,1,0,1,1,1,1,0,0,1]
   ,'koalicjant ponad podzialami':[0,1,1,1,1,1,1,0,0,1]
   ,'Szymek':[0,1,1,1,1,1,1,0,0,1]
   ,'Memcen':[0,0,1,0,0,0,0,1,1,0]
   ,'random':[1,1,0,1,1,1,1,1,0,1] # [random.randint(0,1) for i in range(10)] jednak nie random xd 
   }
data_df=pd.DataFrame(d)
euc_dist=lambda x,y: math.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2)
euc_dist=lambda x,y: np.linalg.norm(x - y)

coordinates_d={}

vr=data_df['random']
for p in partie:
    v=data_df[p].values
    dist=euc_dist(v,vr)
    coordinates_d[p]=dist
    
    


print(data_df)
k=0
circles_d={'partia':[c for c in partie]
           ,'coordinates':[coordinates_d[c] for c in partie]
           ,'color':[kolorki[c] for c in partie]
           } 
circles_df=pd.DataFrame(circles_d)


#circles_df['coordinates']=np.linspace(0,2*np.pi,len(circles_df))
min_coord=np.min(circles_df['coordinates'])
max_coord=np.max(circles_df['coordinates'])
mapped_values = np.interp(circles_df['coordinates'], (min_coord,max_coord), (0,np.pi)) # gotta do half circeleo because min values and max values be different not same same  
circles_df['noorm_coordinates']=mapped_values


print(circles_df)
plot_polar(circles_df,who='partia',color='color',coord='noorm_coordinates')
exit(1)



#coords=[1,1,1,1,1,6]
#new_domain=[-np.pi/2,np.pi/2]
#mapped_values = np.interp(coords, (min(coords),max(coords)), new_domain)
#coords=mapped_values
#df = pd.DataFrame({'coord': coords,'color': ['green', 'blue','red','black','yellow','magenta'],'who':['foo','bar','kez','kez','kez','kez'] })
#plot_intersecting_circles_from_df(df)
#plot_intersecting_circles_from_df(circles_df,who='partia',color='color',coord='noorm_coordinates2')
