
from frameit import SRL
from frameit.api.api_wrapper import create_app
from frameit.api.annotator import Annotator

srl = SRL()

srl.loadFrame("srl_models/ConversationFrame_v13.json")
srl.loadFrame("srl_models/ExerciseFrame4-17_large_seed23_v22.json")
srl.loadFrame("srl_models/MealFrame_4-16_seed63_v12.json")

annotator = Annotator(srl)

app = create_app(annotator)


# this is a hack to fix the current issue
srl.parse('I had lunch with Maria.')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5556)
    

