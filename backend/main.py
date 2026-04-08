from face_emotion import detect_emotions_from_camera
from text_emotion import get_main_emotion, map_emotion
from music_mapper import recommend_music
from collections import Counter


def run_moodmate():

    print("🎥 Detecting face emotion...")

    try:
        face_emotions = detect_emotions_from_camera()
    except Exception as e:
        print("⚠️ Face detection failed:", e)
        face_emotions = []

    #  Normalize face emotions (lowercase + remove invalid ones)
    valid_emotions = ['angry', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    face_emotions = [str(e).lower() for e in face_emotions if str(e).lower() in valid_emotions]

    print("Face emotions:", face_emotions)

    print("\n💬 Enter your text:")
    text = input("How are you feeling? ")

    # 🧠 Text emotion
    try:
        text_raw = get_main_emotion(text)
        text_mapped = map_emotion(text_raw).lower()
    except Exception as e:
        print("⚠️ Text emotion failed:", e)
        text_mapped = "neutral"

    # Ensure text emotion is valid
    if text_mapped not in valid_emotions:
        text_mapped = "neutral"

    print("Text emotion:", text_mapped.capitalize())

    #  Step 1: Take recent frames (reduce noise)
    recent_faces = face_emotions[-20:] if face_emotions else []

    #  Step 2: Count face emotions
    face_count = Counter(recent_faces)

    #  Step 3: Give HIGH priority to text
    # (text is usually more reliable than face)
    face_count[text_mapped] += 5

    #  Step 4: Final decision
    if face_count:
        final_emotion = face_count.most_common(1)[0][0]
    else:
        final_emotion = text_mapped

    # 🔥 Step 5: Normalize (Capital form for music mapper)
    final_emotion = final_emotion.capitalize()

    print("\n🧠 Final Emotion:", final_emotion)

    print("\n🎵 Generating music recommendations...")

    try:
        songs = recommend_music([final_emotion])
    except Exception as e:
        print("⚠️ Music recommendation failed:", e)
        songs = ["Error generating recommendations"]

    print("\n🎶 Recommended Songs:\n")

    if not songs:
        print("No songs found.")
    else:
        for i, s in enumerate(songs, 1):
            print(f"{i}. {s}")


if __name__ == "__main__":
    run_moodmate()