# Module: RCSA Scheduler
# Author: Shantanu Jain
# Date: Aug 15, 2023
# Description: This module provides functions to generate schedules for members based on their 
# availabilitiy and prefrences.

import pandas as pd
import numpy as np
import heapq
import glob
import re
import os



def insert_name_by_preference(names_list, name, preference):
    """Insert a name into a list based on preference order."""
    preference_order = {
        'B1': 0, 'A1': 1, 'A2': 2, 'B2': 3, 'B': 4,
        'A': 5, 'D1': 6, 'D2': 7, 'N': 8
    }
    
    insert_index = next((index for index, (_, pref) in enumerate(names_list)
                         if preference_order[pref] > preference_order[preference]), len(names_list))
    
    names_list.insert(insert_index, (name, preference))
    
    return names_list

def find_total_available_hours(df):
    """Find the total number of hours a person is available each week."""
    name_counts = {}
    for cell_list in df.values.flatten():
        for name, _ in cell_list:
            name_counts[name] = name_counts.get(name, 0) + 1
    return name_counts


columns = ["9-10AM","10-11AM", "11-12PM", "12-1PM", "1-2PM", "2-3PM", "3-4PM", "4-5PM", "5-6PM", "6-7PM","7-8PM"]
labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
data = [[[] for _ in range(len(labels))] for _ in range(len(columns))]
availability_df = pd.DataFrame(data, columns=labels, index=columns)
people_dict = {}

def process_all_files(uploaded_files):
    """
    Process all Excel files in the 'xlsx_files' directory to create an availability matrix for individuals.

    Returns:
    - availability_df (pd.DataFrame): A dataframe containing information about who is available for each slot.
    - people_dict (dict): A dictionary where keys are the names of the people and values are the number of hours they can be assigned.

    Note:
    - Each file is expected to have a specific format.
    - The first column of each file represents the name of the individual.
    - Each cell in the Excel sheet can have either 'B' or 'A' followed by optional 'Y'.
    - If there are two digits present in the cell value after 'B' or 'A', the last one will be removed.
    - A person can be available for 3 hours by default.
    """
    data = [[[] for _ in range(len(labels))] for _ in range(len(columns))]
    availability_df = pd.DataFrame(data, columns=labels, index=columns)
    
    # Modify the path to look in the 'xlsx_files' directory
    path_to_scan = os.path.join(os.getcwd(), 'xlsx_files', '*.xlsx')
    people_dict = {}
    '''
    for filename in glob.glob(path_to_scan):
        try:
            df = pd.read_excel(filename, engine='openpyxl')
        except Exception as e:
            print(f"Error reading file {filename}. Skipping it. Details: {str(e)}")
            continue
    '''
    for uploaded_file in uploaded_files:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        except Exception as e:
            print(f"Error reading file {uploaded_file.name}. Skipping it. Details: {str(e)}")
            continue
        try:
            person_name = df.columns[0].strip()
        except IndexError:
            print(f"Error processing columns in {uploaded_file.name}. Perhaps the file is empty or not in the expected format. Skipping it.")
            continue

        # Validate if the dataframe has expected columns and rows
        if df.shape[0] < len(columns) or df.shape[1] < len(labels):
            print(f"Unexpected shape in file {uploaded_file.name}. Expected at least {len(columns)} rows and {len(labels) + 1} columns. Skipping it.")
            continue
        
        people_dict[person_name] = 3  # Sets 3 hours to each person

        for col in range(len(labels)):
            for row in range(len(columns)):
                cell_val = str(df.iloc[row, col + 1])

                if "B" in cell_val or "A" in cell_val:
                    cell_val = cell_val.replace('Y', '')  # removes Y from any string.
                    cell_val = re.sub(r'(?<=\d)\d$', '', cell_val)  # removes last digit if two digits are present.
                    try:
                        availability_df.iloc[row, col] = insert_name_by_preference(availability_df.iloc[row, col], person_name, cell_val)
                    except Exception as e:
                        print(f"Error inserting name by preference for file: {uploaded_file.name} at row {row} and column {col}. Details: {str(e)}")
    return availability_df, people_dict

