import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


class FilterStructureVisualizer:
    def __init__(self):
        self.circle_radius = 0.3
        self.box_width = 0.6
        self.box_height = 0.6
        self.arrow_head_width = 0.2
        self.arrow_head_length = 0.2
        self.center_x = 4
        self.current_fig = None
        self.current_ax = None

    def _create_figure(self, figsize=(12, 8)):
        """Create new figure and axis or clear existing one"""
        self.current_fig, self.current_ax = plt.subplots(figsize=figsize)
        return self.current_fig, self.current_ax

    def _calculate_delays(self, denominator_coeffs, numerator_coeffs):
        """Calculate number of delay elements needed"""
        if len(denominator_coeffs) >= len(numerator_coeffs) - 1:
            if denominator_coeffs[-1] == 0:
                return len(denominator_coeffs) - 1, True, True
            return len(denominator_coeffs), False, True
        else:
            if numerator_coeffs[-1] == 0:
                return len(numerator_coeffs) - 2, True, False
            return len(numerator_coeffs) - 1, False, False

    def _setup_plot(self, width, height, title):
        """Common plot setup logic"""
        ax = self.current_ax
        ax.set_xlim(-2, width)
        ax.set_ylim(-2 * height - 1, 2)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_aspect('equal')

        # Draw input arrow
        ax.arrow(-1, 0, 2.5, 0,
                 head_width=self.arrow_head_width, head_length=self.arrow_head_length)
        ax.text(-1.5, 0.3, 'x(n)', fontsize=12)

        plt.title(title)

    def _draw_direct_form_2_section(self, ax, denominator_coeffs, numerator_coeffs, offset_x=0):
        """Draw a single Direct Form II section at the specified x offset"""
        # Determine the number of delay elements needed
        if len(denominator_coeffs) >= len(numerator_coeffs) - 1:
            # is_denominator_max_order = True  # Denominator has higher order so it determines the number of delays
            if denominator_coeffs[-1] == 0:  # Check if the last coefficient is zero so no need for the extra delay
                n_delays = len(denominator_coeffs) - 1
                # is_delay_minused = True
            else:
                n_delays = len(denominator_coeffs)
                # is_delay_minused = False
        else:
            # is_denominator_max_order = False
            if numerator_coeffs[-1] == 0:
                n_delays = len(numerator_coeffs) - 2
                # is_delay_minused = True
            else:
                n_delays = len(numerator_coeffs) - 1
                # is_delay_minused = False

        center_x = self.center_x + offset_x

        # Draw delay elements
        for i in range(n_delays):
            y_pos = -2 * (i + 1) - 0.3

            # Draw delay element box
            z_box = Rectangle((center_x - self.box_width / 2, y_pos),
                              self.box_width, self.box_height, fill=False)
            ax.add_patch(z_box)
            ax.text(center_x - 0.2, y_pos + 0.2, r'$z^{-1}$', fontsize=12)

            # Vertical connections for delay elements
            if i == 0:
                ax.arrow(center_x, 0, 0, y_pos + self.box_height + 0.2,
                         head_width=self.arrow_head_width, head_length=self.arrow_head_length)
            else:
                ax.arrow(center_x, y_pos + self.box_height + 1.4, 0, -1.2,
                         head_width=self.arrow_head_width, head_length=self.arrow_head_length)

            # Feedback paths
            if i < len(denominator_coeffs):
                ax.arrow(center_x - self.box_width / 2, y_pos + self.box_height / 2,
                         -1.5 + self.circle_radius, 0,
                         head_width=self.arrow_head_width, head_length=self.arrow_head_length)
                ax.text(center_x - 1.3, y_pos + self.box_height,
                        f'-{denominator_coeffs[i]}', fontsize=12)
                ax.arrow(center_x - 2, y_pos + self.box_height, 0, 1.2,
                         head_width=self.arrow_head_width, head_length=self.arrow_head_length)

            # Feedforward paths
            if i + 1 < len(numerator_coeffs):
                ax.arrow(center_x + self.box_width / 2, y_pos + self.box_height / 2,
                         2.2, 0, head_width=self.arrow_head_width, head_length=self.arrow_head_length)
                ax.text(center_x + 1.5, y_pos + self.box_height,
                        f'{numerator_coeffs[i + 1]}', fontsize=12)
                ax.arrow(center_x + 3, y_pos + self.box_height, 0, 1.2,
                         head_width=self.arrow_head_width, head_length=self.arrow_head_length)

        # Draw feedback summing junctions
        for i in range(len(denominator_coeffs) + 1):
            if i == len(denominator_coeffs) and denominator_coeffs[-1] == 0:
                continue
            y_pos = -2 * i
            feedback_sum = Circle((center_x - 2, y_pos), self.circle_radius, fill=False)
            ax.add_patch(feedback_sum)
            ax.text(center_x - 2, y_pos, '+', ha='center', va='center', fontsize=12)

        # Draw output summing junctions
        for i in range(len(numerator_coeffs)):
            if i == len(numerator_coeffs) - 1 and numerator_coeffs[-1] == 0:
                continue
            y_pos = -2 * i
            output_sum = Circle((center_x + 3, y_pos), self.circle_radius, fill=False)
            ax.add_patch(output_sum)
            ax.text(center_x + 3, y_pos, '+', ha='center', va='center', fontsize=12)

        # Draw main path
        ax.arrow(center_x - 1.7, 0, 4.2, 0,
                 head_width=self.arrow_head_width, head_length=self.arrow_head_length)
        ax.text(center_x + 1.5, 0.3, f'{numerator_coeffs[0]}', fontsize=12)

        return center_x + 3  # Return the x-coordinate of the output

    def _draw_output_arrow(self, start_x):
        """Draw the final output arrow and label"""
        self.current_ax.arrow(start_x + 0.3, 0, 1.5, 0,
                              head_width=self.arrow_head_width, head_length=self.arrow_head_length)
        self.current_ax.text(start_x + 1.2, 0.3, 'y(n)', fontsize=12)

    def create_direct_form_2(self, denominator_coeffs, numerator_coeffs, figsize=(12, 8)):
        """Create Direct Form II structure from filter coefficients"""
        self._create_figure(figsize)

        # Calculate number of delays and plot dimensions
        n_delays, _, _ = self._calculate_delays(denominator_coeffs, numerator_coeffs)
        self._setup_plot(10, n_delays + 1, 'Direct Form II Filter Structure')

        # Draw the section and output
        output_x = self._draw_direct_form_2_section(self.current_ax, denominator_coeffs, numerator_coeffs)
        self._draw_output_arrow(output_x)

        return self.current_fig

    def create_cascade_form(self, sections, figsize=(20, 8)):
        """Create Cascade Form structure from multiple sections"""
        self._create_figure(figsize)

        # Calculate plot dimensions
        max_delays = max(len(d) for d, n in sections)
        width = len(sections) * 8 + 2
        self._setup_plot(width, max_delays + 1, 'Cascade Form Filter Structure')

        # Draw each section
        last_x = None
        for i, (deno, num) in enumerate(sections):
            output_x = self._draw_direct_form_2_section(self.current_ax, deno, num, offset_x=i * 8)
            last_x = output_x

            # Connection to next section
            if i < len(sections) - 1:
                self.current_ax.arrow(output_x + self.circle_radius, 0,
                                      2.2, 0, head_width=self.arrow_head_width,
                                      head_length=self.arrow_head_length)

        # Draw final output
        if last_x is not None:
            self._draw_output_arrow(last_x)

        return self.current_fig, self.current_ax

    def show(self):
        """Display the current figure"""
        if self.current_fig is not None:
            plt.show()
            self.current_fig = None
            self.current_ax = None
        else:
            print("No figure to display")


