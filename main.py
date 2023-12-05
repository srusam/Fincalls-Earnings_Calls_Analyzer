# Import the request library so the we can talk to the Assembly AI API
import requests
from api_secrets import API_KEY_ASSEMBLYAI
# To get the file name from the terminal
import sys
import time

# -------------------------------------------------------------------------------

# endpoint starts
# Endpoint to assembly ai to upload
upload_endpoint = "https://api.assemblyai.com/v2/upload"
# Transcription endpoint
transcript_endpoint = "https://api.assemblyai.com/v2/transcript"
# endpoint ends

# -------------------------------------------------------------------------------

#setting up the headers that are used for  Authentication   
headers = {'authorization': API_KEY_ASSEMBLYAI}

# -------------------------------------------------------------------------------

# The first argument (not the zeroth) is going to be the file name
filename = sys.argv[1]

# -------------------------------------------------------------------------------

# Upload section starts
def upload(filename):
    
    # -------------------------------------------------------------------------------
    
    # Reading the audio files starts
    # We are reading in chunks (5 megabytes) by using the read_file function
    def read_file(filename, chunk_size=5242880):
        with open(filename, 'rb') as _file:
            while True:
                data = _file.read(chunk_size)
                if not data:
                    break
                yield data
    # Reading the audio files ends
    
    # -------------------------------------------------------------------------------

    # When we upload our file to the assemble ai it happens through the post requests and also include the headers which contains our api key.
    upload_response = requests.post(upload_endpoint,headers=headers,data=read_file(filename)) 
    
    # -------------------------------------------------------------------------------

    # print(response.json())
    # Upload section ends
    
    # -------------------------------------------------------------------------------

    # json represents the data that we will send to assembly ai to transcribe. We have accepted it above but we need to extract it. When you run in terminal till the above steps, you get an audio_url which is used below.
    audio_url = upload_response.json()['upload_url']
    return audio_url

# -------------------------------------------------------------------------------

# Transcribe
def transcribe(audio_url):
    transcript_request = {"audio_url": audio_url}
    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    # Using the following print statement, we get a much longer response which contains the audio_url, the id and a lot more. We will be using the id from that response for polling
    # print(response.json())
    transcript_id = transcript_response.json()['id']
    return transcript_id

# audio_url = upload(filename)
# transcript_id = transcribe(audio_url)

# print(transcript_id)
# -------------------------------------------------------------------------------

def poll(transcript_id):
    # Poll - Keep polling the Assembly AI's API to see when the transcription is done
    # combine transcript endpoint with a slash in between with the transcript_id
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    # We have used get because when you send the data to an api, you use post request and when you gain some info you use get request
    polling_response = requests.get(polling_endpoint, headers=headers)
    # what a polling response looks like
    return polling_response.json()

def get_transcription_result_url(audio_url):
    transcript_id = transcribe(audio_url)
    while True:
        data = poll(transcript_id)
        if data['status']=='completed':
            return data, None
        elif data['status']=="error":  
            return data, data['error']
        
        print('The Earnings Call is under process...')
        time.sleep(30)
        

# print(data)
# Saving the transcript 
def save_transcript(audio_url):
    data, error = get_transcription_result_url(audio_url)

    if data:
        text_filename = filename + ".txt"
        with open(text_filename, "w") as f: 
            f.write(data['text'])
        print('Transcription saved!!!')
    elif error:
        print("Error!!!",error)
        
audio_url = upload(filename)
save_transcript(audio_url)