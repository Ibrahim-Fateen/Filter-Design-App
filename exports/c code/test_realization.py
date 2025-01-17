import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arrow, Rectangle
from sympy import false


def draw_direct_form_2(denominator_coeffs, nomirator_coeffs, figsize=(12, 8)):
    """
    Draw a Direct Form II filter structure visualization with separate summing junctions
    for both feedforward and feedback paths

    Parameters:
    denominator_coeffs: list of feedback coefficients [a1, a2, ...] without the first 1 (coeff of z^0)
    nomirator_coeffs: list of feedforward coefficients [b0, b1, b2, ...]
    figsize: tuple for figure size
    """
    is_delay_minused = False
    is_denominator_max_order = False
    y_pos = 0
    i = 0
    # Determine the number of delay elements needed
    if len(denominator_coeffs) >= len(nomirator_coeffs) - 1:
        is_denominator_max_order = True  # Denominator has higher order so it determines the number of delays
        if denominator_coeffs[-1] == 0: # Check if the last coefficient is zero so no need for the extra delay
            n_delays = len(denominator_coeffs) - 1
            is_delay_minused = True
        else:
            n_delays = len(denominator_coeffs)
            is_delay_minused = False
    else:
        is_denominator_max_order = False
        if nomirator_coeffs[-1] == 0:
            n_delays = len(nomirator_coeffs) - 2
            is_delay_minused = True
        else:
            n_delays = len(nomirator_coeffs) - 1
            is_delay_minused = False

    # Create figure and axis with dynamic sizing
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect('equal')

    # Set plot limits based on number of delays
    ax.set_xlim(-2, 10)
    ax.set_ylim(-2 * (n_delays + 1), 4)

    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Constants for drawing
    circle_radius = 0.3
    box_width = 0.6
    box_height = 0.6
    arrow_head_width = 0.2
    arrow_head_length = 0.2

    # Center point for the structure
    center_x = 4

    # Draw feedback summing junctions for each level
    feedback_sums = []
    for i in range(len(denominator_coeffs) + 1):
        if i == len(denominator_coeffs) and denominator_coeffs[-1] == 0:
            continue
        y_pos = -2 * i
        feedback_sum = Circle((center_x - 2, y_pos ), circle_radius, fill=False)
        ax.add_patch(feedback_sum)
        ax.text(center_x - 2, y_pos , '+', ha='center', va='center', fontsize=12)
        feedback_sums.append(feedback_sum)

    # Draw output summing junctions for each level
    output_sums = []
    for i in range(len(nomirator_coeffs)):
        if i == len(nomirator_coeffs) and nomirator_coeffs[-1] == 0:
            continue
        y_pos = -2 * i
        output_sum = Circle((center_x + 3, y_pos), circle_radius, fill=False)
        ax.add_patch(output_sum)
        ax.text(center_x + 3, y_pos, '+', ha='center', va='center', fontsize=12)
        output_sums.append(output_sum)

    # Draw delay elements and connections
    for i in range(n_delays):
        y_pos = -2 * (i + 1) - 0.3

        # Draw delay element (centered)
        z_box = Rectangle((center_x - box_width / 2, y_pos), box_width, box_height, fill=False)
        ax.add_patch(z_box)
        ax.text(center_x - 0.2, y_pos + 0.2, r'$z^{-1}$', fontsize=12)

        # Draw vertical connection from previous level
        if i == 0:
            ax.arrow(center_x, 0, 0, y_pos + box_height + 0.2,
                     head_width=arrow_head_width, head_length=arrow_head_length)
        else:
            ax.arrow(center_x, y_pos + box_height + 1.4, 0, -1.2,
                     head_width=arrow_head_width, head_length=arrow_head_length)

        # Draw feedback path (right to left)
        if i < len(denominator_coeffs):
            # Connection from delay to feedback sum
            ax.arrow(center_x - box_width / 2, y_pos + box_height / 2,
                     -1.5 + circle_radius, 0,
                     head_width=arrow_head_width, head_length=arrow_head_length)
            # Coefficient label
            ax.text(center_x - 1.3, y_pos + box_height, f'-{denominator_coeffs[i]}', fontsize=12)
            # Connection from feedback sum to input (left vertical arrows)
            ax.arrow(center_x - 2 , y_pos + box_height,
                     0, 1.2,
                     head_width=arrow_head_width, head_length=arrow_head_length)


        # Draw feedforward path (right to output)
        if i + 1 < len(nomirator_coeffs):
            ax.arrow(center_x + box_width / 2, y_pos + box_height / 2,
                     2.2, 0,
                     head_width=arrow_head_width, head_length=arrow_head_length)
            ax.text(center_x + 1.5, y_pos + box_height, f'{nomirator_coeffs[i + 1]}', fontsize=12)
            # Connection from forward sum to output (right vertical arrows)
            ax.arrow(center_x + 3, y_pos + box_height,
                     0, 1.2,
                     head_width=arrow_head_width, head_length=arrow_head_length)

    # if is_delay_minused: # draw the missing vertical arrows
    #     y_pos = -2 * (i + 1) - 0.3
    #     if is_denominator_max_order is False: # add a right vertical line
    #         # Connection from forward sum to output (right vertical arrows)
    #         ax.arrow(center_x + 3, y_pos + box_height,
    #                  0, 1.2,
    #                  head_width=arrow_head_width, head_length=arrow_head_length)
    #     else:
    #         # Connection from feedback sum to input (left vertical arrows)
    #         ax.arrow(center_x - 2, y_pos + box_height,
    #                  0, 1.2,
    #                  head_width=arrow_head_width, head_length=arrow_head_length)

    # Draw main signal flow
    # Input
    ax.arrow(0, 0, center_x - 2.5, 0,
             head_width=arrow_head_width, head_length=arrow_head_length)
    ax.text(-0.5, 0.3, 'x(n)', fontsize=12)

    # Main path from input sum to output sum
    ax.arrow(center_x - 1.7, 0, 4.2, 0,
             head_width=arrow_head_width, head_length=arrow_head_length)

    # Add b0 coefficient
    ax.text(center_x + 1.5, 0.3, f'{nomirator_coeffs[0]}', fontsize=12)

    # Final output arrow
    ax.arrow(center_x + 3 + circle_radius, 0, 1.5, 0,
             head_width=arrow_head_width, head_length=arrow_head_length)
    ax.text(center_x + 5, 0.3, 'y(n)', fontsize=12)

    plt.title('Direct Form II Filter Structure')
    plt.grid(False)
    plt.show()




