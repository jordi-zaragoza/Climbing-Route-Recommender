import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

def plot3D(x, y, z, color, fraction = 1):
    '''
    This function plots the x,y,z values in 3D
    color => color array for each value
    fraction => fraction of the data for visualization
    '''
    data = pd.DataFrame({0:x,1:y,2:z,3:color})
    data = data.sample(frac=fraction)
    
    x = data[0]
    y = data[1]
    z = data[2]
    color = data[3]

    sns.set_style("whitegrid", {'axes.grid' : False})

    fig = plt.figure(figsize=(6,6))

    ax = fig.add_subplot(111, projection='3d') # Method 2

    ax.scatter(x, y, z, c=color, marker='o')
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    
    plt.show()