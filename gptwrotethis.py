import logging
import json
import azure.functions as func
from youtube_transcript_api import YouTubeTranscriptApi as yta
from youtube_transcript_api._errors import TranscriptsDisabled
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    video_id = req.params.get('id')
    query = req.params.get('q')
    
    if not video_id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            video_id = req_body.get('id')

    if video_id:
        try:
            transcript = yta.get_transcript(video_id)
        except TranscriptsDisabled:
            return func.HttpResponse(
                 "Transcripts are disabled for the specified video ID.",
                 status_code=404
            )
        except:
            return func.HttpResponse(
                 "No transcript available for the specified video ID.",
                 status_code=404
            )

        transcript_text =''
        for value in transcript:
            for key, val in value.items():
                if key == 'text':
                    transcript_text += val + ' '

        prefix = "https://www.youtube.com/watch?v=" + video_id + "&t="
        filtered_list = []

        for obj in transcript:
            if query in obj['text']:
                filtered_list.append(obj)

        start_values = []
        for obj in filtered_list:
            start_values.append(round(float(obj['start'])))
        start_values_with_prefix = [prefix + str(start_val) + 's' for start_val in start_values]

        transcript_lines = transcript_text.splitlines()
        final_transcript = ' '.join(transcript_lines)
        lowercased_transcript = final_transcript.lower()

        jsdata = {"VideoID": video_id, "Words": len(re.findall(r'\w+', final_transcript)), "QueryCount": lowercased_transcript.count(query), "VideoUrls": start_values_with_prefix ,  "Transcript": final_transcript}

        return func.HttpResponse(json.dumps(jsdata), mimetype="application/json", status_code=200)
    else:
        return func.HttpResponse(
             "Please provide a valid video ID in the query string or in the request body.",
             status_code=400
        )