#Display results
#print(find_total_available_hours(availability_df))
#print(availability_df)
#print(people_dict)

#Version 8/27/2023 (Latest)

# Assuming availibility_df and people_dict are already defined in code

availability_hours = find_total_available_hours(availability_df)

# Convert availability_hours into a heap structure
availability_heap = [(-hours, person) for person, hours in availability_hours.items()]
heapq.heapify(availability_heap)


# Function to check if a cell in finalized_df is empty
def is_cell_empty(row, col, df):
    """Check if a cell in the dataframe is empty."""
    cell_value = df.iloc[row, col]
    if isinstance(cell_value, list):
        return not bool(cell_value)
    else:
        return pd.isna(cell_value)


# Function to find person with least total hours from a given list of tuples
def find_least_hours(persons):
    """Find the person with the least total available hours from a list."""
    least_hours = float('inf')
    selected_person = None

    for person in persons:
        name = person[0]
        hours = availability_hours.get(name, 0)
        if hours < least_hours:
            selected_person = name
            least_hours = hours

    return selected_person

def all_slots_filled(df):
    """Check if all slots in the dataframe have been filled."""
    """
    Determine if all time slots in the provided schedule dataframe are filled.

    Parameters:
    - df (pd.DataFrame): The dataframe representing the schedule.

    Returns:
    - bool: Returns True if all slots in the dataframe are filled, otherwise False.

    Note:
    - The function checks for any NaN (not-a-number) values in the dataframe. If there are any, it means not all slots are filled.
    """
    return not df.isna().any().any()

def update_person_availability(person_to_remove):
    """Update the availability dataframe by removing a person."""
    """
    Update the availability dataframe by excluding a specific person from all slots.

    Parameters:
    - person_to_remove (Any): The identifier of the person to be removed from the availability dataframe.

    Note:
    - This function iterates through all the slots in the availability dataframe.
    - For each slot, it filters out the person_to_remove from the list of available people.
    """
    for row in range(availibility_df.shape[0]):
        for col in range(availibility_df.shape[1]):
            availability_df.iloc[row, col] = [p for p in availability_df.iloc[row, col] if p != person_to_remove]


# Modify the logic for removing the assigned person from the entire availability matrix
def remove_person_from_availability(person_to_remove, availability_df):
    """Remove a person from the availability dataframe if they've been fully assigned."""
    """
    Remove a person from the availability dataframe if they have been completely assigned to their maximum slots.

    Parameters:
    - person_to_remove (Any): The identifier of the person to be removed.
    - availability_df (pd.DataFrame): The dataframe containing information about who is available for each slot.

    Note:
    - Before removal, the function checks if the person has been fully assigned to all their possible hours.
    - If they have, the function iterates through the entire availability dataframe.
    - For each slot, it filters out the person_to_remove from the list of available people.
    """
    if people_dict[person_to_remove] == 0:
        for row in range(availability_df.shape[0]):
            for col in range(availability_df.shape[1]):
                availability_df.iloc[row, col] = [p for p in availability_df.iloc[row, col] if p[0] != person_to_remove]

