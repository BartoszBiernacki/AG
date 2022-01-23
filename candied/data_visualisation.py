"""Contains classes and functions for plotting results."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation


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

        
if __name__ == '__main__':
    df = pd.read_csv('../results/'
                     'Runs=12___Energy=1500___Mut_rate=3___Speed'
                     '=10___View_range=8___Max_steps_per_day=100/'
                     'raw data/'
                     'Id=0000___N_candies=80___N_creatures=50.csv')

    a = AnimatedScatter3D(df=df, fps=10)
    plt.show()
    