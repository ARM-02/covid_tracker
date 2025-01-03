from graphics import GraphWin, Rectangle, Text, Point, Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Load dataset once at the beginning
DATASET = pd.read_csv('clean_covid_data.csv')


# Define reusable functions
def create_button(win, x1, y1, x2, y2, text,color="#4e7997" ):
    rect = Rectangle(Point(x1, y1), Point(x2, y2))
    rect.setFill(color)
    rect.draw(win)
    label = Text(rect.getCenter(), text)
    label.setSize(17)
    label.setTextColor('black')
    label.setStyle('bold')
    label.draw(win)
    return rect, label


def is_button_clicked(click_point, button_rect):
    x1 = button_rect.getP1().getX()
    y1 = button_rect.getP1().getY()
    x2 = button_rect.getP2().getX()
    y2 = button_rect.getP2().getY()
    return x1 <= click_point.getX() <= x2 and y1 <= click_point.getY() <= y2


def undraw_elements(elements):
    for element in elements:
        element.undraw()



# Define welcome page
def welcome_page(win):
    """Displays a welcome page with a message and a continue button."""
    win.setBackground("white")
    title1 = Text(Point(400, 300), "Welcome to the Covid Tracker")
    title1.setSize(30)
    title1.setStyle('bold')
    title1.setTextColor('black')
    title1.draw(win)

    title2 = Text(Point(400, 350), "Visualize the effect of pre-existing conditions on COVID-19 outcomes")
    title2.setSize(20)
    title2.setStyle('bold')
    title2.draw(win)

    title3 = Text(Point(400, 500), "Click continue to create your graphs")
    title3.setSize(20)
    title3.setStyle('bold')
    title3.draw(win)


    elements = [title1,title2,title3]

    continue_button, continue_label = create_button(win, 320, 550, 480, 614, "Continue", "#fdbd22")
    elements.extend([continue_button, continue_label])

    return continue_button, elements


# Define dataset description page
def dataset_description_page(win):
    """Displays dataset description with a continue button."""
    win.setBackground("white")
    title = Text(Point(400, 80), "Dataset Description")
    title.setSize(20)
    title.setStyle('bold')
    title.draw(win)

    # Add a multiline description
    description_text = (
        "This dataset, provided by the Mexican government,\n contains anonymized data on over 1 million COVID-19 patients.\n\n"
        "It includes 21 features that capture key patient information,\n including demographics, medical history, and COVID-19 outcomes.\n\n"
        "Key Information:\n\n"
        "- Timeframe: Data spans from 2020 to 2021.\n\n"
        "- Age Ranges: \n Children(0-12)-Young Adults(13-24)-Adults(25-64)-Older Adults(65-74)-Elderly(75+)\n\n"
        "- Selected Patient Variables:              \n"
        "   1. Diabetes: Whether the patient has a history of diabetes.\n\n"
        "   2. Chronic Renal Disease: Whether the patient has chronic kidney disease.\n\n"
        "   3. Asthma: Whether the patient has a history of asthma.\n\n"
        "   4. Cardiovascular Disease: Whether the patient has a history of heart or vascular diseases.\n\n\n"
        "Exploring the relationships between these variables and COVID-19 outcomes \n can help inform public health strategies and enhance our understanding of the virus's behavior."
    )
    # Description 1
    description = Text(Point(400, 350), description_text)
    description.setSize(18)

    # Draw descriptions
    description.draw(win)

    # Initialize elements list
    elements = [title, description]

    # Add the continue button
    continue_button, continue_label = create_button(win, 320, 680, 480, 744, "Continue", "#fdbd22")
    elements.extend([continue_button, continue_label])

    return continue_button, elements

# Define home page
def home_page(win):
    """Displays the home page with graph type selection."""
    title = Text(Point(400, 80), "Select Desired Graph")
    title.setSize(20)
    title.draw(win)
    win.setBackground("white")

    buttons = []
    elements = [title]  # Track all elements to undraw later
    button_texts = ["Histogram", "Pie Chart", "Bar Plot", "Dataset Description"]
    for i, text in enumerate(button_texts):
        button, label = create_button(win, 240, 160 + i * 140, 560, 240 + i * 140, text)
        buttons.append((button, text))  # Store button rectangle and its label text
        elements.extend([button, label])
    return buttons, elements