def fill_cells_by_count(count, finalized_df):
    """Fill the finalized dataframe cells based on people count availability."""
    """
    Fill the slots in the finalized dataframe where the number of available people matches the specified count.

    Parameters:
    - count (int): The number of available people for a specific time slot.
    - finalized_df (pd.DataFrame): The dataframe representing the schedule.

    Returns:
    - bool: Returns True if any changes were made to the finalized_df during this function call, otherwise False.

    Steps:
    1. The function initially assumes that no changes have been made.
    2. It then checks which cells in the finalized dataframe need to be filled based on the count provided.
    3. For each of these cells, it fetches the list of available people.
    4. If the number of available people matches the count, it pops the person with the least availability hours from the heap.
    5. If this person is available for that slot and has not yet been assigned all their hours, they're assigned to that slot.
    6. The person's availability is decremented, and if they have slots remaining, they're pushed back onto the heap.
    7. If any changes are made, the function will return True.
    """
    changed_in_this_run = False
    to_fill = finalized_df[availability_df.applymap(len) == count].isna()
    for row, col in zip(*np.where(to_fill)):
        available_people = availability_df.at[columns[row], labels[col]]
        if len(available_people) == count:
            while availability_heap:
                _, person_to_assign = heapq.heappop(availability_heap)
                # Ensure person is available and has remaining assignments
                if person_to_assign in [p[0] for p in available_people] and people_dict[person_to_assign] > 0:
                    finalized_df.at[columns[row], labels[col]] = person_to_assign
                    people_dict[person_to_assign] -= 1
                    remove_person_from_availability(person_to_assign, availability_df)
                    # Add back to heap if there are still slots left for this person
                    if people_dict[person_to_assign] > 0:
                        heapq.heappush(availability_heap, (-availability_hours[person_to_assign], person_to_assign))
                    changed_in_this_run = True
                    break
    return changed_in_this_run


def fill_remaining_slots(finalized_df):
    """Fill any remaining unfilled slots in the finalized dataframe."""
    """
    Fill any remaining unfilled slots in the finalized dataframe.

    Parameters:
    - finalized_df (pd.DataFrame): The dataframe representing the schedule.

    Returns:
    - pd.DataFrame: Returns the updated finalized dataframe with all available slots filled.

    Steps:
    1. Iterate through all cells in the finalized dataframe.
    2. For cells that have available people but aren't filled yet, the person with the least total hours from available people is chosen.
    3. This person is then assigned to the slot.
    4. The person's availability is decremented, and if necessary, removed from other available slots.
    """
    for row in range(finalized_df.shape[0]):
        for col in range(finalized_df.shape[1]):
                if len(availability_df.iloc[row, col])>0:
                    person_to_assign = find_least_hours(availability_df.iloc[row, col])             #8/29/30
                    if people_dict[person_to_assign] > 0:
                        finalized_df.iloc[row, col] = person_to_assign
                        people_dict[person_to_assign] -= 1
                        remove_person_from_availability(person_to_assign, availability_df)
    return finalized_df

def fill_slots(finalized_df):
    """Main function to fill all slots in the finalized dataframe."""
    """
    The main scheduling function to iteratively fill all slots in the finalized dataframe.

    Parameters:
    - finalized_df (pd.DataFrame): The dataframe representing the schedule.

    Returns:
    - pd.DataFrame: Returns the completely filled schedule.

    Steps:
    1. The function starts with the assumption that changes can be made.
    2. It enters a loop that continues until all slots are filled or no more changes can be made.
    3. In each iteration of the loop, it tries to fill slots where the number of available people ranges from 1 to the maximum available for any slot.
    4. If slots are filled in an iteration, it marks that changes were made.
    5. Once the iterative process is over, it calls `fill_remaining_slots` to handle any slots that might still be empty.
    """
    changed = True  # A flag to see if anything was changed in a full iteration
    while not all_slots_filled(finalized_df) and changed:
        changed = False  # Initially set to false for each iteration
        max_available_count = max(availability_df.applymap(len).values.ravel())
        for count in range(1, max_available_count+1):
            if fill_cells_by_count(count, finalized_df):  # Now it returns True/False based on changes
                changed = True
    return fill_remaining_slots(finalized_df)


def generate_final_schedule(uploaded_files,excluded_slots=set()):
    #print(f"These are uploaded files: {uploaded_files}")
    """ The function that connects front-end to Back-End"""
    global availability_df, people_dict
    availability_df, people_dict = process_all_files(uploaded_files)
    finalized_df = pd.DataFrame(data, columns=labels, index=columns)
    for (row, col) in excluded_slots:
        availability_df.iloc[row, col] = []

    finalized_df = fill_slots(finalized_df)  # fill_slots modifies the people_dict
    leftovers = {name: hours for name, hours in people_dict.items() if hours > 0}

    for (row, col) in excluded_slots:
        finalized_df.iloc[row, col] = "Lounge Closed"
    return finalized_df, leftovers


#finalized_df