from copy import deepcopy
from logging import getLogger
from pathlib import Path

import numpy as np
import streamlit as st

from shotshaper.projectile import DiscGolfDisc
from utilities.visualize import get_plot, get_subplots, stl_meshes, visualize_disc

# Define the default values
default_U = 24.2
default_omega = 116.8
default_z0 = 1.3
default_pitch = 15.5
default_nose = 0.0
default_roll = 14.7

faq = """
# Motivation
I saw some great work by [kegiljarhus](https://github.com/kegiljarhus) [repo](https://github.com/kegiljarhus/shotshaper)
and wanted to make this available as an app so people could learn more about disc golf. I really want to commend
the amazing idea of writing a [scientific article](https://link.springer.com/article/10.1007/s12283-022-00390-5)
 AND releasing code, and actually executing it well. This is what gets people excited about STEM.

I originally saw this 
[reddit post](https://www.reddit.com/r/discgolf/comments/yyhbcj/wrote_a_scientific_article_on_disc_golf_flight/)
which really piqued my interest.

# Questions
- I imagine some of you will want to add your disc here, if you can convert your disc into an `.stl` then I will 
add it to the database. If this gets common enough I will add an option to upload your own.
    - I imagine there will be a barrier to entry to do this.
    - If you have any ideas, just let me know in a discussion or in a pull request
"""


def main():
    tab1, tab2 = st.tabs(['Simulator', 'FAQ'])
    vb_link = 'https://visitor-badge.glitch.me/badge?page_id=derek-thomas.disc-golf-simulator&left_color=gray&right_color=blue'
    st.sidebar.markdown(f"""
    ![Total Visitors]({vb_link})
    """)
    with tab1:
        disc_names = {
            'Innova Wraith': 'dd2',
            'Innova Firebird': 'cd1',
            'Innova Roadrunner': 'cd5',
            'Innova Fairway Driver': 'fd2',
            }
        disc_selected = st.sidebar.selectbox("Disc Selection", disc_names.keys())
        disc_name = disc_names[disc_selected]

        # Create the sliders with the default values
        with st.container():
            st.sidebar.markdown("### Disc Orientation")
            nose = st.sidebar.slider("Nose Angle (deg) | Up/Down", min_value=-45.0, max_value=90.0, value=default_nose,
                                     help='0 is the disc pointing to the horizon\n90 is the disc pointing to the sky.',
                                     step=0.1)
            roll = st.sidebar.slider("Roll Angle (deg) | Anhyzer/Hyzer", min_value=-90.0, max_value=90.0,
                                     help='-90 the disc is very anhyzer, '
                                          '0 is the disc flat on the table, '
                                          '90 the disc is very hyzer',
                                     value=default_roll,
                                     step=0.1)
        with st.sidebar.container():
            st.sidebar.markdown("### Throwing Properties")
            U = st.sidebar.slider("Throwing Velocity (m/s)", min_value=0.0, max_value=40.0, value=default_U, step=0.1,
                                  help='20m/s is a begginer\'s throw. '
                                       'The fastest throw on record is ~40m/s by Simon Lizotte')
            omega = st.sidebar.slider("Omega (revolutions/s)", min_value=0.0, max_value=200.0, value=default_omega,
                                      step=0.1,
                                      help='How much spin do you have?')
            z0 = st.sidebar.slider("Release Height (m)", min_value=0.0, max_value=2.0, value=default_z0, step=0.1,
                                   help='How high is your arm when throwing?')
            pitch = st.sidebar.slider("Pitch Angle (deg) | Release angle", min_value=0.0, max_value=90.0,
                                      help='0 = flat, 90 = aiming straight up',
                                      value=default_pitch,
                                      step=0.1)

        with st.spinner(text="Calculating Disc Orientation..."):
            pos = np.array((0, 0, z0))
            disc_dict = DiscGolfDisc(disc_name)

            stl_mesh = deepcopy(stl_meshes[disc_name])
            fig = visualize_disc(stl_mesh, nose=nose, roll=roll)

            st.markdown("""
            ## Disc Orientation
            This is what your disc should look like after you release. The `Nose Angle` and `Roll Angle` 
            sidebar sliders control this.""")
            st.plotly_chart(fig)
        with st.spinner(text="Calculating Flight Path..."):
            st.markdown("""
            ## Flight Path
            Based on the sliders to the left, this will determine what your throw will look like.""")
            shot = disc_dict.shoot(speed=U, omega=omega, pitch=pitch,
                                   position=pos, nose_angle=nose, roll_angle=roll)

            # Plot trajectory
            x, y, z = shot.position
            x_new, y_new = -1 * y, x

            # Reversed x and y to mimic a throw
            fig = get_plot(x_new, y_new, z)
            st.plotly_chart(fig, True)
            st.markdown(
                    f"""
            **Arrows in Blue** show you where your *s-turn* is.

            **Arrows in Red** show you your *max height* and *lateral deviance*.

            Hit `Play` to watch your animated throw.

            | Metric       | Value  |
            |--------------|--------|
            | Drift Left   | {round(min(x_new), 2)} |
            | Drift Right  | {round(max(x_new), 2)} |
            | Max Height   | {round(max(z), 2)}    |
            | Distance     | {round(max(y_new), 2)} |

            """
                    )

            arc, alphas, betas, lifts, drags, moms, rolls = disc_dict.post_process(shot, omega)
            fig = get_subplots(arc, alphas, lifts, drags, moms, rolls, shot.velocity)
            with st.expander("Optional Charts for science-y people"):
                st.plotly_chart(fig, True)

    with tab2:
        st.markdown(faq)


if __name__ == "__main__":
    # Setting up Logger and proj_dir
    logger = getLogger(__name__)
    proj_dir = Path(__file__).parent

    st.title("Disc Golf Simulator")

    # initialize_state()
    main()
