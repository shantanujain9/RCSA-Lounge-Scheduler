from django.shortcuts import render
import pandas as pd
from . import schedule_script
from django.http import JsonResponse
import json

from django.shortcuts import render, redirect
from .forms import MultiFileUploadForm
from .schedule_script import process_all_files



def index(request):
    return render(request, 'scheduler_app/index.html')


#from .forms import MultiFileUploadForm  # Make sure you import the right form


def upload_files(request):
    if request.method == 'POST':
        # Print the uploaded files for debugging
        #print(f"request files: \n{request.FILES}")

        # Check if files are present in the request
        if 'files' in request.FILES:
            # Handle the files directly
            uploaded_files = request.FILES.getlist('files')
            # Process the uploaded files using your custom function
            availability_df, people_dict = process_all_files(uploaded_files)
            
            # Convert the dataframe to HTML table
            availability_html = availability_df.to_html(classes='table table-bordered')

            # Return success status, the HTML table, and any relevant data/message
            return JsonResponse({'status': 'success', 'message': 'Files uploaded and processed.', 'availability_html': availability_html})
        else:
            # If no files are present, return an error
            return JsonResponse({'status': 'error', 'message': 'No files uploaded.'})
        
    else:
        # If not a POST request, inform that only POST is supported.
        return JsonResponse({'status': 'error', 'message': 'Only POST requests are supported.'})




def generate_schedule(request):
    # Get excluded slots from the request data
    excluded_slots_json = request.POST.get('excluded_slots')
    excluded_slots_list = json.loads(excluded_slots_json)

    
    # Convert the list of strings to a set of tuple pairs
    excluded_slots = {(int(slot.split('-')[0]), int(slot.split('-')[1])) for slot in excluded_slots_list}

    # Check if files are present in the request
    if 'files' in request.FILES:
        uploaded_files = request.FILES.getlist('files')
    else:
        return JsonResponse({"error": "No files provided."}, status=400)

    finalized_df, leftovers = schedule_script.generate_final_schedule(uploaded_files, excluded_slots)
    
    if finalized_df is None:
        return JsonResponse({"error": "Failed to generate schedule. You are not following the instructions correctly. Pay attention! Read the given instructions carefully!"}, status=500)
    
    data = {
        "finalized_html": finalized_df.to_html(classes='table table-bordered'),
        "leftovers": leftovers
    }
    return JsonResponse(data)






