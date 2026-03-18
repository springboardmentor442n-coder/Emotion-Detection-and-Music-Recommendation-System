"""
API views for MoodMate emotion prediction and music recommendation.

Two endpoints:
    POST /api/predict/image/  —  Receives a selfie, returns emotion + recommendations
    POST /api/predict/text/   —  Receives text, returns emotion + recommendations
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image

from emotion.cnn_predictor import predict_emotion as predict_image_emotion
from emotion.roberta_predictor import predict_emotion as predict_text_emotion
from recommendation.recommender import get_recommendations


class ImagePredictView(APIView):
    """
    POST /api/predict/image/

    Expects:
        - image: uploaded image file (via multipart form data)
        - mode:  'match' or 'uplift' (optional, defaults to 'match')

    Returns:
        {
            "emotion": "happy",
            "recommendations": [ ... ]
        }
    """

    def post(self, request):
        # --- Validate image ---
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'error': 'No image file provided. Send an image via the "image" field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = request.data.get('mode', 'match')

        try:
            # Open the uploaded file as a PIL Image
            image = Image.open(image_file)

            # Predict emotion using CNN
            emotion = predict_image_emotion(image)

            # Determine the target emotion (may differ in uplift mode)
            target_emotion = emotion
            if mode == 'uplift':
                from recommendation.recommender import UPLIFT_MAP
                target_emotion = UPLIFT_MAP.get(emotion, emotion)

            # Get music recommendations
            recommendations = get_recommendations(emotion, mode=mode)

            return Response({
                'emotion': emotion,
                'target_emotion': target_emotion,
                'mode': mode,
                'recommendations': recommendations,
            })

        except Exception as e:
            return Response(
                {'error': f'Image prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TextPredictView(APIView):
    """
    POST /api/predict/text/

    Expects (JSON body):
        - text: the input sentence to classify
        - mode: 'match' or 'uplift' (optional, defaults to 'match')

    Returns:
        {
            "emotion": "sad",
            "recommendations": [ ... ]
        }
    """

    def post(self, request):
        # --- Validate text ---
        text = request.data.get('text')
        if not text or not text.strip():
            return Response(
                {'error': 'No text provided. Send a "text" field in the request body.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mode = request.data.get('mode', 'match')

        try:
            # Predict emotion using RoBERTa
            emotion = predict_text_emotion(text)

            # Determine the target emotion (may differ in uplift mode)
            target_emotion = emotion
            if mode == 'uplift':
                from recommendation.recommender import UPLIFT_MAP
                target_emotion = UPLIFT_MAP.get(emotion, emotion)

            # Get music recommendations
            recommendations = get_recommendations(emotion, mode=mode)

            return Response({
                'emotion': emotion,
                'target_emotion': target_emotion,
                'mode': mode,
                'recommendations': recommendations,
            })

        except Exception as e:
            return Response(
                {'error': f'Text prediction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