def variable_selection_page(win, variables, selected_graph_type):
    """Displays the variable selection page."""
    title = Text(Point(400, 40), "Filters")
    title.setSize(20)
    title.draw(win)

    elements = [title]

    # Add the variable selection text based on chart type
    if selected_graph_type == "histogram":
        select_var_text = Text(Point(400, 83), "Select one, or multiple, variables to analyze")
    else:  # barplot or pie chart
        select_var_text = Text(Point(400, 83), "Select one variable to analyze")

    select_var_text.setSize(18)
    select_var_text.draw(win)
    elements.append(select_var_text)

    # Variable selection buttons
    var_buttons = []
    y_start = 120
    for i, var in enumerate(variables):
        button, label = create_button(win, 240, y_start + i * 80, 560, y_start + 64 + i * 80, var)
        var_buttons.append({"button": button, "variable": var, "selected": False})
        elements.extend([button, label])

    # Confirm button
    confirm_button, confirm_label = create_button(win, 320, y_start + len(variables) * 80 + 40, 480,
                                                  y_start + len(variables) * 80 + 104, "Confirm", "#fdbd22")
    elements.append(confirm_button)
    elements.append(confirm_label)

    return var_buttons, confirm_button, elements

# Define graph display page
def graph_display_page(win, graph_type, selected_variables):
    title = Text(Point(400, 30), f"{graph_type.title()}")
    title.setSize(20)
    title.draw(win)

    elements = [title]

    # Navigation buttons
    back_to_variables_button, back_to_variables_label = create_button(win, 100, 680, 300, 760, "Back to Variables",
                                                                      "#4e7997")  # Adjusted button positions and sizes
    back_to_home_button, back_to_home_label = create_button(win, 500, 680, 700, 760, "Back to Home", "#fdbd22")
    elements.extend([back_to_variables_button, back_to_variables_label, back_to_home_button, back_to_home_label])

    return elements, back_to_variables_button, back_to_home_button

