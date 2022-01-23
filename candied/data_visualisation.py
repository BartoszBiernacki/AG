"""Contains classes and functions for plotting results."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import numpy as np
from matplotlib.animation import PillowWriter
from celluloid import Camera


class AnimatedScatter3D(object):
    """
    An animated scatter plot using matplotlib.animations.FuncAnimation.
    
    Plot shows evolution of entire population in time (view range=X,
    focus angle=Y, speed=Z).
    
    Class constructor gets pandas DataFrame which contains data from model
    level DataCollector (averaged or not).
    
    Based on example from
    https://stackoverflow.com/questions/9401658/how-to-animate-a-scatter-plot
    """
    def __init__(self, df: pd.DataFrame, fps=10):
        self.df = df
        self.fps = fps
        
        self.stream = self.data_stream()
        
        # Setup the figure and axes...
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.scat = None
        
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig,
                                           self.update,
                                           frames=len(df),
                                           init_func=self.setup_plot,
                                           interval=1000/self.fps,
                                           repeat=False,
                                           blit=False)

    def setup_plot(self):
        """Initial drawing of the scatter plot."""

        # Setting the axes properties
        self.ax.set(xlim3d=(0, max(self.df['View'])), xlabel='View range')
        self.ax.set(ylim3d=(0, max(self.df['Focus'])), ylabel='Focus angle')
        self.ax.set(zlim3d=(0, max(self.df['Speed'])), zlabel='Speed')

        self.scat = self.ax.scatter3D([], [], [], color='m')

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,

    def data_stream(self):
        """
        Returns data (x, y, z) from DataFrame.
        Note: this function can't be called more than len(self.df) times.
        """
        for i in range(len(self.df)):
            xyz = (
                self.df['View'][i],
                self.df['Focus'][i],
                self.df['Speed'][i],
            )
            yield xyz

    def update(self, i):
        """Update the scatter plot."""
       
        data = next(self.stream)
        # Set x and y and z data...
        self.scat._offsets3d = ([data[0]], [data[1]], [data[2]])

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.scat,


class AnimatedLine3D(object):
    """
    An animated line plot using matplotlib.animations.FuncAnimation.

    Plot shows evolution of entire population in time (view range=X,
    focus angle=Y, speed=Z).

    Class constructor gets pandas DataFrame which contains data from model
    level DataCollector (averaged or not).

    Based on examples from
    https://stackoverflow.com/questions/9401658/how-to-animate-a-scatter-plot
    https://matplotlib.org/stable/gallery/animation/random_walk.html
    """
    
    def __init__(self, df: pd.DataFrame, fps=10):
        self.df = df
        self.fps = fps
        
        self.stream = self.data_stream()
        
        # Setup the figure and axes...
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        self.line = None
        
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig,
                                           self.update,
                                           frames=len(df),
                                           init_func=self.setup_plot,
                                           interval=1000 / self.fps,
                                           repeat=False,
                                           blit=False)
    
    def setup_plot(self):
        """Initial drawing of the scatter plot."""
        
        # Setting the axes properties
        self.ax.set(xlim3d=(0, max(self.df['View'])), xlabel='View range')
        self.ax.set(ylim3d=(0, max(self.df['Focus'])), ylabel='Focus angle')
        self.ax.set(zlim3d=(0, max(self.df['Speed'])), zlabel='Speed')
        
        self.line = self.ax.plot([], [], [])[0]
        
        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.line,
    
    def data_stream(self):
        """
        Returns data (x, y, z) from DataFrame.
        Note: this function can't be called more than len(self.df) times.
        """
        for i in range(len(self.df)):
            xyz = (
                self.df['View'][i],
                self.df['Focus'][i],
                self.df['Speed'][i],
            )
            yield xyz
    
    def update(self, i):
        """Update the scatter plot."""
        # Get new data point from Dataframe
        data = next(self.stream)
        
        # Get data plotted so far from the line
        xdata, ydata, zdata = self.line._verts3d
        
        # Set x and y and z data...
        # NOTE: there is no .set_data() for 3 dim data...
        self.line.set_data(
            np.append(xdata, data[0]),
            np.append(ydata, data[1]),
        )
        
        self.line.set_3d_properties(np.append(zdata, data[2]))

        # We need to return the updated artist for FuncAnimation to draw..
        # Note that it expects a sequence of artists, thus the trailing comma.
        return self.line,


def animated_history_scatter3D(df: pd.DataFrame, fps: int) -> None:
    """
    Shows how population adapts over time.
    """
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    
    # Setting the axes properties
    ax.set_title("Avg population parameters over time.")
    
    ax.set(xlim3d=(0, max(df['View'])), xlabel='View range')
    ax.set(ylim3d=(0, max(df['Focus'])), ylabel='Focus angle')
    ax.set(zlim3d=(0, max(df['Speed'])), zlabel='Speed')
    
    camera = Camera(fig)
    
    numpoints = len(df)
    colors = cm.rainbow(np.linspace(0, 1, numpoints))
    
    for i in range(len(df)):
        x = df['View'][: i + 1]
        y = df['Focus'][: i + 1]
        z = df['Speed'][: i + 1]
        
        c = colors[: i + 1]
        
        ax.scatter(x, y, z, cmap="rainbow", c=c)
        
        camera.snap()
    anim = camera.animate(
        interval=1000 / fps,
        blit=True,
    )
    plt.tight_layout()
    
    # anim.save("movie.gif", writer=PillowWriter(fps=fps))
    plt.show()

        
if __name__ == '__main__':
    df = pd.read_csv('../results/'
                     'Runs=12___Energy=1500___Mut_rate=3___Speed'
                     '=10___View_range=8___Max_steps_per_day=100/'
                     'raw data/'
                     'Id=0000___N_candies=80___N_creatures=50.csv')

    # a = AnimatedScatter3D(df=df, fps=10)
    # plt.show()
    
    # b = AnimatedLine3D(df=df, fps=20)
    # plt.show()
    
    animated_history_scatter3D(df=df, fps=30)
    