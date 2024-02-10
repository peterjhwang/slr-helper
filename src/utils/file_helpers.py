import csv


def save_tuples_as_csv(tuple_list, columns, filename):
    """
    Save a list of tuples to a CSV file.

    Parameters:
    - tuple_list: List[Tuple]. A list of tuples to be saved.
    - filename: str. The name of the file where the data will be saved.
    """
    # Open the file in write mode
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        # Write the header
        writer.writerow(columns)
        # Write each tuple to the file
        for tup in tuple_list:
            writer.writerow(tup)

    print(f"Data saved to {filename} successfully.")


def read_csv_to_list_of_lists(filename):
    """
    Read a CSV file into a list of lists.

    Parameters:
    - filename: str. The name of the file to be read.

    Returns:
    - List[List[str]]. A list of lists, where each inner list represents a row in the CSV file.
    """
    with open(filename, "r", newline="") as file:
        reader = csv.reader(file)

        # Read all rows into a list of lists
        list_of_lists = list(reader)

    return list_of_lists
