
from frameit import SRL
from frameit.api.api_wrapper import create_app
from frameit.api.annotator import Annotator

srl = SRL()
#srl.loadFrame("ConversationFrame.json")
#srl.loadFrame("ExerciseFrame4-13_large.json")
#srl.loadFrame("MealFrame_4-16_seed63_drop_large.json")
srl.loadFrame("directions_v006.json")
srl.loadFrame("arrival_v003.json")
srl.loadFrame("hotel_facility_v003.json")

annotator = Annotator(srl)

app = create_app(annotator)

# this is a hack to fix the current issue
srl.parse('I will be arriving late.')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)