def generate_bar_plot(win, dataset, selected_characteristic, elements):
    """Generates a bar plot for patients with the selected characteristic by age groups."""

    # Define age groups
    infants_and_children = dataset[dataset['AGE'] <= 12]  # (0-12)
    adolescents_and_young_adults = dataset[(dataset['AGE'] > 12) & (dataset['AGE'] <= 24)]  # (13-24)
    adults = dataset[(dataset['AGE'] > 24) & (dataset['AGE'] <= 64)]  # (25-64)
    older_adults = dataset[(dataset['AGE'] > 64) & (dataset['AGE'] <= 74)]  # (65-74)
    elderly = dataset[dataset['AGE'] > 74]  # 75+

    # Add age groups to a dictionary
    age_groups = {
        "Children": infants_and_children,
        "Young Adults": adolescents_and_young_adults,
        "Adults": adults,
        "Older Adults": older_adults,
        "Elderly": elderly
    }

    # Get total counts and deaths for each age group
    totals = []
    deaths = []
    proportions = []

    for age_group, group_data in age_groups.items():
        has_characteristic = group_data[group_data[selected_characteristic] == 1]  # 1 == has the characteristic
        total = len(has_characteristic)  # Total count with the characteristic
        died = has_characteristic['DATE_DIED'].notnull().sum()  # Count of deaths
        survived = total - died  # Count of survivors

        totals.append(total)
        deaths.append(died)
        proportions.append({
            'Age Group': age_group,
            'Total': total,
            'Survived': survived,
            'Died': died,
            'Survived %': survived / total * 100 if total > 0 else 0,
            'Died %': died / total * 100 if total > 0 else 0
        })

    # Define labels and weights for the bar plot
    labels = [p['Age Group'] for p in proportions]
    survived = [p['Survived'] for p in proportions]
    died = [p['Died'] for p in proportions]

    # Create the stacked bar plot
    plt.figure(figsize=(7, 6), facecolor='white')  # Adjust figure size for better scaling
    width = 0.5
    bottom = np.zeros(len(labels))  # Initialize bottom values for stacking

    # Assign Colors and Hatches to bars
    colors = {
        'Died': '#ee423a',
        'Survived': '#1e82c3',
    }
    hatches = {
        'Died': 'o',
        'Survived': '+',
    }

    # Add bars for each category
    for key, weight_count in zip(['Died', 'Survived'], [died, survived]):
        plt.bar(labels, weight_count, width, label=key, bottom=bottom,
                color=colors[key], hatch=hatches[key], edgecolor='black')
        bottom += weight_count  # Update bottom for stacking

    # Add title and labels
    plt.title(f"Patients with {selected_characteristic} by Combined Age Groups", fontsize=14)
    plt.ylabel("Number of Patients", fontsize=12)
    plt.xticks(rotation=45, fontsize=10)
    plt.yticks(fontsize=10)

    # Legend for Colors and Patterns
    color_pattern_legend = [
        mpatches.Patch(facecolor=colors['Died'], hatch=hatches['Died'], edgecolor='black', label="Died"),
        mpatches.Patch(facecolor=colors['Survived'], hatch=hatches['Survived'], edgecolor='black', label="Survived")
    ]
    legend1 = plt.legend(handles=color_pattern_legend, loc="upper right", fontsize=10,
                         title="Legend: Colors & Patterns", bbox_to_anchor=(1, 1))

    # Add the first legend to the plot
    plt.gca().add_artist(legend1)

    # Map long names to abbreviations for legend
    name_mapping = {
        "Young Adults": "YA",
        "Older Adults": "OA",
    }

    # Proportions as a Secondary Legend
    proportion_text = "Survived vs Died\n" + "\n".join([
        f"{name_mapping.get(p['Age Group'], p['Age Group'])}: {p['Survived %']:.1f}% vs {p['Died %']:.1f}% "
        for p in proportions
    ])
    props = dict(boxstyle="round,pad=0.3", edgecolor="black", facecolor="white")
    plt.gca().text(1.02, 1, proportion_text, transform=plt.gca().transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)

    # Adjust layout
    plt.subplots_adjust(right=0.8, top=0.9)  # Make space for legends

    # Save and display the plot
    plt.savefig("bar_plot_with_two_legends.png", bbox_inches="tight")
    plt.close()

    img = Image(Point(400, 350), "bar_plot_with_two_legends.png")
    img.draw(win)
    elements.append(img)

