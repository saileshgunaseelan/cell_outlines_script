import pandas as pd
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt


"""
This script performs the following tasks:

* Reads cell coordinates from a .csv or .txt file
* Outputs an image displaying the outlines of each cell
* Creates a color gradient based on scaled predicted values

Each complex function is documented with a description above it to guide the user through its execution.
"""


# Displays the outlines of each cell given their coordinates from a .txt file.
def draw_cell_coordinates_from_txt(file_path: str, image_width: int, image_height: int):
    # Creating the image
    cell_outlines = Image.new("RGB", (image_width, image_height), "black")
    draw = ImageDraw.Draw(cell_outlines)

    # Initialize a list to hold cells; each cell contains a list of coordinates (and each coordinate is a tuple).
    cell_data = []
    # Read txt, collect cell and cell's coordinates
    with open(file_path, "r") as file:
        # Read the file's content
        content = file.read()
        # Collect all cells
        cells = content.strip().split("\n")
        # Find x_max, x_min, y_max, and y_min (will be used for cropping)
        x_max = 0
        y_max = 0
        x_min = 0  # x_min and y_min will always remain same
        y_min = 0
        # Process the cell's coordinates
        for current_cell in cells:
            # Create a list of tuples from the coordinates
            cell_coordinates = []
            # Split the coordinates by ',' and iterate over pairs
            current_cell = current_cell.split(",")
            for coordinate in range(0, len(current_cell), 2):
                # Collect x-coordinate
                x_coordinate = int(current_cell[coordinate])
                # Collect y-coordinate
                y_coordinate = int(current_cell[coordinate + 1])
                if x_coordinate > x_max:
                    x_max = x_coordinate
                if y_coordinate > y_max:
                    y_max = y_coordinate
                # Append tuple to cell's coordinates
                cell_coordinates.append((x_coordinate, y_coordinate))
            # Append list of tuples into cell_data (the list of tuples represents the cell)
            cell_data.append(cell_coordinates)

        # Remove cells that will be cropped by x_max, x_min, y_max, and y_min
        cropped = False
        for cell in cell_data:
            for cell_coordinate in cell:
                if cell_coordinate[0] == x_max or cell_coordinate[0] == x_min:
                    cropped = True
                if cell_coordinate[1] == y_max or cell_coordinate[0] == y_min:
                    cropped = True
            if cropped is True:
                cropped = False
                cell_data.remove(cell)

    index = 0
    # Drawing cell's (x, y) coordinates
    for cell in cell_data:
        index = index + 1
        for cell_coordinate in cell:
            # Drawing cell's (x, y) coordinates®
            draw.point((cell_coordinate[0], cell_coordinate[1]), "white")
            # Drawing lines between cell's consecutive points
            point1 = cell_coordinate[0]
            point2 = cell_coordinate[1]
            draw.line((point1, point2), fill="white", width=3)
        # Debugging
        # print("Drawing cell #" + str(index))

    # Resize image (based on x_max, x_min, y_max, y_min)
    cell_outlines = cell_outlines.crop((x_min, y_min, x_max, y_max))

    # Save and display
    cell_outlines.save(
        "images/cell_outlines_from_txt.png"
    )  # Rename the image as necessary
    cell_outlines.show()