# Example usage with different filter orders
# Example 1: Second-order filter
a2 = [0.5, 0.2]
b2 = [1.0, 0.3, 0.1]
draw_direct_form_2(a2, b2)

# Example 2: Fourth-order filter
a4 = [0.4, 0.3, 0.2, 0.1]
b4 = [1.0, 0.5, 0.3, 0.2, 0.1]
draw_direct_form_2(a4, b4)

# Example 3: deno is max and last element is 0
a6 = [0.6, 0.5, 0.4, 0.3, 0.2, 0.0]
b6 = [1.0, 0.6, 0.4, 0.3, 0.2, 0.1]
draw_direct_form_2(a6, b6)

# Example 4: with zero coefficients in the middle
a4_zero = [0.4, 0.0, 0.2, 0.1, 0.0]
b4_zero = [1.0, 0.5, 0.0, 0.2]
draw_direct_form_2(a4_zero, b4_zero)

# Example 4: with zero coefficients in the middle
a4_zero = [0.4, 0.0, 0.2]
b4_zero = [1.0, 0.5, 0.0, 0.2, 0.1]
draw_direct_form_2(a4_zero, b4_zero)

def draw_cascade_form(denominator_coeffs, nomirator_coeffs):
    """
    Draw a Cascade Form filter structure visualization with separate summing junctions
    for both feedforward and feedback paths

    Parameters:
    denominator_coeffs: list of feedback coefficients [a1, a2, ...]
    nomirator_coeffs: list of feedforward coefficients [b0, b1, b2, ...]
    """
    # Create figure and axis with dynamic sizing
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal')

    # Set plot limits
    ax.set_xlim(-2, 10)
    ax.set_ylim(-2, 2)

    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Constants for drawing
    circle_radius = 0.3
    box_width = 0.6
    box_height = 0.6
    arrow_head_width = 0.2
    arrow_head_length = 0.2

    # Center point for the structure
    center_x = 4

    # Draw feedback summing junction
    feedback_sum = Circle((center_x - 2, 0), circle_radius, fill=False)
    ax.add_patch(feedback_sum)
    ax.text(center_x - 2, 0, '+', ha='center', va='center', fontsize=12)

    # Draw output summing junction
    output_sum = Circle((center_x + 3, 0), circle_radius, fill=False)
    ax.add_patch(output_sum)
    ax.text(center_x + 3, 0, '+', ha='center', va='center', fontsize=12)

    # Draw delay element and connections
    y_pos = -0.3

    # Draw delay element (centered)
    z_box = Rectangle((center_x - box_width / 2, y_pos), box_width, box_height, fill=False)
    ax.add_patch(z_box)
    ax.text(center_x - 0.2, y_pos + 0.2, r'$z^{-1}$', fontsize=12)

    # Draw vertical connection from previous level
    ax.arrow(center_x, 0, 0, y_pos + box_height + 0.2,
             head_width=arrow_head_width, head_length=arrow_head_length)

    # Draw feedback path (right to left)
    for i, a in enumerate(denominator_coeffs):
        # Connection from delay to feedback sum
        ax.arrow(center_x - box_width / 2, y_pos + box_height / 2,
                 -1.5 + circle_radius, 0,
                 head_width=arrow_head_width, head_length=arrow_head_length)
        # Coefficient label
        ax.text(center_x - 1.3, y_pos + box_height, f'-{a}', fontsize=12)
        # Connection from feedback sum to input (left vertical arrows)
