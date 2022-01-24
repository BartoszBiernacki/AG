"""Contains classes and functions for plotting results."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import cm
import numpy as np
from celluloid import Camera


class AvgPopAnimatedScatter3D(object):
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


class AvgPopAnimatedLine3D(object):
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


def avg_pop_anim_history_scatter3D(df: pd.DataFrame, fps: int) -> None:
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


def animated_creatures_scatter3D(df: pd.DataFrame,
                                 fps: int,
                                 save=False) -> None:
    """
    Shows how all existing creatures in parameter space in time.

    On the left Axes there is a main 3D plot.
    On the right there are many Axes with the following plots (top to bottom):
        Number of creatures grouped by eaten candies and on the second y axis
        total happiness of population and an moving average of it (20 last
        vales).
        Average and moving average of view range, grouped by eaten candies.
        Average and moving average of focus angle, grouped by eaten candies.
        Average and moving average of speed, grouped by eaten candies.
    """
    fig = plt.figure(figsize=(18, 8), constrained_layout=True)
    spec = fig.add_gridspec(6, 2)
    
    # 3D plot, left half of figure
    ax06_0 = fig.add_subplot(spec[:, 0], projection='3d')
    ax06_0.set_title("Creatures in parameter space over time",
                     fontweight='bold')
    # Setting the axes properties
    ax06_0.set_xlabel('View range', fontweight='bold')
    ax06_0.set_ylabel('Focus angle', fontweight='bold')
    ax06_0.set_zlabel('Speed', fontweight='bold')
    ax06_0.set(xlim3d=(0, max(df['View range'])))
    ax06_0.set(ylim3d=(0, max(df['Focus angle'])))
    ax06_0.set(zlim3d=(0, max(df['Speed'])))
    
    # Axes for plotting num of zero, one and two eaters, right upper quarter
    ax03_1 = fig.add_subplot(spec[0:3, 1])
    ax03_1.set_title("Number of eaters and happiness", fontweight='bold')
    # Setting the axes properties
    ax03_1.set_xlabel('t, population', fontweight='bold')
    ax03_1.set_ylabel('n, number of creatures', fontweight='bold')
    
    # Axes for plotting happiness, share x axis with ax03_1
    ax03_1_r = ax03_1.twinx()
    # Setting the axes properties
    ax03_1_r.set_ylabel('Total happiness', fontweight='bold')
    
    # Axes for plotting each of creatures parameters, right bottom quarter
    # View range
    ax3_1 = fig.add_subplot(spec[3, 1])
    ax3_1.set_title("View range", fontweight='bold')
    # Focus angle
    ax4_1 = fig.add_subplot(spec[4, 1])
    ax4_1.set_title("Focus angle", fontweight='bold')
    # Speed
    ax5_1 = fig.add_subplot(spec[5, 1])
    ax5_1.set_title("Speed", fontweight='bold')
    
    # camera for taking snapshots of plots to animate them
    camera = Camera(fig)
    
    # in lists bellow there will be stored num of zero, one and two eaters
    # lists will be updated to achieve animated plot
    y_num0 = []
    y_num1 = []
    y_num2 = []
    
    # same as above, but for total energy of happiness
    happiness = []
    avg_moving_happiness = []
    
    # same as above but for view range, with respect to eaters
    view_range_0 = []
    view_range_1 = []
    view_range_2 = []
    avg_view_range_0 = []
    avg_view_range_1 = []
    avg_view_range_2 = []
    
    # same as above but for focus angle
    focus_angle_0 = []
    focus_angle_1 = []
    focus_angle_2 = []
    avg_focus_angle_0 = []
    avg_focus_angle_1 = []
    avg_focus_angle_2 = []
    
    # same as above but for speed
    speed_0 = []
    speed_1 = []
    speed_2 = []
    avg_speed_0 = []
    avg_speed_1 = []
    avg_speed_2 = []
    
    # Plot everything as animation
    for step in range(max(df['Step'])):
        sub_df = df.loc[df['Step'] == step + 1]
        
        # group population according to the candies eaten
        # filt0 - zero_eaters, filt1 - one_eaters, ...
        filt2 = sub_df['Moment of second consumption'].notnull()
        
        filt1 = sub_df['Moment of second consumption'].isnull() & \
                sub_df['Moment of first consumption'].notnull()
        
        filt0 = sub_df['Moment of first consumption'].isnull()
        
        # arrange corresponding values in lists
        filters = [filt0, filt1, filt2]
        colors = ['black', 'blue', 'red']
        anim_labels = [f'{np.sum(filt0)} zero eaters ',
                       f'{np.sum(filt1)} one eaters',
                       f'{np.sum(filt2)} two eaters']
        static_labels = [f'Zero eaters',
                         f'One eaters',
                         f'Two eaters']
        
        # update num of zero one and two eaters
        y_num0.append(np.sum(filt0))
        y_num1.append(np.sum(filt1))
        y_num2.append(np.sum(filt2))
        
        # plot num of zero one and two eaters
        num0, = ax03_1.plot(y_num0, c=colors[0])
        num1, = ax03_1.plot(y_num1, c=colors[1])
        num2, = ax03_1.plot(y_num2, c=colors[2])
        
        # update total happiness and moving average of it
        # moving average is an average of 20 last values
        happiness.append(np.sum(sub_df['Energy of happiness']))
        avg_moving_happiness.append(np.average(happiness[-20:]))
        # plot total happiness
        happy_line, = ax03_1_r.plot(happiness,
                                    color='green',
                                    linestyle='none',
                                    marker='o')
        # plot average moving  of total happiness
        moving_avg_happy_line, = ax03_1_r.plot(avg_moving_happiness,
                                               color='lime',
                                               linewidth=3,
                                               linestyle='-.')
        
        # show legend about num of eaters and happiness in one box
        lines = [num0, num1, num2, happy_line, moving_avg_happy_line]
        labels = static_labels + ['Happiness of population'] + \
                 ['Average moving of last 20 happiness']
        ax03_1.legend(lines, labels, loc='upper left')
        
        # plot view range in details  -----------------------------------------
        view_range_0.append(np.average(sub_df[filt0]['View range']))
        avg_view_range_0.append(np.average(view_range_0[-20:]))
        ax3_1.plot(view_range_0, color=colors[0], linestyle='none', marker='o')
        ax3_1.plot(avg_view_range_0, color=colors[0])
        
        view_range_1.append(np.average(sub_df[filt1]['View range']))
        avg_view_range_1.append(np.average(view_range_1[-20:]))
        ax3_1.plot(view_range_1, color=colors[1], linestyle='none', marker='o')
        ax3_1.plot(avg_view_range_1, color=colors[1])
        
        view_range_2.append(np.average(sub_df[filt2]['View range']))
        avg_view_range_2.append(np.average(view_range_2[-20:]))
        ax3_1.plot(view_range_2, color=colors[2], linestyle='none', marker='o')
        ax3_1.plot(avg_view_range_2, color=colors[2])
        
        ax3_1.text(0.825, 0.1, f'avg value = '
                               f'{np.average(sub_df["View range"]):.1f}',
                   transform=ax3_1.transAxes, fontweight='bold')
        
        # plot focus angle in details --------------------------------------
        focus_angle_0.append(np.average(sub_df[filt0]['Focus angle']))
        avg_focus_angle_0.append(np.average(focus_angle_0[-20:]))
        ax4_1.plot(focus_angle_0, color=colors[0], linestyle='none',
                   marker='o')
        ax4_1.plot(avg_focus_angle_0, color=colors[0])
        
        focus_angle_1.append(np.average(sub_df[filt1]['Focus angle']))
        avg_focus_angle_1.append(np.average(focus_angle_1[-20:]))
        ax4_1.plot(focus_angle_1, color=colors[1], linestyle='none',
                   marker='o')
        ax4_1.plot(avg_focus_angle_1, color=colors[1])
        
        focus_angle_2.append(np.average(sub_df[filt2]['Focus angle']))
        avg_focus_angle_2.append(np.average(focus_angle_2[-20:]))
        ax4_1.plot(focus_angle_2, color=colors[2], linestyle='none',
                   marker='o')
        ax4_1.plot(avg_focus_angle_2, color=colors[2])
        
        ax4_1.text(0.825, 0.75, f'avg value = '
                                f'{np.average(sub_df["Focus angle"]):.1f}',
                   transform=ax4_1.transAxes, fontweight='bold')
        
        # plot speed in details -------------------------------------------
        speed_0.append(np.average(sub_df[filt0]['Speed']))
        avg_speed_0.append(np.average(speed_0[-20:]))
        ax5_1.plot(speed_0, color=colors[0], linestyle='none',
                   marker='o')
        ax5_1.plot(avg_speed_0, color=colors[0])
        
        speed_1.append(np.average(sub_df[filt1]['Speed']))
        avg_speed_1.append(np.average(speed_1[-20:]))
        ax5_1.plot(speed_1, color=colors[1], linestyle='none',
                   marker='o')
        ax5_1.plot(avg_speed_1, color=colors[1])
        
        speed_2.append(np.average(sub_df[filt2]['Speed']))
        avg_speed_2.append(np.average(speed_2[-20:]))
        ax5_1.plot(speed_2, color=colors[2], linestyle='none',
                   marker='o')
        ax5_1.plot(avg_speed_2, color=colors[2])
        
        ax5_1.text(0.825, 0.1, f'avg value = '
                               f'{np.average(sub_df["Speed"]):.1f}',
                   transform=ax5_1.transAxes, fontweight='bold')
        
        # plot each subpopulation separately
        for filt, color in zip(filters, colors):
            x = sub_df[filt]['View range']
            y = sub_df[filt]['Focus angle']
            z = sub_df[filt]['Speed']
            
            # most important plot, tracks entire population
            scat = ax06_0.scatter(x, y, z,
                                  c=color,
                                  alpha=1,
                                  )
            
            # show average of each subpopulation
            scat_avg = ax06_0.scatter(np.average(x),
                                      np.average(y),
                                      np.average(z),
                                      c=color,
                                      alpha=0.3,
                                      s=500,
                                      )
        
        # show history of an average of zero eaters subpopulation
        avg_0_eaters_history = ax06_0.plot(avg_view_range_0,
                                           avg_focus_angle_0,
                                           avg_speed_0,
                                           c=colors[0],
                                           alpha=0.5,
                                           )
        
        # show history of an average of one eaters subpopulation
        avg_1_eaters_history = ax06_0.plot(avg_view_range_1,
                                           avg_focus_angle_1,
                                           avg_speed_1,
                                           c=colors[1],
                                           alpha=0.5,
                                           )
        
        # show history of an average of two eaters subpopulation
        avg_2_eaters_history = ax06_0.plot(avg_view_range_2,
                                           avg_focus_angle_2,
                                           avg_speed_2,
                                           c=colors[2],
                                           alpha=0.5,
                                           )
        
        """
        Part below is a bit fucked up, because of the legend.

        The problem is that the legend function don't support the type returned
        by a 3D scatter. So I have to create a "dummy plot" with the same
        characteristics and put those in the legend.
        Solution from: https://stackoverflow.com/questions/20505105/
        add-a-legend-in-a-3d-scatterplot-with-scatter-in-matplotlib

        Well some may think about making legend by default call 'ax06_0.legend()'.
        In normal situation (not animated by celluloid camera) that would
        work, but as celluloid documentation says: ,,Legends will accumulate
        from previous frames. Pass the artists to the legend function to draw
        them separately.'' (https://github.com/jwkvam/celluloid).
        Unfortunately as said above it is impossible to use
        'ax06_0.legend(scatter3D)'.
        """
        scat_proxy0, = ax06_0.plot([], [],
                                   linestyle="none",
                                   c=colors[0],
                                   marker='o',
                                   )
        
        scat_proxy1, = ax06_0.plot([], [],
                                   linestyle="none",
                                   c=colors[1],
                                   marker='o',
                                   )
        
        scat_proxy2, = ax06_0.plot([], [],
                                   linestyle="none",
                                   c=colors[2],
                                   marker='o',
                                   )
        
        # finally show the goddam legend...
        ax06_0.legend([scat_proxy0, scat_proxy1, scat_proxy2], anim_labels)
        
        # improve axis limits
        ax03_1.set_ylim(bottom=0)
        ax03_1_r.set_ylim(bottom=0, top=1.2 * max(happiness))
        
        ax3_1.set_ylim(bottom=0, top=1.2 * np.max([view_range_0,
                                                   view_range_1,
                                                   view_range_2]))
        
        ax4_1.set_ylim(bottom=0, top=1.2 * np.max([focus_angle_0,
                                                   focus_angle_1,
                                                   focus_angle_2]))
        
        ax5_1.set_ylim(bottom=0, top=1.2 * np.max([speed_0,
                                                   speed_1,
                                                   speed_2]))
        
        camera.snap()
        
    anim = camera.animate(
        interval=1000 / fps,
        blit=True,
    )
    
    # TODO speed this process up
    if save:
        anim.save(filename="creatures_in_parameter_space.gif",
                  writer=animation.PillowWriter(fps=fps))
    
    plt.show()

        
if __name__ == '__main__':
    df_avg_model = pd.read_csv('../results/avg_model_data/'
                               'Runs=10___'
                               'Max_days=800___'
                               'Energy=1500___'
                               'Mut_rate=3___'
                               'Speed=10___'
                               'View_range=8___'
                               'Max_steps_per_day=100/'
                               'raw data/'
                               'Id=0000___N_candies=70___N_creatures=50.csv')

    df_creatures = pd.read_csv('../results/agents_data/'
                               'Max_days=800___'
                               'Energy=1500___'
                               'Mut_rate=3___'
                               'Speed=10___'
                               'View_range=8___'
                               'Max_steps_per_day=100/'
                               'raw data/'
                               'Id=0009___N_candies=70___N_creatures=50.csv')

    # a = AvgPopAnimatedScatter3D(df=df_avg_model, fps=10)
    # plt.show()
    
    # b = AvgPopAnimatedLine3D(df=df_avg_model, fps=20)
    # plt.show()
    
    # avg_pop_anim_history_scatter3D(df=df_avg_model, fps=30)
    
    """
    Warning[1]: saving this takes a lot of time, but fps is real!
    Warning[2]: generating plotting is faster, but fps will be most
    likely lower than specified. It depends on num of simulated days.
    
    Note: that is caused, because on the Axes there are plenty of
    lines/scatters, and it take some time to draw them. This is because in each
    day (iteration over for loop) there are new 32 lines added to figure. So
    for 100 days on the fig there are 32000 lines/scatters in total!
    """
    animated_creatures_scatter3D(df=df_creatures, fps=20, save=False)
    