def generate_histogram(win, dataset, filters, elements):
    """Generates a histogram for the dataset and selected filters."""
    # Undraw any existing graph elements before drawing a new one
    graph_elements = [el for el in elements if isinstance(el, Image)]  # Find existing graph images
    undraw_elements(graph_elements)
    elements[:] = [el for el in elements if el not in graph_elements]  # Remove undrawn graph images from elements

    # Filter and prepare the data
    dataset = filter_dataset(dataset, filters)

    # Ensure DATE_DIED is a datetime column
    dataset['DATE_DIED'] = pd.to_datetime(dataset['DATE_DIED'], errors='coerce')

    # Extract the month from DATE_DIED
    final = dataset['DATE_DIED'].dt.month

    # Create the histogram
    plt.figure(figsize=(7, 5), facecolor='white')
    bins = np.arange(1, 14) - 0.5  # 12 bins for months
    counts, edges, _ = plt.hist(final.dropna(), bins=bins, histtype='stepfilled', align='mid',
                                edgecolor='black', color='#1e82c3', label='Deaths by Month')
    for count, edge_left, edge_right in zip(counts, edges[:-1], edges[1:]):
        x = (edge_left + edge_right) / 2  # Midpoint of the bin
        y = count
        plt.text(x, y, f'{int(count)}', ha='center', va='bottom', fontsize=8)

    filters_text = ", ".join(filters) if filters else "No Filters"
    plt.title(f'Histogram ({filters_text})')
    plt.xlabel('Month')
    plt.ylabel('Number of Deaths')
    plt.xticks(ticks=np.arange(1, 13), labels=["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
    plt.legend()

    # Save and display the histogram
    plt.savefig("histogram.png")
    plt.close()

    # Draw the new graph
    img = Image(Point(400, 300), "histogram.png")
    img.draw(win)
    elements.append(img)  # Add the new graph image to the elements list

#generate Pie Chart
def generate_pie_chart(win, dataset, variable, elements):
    """Generates and displays two pie charts for a selected variable."""
    # Ensure the variable has expected values (e.g., 1 and 2 for "Had it" and "Did not have it")
    filtered_dataset = dataset[dataset[variable].isin([1, 2])]

    # Split into 'dead' and 'alive' groups
    dead = filtered_dataset[filtered_dataset['DATE_DIED'].notna()]
    alive = filtered_dataset[filtered_dataset['DATE_DIED'].isna()]

    # Count occurrences of the selected variable in each group
    dead_counts = dead[variable].value_counts(sort=False)
    alive_counts = alive[variable].value_counts(sort=False)

    # Define labels for the pie chart
    labels = {1: 'Had it', 2: 'Did not have it'}
    dead_labels = [labels.get(i, f"Other ({i})") for i in dead_counts.index]
    alive_labels = [labels.get(i, f"Other ({i})") for i in alive_counts.index]

    # Ensure both groups have the same categories for consistency in pie charts
    all_labels = sorted(set(dead_counts.index).union(set(alive_counts.index)))
    dead_counts = dead_counts.reindex(all_labels, fill_value=0)
    alive_counts = alive_counts.reindex(all_labels, fill_value=0)
    legend_labels = [labels.get(i, f"Other ({i})") for i in all_labels]

    # Create the pie chart
    plt.figure(figsize=(7, 5))
    plt.suptitle(f"Pie Chart for {variable}", fontsize=16)

    # Dead Pie Chart
    plt.subplot(121)
    patches_dead, _, _ = plt.pie(dead_counts, labels=['' for _ in dead_counts], autopct='%1.1f%%',
                                 colors=["#1e82c3", "#ee423a"], hatch=['o', '+'], pctdistance=1.18)
    plt.title('Died')

    # Alive Pie Chart
    plt.subplot(122)
    patches_alive, _, _ = plt.pie(alive_counts, labels=['' for _ in alive_counts], autopct='%1.1f%%',
                                  colors=["#1e82c3", "#ee423a"], hatch=['o', '+'], pctdistance=1.20)
    plt.title('Survived')

    # Add the legend with the custom patches
    combined_patches = patches_dead[:len(legend_labels)]
    plt.legend(combined_patches, legend_labels, title="Legend",
               loc="upper right", bbox_to_anchor=(0, -0.2), ncol=1)

    # Save and display the chart
    plt.tight_layout()
    plt.savefig("pie_chart.png")
    plt.close()

    img = Image(Point(400, 350), "pie_chart.png")
    img.draw(win)
    elements.append(img)


def filter_deaths(dataset):
    """Filters the dataset to include only rows where a death is recorded."""
    dataset['DATE_DIED'] = pd.to_datetime(dataset['DATE_DIED'], format='%d/%m/%Y', errors='coerce')
    dataset = dataset[dataset['DATE_DIED'].notna()]
    return dataset


def filter_dataset(dataset, selected_variables):
    """Filters the dataset based on selected variables."""
    for var in selected_variables:
        dataset = dataset[dataset[var] != 2]
    return dataset


def main():
    variables = ["DIABETES", "RENAL_CHRONIC", "ASTHMA", "CARDIOVASCULAR"]

    win = GraphWin("Graph Interface", 800, 800)
    current_page = "welcome"
    elements = []

    while True:
        if current_page == "welcome":
            undraw_elements(elements)
            continue_button, elements = welcome_page(win)
            click = win.getMouse()
            if is_button_clicked(click, continue_button):
                current_page = "dataset_description"

        elif current_page == "dataset_description":
            undraw_elements(elements)
            continue_button, elements = dataset_description_page(win)
            click = win.getMouse()
            if is_button_clicked(click, continue_button):
                current_page = "home"

        elif current_page == "home":
            undraw_elements(elements)
            buttons, elements = home_page(win)
            click = win.getMouse()
            for button, graph_type in buttons:
                if is_button_clicked(click, button):
                    if graph_type == "Dataset Description":
                        current_page = "dataset_description"
                    else:
                        selected_graph_type = graph_type.lower()
                        single_selection = selected_graph_type in ["pie chart", "bar plot"]
                        current_page = "variable_selection"
                    break

        elif current_page == "variable_selection":
            undraw_elements(elements)
            var_buttons, confirm_button, elements = variable_selection_page(win, variables, selected_graph_type)

            selected_variables = []

            while True:
                click = win.getMouse()

                # Handle variable selection (single or multiple selection)
                for var_data in var_buttons:
                    if is_button_clicked(click, var_data["button"]):
                        if single_selection:
                            # If single selection is enabled, deselect others
                            for other_var in var_buttons:
                                if other_var != var_data:
                                    other_var["selected"] = False
                                    other_var["button"].setFill("#4e7997")
                        var_data["selected"] = not var_data["selected"]
                        var_data["button"].setFill("#aad4d8" if var_data["selected"] else "#4e7997")
                        selected_variables = [v["variable"] for v in var_buttons if v["selected"]]

                # Confirm button
                if is_button_clicked(click, confirm_button) and selected_variables:
                    current_page = "graph_display"
                    break

        elif current_page == "graph_display":
            undraw_elements(elements)

            # Load the graph display page
            elements, back_to_variables_button, back_to_home_button = graph_display_page(win, selected_graph_type,
                                                                                         selected_variables)

            # Generate the selected graph and ensure it is added to the elements list
            if selected_graph_type == "histogram":
                generate_histogram(win, DATASET, selected_variables, elements)

                variable_buttons = []
                for i, var in enumerate(variables):
                    button, label = create_button(win, 60 + i * (160 + 20), 580, 230 + i * (160 + 20), 620, var)
                    variable_buttons.append({"button": button, "variable": var, "selected": False})
                    elements.extend([button, label])

                confirm_button, confirm_label = create_button(win, 320, 640, 480, 680, "Confirm", "#fdbd22")
                elements.extend([confirm_button, confirm_label])

                while True:
                    click = win.getMouse()

                    # Handle variable selection
                    for var_data in variable_buttons:
                        if is_button_clicked(click, var_data["button"]):
                            var_data["selected"] = not var_data["selected"]
                            var_data["button"].setFill("#aad4d8" if var_data["selected"] else "#4e7997")
                            selected_variables = [v["variable"] for v in variable_buttons if v["selected"]]

                    if is_button_clicked(click, confirm_button) and selected_variables:
                        generate_histogram(win, DATASET, selected_variables, elements)

                    if is_button_clicked(click, back_to_variables_button):
                        current_page = "variable_selection"
                        break

                    elif is_button_clicked(click, back_to_home_button):
                        current_page = "home"
                        break

            elif selected_graph_type == "pie chart":
                generate_pie_chart(win, DATASET, selected_variables[0], elements)

                while True:
                    click = win.getMouse()

                    if is_button_clicked(click, back_to_variables_button):
                        current_page = "variable_selection"
                        break

                    elif is_button_clicked(click, back_to_home_button):
                        current_page = "home"
                        break

            elif selected_graph_type == "bar plot":
                generate_bar_plot(win, DATASET, selected_variables[0], elements)

                while True:
                    click = win.getMouse()

                    if is_button_clicked(click, back_to_variables_button):
                        current_page = "variable_selection"
                        break

                    elif is_button_clicked(click, back_to_home_button):
                        current_page = "home"
                        break


main()