# Displays the outlines of each cell given their coordinates from a .csv file.
# Users can generate a color gradient based on each cell's scaled predicted value.
def draw_cell_coordinates_from_csv(file_path: str, image_width: int, image_height: int):
    # Creating the image
    cell_outlines = Image.new("RGB", (image_width, image_height), "black")
    draw = ImageDraw.Draw(cell_outlines)

    # Reading .csv file
    pre_cyto_outlines_df = pd.read_csv(file_path)

    # Load predicted values
    predicted_value_excel = load_predicted_values(
        "csv_data/predicted value_unicell and multicell.xlsx"
    )

    # Load palette and font, prepare image for eventual coloring
    color_palette = load_gradient_and_bar(cell_outlines, image_width, image_height)
    font = load_font()

    # Creating a nested for loop that outlines each cell.
    # The outer loop iterates over the columns. Every two adjacent columns represent one cell.
    for cell in range(1, (len(pre_cyto_outlines_df.columns) // 2) + 1):
        # Assigning column coordinates based on cell
        # cell 1: (X1, Y1)
        # cell 2: (X2, Y2)...
        x_column = "X" + str(cell)
        y_column = "Y" + str(cell)

        # Creating an empty list to store cell's (x, y) coordinates from .csv file
        cell_coordinates = []

        # Initializing skip_cell variable to False.
        # This variable will be used when cells have nonzero integers past row 400.
        skip_cell = False

        # Iterating through columns X[cell#] and Y[cell#] to collect cell's (x, y) coordinates
        if (
            pre_cyto_outlines_df.at[0, x_column] != 0
            and pre_cyto_outlines_df.at[0, y_column] != 0
        ):
            for row_index in range(0, len(pre_cyto_outlines_df)):
                x_coordinate = pre_cyto_outlines_df.at[row_index, x_column]
                y_coordinate = pre_cyto_outlines_df.at[row_index, y_column]
                # Terminate for loop when the coordinate is (0, 0).
                if x_coordinate == 0 and y_coordinate == 0:
                    break
                # Checks if cell has nonzero integers past row 400.
                if row_index > 400 and x_coordinate != 0 and y_coordinate != 0:
                    # Cell has nonzero integer past row 400 therefore variable skip_cell is assigned to True.
                    skip_cell = True
                    break
                # Append (x, y) coordinate in current row to cell_coordinates list
                cell_coordinates.append((x_coordinate, y_coordinate))

            # If skip_cell is True, the cell had nonzero integers past row 400.
            # As a result, the cell is skipped and its outline is not drawn.
            if skip_cell:
                # Identifying cells that have nonzero integers past row 400
                # Debugging
                # print("Identified cell #" + str(cell))
                continue

            # Removing cells that are not mentioned in predicted_value_excel
            for index, row in predicted_value_excel.iterrows():
                if cell == row[" order"]:
                    skip_cell = True

            if not skip_cell:
                continue

            # Drawing cell's (x, y) coordinates
            for (x, y) in cell_coordinates:
                draw.point((x, y), "white")
            # Drawing lines between cell's consecutive points
            for point in range(len(cell_coordinates) - 1):
                point1 = cell_coordinates[point]
                point2 = cell_coordinates[point + 1]
                draw.line((point1, point2), fill="white", width=3)
            # Debugging
            print("Drawing cell #" + str(cell))

            # Gradient
            color_cell(
                draw, color_palette, cell, cell_coordinates, predicted_value_excel
            )

            # Labeling
            label_cell(draw, font, cell, cell_coordinates)

    # Save and display
    cell_outlines.save(
        "images/cell_outlines_from_csv.png"
    )  # Rename the image as necessary
    cell_outlines.show()


def load_predicted_values(file_path: str):
    # Loading multicell into a DataFrame
    multicell_file_path = file_path

    # Modify DataFrame as necessary
    multicell_sheet_excel = pd.read_excel(multicell_file_path, sheet_name="multi cell")
    # Identifying the minimum and maximum values of the predicted cyto column
    minimum_predicted_cyto = multicell_sheet_excel["predicted cyto"].min()
    maximum_predicted_cyto = multicell_sheet_excel["predicted cyto"].max()
    # Adding the column 'scaled predicted cyto' to DataFrame which scales 'predicted cyto' to the range (0, 1).
    multicell_sheet_excel["scaled predicted cyto"] = (
        multicell_sheet_excel["predicted cyto"] - minimum_predicted_cyto
    ) / (maximum_predicted_cyto - minimum_predicted_cyto)

    # Another example of loading predicted values (unicell)
    # # Loading unicell into a DataFrame
    # unicell_file_path = file_path

    # # Modify DataFrame as necessary
    # unicell_sheet_excel = pd.read_excel(unicell_file_path, sheet_name='unicell')
    # # Identifying the minimum and maximum values of the predicted nuc column
    # minimum_predicted_nuc = unicell_sheet_excel['predicted nuc'].min()
    # maximum_predicted_nuc = unicell_sheet_excel['predicted nuc'].max()
    # # Adding the column 'scaled predicted nuc' to DataFrame which scales 'predicted nuc' to the range (0, 1).
    # unicell_sheet_excel['scaled predicted nuc'] = (unicell_sheet_excel['predicted nuc'] - minimum_predicted_nuc) / (maximum_predicted_nuc - minimum_predicted_nuc)

    return multicell_sheet_excel


def load_gradient_and_bar(cell_outlines: Image, image_width: int, image_height: int):
    # Creating a colormap object
    cmap_name = "Blues"
    num_shades = 50
    cmap = plt.cm.get_cmap(cmap_name, num_shades)
    # Generating a list of colors
    color_palette = [cmap(i) for i in np.linspace(0, 1, num_shades)]

    # Color bar's size within image
    color_bar_width = 1000  # width
    color_bar_height = 65  # height
    # Color bar's position within image
    color_bar_x_coordinate = (
        image_width - color_bar_width
    ) // 2  # x-coordinate for placing color bar
    color_bar_y_coordinate = (
        image_height - color_bar_height
    ) - 200  # y-coordinate for placing color bar
    color_bar_position = (
        color_bar_x_coordinate,
        color_bar_y_coordinate,
    )  # top-left corner of color bar
    # Creating color bar using matplotlib
    color_bar = np.linspace(0, 1, num_shades)
    color_bar = np.vstack((color_bar, color_bar))
    # Plotting the color bar
    plt.imshow(color_bar, aspect="auto", cmap=cmap_name)
    # plt.axis("off")  # turns off axis
    plt.savefig(
        "/tmp/color_bar.png", bbox_inches="tight", transparent=True, pad_inches=0
    )  # saving color bar as PNG
    plt.close()
    # Loading the color bar as PIL
    color_bar_image = Image.open("/tmp/color_bar.png")
    # Pasting the color bar onto the existing image
    cell_outlines.paste(
        color_bar_image.resize((color_bar_width, color_bar_height)), color_bar_position
    )

    return color_palette


# Assigns a color to the specified cell based on the scaled predicted value
# Repeat assignment for all cells (shown in draw_cell_coordinates_from_csv)
def color_cell(
    draw: ImageDraw,
    color_palette: list,
    cell: int,
    cell_coordinates: list,
    predicted_value_excel: str,
):
    # Color cell based on scaled predicted value (only if the cell has a predicted deformation value)
    for index, row in predicted_value_excel.iterrows():
        if cell == row[" order"]:
            # Interpolate color using scaled predicted value
            interpolated_color_index = int(
                row["scaled predicted cyto"] * (len(color_palette) - 1)
            )
            # Retrieving color from color palette using the interpolated_color_index
            # Make sure each RGB value is a tuple of integers
            color = color_palette[interpolated_color_index]
            color = tuple(int(component * 255) for component in color)
            # Color :)
            draw.polygon(cell_coordinates, fill=color)


# Users can download their preferred font in .tff format.
def load_font():
    font_path = "font/times_new_roman.ttf"
    font_size = 15
    font = ImageFont.truetype(font_path, font_size)

    return font


def label_cell(draw: ImageDraw, font: ImageFont, cell: int, cell_coordinates: list):
    # Labeling
    # Calculating the centroid of the cell
    centroid_x = (sum(x for (x, y) in cell_coordinates)) // (len(cell_coordinates))
    centroid_y = (sum(y for (x, y) in cell_coordinates)) // (len(cell_coordinates))
    # Determining the width and height of the text
    text_width, text_height = font.getsize(str(cell))
    # The position of the cell's number is based on the centroid of the cell and the width and height of the text.
    number_position = (centroid_x - (text_width / 2), centroid_y - (text_height / 2))
    # Labeling each cell with its respective number
    draw.text(number_position, str(cell), font=font, fill="white")


def main():
    # Creating cell outline from .txt file
    draw_cell_coordinates_from_txt(
        "txt_data/nucleus_20X_zstackEDF - Cropped 1_cp_outlines.txt", 5000, 5000
    )

    # Creating cell outline from .csv file + color gradient + labeling
    draw_cell_coordinates_from_csv("csv_data/pre_cyto_outlines.csv", 2075, 2200)


if __name__ == "__main__":
    main()