# Example usage:
visualizer = FilterStructureVisualizer()

# Example 1: Single Direct Form II
deno1 = [0.5]
num1 = [1.0, 0.3]
visualizer.create_direct_form_2(deno1, num1)
plt.title('Direct Form II Filter Structure')
visualizer.show()

# Example: Cascade Form with three sections
sections = [
    ([0.2, 0.1], [1.0, 0.4, 0.2]),  # First section
    ([0.1], [1.0, 0.3]),  # Second section
    ([0.15], [1.0, 0.25])  # Third section
]
visualizer.create_cascade_form(sections)
visualizer.show()

# Example 3: nomirator longer than denominator
deno2 = [0.5, 0.2, 0.1]
num2 = [1.0, 0.3, 0.1, 0.05, 0.44]
visualizer.create_direct_form_2(deno2, num2)
plt.title('Direct Form II dfgsdfure')
visualizer.show()

# Example 4: denominator longer than numerator
deno3 = [0.5, 0.2, 0.1, 0.05, 0.44]
num3 = [1.0, 0.3, 0.1]
visualizer.create_direct_form_2(deno3, num3)
plt.title('Direct Form II Filter Structure')
visualizer.show()

# Example 4: denominator longer than numerator with zero end
deno3 = [0.5, 0.2, 0.1, 0.05, 0.44, 0]
num3 = [1.0, 0.3, 0.1]
visualizer.create_direct_form_2(deno3, num3)
plt.title('Direct Form II Filter Structure')
visualizer.show()

# Example 3: nomirator longer than denominator with zero end
deno2 = [0.5, 0.2, 0.1]
num2 = [1.0, 0.3, 0.1, 0.05, 0.44, 0]
visualizer.create_direct_form_2(deno2, num2)
plt.title('Direct Form II dfgsdfure')
visualizer.show()

# Example: Cascade Form
sections = [
    ([1.0, -0.5], [0.5, 0.5]),  # First section coefficients
    ([1.0, -0.3], [0.6, 0.4])   # Second section coefficients
]
visualizer.create_cascade_form(sections)
plt.title('Casc 3')
visualizer.show()